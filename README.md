# Minimum Assignment

I made some design decisions while implementing my solution, and I wanted to create this readme document to explain why I made these decisions, and add some additional information that I think could be relevant.

## Setup and Running

We have a requirements.txt file which includes the third party libraries we need installed to run our project. Assuming we have python 3 installed, we can use "pip install -r requirements.txt" to install the required libraries. A virtual environment is recommended for the run environment. After the required libraries are installed, the django server can be started with: "python manage.py runserver"

## Logging

I did not implement a sophisticated logging system, instead choosing to use print statements where I would normally log important events. I did put comments next to these lines to indicate my purpose with these statements.

## Endpoint Flow

I created three endpoints to capture the flow: Endpoint one reads the csv which has the emmission factors data and records them in the database. The second endpoint reads a csv file which has the activity data, calculates the correct emmission value, and records this data in the database. The third endpoint is to retrieve the emmission data, and the filtering, sorting and grouping functionality is also implemented in this endpoint. I used post endpoints for all three endpoints, for consistency's sake.

### register_emmission_factors

This endpoint is used to register the emmission factor data in the database. A variable named "filepath" is expected in the body of the request. A success field is returned as True if all emmission factor entries were successfully created in the database.

### read_emmission_records

This endpoint is used to read activity data, calculate emmission values and record them in the database. A variable named "filepath" is expected in the body of the request. A success field is returned as True if emmission data was successfully calculated and recorded for every row.

The way this endpoint is implemented is so that if we have a problem recording a row of the csv, (for example: unknown unit, unknown lookup identifier, unknown activity) we continue with the other rows of the csv, and record every valid row we find in the database. This function can be changed to use a transaction, so we would either capture every row or none of them. I chose to write it this way, so if we fail on some rows, we still capture the valid rows, and we have log statements to indicate which rows caused issues. If there are any rows that failed, we will return False in the success field.

### get_emmissions

This endpoint is used to get the requested emmission records and the total emmission sum. The fields expected in the request body are: is_sorted: bool, filter_category: int, filter_scope: int, grouped: bool. All of these fields can be None or not sent over at all.

If the is_sorted field is missing, we do not sort the data at all. If the field is True, we sort the result in descending order, if False, we sort in ascending order.

If filter_category is missing, we do not filter by category. If it is filled, we only show emmission records with the given category value.

If filter_scope is missing, we do not filter by scope. If it is filled, we only show emmission records with the given scope value.

If grouped is missing or false, we do not group the emmission records. If true, we group by ativity type, and give the count and total co2e values for the grouped records.

We currently return a list of dicts in the emmissions field, and the fields will differ depending on whether the records are grouped or not. We also return the total sum of all emmission records in the emmissions_sum field.

The filters, grouping and sorting features can be used in any combination, for example if is_sorted=True and grouped=True, the returned groups will be in sorted order.

## Testing/UI

For testing, I used the default UI's provided by the django rest framework. For example, a flow could be:

going to http://127.0.0.1:8000/calculator/register_emmission_factor
sending a post request with
{
"filepath":"Minimum Technical Exercise/Technical interview - Emission Factors and Activity Data - Emission Factors.csv"
}

going to http://127.0.0.1:8000/calculator/read_emmission_records
sending a post request with
{
"filepath":"Minimum Technical Exercise/Technical interview - Emission Factors and Activity Data - Air Travel.csv"
}

going to http://127.0.0.1:8000/calculator/get_emmissions
sending a post request with
{
"is_sorted" : true,
"filter_category" : 6,
"filter_scope": 3,
"grouped" : true
}

## Design Decisions

Some discrepancies in capitalization between the different csv files led me to getting rid of capitalization altogether for string fields, so we don't miss matches due to inconsistent capitalization.

There was a unit mismatch between the activity records and emmission factors for Air Travel, so I created a TYPE_CONVERSIONS_DICT dictionary so I can convert from miles to kilometers. More conversion values can be added to this dict so we can handle more unit mismatches coming from activity records, such as converting USD to GBP for Purchased Goods and Services records, but right now only miles-kilometres is implemented since that was the only one needed in the test cases.

### Error Handling

In a lot of places where errors could be raised, I chose to handle the errors instead, create log statements and return None values. These behaviours could be changed according to what the project needs.
