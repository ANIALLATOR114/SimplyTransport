import pytest
from litestar.testing import TestClient

from SimplyTransport.controllers.events import ALL_EVENTS
from SimplyTransport.domain.events.event_types import EventType


def test_events_200(client: TestClient) -> None:
    response = client.get("events")
    assert response.status_code == 200
    assert "Events are records of things that have happened in the system" in response.text


@pytest.mark.parametrize("value", [
    '<select class="dropdown" name="pageSize">',
    '<option value="10">PageSize : 10</option>',
    '<option value="20">20</option>',
    '<option value="50">50</option>',
    '<option value="100">100</option>'
])
def test_events_with_pagesizes(client: TestClient, value):
    response = client.get("events")
    assert response.status_code == 200
    assert value in response.text


def test_event_types_all_present(client: TestClient) -> None:
    response = client.get("events")
    assert response.status_code == 200
    expected_values = [
        f'<option value="{ALL_EVENTS}">{ALL_EVENTS}</option>',
    ]

    for event_type in EventType:
        expected_values.append(f'<option value="{event_type.value}">{event_type.value}</option>')

    for value in expected_values:
        assert value in response.text


def test_event_search_defaults(client: TestClient) -> None:
    response = client.get("events/search")
    assert response.status_code == 200
    assert "Limit: 20" in response.text
    print(response.text)
    assert f'<span class="event-chip">{ALL_EVENTS}</span>' in response.text
    assert '<span class="event-chip">desc</span>' in response.text


def test_event_search_sort_and_type(client: TestClient) -> None:
    response = client.get("events/search?sort=asc&type=gtfs.database.updated")
    assert response.status_code == 200
    assert "Limit: 20" in response.text
    assert f'<span class="event-chip">{EventType.GTFS_DATABASE_UPDATED.value}</span>' in response.text
    assert '<span class="event-chip">asc</span>' in response.text


def test_event_search_invalid_type(client: TestClient) -> None:
    response = client.get("events/search?type=invalid")
    assert response.status_code == 400
    assert "500 Error" in response.text
