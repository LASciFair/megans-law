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
TODO: Most is hard-coded here. Need to revise the script to
accept command line arguments.

PEP8 the code.

Refining the search and hit strategy would be good - automate birthdate and
address checking.

Refine into functions to be extended to on-the-fly checking, e.g. as a
component of the online registration process itself.
Add comments accordingly to each function.

Refine the output format. Would be good to the output as a CSV or Excel file.
"""

import sys
import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import NoAlertPresentException

import pandas as pd


def main():
    df_to_check = read_input_file(sys.argv[1])

    # start up selenium instance
    driver = webdriver.Firefox()
    driver.implicitly_wait(30)
    driver.get('http://meganslaw.ca.gov/')

    # pass instance with names to check
    check_names_with_website(driver, df_to_check)

    # end selenium instance
    driver.quit()

    return

def read_input_file(filename):
    try:
        to_check = pd.read_excel(filename, header=0)
    except IndexError, IOError:
        raise ValueError("Filename arguement not provided or doesn't exist")

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

    name = pd.DataFrame(name_split, columns=['last_name', 'first_name'])
    name.last_name = name.last_name.str.strip()
    name.first_name = name.first_name.str.strip()
    to_check = pd.concat([to_check, name], axis=1)

    to_check['same_first_name'] = \
        to_check.legal_first_name == to_check.first_name

    return to_check

def check_names_with_website(driver, to_check):
    # read in file
    driver.find_element_by_id("B1").click()
    driver.find_element_by_name("cbAgree").click()
    driver.find_element_by_id("B1").click()
    driver.find_element_by_css_selector("img[alt=\"Name Search\"]").click()

    # to_check is the df to check
    to_check = to_check.loc[20:90]

    for index, row in to_check.iterrows():
        test_name(driver, last=row.last_name, first=row.first_name)

        if not row.same_first_name:
            test_name(driver, last=row.last_name, first=row.legal_first_name)

        if index % 10 == 0:
            # POSITIVE CONTROL
            test_name(driver, last="AMAYA", first="OSCAR")

    return

def test_name(driver, last, first):
    driver.find_element_by_name("lastName").clear()
    driver.find_element_by_name("lastName").send_keys(last)
    driver.find_element_by_name("firstName").clear()
    driver.find_element_by_name("firstName").send_keys(first)
    time.sleep(1)
    driver.find_element_by_css_selector("img[alt=\"search\"]").click()
    body = driver.find_element_by_tag_name("body").text

    if "Your search returned no results." in body:
        print "#### %s\t%s\tNO RESULTS" % (last, first)
        driver.find_element_by_css_selector("img[alt=\"New Search\"]").click()
        return False
    else:
        print "#### %s\t%s\tCHECK THIS" % (last, first)
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

if __name__ == "__main__":
    main()
