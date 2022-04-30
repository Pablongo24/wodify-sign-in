from datetime import datetime
from auto_reserve.wodify_reserve import WodifyScraper


def test_init():
    wodify = WodifyScraper()
    assert hasattr(wodify, 'login_page')
    assert hasattr(wodify, 'calendar_page')
    assert hasattr(wodify, 'driver')


def test_reserve(wodify):
    # Test reservation for day that isn't open yet
    time_delta = 10  # Reservations only open 5 days in advance
    wodify.reserve(time_delta=time_delta)
    assert wodify.reservation_status == 'cannot reserve'

    # Test reservation success. Use Sunday since it always has availability.
    SUNDAY_DAY_OF_WEEK = 6  # Sunday is index 6 in `weekday()`
    CLASS_TO_RESERVE = 'Open Gym: 8:00 AM - 4:00 PM'
    today = datetime.today()
    time_delta = SUNDAY_DAY_OF_WEEK - today.weekday()
    wodify.reserve(time_delta=time_delta, class_to_reserve=CLASS_TO_RESERVE)
    assert wodify.reservation_status == 'success'

    # Test already reserved case.
    wodify.reserve(time_delta=time_delta, class_to_reserve=CLASS_TO_RESERVE)
    assert wodify.reservation_status == 'already reserved'
