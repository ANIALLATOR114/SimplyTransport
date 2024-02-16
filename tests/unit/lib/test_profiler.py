import cProfile
import pytest
from SimplyTransport.lib import profiling

@pytest.mark.asyncio
async def test_profile_decorator(capsys):
    @profiling.profile
    async def async_test_func():
        return "Test"

    result = await async_test_func()
    assert result == "Test"

    out, err = capsys.readouterr()
    assert "Profiling function: async_test_func" in out
    assert "function calls" in out
    assert "Ordered by: cumulative" in out


def test_profiler_context_manager(capsys):
    with profiling.Profiler() as p:
        1+1

    assert isinstance(p.pr, cProfile.Profile)

    out, err = capsys.readouterr()
    assert "function calls" in out
    assert "Ordered by: cumulative" in out
