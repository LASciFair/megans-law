#!/usr/bin/env python
import sys
import argparse

import pandas as pd
import megans_law

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

    driver = megans_law.setup_driver()

    # pass instance with names to check
    megans_law.check_names_with_website(driver, df_to_check.loc[120:])

    # end selenium instance
    driver.quit()

    return


def read_input_file(filename):
    """
    Write docs
    """
    try:
        to_check = pd.read_excel(filename, header=0)
    except (IndexError, IOError):
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


if __name__ == '__main__':
    main()
