"""Realtime stop HTML with frozen clock; CI runs importgtfs + seedrealtimefromfile first."""

from freezegun import freeze_time
from litestar.testing import TestClient


@freeze_time("2025-03-21 12:00:00")
def test_realtime_stop_e2e_removed_trip_row_and_delays(client: TestClient) -> None:
    stop_api = client.get("/api/v1/stop/RT_E2E_S1")
    assert stop_api.status_code == 200, (
        "Fixture stop RT_E2E_S1 missing from DB: import tests/gtfs_test_data/TFI via importgtfs, "
        "then seed realtime_e2e_trip_updates.json (see README local testing)."
    )

    response = client.get("/realtime/stop/RT_E2E_S1")
    assert response.status_code == 200
    html = response.text
    assert "Sorry this stop could not be found" not in html
    assert "Test 1" in html
    assert "/realtime/stop/RT_E2E_S1/realtime-table" in html

    partial = client.get("/realtime/stop/RT_E2E_S1/realtime-table")
    assert partial.status_code == 200
    fragment = partial.text
    assert "realtime-row-removed" in fragment
    assert "color-late" in fragment
