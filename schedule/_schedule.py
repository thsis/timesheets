import os
import datetime
import random
import pandas as pd
import numpy as np
from calendar import monthrange
from dateutil.easter import easter
from utilities import get_path, get_config


DAYS = {"MON": 0, "Mon": 0, "Mo": 0, "Montag": 0, "Monday": 0,
        "TUE": 1, "Tue": 1, "Di": 1, "Dienstag": 1, "Tuesday": 1,
        "WED": 2, "Wed": 2, "Mi": 2, "Mittwoch": 2, "Wednesday": 2,
        "THU": 3, "Thu": 3, "Do": 3, "Donnerstag": 3, "Thursday": 3,
        "FRI": 4, "Fri": 4, "Fr": 4, "Freitag": 4, "Friday": 4,
        "SAT": 5, "Sat": 5, "Sa": 5, "Samstag": 5, "Saturday": 5,
        "SUN": 6, "Sun": 6, "So": 6, "Sonntag": 6, "Sunday": 6}
MONTHS = {"Januar": 1,
          "Februar": 2,
          "März": 3,
          "April": 4,
          "Mai": 5,
          "Juni": 6,
          "Juli": 7,
          "August": 8,
          "September": 9,
          "Oktober": 10,
          "November": 11,
          "Dezember": 12}
MONTHS_REV = {v: k for k, v in MONTHS.items()}
CONFIG = get_config()


def get_all_dates(year, month):
    _, max_date = monthrange(year, month)
    start = f"{year}-{month:02}-01"
    end = f"{year}-{month:02}-{max_date:02}"
    out = pd.date_range(start, end)
    return out


def get_holidays(year):
    new_year = f"{year}-01-01"
    womens_day = f"{year}-03-08"
    easter_sun = easter(year)
    easter_mon = easter_sun + datetime.timedelta(days=1)
    easter_fri = easter_sun - datetime.timedelta(days=2)
    may_first = f"{year}-05-01"
    fathers_day = easter_sun + datetime.timedelta(days=40)
    whitsun = easter_sun + datetime.timedelta(days=50)
    unification_day = f"{year}-10-03"
    christmas_1 = f"{year}-12-25"
    christmas_2 = f"{year}-12-26"
    new_years_eve = f"{year}-12-31"
    out = pd.to_datetime([new_year, womens_day, easter_fri, easter_sun,
                          easter_mon, may_first, fathers_day, whitsun,
                          unification_day, christmas_1, christmas_2,
                          new_years_eve])
    return out


def get_work_days(year, month):
    all_days = get_all_dates(year, month)
    holidays = get_holidays(year)
    work_days = pd.to_datetime([d for d in all_days if d not in holidays])
    return work_days


def get_penalty(x):
    if x > pd.Timedelta('9 hours'):
        return pd.Timedelta('45 minutes')
    elif x > pd.Timedelta('6 hours'):
        return pd.Timedelta('30 minutes')
    else:
        return pd.Timedelta('0 seconds')


def get_net_working_hours(df):
    duration = pd.to_timedelta(df.activity_end) - pd.to_timedelta(df.activity_start)
    penalties = duration.apply(get_penalty)
    out = (duration - penalties).sum() / pd.Timedelta('1 hour')
    return out


def generate_slot():
    for h in np.arange(5, 0, -0.25):
        yield pd.Timedelta(hours=h)


def strfdelta(tdelta, fmt="{hours:02}:{minutes:02}:{seconds:02}"):
    d = {"days": tdelta.days}
    d["hours"], rem = divmod(tdelta.seconds, 3600)
    d["minutes"], d["seconds"] = divmod(rem, 60)
    return fmt.format(**d)


def create_row(indexes, slot, note=None):
    idx = indexes[np.random.randint(0, len(indexes))]
    start_time = pd.Timedelta(hours=np.random.randint(6, 15))
    end_time = start_time + slot
    out = pd.DataFrame({"activity_start": strfdelta(start_time),
                        "activity_end": strfdelta(end_time),
                        "note": note},
                       index=[idx])
    return out


class Schedule:
    template = pd.read_csv(get_path("schedule.csv"), comment='#',
                           skipinitialspace=True,
                           parse_dates=["valid_from", "valid_until"],
                           converters={"day_of_week": lambda x: DAYS.get(x)})
    activities = pd.read_csv(get_path("activities.txt"), comment='#',
                             header=None, names=["title"]).title.to_list()
    # Ensure that activities has len of 2 - otherwise 'choice' throws a tantrum
    activities += [None, None]

    def __init__(self):
        self.total_hours = CONFIG["setup"]["total_hours"]
        self.year = CONFIG["setup"]["year"]
        self.start_sheet = CONFIG["general"]["start_sheet"]
        self.fill_missing = CONFIG["fill"]["fill_missing"]
        self.avoid_weekends = CONFIG["fill"]["avoid_weekends"]
        self.max_overtime = CONFIG["fill"]["max_overtime"]
        self.max_undertime = CONFIG["fill"]["max_undertime"]
        self.dates = None

    def fill(self, year, month):
        idx = get_work_days(year, month)
        df = pd.DataFrame(index=idx)
        df["day_of_week"] = df.index.dayofweek
        df = df.merge(self.template,
                      left_on="day_of_week",
                      right_on="day_of_week",
                      how="left").set_index(idx)
        df = df.loc[(df.valid_from <= df.index) & (df.index <= df.valid_until),
                    ["activity_start", "activity_end", "note"]]
        if len(df) == 0:
            df = pd.DataFrame(index=[idx.min()],
                              columns=["activity_start", "activity_end", "note"])
        self.dates = df
        return df.copy()

    def autocomplete(self, df):
        error = random.randint(-int(self.max_undertime), int(self.max_overtime))
        target = int(self.total_hours) + error
        work_days = get_work_days(df.index.min().year, df.index.min().month)
        slot_generator = generate_slot()
        slot = next(slot_generator)

        while get_net_working_hours(df) < target:
            try:
                indexes = work_days[~work_days.isin(df.index)]
                activity = np.random.choice(self.activities)
                row = create_row(indexes, slot, activity)
                assert get_net_working_hours(df) + get_net_working_hours(row) <= target
                df = pd.concat([df, row], axis=0)
            except AssertionError:
                slot = next(slot_generator)
                continue
            except StopIteration:
                break
        return df.sort_index().dropna(subset=["activity_start"], axis=0)


if __name__ == "__main__":
    schedule = Schedule()
    res = schedule.fill(2019, 12)
    complete = schedule.autocomplete(res)







