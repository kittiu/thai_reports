# Copyright (c) 2024, Ecosoft and contributors
# For license information, please see license.txt

import frappe # type: ignore
from frappe import _ # type: ignore
import json 
from dateutil.relativedelta import relativedelta
from datetime import datetime, date, time, timedelta
from collections import defaultdict
from erpnext.accounts.report.trial_balance.trial_balance import validate_filters, get_data as get_data_from_trial_balance  # type: ignore

def execute(filters=None):
    # validate_filters(filters)
    data = get_data(filters)
    columns = get_columns(filters)
    return columns, data

def custom_date_serializer(obj):
    if isinstance(obj, date):
        return obj.isoformat()  # Convert date to ISO 8601 string format
    raise TypeError(f"Type {type(obj)} not serializable")

def get_data(filters):
    data = []
    from_date = datetime.strptime(filters.from_date, '%Y-%m-%d')
    to_date = datetime.strptime(filters.to_date, '%Y-%m-%d')

    month_all = []
    month_all = get_month_by_from_to_date(from_date, to_date)
    # Iterate through each month between from_date and to_date


    
    # Initialize a dictionary to store data by account
    combined_data = defaultdict(dict)

    # Initialize month counter
    month_counter = 1
    index = 0
    # Process data for each date range
    total_account = None

    for filter_date in month_all:
        filters.from_date = filter_date['from_date']
        filters.to_date = filter_date['to_date']
        data = get_data_from_trial_balance(filters)
        index += 1

        # Serialize data with custom date handler
        # try:
        #     print(f'data: {index} :', json.dumps(data, default=custom_date_serializer))
        # except TypeError as e:
        #     print(f"Error serializing data: {e}")

        for record in data:
            account = record.get('account')
            if not account:
                # print(f"Skipping record due to missing 'account': {record}")
                continue

            # Check if the account is "Total" and store it separately
            if account == "'Total'":
                total_account = record.copy()  # Save the "Total" account to add it later
                continue

            # Initialize account if not already present
            if account not in combined_data:
                combined_data[account] = {
                    **record,  # Copy all initial data from the record
                    f'm{month_counter}': 0  # Initialize the first monthly field
                }

            # Get the closing values
            closing_debit = record.get('closing_debit', 0)
            closing_credit = record.get('closing_credit', 0)

            # Update the monthly fields (m1, m2, m3, etc.)
            combined_data[account][f'm{month_counter}'] = closing_debit if closing_debit else -closing_credit
        # Increment the month counter for the next iteration
        month_counter += 1

    # Convert the combined_data to a list of dictionaries
    final_data = list(combined_data.values())

    # If the "Total" account was found, append it to the end
    # if total_account:
    #     final_data.append(total_account)


    return final_data

def get_columns(filters):

    from_date, to_date = frappe.db.get_value("Fiscal Year", filters.fiscal_year, "year_start_date, year_end_date", cache=True)

    # Convert to datetime objects if necessary
    if isinstance(from_date, str):
        from_date = datetime.strptime(from_date, '%Y-%m-%d').date()
    if isinstance(to_date, str):
        to_date = datetime.strptime(to_date, '%Y-%m-%d').date()

    # Calculate the first and last month in the range
    start_month = datetime(from_date.year, from_date.month, 1)
    end_month = datetime(to_date.year, to_date.month, 1)

    months = []
    while start_month <= end_month:
        months.append(start_month.strftime('%Y-%m'))  # Format as 'YYYY-MM'
        # Move to the next month
        next_month = start_month + timedelta(days=31)
        start_month = datetime(next_month.year, next_month.month, 1)


    # List of month names
    # month_names = ['มกราคม', 'กุมภาพันธ์', 'มีนาคม', 'เมษายน', 'พฤษภาคม', 'มิถุนายน',
    #                 'กรกฎาคม', 'สิงหาคม', 'กันยายน', 'ตุลาคม', 'พฤศจิกายน', 'ธันวาคม']
    month_names = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
    # Create a dictionary to hold the month variables
    month_vars = {}

    # Map each month from the list to its corresponding variable
    for i, month in enumerate(months):
        year_month = datetime.strptime(month, '%Y-%m')
        month_name = month_names[year_month.month - 1]  # Get month name from month index
        month_vars[f"m{i+1}"] = month_name
        

    # # Print the variables
    # for key, value in month_vars.items():
    #     print(f"{key} = \"{value}\"")

    # print('m1 month name:', month_vars.get('m1'))  # Output: "October"
    # print('m1 month name:', month_vars) 
    # print('from_date', from_date)
    # print('to_date', to_date)

    colmun =  [
        {
            "fieldname": "account",
            "label": _("Account"),
            "fieldtype": "Data",
            "options": "Account",
            "width": 300,
        },
        {
            "fieldname": "m1",
            "label": _(month_vars.get('m1')),
            "fieldtype": "Currency",
            "options": "currency",
            "width": 300,
        },
        {
            "fieldname": "m2",
            "label": _(month_vars.get('m2')),
            "fieldtype": "Currency",
            "width": 300,
        },
        {
            "fieldname": "m3",
            "label": _(month_vars.get('m3')),
            "fieldtype": "Currency",
            "width": 300,
        },
        {
            "fieldname": "m4",
            "label": _(month_vars.get('m4')),
            "fieldtype": "Currency",
            "options": "currency",
            "width": 300,
        },
        {
            "fieldname": "m5",
            "label": _(month_vars.get('m5')),
            "fieldtype": "Currency",
            "options": "currency",
            "width": 300,
        },
        {
            "fieldname": "m6",
            "label": _(month_vars.get('m6')),
            "fieldtype": "Currency",
            "options": "currency",
            "width": 300,
        },
        {
            "fieldname": "m7",
            "label": _(month_vars.get('m7')),
            "fieldtype": "Currency",
            "options": "currency",
            "width": 300,
        },
        {
            "fieldname": "m8",
            "label": _(month_vars.get('m8')),
            "fieldtype": "Currency",
            "options": "currency",
            "width": 300,
        },
        {
            "fieldname": "m9",
            "label": _(month_vars.get('m9')),
            "fieldtype": "Currency",
            "options": "currency",
            "width": 300,
        },
        {
            "fieldname": "m10",
            "label": _(month_vars.get('m10')),
            "fieldtype": "Currency",
            "options": "currency",
            "width": 300,
        },
        {
            "fieldname": "m11",
            "label": _(month_vars.get('m11')),
            "fieldtype": "Currency",
            "options": "currency",
            "width": 300,
        },
        {
            "fieldname": "m12",
            "label": _(month_vars.get('m12')),
            "fieldtype": "Currency",
            "options": "currency",
            "width": 300,
        },
    ]

    return colmun


def get_month_by_from_to_date(from_date, to_date):
    month = []
    current_date = from_date
    while current_date <= to_date:
        # Calculate the last day of the current month
        next_month = current_date + relativedelta(months=1)
        last_day_of_month = next_month - relativedelta(days=1)
        
        # Append the date range dictionary to month_all
        month.append({
            "from_date": current_date.date(),  # Convert to date type
            "to_date": last_day_of_month.date()  # Convert to date type
        })
        
        # Move to the next month
        current_date = next_month

    return month