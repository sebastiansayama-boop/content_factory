import os

import pytest

from content_factory.integrations import IntegrationConfig, IntegrationError


def test_integration_rejects_non_http_endpoint():
    with pytest.raises(IntegrationError):
        IntegrationConfig("x", "file:///tmp/provider").validate()


def test_integration_requires_declared_secret():
    os.environ.pop("CF_TEST_SECRET", None)
    with pytest.raises(IntegrationError):
        IntegrationConfig("x", "https://example.invalid", "CF_TEST_SECRET").validate()
