from datetime import datetime, timedelta

def generate_days_with_weekday(start_date, end_date):
    # Convert string inputs to datetime objects if they are in string format
    if isinstance(start_date, str):
        start_date = datetime.strptime(start_date, "%d-%m-%Y")
    if isinstance(end_date, str):
        end_date = datetime.strptime(end_date, "%d-%m-%Y")
    
    # Generate list of dates and corresponding weekday short names
    days_with_weekdays = []
    current_date = start_date
    while current_date <= end_date:
        day_data = {}
        weekday_short_name = current_date.strftime('%a')
        day_data['date'] = current_date.strftime('%d-%m-%Y')
        day_data['date2'] = current_date.strftime('%b, %d %Y')
        day_data['weekday'] = weekday_short_name
        days_with_weekdays.append(day_data)
        current_date += timedelta(days=1)  # Move to the next day

    return days_with_weekdays


