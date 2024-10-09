from json import JSONDecodeError
from typing import List
import httpx
from datetime import datetime, timedelta, timezone
from sqlalchemy import delete, select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from .logging.logging import provide_logger
from .db.database import async_session_factory
from . import time_date_conversions as tdc

from ..domain.realtime.stop_time.model import RTStopTimeModel
from ..domain.realtime.trip.model import RTTripModel
from ..domain.route.model import RouteModel
from ..domain.trip.model import TripModel
from ..domain.realtime.vehicle.model import RTVehicleModel
from ..domain.stop.model import StopModel

import rich.progress as rp

logger = provide_logger(__name__)

progress_columns = (
    rp.SpinnerColumn(finished_text="✅"),
    "[progress.description]{task.description}",
    rp.BarColumn(),
    rp.MofNCompleteColumn(),
    rp.TaskProgressColumn(),
    "|| Taken:",
    rp.TimeElapsedColumn(),
    "|| Left:",
    rp.TimeRemainingColumn(),
)

RETENTION_PERIOD = datetime.now(timezone.utc) - timedelta(minutes=30)


class RealTimeImporter:
    def __init__(self, url: str, api_key: str, dataset: str) -> None:
        self.url = url
        self.api_key = api_key
        self.dataset = dataset

    def bulk_upsert_statement(self, model, objects_to_commit, index_elements: List[str], update_dict: dict):
        stmt = insert(model).values(objects_to_commit)
        stmt = stmt.on_conflict_do_update(
            index_elements=index_elements,
            set_={key: getattr(stmt.excluded, key) for key in update_dict},
        )
        return stmt

    async def bulk_upsert(
        self, model, objects_to_commit, index_elements: List[str], update_dict: dict, session: AsyncSession
    ):
        batch_size = 3000
        for i in range(0, len(objects_to_commit), batch_size):
            batch = objects_to_commit[i : i + batch_size]
            stmt = self.bulk_upsert_statement(model, batch, index_elements, update_dict)
            await session.execute(stmt)
        await session.commit()

    async def get_data(self) -> dict | None:
        # import json
        # with open("./tests/gtfs_test_data/TFI/realtime_sample_response.json") as f:
        #     return json.loads(f.read())

        headers = {
            "Cache-Control": "no-cache",
            "x-api-key": self.api_key,
        }

        async with httpx.AsyncClient() as client:
            response = await client.get(self.url, headers=headers)
            if response.status_code != 200:
                logger.warning(f"RealTime: {self.url} returned {response.status_code}")
                return None

            try:
                return response.json()
            except JSONDecodeError as e:
                logger.error(f"RealTime: {self.url} returned invalid JSON: {e}")
                return None

    async def clear_table_stop_trip(self):
        """Clears the table in the database that corresponds to the dataset for rows older than 60 mins"""

        async with async_session_factory() as session:
            delete_stoptime = delete(RTStopTimeModel).where(
                RTStopTimeModel.created_at < RETENTION_PERIOD,
                RTStopTimeModel.dataset == self.dataset,
            )
            await session.execute(delete_stoptime)

            delete_trip = delete(RTTripModel).where(
                RTTripModel.created_at < RETENTION_PERIOD,
                RTTripModel.dataset == self.dataset,
            )
            await session.execute(delete_trip)

            await session.commit()

    async def import_stop_times(self, data: dict, progress: rp.Progress) -> int:
        """Imports the stop times from the dataset into the database"""

        stop_time_update_count = sum(
            len(item["trip_update"].get("stop_time_update", []))
            for item in data["entity"]
            if item["trip_update"]["trip"]["schedule_relationship"] not in ["CANCELED", "ADDED"]
        )
        task = progress.add_task("[green]Importing RT Stop Times...", total=stop_time_update_count)

        async with async_session_factory() as session:
            objects_to_commit = []
            # Foreign key exceptions
            result_trips = await session.execute(
                select(TripModel.id).filter(TripModel.dataset == self.dataset).distinct()
            )
            trips_in_db = set(result_trips.scalars())

            result_stops = await session.execute(
                select(StopModel.id).filter(StopModel.dataset == self.dataset).distinct()
            )
            stops_in_db = set(result_stops.scalars())

            try:
                for item in data.get("entity", []):
                    trip_update = item.get("trip_update", {})
                    trip = trip_update.get("trip", {})
                    schedule_relationship = trip.get("schedule_relationship")

                    if schedule_relationship in ["CANCELED", "ADDED"]:
                        continue  # TODO: Import canceled and added trips

                    # Foreign key exceptions
                    if trip.get("trip_id") not in trips_in_db:
                        continue

                    for stop_time in trip_update.get("stop_time_update", []):
                        if stop_time.get("schedule_relationship") == "SKIPPED":
                            continue  # TODO: Import skipped stops

                        if stop_time.get("stop_id") not in stops_in_db:
                            continue

                        arrival = stop_time.get("arrival", {})
                        departure = stop_time.get("departure", {})

                        new_rt_stop_time = {
                            "stop_id": stop_time.get("stop_id"),
                            "trip_id": trip.get("trip_id"),
                            "stop_sequence": stop_time.get("stop_sequence"),
                            "schedule_relationship": stop_time.get("schedule_relationship"),
                            "arrival_delay": arrival.get("delay"),
                            "departure_delay": departure.get("delay"),
                            "entity_id": item.get("id"),
                            "dataset": self.dataset,
                        }

                        objects_to_commit.append(new_rt_stop_time)
                        progress.update(task, advance=1)

                if objects_to_commit:
                    try:
                        await self.bulk_upsert(
                            RTStopTimeModel,
                            objects_to_commit,
                            ["stop_id", "trip_id", "stop_sequence", "dataset"],
                            {
                                "arrival_delay": "arrival_delay",
                                "departure_delay": "departure_delay",
                                "entity_id": "entity_id",
                                "dataset": "dataset",
                            },
                            session,
                        )
                    except Exception as e:
                        logger.error(f"RealTime: {self.url} failed to commit stop times: {e}")
            except Exception as e:
                logger.warning(f"RealTime: {self.url} returned invalid JSON in entities: {e}")
                return 0

        return stop_time_update_count

    async def import_trips(self, data: dict, progress: rp.Progress) -> int:
        """Imports the trips from the dataset into the database"""

        trip_update_count = sum(
            1
            for item in data["entity"]
            if item["trip_update"]["trip"]["schedule_relationship"] not in ["CANCELED", "ADDED"]
        )
        task = progress.add_task("[green]Importing RT Trips...", total=trip_update_count)

        async with async_session_factory() as session:
            objects_to_commit = []
            # Foreign key exceptions
            result_routes = await session.execute(
                select(RouteModel.id).filter(RouteModel.dataset == self.dataset).distinct()
            )
            routes_in_db = set(result_routes.scalars())
            result_trips = await session.execute(
                select(TripModel.id).filter(TripModel.dataset == self.dataset).distinct()
            )
            trips_in_db = set(result_trips.scalars())

            for item in data.get("entity", []):
                trip_update = item.get("trip_update", {})
                trip = trip_update.get("trip", {})
                schedule_relationship = trip.get("schedule_relationship")

                if schedule_relationship in ["CANCELED", "ADDED"]:
                    continue  # TODO: Import canceled and added trips

                # Foreign key exceptions
                if trip.get("route_id") not in routes_in_db:
                    continue

                if trip.get("trip_id") not in trips_in_db:
                    continue

                new_rt_trip = {
                    "trip_id": trip.get("trip_id"),
                    "route_id": trip.get("route_id"),
                    "start_time": tdc.convert_29_hours_to_24_hours(trip.get("start_time")),
                    "start_date": tdc.convert_joined_date_to_date(trip.get("start_date")),
                    "schedule_relationship": schedule_relationship,
                    "direction": trip.get("direction_id"),
                    "entity_id": item.get("id"),
                    "dataset": self.dataset,
                }

                objects_to_commit.append(new_rt_trip)
                progress.update(task, advance=1)

            if objects_to_commit:
                try:
                    await self.bulk_upsert(
                        RTTripModel,
                        objects_to_commit,
                        ["trip_id", "route_id", "dataset"],
                        {
                            "start_time": "start_time",
                            "start_date": "start_date",
                            "schedule_relationship": "schedule_relationship",
                            "entity_id": "entity_id",
                            "dataset": "dataset",
                        },
                        session,
                    )
                except Exception as e:
                    logger.error(f"RealTime: {self.url} failed to commit trips: {e}")

        return trip_update_count


class RealTimeVehiclesImporter:
    def __init__(self, url: str, api_key: str, dataset: str) -> None:
        self.url = url
        self.api_key = api_key
        self.dataset = dataset

    async def get_data(self) -> dict | None:
        # import json
        # with open("./tests/gtfs_test_data/TFI/realtime_vehicles_sample_response.json") as f:
        #     return json.loads(f.read())

        headers = {
            "Cache-Control": "no-cache",
            "x-api-key": self.api_key,
        }

        async with httpx.AsyncClient() as client:
            response = await client.get(self.url, headers=headers)
            if response.status_code != 200:
                logger.warning(f"RealTime Vehicles: {self.url} returned {response.status_code}")
                return None

            try:
                return response.json()
            except JSONDecodeError as e:
                logger.error(f"RealTime Vehicles: {self.url} returned invalid JSON: {e}")
                return None

    async def clear_table_vehicles(self):
        """Clears the table in the database that corresponds to the dataset for rows older than 60 mins"""

        async with async_session_factory() as session:
            delete_vehicles = delete(RTVehicleModel).where(
                RTVehicleModel.created_at < RETENTION_PERIOD,
                RTVehicleModel.dataset == self.dataset,
            )
            await session.execute(delete_vehicles)
            await session.commit()

    async def import_vehicles(self, data: dict) -> int:
        """Imports the vehicles from the dataset into the database"""

        vehicle_count = sum(
            1
            for item in data["entity"]
            if item["vehicle"]["trip"]["schedule_relationship"] not in ["CANCELED", "ADDED"]
        )
        with rp.Progress(*progress_columns) as progress:
            task = progress.add_task("[green]Importing RT Vehicles...", total=vehicle_count)

            async with async_session_factory() as session:
                objects_to_commit = []
                # Foreign key exceptions
                result_trips = await session.execute(
                    select(TripModel.id).filter(TripModel.dataset == self.dataset).distinct()
                )
                trips_in_db = set(result_trips.scalars())

                try:
                    for item in data.get("entity", []):
                        vehicle_update = item.get("vehicle", {})
                        trip = vehicle_update.get("trip", {})
                        schedule_relationship = trip.get("schedule_relationship")

                        if schedule_relationship in ["CANCELED", "ADDED"]:
                            continue  # TODO: Import canceled and added trips

                        # Foreign key exceptions
                        if trip.get("trip_id") not in trips_in_db:
                            continue

                        new_rt_vehicle = RTVehicleModel(
                            vehicle_id=int(vehicle_update.get("vehicle", {}).get("id")),
                            trip_id=trip.get("trip_id"),
                            time_of_update=datetime.fromtimestamp(int(vehicle_update.get("timestamp"))),
                            lat=vehicle_update.get("position", {}).get("latitude"),
                            lon=vehicle_update.get("position", {}).get("longitude"),
                            dataset=self.dataset,
                        )

                        objects_to_commit.append(new_rt_vehicle)
                        progress.update(task, advance=1)

                    try:
                        session.add_all(objects_to_commit)
                        await session.commit()
                    except Exception as e:
                        logger.error(f"RealTime: {self.url} failed to commit vehicles: {e}")
                except Exception as e:
                    logger.warning(f"RealTime: {self.url} returned invalid JSON in entities: {e}")
                    return 0

                return vehicle_count
