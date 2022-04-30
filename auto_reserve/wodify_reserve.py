#!/usr/bin/env python
"""
I'm tired of being wait-listed for classes.
So, I'm automating the reservation.

References
----------
https://github.com/thayton/wodify/blob/master/wodify-scraper.py
"""
import os
import time
from datetime import datetime, timedelta, date

from bs4 import BeautifulSoup
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager

from auto_reserve.send_email_confirmation import send_email

load_dotenv()


class WodifyScraper:
    """Scrape the Wodify Web App.

    Attributes
    ----------
    login_page : str
        Wodify App URL
    calendar_page : str
        URL for the Wodify calendar. This page contains the class schedule.
    driver : ChromeDriver object
        Selenium ChromeDriver
    """

    def __init__(self):
        self.login_page = 'https://app.wodify.com/SignIn/Login?OriginalURL=&RequiresConfirm=false'
        self.calendar_page = 'https://app.wodify.com/Schedule/CalendarListViewEntry.aspx'
        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
        self.reservation_status = None
        self.class_time = None
        self.class_date = None
        self.reservation_return_status = {
            'status': self.reservation_status,
            'class_time': self.class_time,
            'class_date': self.class_date
        }

    def _update_return_status(self):
        self.reservation_return_status = {
            'status': self.reservation_status,
            'class_time': self.class_time,
            'class_date': self.class_date
        }

    def login(self):
        """Log-in to the web app.

        Uses username and password stored as secrets.
        """
        username_element = self.driver.find_element(by=By.ID, value="Input_UserName")
        password_element = self.driver.find_element(by=By.ID, value="Input_Password")

        username_element.send_keys(os.environ.get("USERNAME"))
        password_element.send_keys(os.environ.get("PASSWORD"))

        login_elem = self.driver.find_element(by=By.CLASS_NAME, value='signin-btn')
        login_elem.click()

    def switch_to_calendar(self):
        """Change from the landing page after logging in to the Calendar page."""
        calendar_elem_id = "AthleteTheme_wtLayoutNormal_block_wtMenu_AthleteTheme_wt67_block_wt37"
        calendar_elem = self.driver.find_element(by=By.ID, value=calendar_elem_id)
        calendar_elem.click()

    def change_date_field(self, input_date=datetime.today()):
        """Select the date for class sign up.

        When you arrive in the calendar page, the default view is today's date.
        CrossFit Union Square's class sign-up opens 5 days in advance.
        Hence, `time_delta`=5

        Parameters
        ----------
        input_date : datetime
            Calendar date for class reservation.
        """
        date_elem_id = 'AthleteTheme_wt6_block_wtMainContent_wt9_W_Utils_UI_wt216_block_wtDateInputFrom'
        date_elem = self.driver.find_element(by=By.ID, value=date_elem_id)
        date_elem.clear()
        date_elem.send_keys(input_date.strftime('%m/%d/%Y'))
        date_elem.send_keys(Keys.RETURN)

    def get_reserve_link(self):
        soup = BeautifulSoup(self.driver.page_source, features='html.parser')
        span = soup.find('span', attrs={'title': self.class_time})
        tr = span.parent.parent.parent
        reserve_link = tr.find('a', attrs={'href': '#'})
        return reserve_link

    def make_reservation(self, class_time='WOD 6:00 AM'):
        """Reserve a class_time in the calendar list view.

        Parameters
        ----------
        class_time : str or datetime object
            If str: expected format '6:00 AM'
        """
        self.class_time = class_time
        reserve_link = self.get_reserve_link()

        if reserve_link.find('svg', {'class': 'icon-ticket'}):
            self.reservation_status = 'already reserved'
            self._update_return_status()
            return True

        if reserve_link.find('svg', {'class': 'icon-calendar--disabled'}):
            self.reservation_status = 'cannot reserve'
            self._update_return_status()
            return True

        element_was_clickable = False
        if reserve_link.find('svg', {'class': 'icon-calendar'}):
            reserve_elem = self.driver.find_element(by=By.ID, value=reserve_link.next.attrs['id'])
            reserve_elem.click()

            element_was_clickable = True

        self.driver.refresh()
        reserve_link = self.get_reserve_link()

        if reserve_link.find('svg', {'class': 'icon-ticket'}) and element_was_clickable:
            self.reservation_status = 'success'
            self._update_return_status()
            return True
        else:
            self.reservation_status = 'there was a problem'
            self._update_return_status()
            return True

    def setup_reservation(self, time_delta=5):
        """Main runner of all methods.

        Sets an implicit wait in case DOM elements take a long time to load.
        """
        self.driver.get(self.login_page)
        self.driver.implicitly_wait(1)  #
        self.login()
        self.switch_to_calendar()
        input_date = datetime.today() + timedelta(time_delta)
        self.class_date = input_date
        self.change_date_field(input_date=input_date)


def sleep_until_2_pm():
    """Check if current time is between 1:59 and 2:01pm.

    This is specific to this project, since CFUS Wodify class reservation opens at exactly 2pm.
    This process is intended to run in Github actions, where runners may be delayed if there
    is high demand for workflows, which typically happens at the start of every hour, per
    https://docs.github.com/en/actions/using-workflows/events-that-trigger-workflows#schedule

    Thus, I will kick off this workflow at 1:59pm and check how many seconds until 2:00pm before
    trying to make the reservation.
    """
    current_time = datetime.today()
    two_pm = datetime.strptime('1400', '%H%M').time()
    if 13 < current_time.hour < 14:
        two_pm_today = datetime.combine(date.today(), two_pm)
        sleep = two_pm_today - datetime.today()
        time.sleep(int(sleep.seconds))


if __name__ == '__main__':
    DEBUGGING = os.environ.get("DEBUGGING")
    SUNDAY_DAY_OF_WEEK = 6  # Sunday is index 6 in `weekday()`
    EMAIL_ALEX = False

    wodify = WodifyScraper()

    if DEBUGGING:
        today_day_of_week = datetime.today().weekday()
        days_delta = SUNDAY_DAY_OF_WEEK - today_day_of_week
        CLASS_TO_RESERVE = 'Open Gym: 8:00 AM - 4:00 PM'
        wodify.setup_reservation(time_delta=days_delta)
        time.sleep(5)
        wodify.make_reservation(class_time=CLASS_TO_RESERVE)
    else:
        wodify.setup_reservation()
        sleep_until_2_pm()
        wodify.make_reservation()
        EMAIL_ALEX = True

    wodify.driver.quit()

    reservation_status = wodify.reservation_return_status['status']
    reservation_date = wodify.class_date
    reservation_time = wodify.class_time

    send_email(reservation_status=reservation_status,
               class_date=reservation_date,
               class_time=reservation_time,
               email_alex=EMAIL_ALEX)
