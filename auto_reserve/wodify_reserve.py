#!/usr/bin/env python
"""
I'm tired of being wait-listed for classes.
So, I'm automating the reservation.

References
----------
https://github.com/thayton/wodify/blob/master/wodify-scraper.py
"""
import os
from datetime import datetime, timedelta

from dotenv import load_dotenv
from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
# from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.keys import Keys
from send_email_confirmation import send_email

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
        # TODO: change the Service path to run in Github Actions runner.

    """
    def __init__(self, chromedriver_path=None):
        self.login_page = 'https://app.wodify.com/SignIn/Login?OriginalURL=&RequiresConfirm=false'
        self.calendar_page = 'https://app.wodify.com/Schedule/CalendarListViewEntry.aspx'
        self.driver = webdriver.Chrome(service=Service(chromedriver_path))

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

    def change_date_field(self, time_delta=5):
        """Select the date for class sign up.

        When you arrive in the calendar page, the default view is today's date.
        CrossFit Union Square's class sign-up opens 5 days in advance.
        Hence, `time_delta`=5

        Parameters
        ----------
        time_delta : int
            Number of days from today's date to jump forward in the calendar.
        """
        date_elem_id = 'AthleteTheme_wt6_block_wtMainContent_wt9_W_Utils_UI_wt216_block_wtDateInputFrom'
        date_elem = self.driver.find_element(by=By.ID, value=date_elem_id)
        input_date = datetime.today() + timedelta(time_delta)
        date_elem.clear()
        date_elem.send_keys(input_date.strftime('%m/%d/%Y'))
        date_elem.send_keys(Keys.RETURN)

    def make_reservation(self, class_time='6:00 AM'):
        """Reserve a class_time in the calendar list view.

        Parameters
        ----------
        class_time : str or datetime object
            If str: expected format '6:00 AM'
        """
        soup = BeautifulSoup(self.driver.page_source, features='html.parser')
        span = soup.find('span', attrs={'title': class_time})
        tr = span.parent.parent.parent
        reserve_link = tr.find('a', attrs={'href': '#'})
        reserve_elem = self.driver.find_element(by=By.ID, value=reserve_link.attrs['id'])
        reserve_elem.click()
        return True

    def reserve(self, time_delta=5, class_to_reserve='WOD 6:00 AM'):
        """Main runner of all methods.

        Sets an implicit wait in case DOM elements take a long time to load.
        """
        self.driver.get(self.login_page)
        self.driver.implicitly_wait(1)  #
        self.login()
        self.switch_to_calendar()
        self.change_date_field(time_delta=time_delta)
        class_reserved = self.make_reservation(class_time=class_to_reserve)

        return class_reserved


if __name__ == '__main__':
    DEBUGGING = os.environ.get("DEBUGGING")
    SUNDAY_DAY_OF_WEEK = 6  # Sunday is index 6 in `weekday()`
    CHROMEDRIVER_EXECUTABLE = '/Users/pablo.vega-behar/Desktop/chromedriver'
    EMAIL_ALEX = False

    wodify = WodifyScraper(chromedriver_path=CHROMEDRIVER_EXECUTABLE)

    if DEBUGGING:
        today_day_of_week = datetime.today().weekday()
        days_delta = SUNDAY_DAY_OF_WEEK - today_day_of_week
        CLASS_TO_RESERVE = 'Open Gym: 8:00 AM - 4:00 PM'
        reservation = wodify.reserve(time_delta=days_delta, class_to_reserve=CLASS_TO_RESERVE)
    else:
        reservation = wodify.reserve()
        EMAIL_ALEX = True

    if reservation:
        send_email(reservation, email_alex=EMAIL_ALEX)
