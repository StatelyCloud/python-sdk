"""Tests for the Client class."""

from statelydb.src.client import Client

# ruff: noqa: SLF001


def test_make_endpoint() -> None:
    # passing an endpoint and region. the region is ignored
    assert (
        Client._make_endpoint(endpoint="http://localhost", region="test")  # type: ignore[reportPrivateUsage]
        == "http://localhost"
    )

    # passing region without endpoint. the regional
    # endpoint is used
    assert (
        Client._make_endpoint(region="us-west-1")  # type: ignore[reportPrivateUsage]
        == "https://us-west-1.aws.api.stately.cloud"
    )

    # check that the aws- prefix is stripped from the region
    assert (
        Client._make_endpoint(region="aws-us-west-1")  # type: ignore[reportPrivateUsage]
        == "https://us-west-1.aws.api.stately.cloud"
    )

    # passing nothing results in the default endpoint
    assert Client._make_endpoint() == "https://api.stately.cloud"  # type: ignore[reportPrivateUsage]
