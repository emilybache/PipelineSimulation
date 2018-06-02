from datetime import timedelta


def next_weekday(now):
    next_day = now + timedelta(days=1)
    if next_day.isoweekday() == 6: # saturday
        next_day += timedelta(days=2)
    if next_day.isoweekday() == 7: # sunday
        next_day += timedelta(days=1)
    return next_day


def weekday_offset(today, target_weekday):
    days = (7 - today + target_weekday)
    if days > 7:
        days -= 7
    return days


def next_day_of_week(now, target_weekday):
    n = weekday_offset(now.isoweekday(), target_weekday)
    return now + timedelta(days=n)