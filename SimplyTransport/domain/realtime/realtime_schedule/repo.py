import datetime
from collections import defaultdict
from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ...schedule.model import StaticScheduleModel
from ..stop_time.model import RTStopTimeModel
from ..trip.model import RTTripModel


class RealtimeScheduleRepository:
    """RealtimeScheduleRepository repository."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def load_recent_rt_overlay_for_schedules(
        self, schedules: Sequence[StaticScheduleModel]
    ) -> tuple[dict[str, RTTripModel], dict[tuple[str, str, int], RTStopTimeModel]]:
        """
        Load recent rt_trip rows by trip_id and rt_stop_time overlay keyed by
        (trip_id, stop_id, stop_sequence) for each static schedule row.

        Feeds often omit many stops; we only store updates the producer sent. Match in order:
        exact (trip, stop, sequence); else latest RT row on that trip with stop_sequence <= static
        (delay carried forward); else earliest RT row with stop_sequence >= static.
        """
        if not schedules:
            return {}, {}

        dataset = schedules[0].trip.dataset
        trip_ids = list[str](set[str]({s.trip.id for s in schedules}))
        thirty_mins_ago = datetime.datetime.now(datetime.UTC) - datetime.timedelta(minutes=30)

        trips_stmt = select(RTTripModel).where(
            RTTripModel.trip_id.in_(trip_ids),
            RTTripModel.dataset == dataset,
            RTTripModel.created_at >= thirty_mins_ago,
        )
        trips_result = await self.session.execute(trips_stmt)
        trips_by_id: dict[str, RTTripModel] = {}
        for row in trips_result.scalars():
            existing = trips_by_id.get(row.trip_id)
            if existing is None or row.created_at > existing.created_at:
                trips_by_id[row.trip_id] = row

        stop_map: dict[tuple[str, str, int], RTStopTimeModel] = {}
        if trip_ids:
            st_stmt = select(RTStopTimeModel).where(
                RTStopTimeModel.dataset == dataset,
                RTStopTimeModel.created_at >= thirty_mins_ago,
                RTStopTimeModel.trip_id.in_(trip_ids),
            )
            st_result = await self.session.execute(st_stmt)
            by_triple: dict[tuple[str, str, int], RTStopTimeModel] = {}
            by_trip: dict[str, list[RTStopTimeModel]] = defaultdict(list)
            for st in st_result.scalars():
                t, s, sq = st.trip_id, st.stop_id, st.stop_sequence
                by_trip[t].append(st)
                k3 = (t, s, sq)
                prev = by_triple.get(k3)
                if prev is None or st.created_at > prev.created_at:
                    by_triple[k3] = st

            for static in schedules:
                trip_id = static.trip.id
                stop_id = static.stop.id
                seq = static.stop_time.stop_sequence
                key = (trip_id, stop_id, seq)
                row = by_triple.get(key)
                if row is None:
                    trip_rows = by_trip.get(trip_id, [])
                    predecessors = [r for r in trip_rows if r.stop_sequence <= seq]
                    if predecessors:
                        row = max(predecessors, key=lambda r: (r.stop_sequence, r.created_at))
                    else:
                        successors = [r for r in trip_rows if r.stop_sequence >= seq]
                        if successors:
                            min_sq = min(r.stop_sequence for r in successors)
                            at_min = [r for r in successors if r.stop_sequence == min_sq]
                            row = max(at_min, key=lambda r: r.created_at)
                if row is not None:
                    stop_map[key] = row

        return trips_by_id, stop_map

    async def get_distinct_realtime_trips(self) -> list[str]:
        """
        Returns all distinct trips.
        """
        trips_statement = select(RTTripModel.trip_id).distinct()
        result = await self.session.execute(trips_statement)
        return [trip[0] for trip in result]


async def provide_schedule_update_repo(db_session: AsyncSession) -> RealtimeScheduleRepository:
    """This provides the RealtimeSchedule repository."""

    return RealtimeScheduleRepository(session=db_session)
