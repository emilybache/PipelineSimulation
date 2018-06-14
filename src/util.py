from datetime import timedelta


class OfficeHours:
    def __init__(self):
        self.working_hour_start = 8
        self.working_hour_end = 18

    def interval(self, start_time, end_time):
        interval = end_time - start_time
        # if its overnight, don't count the night
        if start_time.day != end_time.day:
            interval -= timedelta(hours=24-self.working_hour_end+self.working_hour_start)
            # if its a friday - monday, don't count the weekend
            if end_time.isoweekday() == 1 and start_time.isoweekday() == 5:
                interval -= timedelta(days=2)
        return interval


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