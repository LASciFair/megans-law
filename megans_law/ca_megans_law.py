# -*- coding: utf-8 -*-
"""California Megan's Law Search Sript

"""

from __future__ import print_function

import sys
import argparse
import time

import pandas as pd

import selenium
import selenium.webdriver
import selenium.common.exceptions

def setup_driver():
    """
    Write docs
    """
    # start up selenium instance
    driver = selenium.webdriver.Firefox()
    driver.implicitly_wait(30)
    driver.get('https://meganslaw.ca.gov/Search.aspx')
    driver.find_element_by_id("AcceptDisclaimer").click()
    # human needs to do Captcha
    driver.implicitly_wait(30)
    return driver

def check_names_with_website(driver, to_check):
    """
    Write docs
    """

    driver.find_element_by_id("IncludeTransient").click()

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
    driver.find_element_by_name("OLastName").clear()
    driver.find_element_by_name("OLastName").send_keys(last)
    driver.find_element_by_name("OFirstName").clear()
    driver.find_element_by_name("OFirstName").send_keys(first)
    time.sleep(1)
    #driver.find_element_by_css_selector("img[alt=\"search\"]").click()
    driver.find_element_by_xpath('.//input[@onclick="doNameSearch()"]').click()


    driver.find_element_by_xpath('.//a[@onclick="showListResults()"]').click()


    body = driver.find_element_by_tag_name("body").text

    if "No offenders matched your search." in body:
        print("#### %s\t%s\tNO RESULTS" % (last, first))
        driver.find_element_by_xpath('.//input[@value="Close"]').click()
        return False
    else:
        print("#### %s\t%s\tCHECK THIS" % (last, first))
        # print driver.current_url
        print(body)
        print("//")
        return True


def read_input_file(filename):
    """
    Write docs
    """
    try:
        to_check = pd.read_excel(filename, header=0)
    except (IndexError, IOError):
        raise ValueError("Filename arguement not provided or doesn't exist")
    print(to_check.columns)
    for col in ['legal_first_name', 'first_name', 'last_name']:
        to_check[col] = to_check[col].astype(str)
        to_check[col] = to_check[col].str.upper().str.strip().str.rstrip()

    # remove those that don't have last name
#    for item in to_check.full_name.str.split(',', 1).tolist():
#        if type(item) is list:
#            name_split.append(item)

#    to_check = pd.concat([to_check, name], axis=1)

    to_check['same_first_name'] = \
        to_check.legal_first_name == to_check.first_name

    return to_check


def main():
    """
    Write docs
    """
    parser = argparse.ArgumentParser(
        description="Run query through Megan's law database.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument('inputfile',
                        type=str,
                        help='File to check')

    args = parser.parse_args()

    if(args.inputfile == '-'):
        args.inputfile = sys.stdin

    df_to_check = read_input_file(args.inputfile)

    driver = setup_driver()

    # pass instance with names to check
    check_names_with_website(driver, df_to_check.loc[120:])

    # end selenium instance
    driver.quit()

    return


if __name__ == '__main__':
    main()
