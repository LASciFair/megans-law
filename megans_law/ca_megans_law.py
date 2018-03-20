# -*- coding: utf-8 -*-
"""California Megan's Law Search Script

"""

import sys
import os.path
import argparse

import pandas as pd
import xlrd

import selenium
import selenium.webdriver
from selenium.common.exceptions import ElementNotInteractableException, ElementClickInterceptedException

class CAMeagansLaw():
    """
    """
    count = 0

    def __init__(self, debug, transient=True, pos_interval=10):
        """Initialize object.

        `transient` refers to transient offenders as specified online
        """
        self.debug = bool(debug)
        self.transient = transient
        self.pos_interval = pos_interval
        self.recheck = 0
        self.neg = 0

    def __enter__(self):
        """Startup connection to the database
        """
        # start up selenium instance
        self.driver = selenium.webdriver.Firefox()
        self.driver.implicitly_wait(30)
        self.driver.get('https://meganslaw.ca.gov/Search.aspx')
        self.driver.find_element_by_id("AcceptDisclaimer").click()

        # Human to do Captcha
        self.driver.implicitly_wait(30)

        # select
        if self.transient:
            self.driver.find_element_by_id("IncludeTransient").click()

        return self


    def __exit__(self, *args):
        """Close driver instance
        """
        self.driver.quit()
        return


    def query_df(self, df, last='last_name', first='first_name',
                 legal_first='legal_first_name'):
        """Convenience method to query with a dataframe

        pos_interval refers to how often the positive control is checked

        """
        return df.apply(self.query_series, axis=1,
                        last=last, first=first, legal_first=legal_first)


    def query_series(self, ser, last, first, legal_first=False):
        """Another convenience method to query with a series object.
        Probably will only ever be used by `query_df`
        """
        result = self.query(last=ser[last], first=ser[first])

        # Check legal first name if it's different and result has not already
        # come up as positive
        if legal_first and not result and ser[first] != ser[legal_first]:
            result = self.query(last=ser[last], first=ser[legal_first])

        if result:
            self.recheck += 1
        else:
            self.neg += 1

        print("Recheck: {}, Negative: {}".format(self.recheck, self.neg), end="\r")

        return result


    def positive_query(self):
        """Make sure positive control comes up correctly
        """
        if not self.query(last="AMAYA", first="OSCAR"):
            raise RuntimeError("Positive control not showing")
        return True


    def query(self, last, first):
        """Query database for the given name

        This method should be updated as the online interface changes over
        time.
        """
        self.count += 1
        # Check positive control, if necessary
        if self.pos_interval > 0 and self.count % self.pos_interval == 0:
            self.positive_query()

        # Close results window
        try:
            self.driver.find_element_by_xpath("//input[@value='Close']").click()
            self.driver.find_element_by_xpath("//div[6]/div/button/span").click()
        except ElementNotInteractableException:
            pass

        # Enter query info
        try:
            self.driver.find_element_by_name("OLastName").clear()
            self.driver.find_element_by_name("OLastName").send_keys(last)
            self.driver.find_element_by_name("OFirstName").clear()
            self.driver.find_element_by_name("OFirstName").send_keys(first)

            self.driver.find_element_by_xpath("//input[@value='Search']").click()
            self.driver.implicitly_wait(10)

            # Press "Show List", if possible
            try:
                self.driver.find_element_by_link_text("Show List").click()
            except ElementClickInterceptedException:
                pass

            # Pull results
            body = self.driver.find_element_by_tag_name("body").text
        except Exception as e:
            self.driver.save_screenshot('error_screenshot.png')
            raise e


        if "No matches." in body or "No offenders matched your search." in body:
            if self.debug:
                print("#### %s\t%s\tNO RESULTS" % (last, first))
            self.driver.find_element_by_xpath(
                    './/input[@value="Close"]').click()
            return False
        else:
            if self.debug:
                print("#### %s\t%s\tCHECK THIS\n%s\n//" % (last, first, body))
            return True


def read_input_file(filename):
    """Convenience method to clean up input file supplied
    """
    try:
        to_check = pd.read_excel(filename, header=0)
    except xlrd.biffh.XLRDError:
        to_check = pd.read_csv(filename, header=0)
    except (IndexError, IOError):
        raise ValueError("Filename argument not provided or doesn't exist")

    for col in ['legal_first_name', 'first_name', 'last_name']:
        to_check[col] = to_check[col].astype(str)
        to_check[col] = to_check[col].str.upper().str.strip().str.rstrip()

    return to_check


def main():
    parser = argparse.ArgumentParser(
        description="Run query through Megan's law database.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument('inputfile',
                        type=str,
                        help='File to check')

    parser.add_argument('--output',
         type=str,
         default=None,
         help='Output filename. Default: basename(`inputfile`)._check.csv')

    parser.add_argument('--debug',
         action='store_true',
         help='Turn on verbose output to stdout')

    args = parser.parse_args()

    if(args.inputfile == '-'):
        args.inputfile = sys.stdin

    df = read_input_file(args.inputfile)

    with CAMeagansLaw(debug=args.debug) as h:
        # pass instance with names to check
        df['recheck'] = h.query_df(df)

    if args.output is None:
        outfn, _ = os.path.splitext(args.inputfile)
        outfn += '_check'
    else:
        outfn = args.output

    df.to_csv(outfn + '.csv', index=False)

    return


if __name__ == '__main__':
    main()
