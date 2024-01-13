import requests

from SimplyTransport.lib.logging import logger
from SimplyTransport.lib.db.database import session
from SimplyTransport.lib import time_date_conversions as tdc

from SimplyTransport.domain.realtime.stop_time.model import RTStopTimeModel
from SimplyTransport.domain.realtime.trip.model import RTTripModel
from SimplyTransport.domain.route.model import RouteModel
from SimplyTransport.domain.trip.model import TripModel

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
        """Clears the table in the database that corresponds to the dataset"""

        with session:
            session.query(RTStopTimeModel).filter(RTStopTimeModel.dataset == self.dataset).delete()
            session.query(RTTripModel).filter(RTTripModel.dataset == self.dataset).delete()
            session.commit()

    def import_stop_times(self, data: dict) -> int:
        """Imports the stop times from the dataset into the database"""

        stop_time_update_count = sum(
            len(item["trip_update"]["stop_time_update"])
            for item in data["entity"]
            if item["trip_update"]["trip"]["schedule_relationship"] != "CANCELED"
            and item["trip_update"]["trip"]["schedule_relationship"] != "ADDED"
        )
        with rp.Progress(*progress_columns) as progress:
            task = progress.add_task("[green]Importing RT Stop Times...", total=stop_time_update_count)

            with session:
                objects_to_commit = []
                # Foreign key exceptions
                trips_in_db = session.query(TripModel.id).filter(TripModel.dataset == self.dataset).all()
                trips_in_db = {trip[0] for trip in trips_in_db}

                try:
                    for item in data["entity"]:
                        try:
                            if item["trip_update"]["trip"]["schedule_relationship"] == "CANCELED":
                                continue  # TODO: Import canceled trips

                            if item["trip_update"]["trip"]["schedule_relationship"] == "ADDED":
                                continue  # TODO: Import added trips

                            # Foreign key exceptions
                            if item["trip_update"]["trip"]["trip_id"] not in trips_in_db:
                                continue

                            for stop_time in item["trip_update"]["stop_time_update"]:
                                arrival_delay = None
                                departure_delay = None

                                if stop_time["schedule_relationship"] == "SKIPPED":
                                    continue  # TODO: Import skipped stops

                                if "arrival" in stop_time and "delay" in stop_time["arrival"]:
                                    arrival_delay = stop_time["arrival"]["delay"]

                                if "departure" in stop_time and "delay" in stop_time["departure"]:
                                    departure_delay = stop_time["departure"]["delay"]

                                new_rt_stop_time = RTStopTimeModel(
                                    stop_id=stop_time["stop_id"],
                                    trip_id=item["trip_update"]["trip"]["trip_id"],
                                    stop_sequence=stop_time["stop_sequence"],
                                    schedule_relationship=stop_time["schedule_relationship"],
                                    arrival_delay=arrival_delay,
                                    departure_delay=departure_delay,
                                    entity_id=item["id"],
                                    dataset=self.dataset,
                                )

                                objects_to_commit.append(new_rt_stop_time)
                                progress.update(task, advance=1)

                        except KeyError as e:
                            logger.warning(
                                f"RealTime: {self.url} returned invalid JSON in stop times: {e} - {item}"
                            )
                            continue
                    try:
                        session.bulk_save_objects(objects_to_commit)
                        session.commit()
                    except Exception as e:
                        logger.error(f"RealTime: {self.url} failed to commit stop times: {e}")
                except KeyError as e:
                    logger.warning(f"RealTime: {self.url} returned invalid JSON in entitys: {e}")
                    return 0

                return stop_time_update_count

    def import_trips(self, data: dict) -> int:
        """Imports the trips from the dataset into the database"""

        trip_update_count = sum(
            1
            for item in data["entity"]
            if item["trip_update"]["trip"]["schedule_relationship"] != "CANCELED"
            and item["trip_update"]["trip"]["schedule_relationship"] != "ADDED"
        )
        with rp.Progress(*progress_columns) as progress:
            task = progress.add_task("[green]Importing RT Trips...", total=trip_update_count)

            with session:
                objects_to_commit = []
                # Foreign key exceptions
                routes_in_db = session.query(RouteModel.id).filter(RouteModel.dataset == self.dataset).all()
                routes_in_db = {route[0] for route in routes_in_db}

                try:
                    for item in data["entity"]:
                        try:
                            if item["trip_update"]["trip"]["schedule_relationship"] == "CANCELED":
                                continue  # TODO: Import canceled trips

                            if item["trip_update"]["trip"]["schedule_relationship"] == "ADDED":
                                continue  # TODO: Import added trips

                            # Foreign key exceptions
                            if item["trip_update"]["trip"]["route_id"] not in routes_in_db:
                                continue

                            new_rt_trip = RTTripModel(
                                trip_id=item["trip_update"]["trip"]["trip_id"],
                                route_id=item["trip_update"]["trip"]["route_id"],
                                start_time=tdc.convert_29_hours_to_24_hours(
                                    item["trip_update"]["trip"]["start_time"]
                                ),
                                start_date=tdc.convert_joined_date_to_date(
                                    item["trip_update"]["trip"]["start_date"]
                                ),
                                schedule_relationship=item["trip_update"]["trip"]["schedule_relationship"],
                                direction=item["trip_update"]["trip"]["direction_id"],
                                entity_id=item["id"],
                                dataset=self.dataset,
                            )

                            objects_to_commit.append(new_rt_trip)
                            progress.update(task, advance=1)
                        except KeyError as e:
                            logger.warning(
                                f"RealTime: {self.url} returned invalid JSON in trips: {e} - {item}"
                            )
                            continue
                    try:
                        session.bulk_save_objects(objects_to_commit)
                        session.commit()
                    except Exception as e:
                        logger.error(f"RealTime: {self.url} failed to commit trips: {e}")

                except KeyError as e:
                    logger.warning(f"RealTime: {self.url} returned invalid JSON in entitys: {e}")
                    return 0

                return trip_update_count
