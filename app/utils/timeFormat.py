from datetime import datetime, timezone, time, timedelta
import calendar
import pytz

def format_ist(dt: datetime) -> str:
    """Convert UTC datetime to IST readable format"""
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=pytz.utc)
    ist = dt.astimezone(pytz.timezone('Asia/Kolkata'))
    return ist.strftime("%d %B %Y %I:%M %p IST")

def get_utc_timestamp():
    return datetime.now(timezone.utc)

def get_ist_timestamp():
    return datetime.now(timezone.utc).astimezone(pytz.timezone('Asia/Kolkata'))

def get_date():
    return datetime.now(timezone.utc).date()

def get_year() -> int:
    return datetime.now(timezone.utc).year

def format_date_to_datetime(date):
    return datetime.combine(date, time.min)

def get_remaining_days_month_ratio(current_date:datetime):
    total_days = calendar.monthrange(current_date.year, current_date.month)[1]
    remaining_days = total_days - current_date.day + 1
    return remaining_days/total_days

