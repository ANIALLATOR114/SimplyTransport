from litestar.contrib.sqlalchemy.repository import SQLAlchemyAsyncRepository
from sqlalchemy import func
from sqlalchemy.ext.asyncio import AsyncSession

from sqlalchemy.sql.expression import select

from SimplyTransport.domain.agency.model import AgencyModel
from SimplyTransport.domain.calendar.model import CalendarModel
from SimplyTransport.domain.calendar_dates.model import CalendarDateModel
from SimplyTransport.domain.database_statistics.statistic_type import StatisticType
from SimplyTransport.domain.route.model import RouteModel
from SimplyTransport.domain.shape.model import ShapeModel
from SimplyTransport.domain.stop.model import StopModel
from SimplyTransport.domain.stop_features.model import StopFeatureModel
from SimplyTransport.domain.stop_times.model import StopTimeModel
from SimplyTransport.domain.trip.model import TripModel

from .model import DatabaseStatisticModel

class DatabaseStatisticRepository(SQLAlchemyAsyncRepository[DatabaseStatisticModel]):
    """Database Statistic repository."""

    async def get_gtfs_record_counts(self) -> dict[str, int | None]:
        """Returns a dictionary of the counts of each GTFS record type."""

        record_counts = {
            "Operators": (
                await self.session.execute(
                    select(func.count()).select_from(AgencyModel)
                )
            ).scalar(),
            "Routes": (
                await self.session.execute(select(func.count()).select_from(RouteModel))
            ).scalar(),
            "Trips": (
                await self.session.execute(select(func.count()).select_from(TripModel))
            ).scalar(),
            "Stops": (
                await self.session.execute(select(func.count()).select_from(StopModel))
            ).scalar(),
            "Stop Features": (
                await self.session.execute(
                    select(func.count()).select_from(StopFeatureModel)
                )
            ).scalar(),
            "Calendars": (
                await self.session.execute(
                    select(func.count()).select_from(CalendarModel)
                )
            ).scalar(),
            "Calendar Dates": (
                await self.session.execute(
                    select(func.count()).select_from(CalendarDateModel)
                )
            ).scalar(),
            "Stop Times": (
                await self.session.execute(
                    select(func.count()).select_from(StopTimeModel)
                )
            ).scalar(),
            "Shapes": (
                await self.session.execute(select(func.count()).select_from(ShapeModel))
            ).scalar(),
        }

        return record_counts
    

    async def get_operator_route_counts(self) -> dict[str, int | None]:
        """Returns a dictionary of the counts of each operator's routes."""

        route_counts = (
            await self.session.execute(
                select(AgencyModel.name, func.count(RouteModel.id))
                .join(RouteModel, RouteModel.agency_id == AgencyModel.id)
                .group_by(AgencyModel.name)
            )
        ).all()

        return {name: count for name, count in route_counts}
    

    async def get_operator_trip_counts(self) -> dict[str, int | None]:
        """Returns a dictionary of the counts of each operator's trips."""

        trip_counts = (
            await self.session.execute(
                select(AgencyModel.name, func.count(TripModel.id))
                .join(RouteModel, RouteModel.agency_id == AgencyModel.id)
                .join(TripModel, TripModel.route_id == RouteModel.id)
                .group_by(AgencyModel.name)
            )
        ).all()

        return {name: count for name, count in trip_counts}
    
    async def get_stop_feature_counts(self) -> dict[str, int | None]:
        """Returns a dictionary of the counts of each stop feature type."""

        record_counts = {
            "Surveyed Stops": (
                await self.session.execute(
                    select(func.count())
                    .select_from(StopFeatureModel)
                    .where(StopFeatureModel.surveyed)
                )
            ).scalar(),
            "Wheelchair Accessible": (
                await self.session.execute(
                    select(func.count())
                    .select_from(StopFeatureModel)
                    .where(StopFeatureModel.wheelchair_accessability)
                )
            ).scalar(),
            "RealTime Display": (
                await self.session.execute(
                    select(func.count())
                    .select_from(StopFeatureModel)
                    .where(StopFeatureModel.rtpi_active)
                )
            ).scalar(),
            "Shelter Available": (
                await self.session.execute(
                    select(func.count())
                    .select_from(StopFeatureModel)
                    .where(StopFeatureModel.shelter_active)
                )
            ).scalar(),
            "Light Available(Shelter)": (
                await self.session.execute(
                    select(func.count())
                    .select_from(StopFeatureModel)
                    .where(StopFeatureModel.light)
                )
            ).scalar(),
            "Bench Available": (
                await self.session.execute(
                    select(func.count()).select_from(StopFeatureModel).where(StopFeatureModel.bench)
                )
            ).scalar(),
            "Bin Available": (
                await self.session.execute(
                    select(func.count()).select_from(StopFeatureModel).where(StopFeatureModel.bin)
                )
            ).scalar(),
        }

        return record_counts

    async def add_row_counts(
        self, row_counts: dict[str, int | None], statistic_type: StatisticType
    ) -> None:
        """Adds a row count entry to the database."""

        for key, value in row_counts.items():
            self.session.add(
                DatabaseStatisticModel(
                    statistic_type=statistic_type,
                    key=key,
                    value=value if value is not None else 0,
                )
            )

        await self.session.commit()

    model_type = DatabaseStatisticModel


async def provide_database_statistic_repo(
    db_session: AsyncSession,
) -> DatabaseStatisticRepository:
    """This provides the Database Statistic repository."""

    return DatabaseStatisticRepository(session=db_session)
