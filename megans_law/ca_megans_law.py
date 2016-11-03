# -*- coding: utf-8 -*-
"""California Megan's Law Search Sript

"""

from __future__ import print_function

import time

import selenium
# from selenium.webdriver.common.by import By
# from selenium.webdriver.common.keys import Keys
# from selenium.webdriver.support.ui import Select
# from selenium.common.exceptions import NoSuchElementException
# from selenium.common.exceptions import NoAlertPresentException

def setup_driver():
    """
    Write docs
    """
    # start up selenium instance
    driver = selenium.webdriver.Firefox()
    driver.implicitly_wait(30)
    driver.get('http://meganslaw.ca.gov/')
    return driver

def check_names_with_website(driver, to_check):
    """
    Write docs
    """
    # read in file
    driver.find_element_by_id("B1").click()
    driver.find_element_by_name("cbAgree").click()
    driver.find_element_by_id("B1").click()
    driver.find_element_by_css_selector("img[alt=\"Name Search\"]").click()

    for index, row in to_check.iterrows():
        test_name(driver, last=row.last_name, first=row.first_name)

        if not row.same_first_name:
            test_name(driver, last=row.last_name, first=row.legal_first_name)

        if index % 10 == 0:
            # POSITIVE CONTROL
            test_name(driver, last="AMAYA", first="OSCAR")

    return


def test_name(driver, last, first):
    """
    Write docs
    """
    driver.find_element_by_name("lastName").clear()
    driver.find_element_by_name("lastName").send_keys(last)
    driver.find_element_by_name("firstName").clear()
    driver.find_element_by_name("firstName").send_keys(first)
    time.sleep(1)
    driver.find_element_by_css_selector("img[alt=\"search\"]").click()
    body = driver.find_element_by_tag_name("body").text

    if "Your search returned no results." in body:
        print("#### %s\t%s\tNO RESULTS" % (last, first))
        driver.find_element_by_css_selector("img[alt=\"New Search\"]").click()
        return False
    else:
        print("#### %s\t%s\tCHECK THIS" % (last, first))
        # print driver.current_url
        print(body)
        print("//")
        if 'page 1' in body:
            driver.find_element_by_css_selector(
                "img[alt=\"New Search\"]").click()
            driver.find_element_by_css_selector(
                "img[alt=\"Name Search\"]").click()
            return True
        else:
            driver.execute_script("window.history.go(-1)")
            return True
