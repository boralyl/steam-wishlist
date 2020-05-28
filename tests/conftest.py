
import pytest

from homeassistant.exceptions import ServiceNotFound

from tests.common import (  # noqa: E402, isort:skip
    async_test_home_assistant,
    mock_storage as mock_storage,
)


@pytest.fixture
def hass_storage():
    """Fixture to mock storage."""
    with mock_storage() as stored_data:
        yield stored_data


@pytest.fixture
def hass(loop, hass_storage, request):
    """Fixture to provide a test instance of Home Assistant."""

    def exc_handle(loop, context):
        """Handle exceptions by rethrowing them, which will fail the test."""
        exceptions.append(context["exception"])
        orig_exception_handler(loop, context)

    exceptions = []
    hass = loop.run_until_complete(async_test_home_assistant(loop))
    orig_exception_handler = loop.get_exception_handler()
    loop.set_exception_handler(exc_handle)

    yield hass

    loop.run_until_complete(hass.async_stop(force=True))
    for ex in exceptions:
        if isinstance(ex, ServiceNotFound):
            continue
        raise ex
