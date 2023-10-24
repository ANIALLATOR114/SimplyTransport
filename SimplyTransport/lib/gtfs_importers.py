import csv
from datetime import datetime

import rich.progress as rp

from SimplyTransport.domain.agency.model import AgencyModel
from SimplyTransport.domain.calendar.model import CalendarModel
from SimplyTransport.lib.db.database import session

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


def get_importer_for_file(file: str, reader: csv.DictReader, row_count: int, dataset: str):
    """Maps a file name to the appropriate importer class"""

    map_file_to_importer = {"agency.txt": AgencyImporter, "calendar.txt": CalendarImporter}
    try:
        importer_class = map_file_to_importer[file]
    except KeyError:
        raise ValueError(f"File '{file}' does not have a supported importer.")
    importer = importer_class(reader, row_count, dataset)
    return importer


class GTFSImporter:
    def __init__(self, filename: str, path: str, batchsize: int = 1000):
        self.path = path
        self.filename = filename
        self.batchsize = batchsize

    def get_reader(self):
        """Returns a csv.DictReader object"""

        with open(self.path + self.filename, "r", encoding="utf8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                yield row

    def get_row_count(self):
        """Returns the number of rows in the file"""

        with rp.open(
            self.path + self.filename,
            "r",
            encoding="utf8",
            description=f"Reading {self.filename}",
            transient=True,
        ) as f:
            reader = csv.reader(f)
            next(reader)  # Skip the header row
            return sum(1 for _ in reader)


class AgencyImporter(GTFSImporter):
    def __init__(self, reader: csv.DictReader, row_count: int, dataset: str):
        self.reader = reader
        self.row_count = row_count
        self.dataset = dataset

    def __str__(self) -> str:
        return "AgencyImporter"

    def import_data(self):
        """Imports the data from the csv.DictReader object into the database"""

        with rp.Progress(*progress_columns) as progress:
            task = progress.add_task(f"[green]Importing Agencies...", total=self.row_count)
            with session:
                for row in self.reader:
                    new_agency = AgencyModel(
                        id=row["agency_id"],
                        name=row["agency_name"],
                        url=row["agency_url"],
                        timezone=row["agency_timezone"],
                        dataset=self.dataset,
                    )
                    session.add(new_agency)
                    progress.update(task, advance=1)
                session.commit()

    def clear_table(self):
        """Clears the table in the database that corresponds to the file"""

        with session:
            session.query(AgencyModel).filter(AgencyModel.dataset == self.dataset).delete()
            session.commit()


class CalendarImporter(GTFSImporter):
    def __init__(self, reader: csv.DictReader, row_count: int, dataset: str):
        self.reader = reader
        self.row_count = row_count
        self.dataset = dataset

    def __str__(self) -> str:
        return "CalendarImporter"

    def import_data(self):
        """Imports the data from the csv.DictReader object into the database"""

        with rp.Progress(*progress_columns) as progress:
            task = progress.add_task(f"[green]Importing Calendars...", total=self.row_count)
            with session:
                for row in self.reader:
                    new_calendar = CalendarModel(
                        id=row["service_id"],
                        monday=row["monday"],
                        tuesday=row["tuesday"],
                        wednesday=row["wednesday"],
                        thursday=row["thursday"],
                        friday=row["friday"],
                        saturday=row["saturday"],
                        sunday=row["sunday"],
                        start_date=datetime.strptime(row["start_date"], "%Y%m%d").date(),
                        end_date=datetime.strptime(row["end_date"], "%Y%m%d").date(),
                        dataset=self.dataset,
                    )
                    session.add(new_calendar)
                    progress.update(task, advance=1)
                session.commit()

    def clear_table(self):
        """Clears the table in the database that corresponds to the file"""

        with session:
            session.query(CalendarModel).filter(CalendarModel.dataset == self.dataset).delete()
            session.commit()
