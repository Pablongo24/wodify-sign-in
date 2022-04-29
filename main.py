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
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

load_dotenv()
USERNAME = os.environ.get("USERNAME")
PASSWORD = os.environ.get("PASSWORD")


class WodifyScraper:
    def __init__(self):
        self.login_page = 'https://app.wodify.com/SignIn/Login?OriginalURL=&RequiresConfirm=false'
        self.calendar_page = 'https://app.wodify.com/Schedule/CalendarListViewEntry.aspx'
        self.driver = webdriver.Chrome(executable_path='/Users/pablo.vega-behar/Desktop/chromedriver')

    def login(self):
        username_element = self.driver.find_element(by=By.ID, value="Input_UserName")
        password_element = self.driver.find_element(by=By.ID, value="Input_Password")

        username_element.send_keys(USERNAME)
        password_element.send_keys(PASSWORD)

        login_elem = self.driver.find_element(by=By.CLASS_NAME, value='signin-btn')
        login_elem.click()

    def switch_to_calendar(self):
        calendar_elem = self.driver.find_element(by=By.ID,
                                                 value="AthleteTheme_wtLayoutNormal_block_wtMenu_AthleteTheme_wt67_block_wt37")
        calendar_elem.click()

    def change_date_field(self):
        date_elem = self.driver.find_element(by=By.ID,
                                             value='AthleteTheme_wt6_block_wtMainContent_wt9_W_Utils_UI_wt216_block_wtDateInputFrom')
        input_date = datetime.today() + timedelta(5)
        date_elem.clear()
        date_elem.send_keys(input_date.strftime('%m/%d/%Y'))
        date_elem.send_keys(Keys.RETURN)

    def scrape(self):
        self.driver.get(self.login_page)
        self.driver.implicitly_wait(2)
        self.login()
        self.driver.implicitly_wait(1)
        self.switch_to_calendar()
        self.driver.implicitly_wait(1)
        self.change_date_field()


if __name__ == '__main__':
    wodify = WodifyScraper()
    wodify.scrape()
