megans-law
==========

This is an **alpha** version of a package to query California's Megan's Law
database. There is much to be done to improve the code.

The script takes an excel file with names, searches the California Megan's Law
database and returns whether any hits were found along with those detail. Each
hit can then be verified by hand via other information, e.g. birthdate, address.

Every 10 searches, a known hit is run to check the searching continues to work
properly.

The original script was created by using Selenium GUI and searching
http://meganslaw.ca.gov/ by hand with names in and not in the database.


### Example

```bash
pip install .
ca_megans_law.py INPUT
```

### TODO

* Most is hard-coded here. Need to revise the script to
accept command line arguments.

* Formal tests

* Set up travis-ci and appveyor

* code documentation

* Refining the search and hit strategy would be good - automate birthdate and
address checking.

* Refine into functions to be extended to on-the-fly checking, e.g. as a
component of the online registration process itself.
Add comments accordingly to each function.

* Refine the output format. Would be good to the output as a CSV or Excel file.


### Query to generate people to screen
```mysql
    SELECT user_id, legal_first_name, first_name, middle_initial, last_name,
            address, city, state, zip, gender,
            month_of_birth, day_of_birth, year_of_birth
    FROM
    (
        SELECT user_id, legal_first_name, middle_initial,
                month_of_birth, day_of_birth, year_of_birth FROM judges
        UNION ALL
        SELECT user_id, legal_first_name, middle_initial,
                month_of_birth, day_of_birth, year_of_birth FROM volunteers
    ) people
    JOIN users ON users.id = people.user_id
    WHERE users.role IN ('J', 'V')
```
