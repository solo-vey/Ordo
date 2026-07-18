from ordo_pathwalk.runner.model_drivers import _call_with_backoff, _is_retryable_exception


class RateLimitError(Exception):
    pass


class AuthenticationError(Exception):
    pass


def test_retryable_rate_limit_name():
    assert _is_retryable_exception(RateLimitError("429 rate limit")) is True


def test_non_retryable_auth_error():
    assert _is_retryable_exception(AuthenticationError("bad key")) is False


def test_call_with_backoff_retries_then_succeeds():
    calls = {"n": 0}
    sleeps = []
    def fn():
        calls["n"] += 1
        if calls["n"] < 3:
            raise RateLimitError("rate limit")
        return "ok"
    retry_log = []
    result = _call_with_backoff(fn, max_retries=4, retry_log=retry_log, sleep=sleeps.append)
    assert result == "ok"
    assert calls["n"] == 3
    assert len(retry_log) == 2
    assert sleeps == [1.0, 2.0]
