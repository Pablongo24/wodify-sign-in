import os

# noinspection PyPackageRequirements
import pytest
from dotenv import load_dotenv

from auto_reserve import WodifyScraper


@pytest.fixture()
def wodify(chromedriver_path):
    wodify_instance = WodifyScraper()
    return wodify_instance


@pytest.fixture()
def chromedriver_path():
    load_dotenv()
    path = os.environ.get('CHROMEDRIVER_EXECUTABLE')
    return path
