from auto_reserve.wodify_reserve import WodifyScraper


def test_init():
    wodify = WodifyScraper()
    assert hasattr(wodify, 'login_page')
    assert hasattr(wodify, 'calendar_page')
    assert hasattr(wodify, 'driver')
