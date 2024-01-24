from datetime import datetime, timedelta, timezone
import requests

from .logging import logger
from .db.database import session
from . import time_date_conversions as tdc

from ..domain.realtime.stop_time.model import RTStopTimeModel
from ..domain.realtime.trip.model import RTTripModel
from ..domain.route.model import RouteModel
from ..domain.trip.model import TripModel
from ..domain.realtime.vehicle.model import RTVehicleModel

import rich.progress as rp

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


class RealTimeImporter:
    def __init__(self, url: str, api_key: str, dataset: str) -> None:
        self.url = url
        self.api_key = api_key
        self.dataset = dataset

    def get_data(self) -> dict | None:
        # with open("./tests/gtfs_test_data/TFI/realtime_sample_response.json") as f:
        # return json.loads(f.read())

        header = {
            "Cache-Control": "no-cache",
            "x-api-key": self.api_key,
        }

        response = requests.get(self.url, headers=header)
        if response.status_code != 200:
            logger.warning(f"RealTime: {self.url} returned {response.status_code}")
            return None

        try:
            return response.json()
        except requests.exceptions.JSONDecodeError as e:
            logger.error(f"RealTime: {self.url} returned invalid JSON: {e}")
            return None

    def clear_table_stop_trip(self):
        """Clears the table in the database that corresponds to the dataset for rows older than 60 mins"""

        sixty_mins_ago = datetime.now(timezone.utc) - timedelta(minutes=60)
        with session:
            session.query(RTStopTimeModel).filter(
                RTStopTimeModel.created_at < sixty_mins_ago, RTStopTimeModel.dataset == self.dataset
            ).delete()
            session.query(RTTripModel).filter(
                RTTripModel.created_at < sixty_mins_ago, RTTripModel.dataset == self.dataset
            ).delete()
            session.commit()

    def import_stop_times(self, data: dict) -> int:
        """Imports the stop times from the dataset into the database"""

        stop_time_update_count = sum(
            len(item["trip_update"].get("stop_time_update", []))
            for item in data["entity"]
            if item["trip_update"]["trip"]["schedule_relationship"] not in ["CANCELED", "ADDED"]
        )
        with rp.Progress(*progress_columns) as progress:
            task = progress.add_task("[green]Importing RT Stop Times...", total=stop_time_update_count)

            with session:
                objects_to_commit = []
                # Foreign key exceptions
                trips_in_db = session.query(TripModel.id).filter(TripModel.dataset == self.dataset).all()
                trips_in_db = {trip[0] for trip in trips_in_db}

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

                            arrival = stop_time.get("arrival", {})
                            departure = stop_time.get("departure", {})

                            new_rt_stop_time = RTStopTimeModel(
                                stop_id=stop_time.get("stop_id"),
                                trip_id=trip.get("trip_id"),
                                stop_sequence=stop_time.get("stop_sequence"),
                                schedule_relationship=stop_time.get("schedule_relationship"),
                                arrival_delay=arrival.get("delay"),
                                departure_delay=departure.get("delay"),
                                entity_id=item.get("id"),
                                dataset=self.dataset,
                            )

                            objects_to_commit.append(new_rt_stop_time)
                            progress.update(task, advance=1)

                    try:
                        session.bulk_save_objects(objects_to_commit)
                        session.commit()
                    except Exception as e:
                        logger.error(f"RealTime: {self.url} failed to commit stop times: {e}")
                except Exception as e:
                    logger.warning(f"RealTime: {self.url} returned invalid JSON in entities: {e}")
                    return 0

                return stop_time_update_count

    def import_trips(self, data: dict) -> int:
        """Imports the trips from the dataset into the database"""

        trip_update_count = sum(
            1
            for item in data["entity"]
            if item["trip_update"]["trip"]["schedule_relationship"] not in ["CANCELED", "ADDED"]
        )
        with rp.Progress(*progress_columns) as progress:
            task = progress.add_task("[green]Importing RT Trips...", total=trip_update_count)

            with session:
                objects_to_commit = []
                # Foreign key exceptions
                routes_in_db = session.query(RouteModel.id).filter(RouteModel.dataset == self.dataset).all()
                routes_in_db = {route[0] for route in routes_in_db}

                for item in data.get("entity", []):
                    trip_update = item.get("trip_update", {})
                    trip = trip_update.get("trip", {})
                    schedule_relationship = trip.get("schedule_relationship")

                    if schedule_relationship in ["CANCELED", "ADDED"]:
                        continue  # TODO: Import canceled and added trips

                    # Foreign key exceptions
                    if trip.get("route_id") not in routes_in_db:
                        continue

                    new_rt_trip = RTTripModel(
                        trip_id=trip.get("trip_id"),
                        route_id=trip.get("route_id"),
                        start_time=tdc.convert_29_hours_to_24_hours(trip.get("start_time")),
                        start_date=tdc.convert_joined_date_to_date(trip.get("start_date")),
                        schedule_relationship=schedule_relationship,
                        direction=trip.get("direction_id"),
                        entity_id=item.get("id"),
                        dataset=self.dataset,
                    )

                    objects_to_commit.append(new_rt_trip)
                    progress.update(task, advance=1)

                try:
                    session.bulk_save_objects(objects_to_commit)
                    session.commit()
                except Exception as e:
                    logger.error(f"RealTime: {self.url} failed to commit trips: {e}")

        return trip_update_count


class RealTimeVehiclesImporter:
    def __init__(self, url: str, api_key: str, dataset: str) -> None:
        self.url = url
        self.api_key = api_key
        self.dataset = dataset

    def get_data(self) -> dict | None:
        # import json
        # with open("./tests/gtfs_test_data/TFI/realtime_vehicles_sample_response.json") as f:
        #     return json.loads(f.read())

        header = {
            "Cache-Control": "no-cache",
            "x-api-key": self.api_key,
        }

        response = requests.get(self.url, headers=header)
        if response.status_code != 200:
            logger.warning(f"RealTime Vehicles: {self.url} returned {response.status_code}")
            return None

        try:
            return response.json()
        except requests.exceptions.JSONDecodeError as e:
            logger.error(f"RealTime Vehicles: {self.url} returned invalid JSON: {e}")
            return None

    def clear_table_vehicles(self):
        """Clears the table in the database that corresponds to the dataset for rows older than 60 mins"""

        sixty_mins_ago = datetime.now(timezone.utc) - timedelta(minutes=60)
        with session:
            session.query(RTVehicleModel).filter(
                RTVehicleModel.created_at < sixty_mins_ago, RTVehicleModel.dataset == self.dataset
            ).delete()
            session.commit()

    def import_vehicles(self, data: dict) -> int:
        """Imports the vehicles from the dataset into the database"""

        vehicle_count = sum(
            1
            for item in data["entity"]
            if item["vehicle"]["trip"]["schedule_relationship"] not in ["CANCELED", "ADDED"]
        )
        with rp.Progress(*progress_columns) as progress:
            task = progress.add_task("[green]Importing RT Vehicles...", total=vehicle_count)

            with session:
                objects_to_commit = []
                # Foreign key exceptions
                trips_in_db = session.query(TripModel.id).filter(TripModel.dataset == self.dataset).all()
                trips_in_db = {trip[0] for trip in trips_in_db}

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
                        session.bulk_save_objects(objects_to_commit)
                        session.commit()
                    except Exception as e:
                        logger.error(f"RealTime: {self.url} failed to commit vehicles: {e}")
                except Exception as e:
                    logger.warning(f"RealTime: {self.url} returned invalid JSON in entities: {e}")
                    return 0

                return vehicle_count
