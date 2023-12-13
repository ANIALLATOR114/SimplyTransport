from unittest.mock import AsyncMock

import pytest

from SimplyTransport.domain.events.repo import EventRepository


@pytest.mark.asyncio
async def test_create_event_calls_add_and_commit():
    # Arrange
    session = AsyncMock()
    event_repository = EventRepository(session=session)

    event_type = "event_type"
    description = "description"
    attributes = {"key": "value"}

    # Act
    await event_repository.create_event(event_type, description, attributes)

    # Assert
    session.add.assert_called_once()
    session.commit.assert_called_once()
