# noinspection PyPackageRequirements
import pytest

from auto_reserve import WodifyScraper


@pytest.fixture()
def wodify():
    wodify_instance = WodifyScraper()
    return wodify_instance
