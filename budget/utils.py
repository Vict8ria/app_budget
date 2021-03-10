from datetime import datetime
from dateutil.relativedelta import relativedelta


def get_months(count):
    today = datetime.today()
    current_date = datetime(today.year, today.month, 1)
    months_list = [current_date]
    for count_number in range(1, count):
        month = current_date - relativedelta(months=count_number)
        months_list.append(month)
    return months_list
