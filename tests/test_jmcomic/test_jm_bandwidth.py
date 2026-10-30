from __future__ import annotations

from jmcomic import JmOption
from jmcomic.bandwidth import DEFAULT_DOWNLOAD_RATE, BandwidthLimiter


def test_bandwidth_limiter_schedules_bytes_at_configured_rate() -> None:
    now = [0.0]
    sleeps: list[float] = []
    limiter = BandwidthLimiter(10, clock=lambda: now[0], sleeper=lambda value: sleeps.append(value))

    limiter.consume(10)
    limiter.consume(10)

    assert sleeps == [1.0]


def test_bandwidth_limiter_zero_is_unlimited() -> None:
    sleeps: list[float] = []
    limiter = BandwidthLimiter(0, clock=lambda: 0.0, sleeper=lambda value: sleeps.append(value))

    limiter.consume(10_000_000)

    assert sleeps == []


def test_download_rate_limit_stays_out_of_postman_request_metadata() -> None:
    option = JmOption.default()
    client = option.new_jm_client(
        impl="html",
        domain_list=["example.invalid"],
        cache=False,
    )

    assert "download_rate_limit" not in client.postman.meta_data
    assert client._download_limiter.rate == DEFAULT_DOWNLOAD_RATE
