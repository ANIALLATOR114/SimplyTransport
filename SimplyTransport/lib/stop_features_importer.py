from geojson import FeatureCollection
from datetime import datetime
from SimplyTransport.domain.stop.model import StopModel

from SimplyTransport.lib.db.database import session

from SimplyTransport.domain.stop_features.model import StopFeatureModel
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


class StopFeaturesImporter:
    def __init__(
        self,
        dataset: str,
        stops: list[FeatureCollection],
        poles: list[FeatureCollection],
        shelters: list[FeatureCollection],
        rtpis: list[FeatureCollection],
    ):
        self.dataset = dataset
        self.stops = stops
        self.poles = poles
        self.shelters = shelters
        self.rtpis = rtpis

    def clear_database(self):
        """Clears the table in the database that corresponds to the dataset"""

        with rp.Progress(*progress_columns) as progress:
            task = progress.add_task("[green]Clearing database...", total=1)
            with session:
                session.query(StopFeatureModel).filter(StopFeatureModel.dataset == self.dataset).delete()
                session.commit()
                progress.update(task, advance=1)

    def import_stop_features(self) -> dict:
        """Imports stop features from the given dataset"""

        total_stop_features = len(self.stops["features"])

        with rp.Progress(*progress_columns) as progress:
            task = progress.add_task("[green]Importing Stop Features...", total=total_stop_features)

            objects_to_commit = []

            existing_stops = set(
                stop_id[0]
                for stop_id in session.query(StopModel.id).filter(StopModel.dataset == self.dataset).all()
            )

            for stop in self.stops["features"]:
                if stop["properties"]["AtcoCode"] == "":
                    progress.update(task, advance=1)
                    continue

                if stop["properties"]["AtcoCode"] not in existing_stops:
                    progress.update(task, advance=1)
                    continue

                if stop["properties"]["IsSurveyed"] == "0":
                    survey_parsed_to_bool = False
                else:
                    survey_parsed_to_bool = True

                stop_feature = StopFeatureModel(
                    stop_id=stop["properties"]["AtcoCode"],
                    stop_name_ie=stop["properties"]["SCN_Gaeilge"],
                    stop_type=stop["properties"]["StopType"],
                    bearing=stop["properties"]["Bearing"],
                    nptg_locality_ref=stop["properties"]["NptgLocalityRef"],
                    bays=stop["properties"]["PtBayCount"],
                    standing_area=stop["properties"]["StandingArea"],
                    bike_stand=stop["properties"]["BikeStand"],
                    bench=stop["properties"]["Bench"],
                    bin=stop["properties"]["Bin"],
                    stop_accessability=stop["properties"]["StopAccessibility"],
                    wheelchair_accessability=stop["properties"]["WheelchairAccessibility"],
                    castle_kerbing=stop["properties"]["CastleKerbing"],
                    footpath_to_stop=stop["properties"]["FootpathToStop"],
                    step_at_stop=stop["properties"]["StepAtStop"],
                    bike_lane_front=stop["properties"]["BikeLaneFront"],
                    bike_lane_rear=stop["properties"]["BikeLaneRear"],
                    surveyed=survey_parsed_to_bool,
                    ud_surveyor=stop["properties"]["UD_Surveyor"],
                    ud_calculated=stop["properties"]["UD_Calculated"],
                    rtpi_active=False,
                    shelter_active=False,
                    pole_active=False,
                    dataset=self.dataset,
                )

                for i, rtpi in enumerate(self.rtpis["features"]):
                    if rtpi["properties"]["AtcoCode"] == stop_feature.stop_id:
                        stop_feature.rtpi_active = True
                        stop_feature.lines = rtpi["properties"]["Name"]
                        stop_feature.integrated_into_shelter = rtpi["properties"]["IntegratedIntoShelter"]
                        stop_feature.last_updated_rtpi = datetime.strptime(
                            rtpi["properties"]["LastUpdatedDateUtc"][:-1], "%Y-%m-%d %H:%M:%S.%f"
                        )
                        del self.rtpis["features"][i]
                        break

                for i, shelter in enumerate(self.shelters["features"]):
                    if shelter["properties"]["AtcoCode"] == stop_feature.stop_id:
                        stop_feature.shelter_active = True
                        stop_feature.shelter_description = shelter["properties"]["Description"]
                        stop_feature.shelter_type = shelter["properties"]["ShelterTypeId"]
                        stop_feature.power = shelter["properties"]["Power"]
                        stop_feature.light = shelter["properties"]["Light"]
                        stop_feature.last_updated_shelter = datetime.strptime(
                            shelter["properties"]["LastUpdatedDateUtc"][:-1],
                            "%Y-%m-%d %H:%M:%S.%f",
                        )
                        del self.shelters["features"][i]
                        break

                for i, pole in enumerate(self.poles["features"]):
                    if pole["properties"]["AtcoCode"] == stop_feature.stop_id:
                        stop_feature.pole_active = True
                        stop_feature.position = pole["properties"]["Position"]
                        stop_feature.socket_type = pole["properties"]["SocketType"]
                        stop_feature.pole_type = pole["properties"]["PoleType"]
                        stop_feature.last_updated_pole = datetime.strptime(
                            pole["properties"]["LastUpdatedDateUtc"][:-1], "%Y-%m-%d %H:%M:%S.%f"
                        )
                        del self.poles["features"][i]
                        break

                objects_to_commit.append(stop_feature)
                progress.update(task, advance=1)

            session.bulk_save_objects(objects_to_commit)
            session.commit()

        return {
            "total_stops": len(self.stops["features"]),
            "total_poles": len(self.poles["features"]),
            "total_shelters": len(self.shelters["features"]),
            "total_rtpis": len(self.rtpis["features"]),
            "total_added_to_database": len(objects_to_commit),
        }
