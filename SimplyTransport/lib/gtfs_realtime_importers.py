import requests
from SimplyTransport.lib.logging import logger
from SimplyTransport.lib.db.database import session

from SimplyTransport.domain.realtime.stop_time.model import RTStopTimeModel
from SimplyTransport.domain.realtime.trip.model import RTTripModel

class RealTimeImporter:
    def __init__(self, url:str, api_key:str, dataset:str) -> None:
        self.url = url
        self.api_key = api_key
        self.dataset = dataset

    def get_data(self) -> dict | None:
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
        """Clears the table in the database that corresponds to the file"""

        with session:
            session.query(RTStopTimeModel).filter(RTStopTimeModel.dataset == self.dataset).delete()
            session.query(RTTripModel).filter(RTTripModel.dataset == self.dataset).delete()
            session.commit()

    def import_stop_times(self, data:dict):
        try: 
            for item in data["entity"]:
                try:
                    for stop_time in item["trip_update"]["stop_time_update"]:
                        pass # TODO: Import stop times
                except KeyError as e:
                    logger.warning(f"RealTime: {self.url} returned invalid JSON in stop times: {e}")
                    pass
        except KeyError as e:
            logger.warning(f"RealTime: {self.url} returned invalid JSON in entitys: {e}")
            return None
    
    def import_trips(self, data:dict):
        try: 
            for item in data["entity"]:
                try:
                    pass # TODO: Import trips
                except KeyError as e:
                    logger.warning(f"RealTime: {self.url} returned invalid JSON in trips: {e}")
                    pass
        except KeyError as e:
            logger.warning(f"RealTime: {self.url} returned invalid JSON in entitys: {e}")
            return None

