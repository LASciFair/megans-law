# -*- coding: utf-8 -*-
"""California Megan's Law Search Sript

This script takes an excel file with names, searches the California Megan's Law
database and returns whether any hits were found along with those detail. Each
hit can then be verified by hand via other information, e.g. birthdate, address.

Every 10 searches, a known hit is run to check the searching continues to work
properly.

The original script was created by using Selenium GUI and searching
http://meganslaw.ca.gov/ by hand with names in and not in the database.

Written by Shyam Saladi (saladi@caltech.edu)
March 9, 2016

Example
-------
How to run the code:

    $ python ca_megans_law.py


Notes
-----
TODO: Virtually everything is hard coded here. Need to revise the script to
accept command line arguments.

PEP8 the code.

Refining the search and hit strategy would be good - automate birthdate and
address checking.

Remove selenium out of unittest framework. Refine into self-contained functions
to be extended to on-the-fly checking, e.g. as a component of the online
registration process itself. Add comments accordingly to each function.

Refine the output format. Would be good to the output as a CSV or Excel file.
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import NoAlertPresentException
import unittest, time, re, time, random

import pandas as pd

class Selenium2(unittest.TestCase):
    def setUp(self):
        self.driver = webdriver.Firefox()
        self.driver.implicitly_wait(30)
        self.base_url = "http://meganslaw.ca.gov/"
        self.verificationErrors = []
        self.accept_next_alert = True

    def test_selenium2(self):
        # read in file
        to_check = pd.read_excel("judges megan list.xlsx", header = 0)

        # throw to upper case to avoid errors and clean up
        to_check.full_name = to_check.full_name.astype(str)
        to_check.legal_first_name = to_check.legal_first_name.astype(str)

        to_check.full_name = to_check.full_name.str.upper()
        to_check.legal_first_name = to_check.legal_first_name.str.upper()

        to_check.full_name = to_check.full_name.str.strip()
        to_check.legal_first_name = to_check.legal_first_name.str.strip()


        # split full name column into two
        name_split = []

        # remove those that don't have last name
        for item in to_check.full_name.str.split(',', 1).tolist():
            if type(item) is list:
                name_split.append(item)

        name = pd.DataFrame(name_split, columns = ['last_name', 'first_name'])
        name.last_name = name.last_name.str.strip()
        name.first_name = name.first_name.str.strip()
        to_check = pd.concat([to_check, name], axis = 1)

        to_check['same_first_name'] = to_check.legal_first_name == to_check.first_name

        def test_name(last, first):
            driver.find_element_by_name("lastName").clear()
            driver.find_element_by_name("lastName").send_keys(last)
            driver.find_element_by_name("firstName").clear()
            driver.find_element_by_name("firstName").send_keys(first)
            time.sleep(1)
            driver.find_element_by_css_selector("img[alt=\"search\"]").click()
            body = driver.find_element_by_tag_name("body").text

            if "Your search returned no results." in body:
                print "####%s\t%s\tNO RESULTS" % (last, first)
                driver.find_element_by_css_selector("img[alt=\"New Search\"]").click()
                return False
            else:
                print "####%s\t%s\tCHECK THIS" % (last, first)
                # print driver.current_url
                print body
                print "//"
                if 'page 1' in body:
                    driver.find_element_by_css_selector("img[alt=\"New Search\"]").click()
                    driver.find_element_by_css_selector("img[alt=\"Name Search\"]").click()
                    return True
                else:
                    driver.execute_script("window.history.go(-1)")
                    return True

        driver = self.driver
        driver.get(self.base_url + "/")
        driver.find_element_by_id("B1").click()
        driver.find_element_by_name("cbAgree").click()
        driver.find_element_by_id("B1").click()
        driver.find_element_by_css_selector("img[alt=\"Name Search\"]").click()

        # to_check is the df to check
        to_check = to_check.loc[79:123]

        for index, row in to_check.iterrows():
            test_name(last = row.last_name, first = row.first_name)

            if not row.same_first_name:
                test_name(last = row.last_name, first = row.legal_first_name)

            if index % 10 == 0:
                # POSITIVE CONTROL
                test_name(last = "AMAYA", first = "OSCAR")

        return


    def is_element_present(self, how, what):
        try: self.driver.find_element(by=how, value=what)
        except NoSuchElementException as e: return False
        return True

    def is_alert_present(self):
        try: self.driver.switch_to_alert()
        except NoAlertPresentException as e: return False
        return True

    def close_alert_and_get_its_text(self):
        try:
            alert = self.driver.switch_to_alert()
            alert_text = alert.text
            if self.accept_next_alert:
                alert.accept()
            else:
                alert.dismiss()
            return alert_text
        finally: self.accept_next_alert = True

    def tearDown(self):
        self.driver.quit()
        self.assertEqual([], self.verificationErrors)

if __name__ == "__main__":
    unittest.main()
