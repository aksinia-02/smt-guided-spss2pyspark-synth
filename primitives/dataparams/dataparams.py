from dataclasses import dataclass, field
from datetime import date
from dateutil.relativedelta import relativedelta


@dataclass
class DatesNamespace:
    # Get business date
    """
    Parameters
    ----------
    input_date : str
        Input date in isoformat: 'YYYYMMDD' or 'YYYY-MM-DD'
    offset : int, optional
        Offset in days; default is -1,
    Returns
    -------
    date : date | str | int
        Dates in isoformat: 'YYYYMMDD' or 'YYYY-MM-DD' or as int

    Business date by default is set to one day before (offset=-1) the input date, which by default is expected to be given as today.
    To get exactly the input date, set offset=0.

    ## Business date by default is set to match the input date.
    ## To get a day before or after the input date, change the to offset=-1 for previous day or offset=1 for next day.
    """
    input_date: str | int
    offset: int = -1   # day given

    as_date: "_ShowDate" = field(init=False)
    as_int: "_ShowInt" = field(init=False)
    as_str: "_ShowStr" = field(init=False)
    as_intYM: "_ShowIntYM" = field(init=False)

    def __post_init__(self):
        try:
            self._BD = date.fromisoformat(str(self.input_date)) + relativedelta(days=self.offset)
        except ValueError:
            print("Business date must be in isoformat: 'YYYYMMDD' or 'YYYY-MM-DD'")
        self._month_start = self._BD + relativedelta(day=1)
        self._month_end = self._BD + relativedelta(day=31)
        self._year_start = self._BD + relativedelta(day=1, month=1)
        self._year_end = self._BD + relativedelta(day=31, month=12)

        # next:
        self._plus_days = {k: self._BD + relativedelta(days=k) for k in range(1, 11)}
        self._plus_weeks = {k: self._BD + relativedelta(weeks=k) for k in range(1, 5)}
        self._plus_year = self._BD + relativedelta(years=1)
        self._plus_months = {
            k: self._BD + relativedelta(months=k) for k in range(1, 19)
        }
        self._plus_months_start = {
            k: self._BD + relativedelta(months=k, day=1) for k in range(1, 19)
        }
        self._plus_months_end = {
            k: self._BD + relativedelta(months=k, day=31) for k in range(1, 19)
        }
        # past:
        self._minus_days = {k: self._BD + relativedelta(days=-k) for k in range(1, 11)}
        self._minus_weeks = {k: self._BD + relativedelta(weeks=-k) for k in range(1, 5)}
        self._minus_months = {
            k: self._BD + relativedelta(months=-k) for k in range(1, 19)
        }
        self._minus_months_start = {
            k: self._BD + relativedelta(months=-k, day=1) for k in range(1, 19)
        }
        self._minus_months_end = {
            k: self._BD + relativedelta(months=-k, day=31) for k in range(1, 19)
        }
        self._minus_year = self._BD + relativedelta(years=-1)
        self._minus_year_start = self._BD + relativedelta(years=-1, day=1, month=1)
        self._minus_year_end = self._BD + relativedelta(years=-1, day=31, month=12)
        self._minus_30days = self._BD + relativedelta(days=-30)
        self._minus_60days = self._BD + relativedelta(days=-60)
        self._minus_90days = self._BD + relativedelta(days=-90)
        # Access types:
        self.as_date = self._ShowDate(self)
        self.as_int = self._ShowInt(self)
        self.as_str = self._ShowStr(self)
        self.as_intYM = self._ShowIntYM(self)

    # Set helpers
    def _validate_day_index(self, n: int) -> int:
        if not 1 <= n < 11:
            raise ValueError("n must be between 1 and 10")
        return n

    def _validate_week_index(self, n: int) -> int:
        if not 1 <= n < 5:
            raise ValueError("n must be between 1 and 4")
        return n

    def _validate_month_index(self, n: int) -> int:
        if not 1 <= n < 19:
            raise ValueError("n must be between 1 and 18")
        return n

    def _get_plus_day(self, n: int) -> date:
        return self._plus_days[self._validate_day_index(n)]

    def _get_plus_week(self, n: int) -> date:
        return self._plus_weeks[self._validate_week_index(n)]

    def _get_plus_month(self, n: int) -> date:
        return self._plus_months[self._validate_month_index(n)]

    def _get_plus_month_start(self, n: int) -> date:
        return self._plus_months_start[self._validate_month_index(n)]

    def _get_plus_month_end(self, n: int) -> date:
        return self._plus_months_end[self._validate_month_index(n)]

    def _get_minus_day(self, n: int) -> date:
        return self._minus_days[self._validate_day_index(n)]

    def _get_minus_week(self, n: int) -> date:
        return self._minus_weeks[self._validate_week_index(n)]

    def _get_minus_month(self, n: int) -> date:
        return self._minus_months[self._validate_month_index(n)]

    def _get_minus_month_start(self, n: int) -> date:
        return self._minus_months_start[self._validate_month_index(n)]

    def _get_minus_month_end(self, n: int) -> date:
        return self._minus_months_end[self._validate_month_index(n)]

    class _ShowDate:
        def __init__(self, dates):
            self._dates = dates

        # current
        @property
        def BD(self) -> date:
            return self._dates._BD

        @property
        def month_start(self) -> date:
            return self._dates._month_start

        @property
        def month_end(self) -> date:
            return self._dates._month_end

        @property
        def year_start(self) -> date:
            return self._dates._year_start

        @property
        def year_end(self) -> date:
            return self._dates._year_end

        # next
        def plus_day(self, n: int) -> date:
            return self._dates._get_plus_day(n)

        def plus_week(self, n: int):
            return self._dates._get_plus_week(n)

        def plus_month(self, n: int) -> date:
            return self._dates._get_plus_month(n)

        def plus_month_start(self, n: int) -> date:
            return self._dates._get_plus_month_start(n)

        def plus_month_end(self, n: int) -> date:
            return self._dates._get_plus_month_end(n)

        @property
        def plus_year(self) -> date:
            return self._dates._plus_year

        # past
        def minus_day(self, n: int) -> date:
            return self._dates._get_minus_day(n)

        def minus_week(self, n: int) -> date:
            return self._dates._get_minus_week(n)

        def minus_month(self, n: int) -> date:
            return self._dates._get_minus_month(n)

        def minus_month_start(self, n: int) -> date:
            return self._dates._get_minus_month_start(n)

        def minus_month_end(self, n: int) -> date:
            return self._dates._get_minus_month_end(n)

        @property
        def minus_year(self) -> date:
            return self._dates._minus_year

        @property
        def minus_year_start(self) -> date:
            return self._dates._minus_year_start

        @property
        def minus_year_end(self) -> date:
            return self._dates._minus_year_end

        @property
        def minus_30days(self) -> date:
            return self._dates._minus_30days

        @property
        def minus_60days(self) -> date:
            return self._dates._minus_60days

        @property
        def minus_90days(self) -> date:
            return self._dates._minus_90days

        ### Aliases ###
        @property
        def tomorrow(self) -> date:
            return self.plus_day(1)

        @property
        def next_week(self) -> date:
            return self.plus_week

        @property
        def next_month(self) -> date:
            return self.plus_month(1)

        @property
        def next_year(self) -> date:
            return self.plus_year

        @property
        def yesterday(self) -> date:
            return self.minus_day(1)

        @property
        def week_ago(self) -> date:
            return self.minus_week(1)

        @property
        def month_ago(self) -> date:
            return self.minus_month(1)

        @property
        def year_ago(self) -> date:
            return self.minus_year

    class _ShowInt:
        def __init__(self, dates):
            self._dates = dates

        def _to_int(self, d) -> int:
            return int(d.strftime("%Y%m%d"))

        # current
        @property
        def BD(self):
            return self._to_int(self._dates._BD)

        @property
        def month_start(self):
            return self._to_int(self._dates._month_start)

        @property
        def month_end(self):
            return self._to_int(self._dates._month_end)

        @property
        def year_start(self) -> date:
            return self._to_int(self._dates._year_start)

        @property
        def year_end(self) -> date:
            return self._to_int(self._dates._year_end)

        # next
        def plus_day(self, n: int) -> date:
            return self._to_int(self._dates._get_plus_day(n))

        def plus_week(self, n: int):
            return self._dates._get_plus_week(n)

        def plus_month(self, n: int):
            return self._to_int(self._dates._get_plus_month(n))

        def plus_month_start(self, n: int):
            return self._to_int(self._dates._get_plus_month_start(n))

        def plus_month_end(self, n: int):
            return self._to_int(self._dates._get_plus_month_end(n))

        @property
        def plus_year(self):
            return self._to_int(self._dates._plus_year)

        # past
        def minus_day(self, n: int) -> date:
            return self._to_int(self._dates._get_minus_day(n))

        def minus_week(self, n: int) -> date:
            return self._to_int(self._dates._get_minus_week(n))

        def minus_month(self, n: int):
            return self._to_int(self._dates._get_minus_month(n))

        def minus_month_start(self, n: int):
            return self._to_int(self._dates._get_minus_month_start(n))

        def minus_month_end(self, n: int):
            return self._to_int(self._dates._get_minus_month_end(n))

        @property
        def minus_year(self):
            return self._to_int(self._dates._minus_year)

        @property
        def minus_year_start(self) -> date:
            return self._to_int(self._dates._minus_year_start)

        @property
        def minus_year_end(self) -> date:
            return self._to_int(self._dates._minus_year_end)

        @property
        def minus_30days(self) -> date:
            return self._to_int(self._dates._minus_30days)

        @property
        def minus_60days(self) -> date:
            return self._to_int(self._dates._minus_60days)

        @property
        def minus_90days(self) -> date:
            return self._to_int(self._dates._minus_90days)

        ### Aliases ###
        @property
        def tomorrow(self):
            return self.plus_day(1)

        @property
        def next_week(self):
            return self.plus_week

        @property
        def next_month(self):
            return self.plus_month(1)

        @property
        def next_year(self):
            return self.plus_year

        @property
        def yesterday(self):
            return self.minus_day(1)

        @property
        def week_ago(self):
            return self.minus_week(1)

        @property
        def month_ago(self):
            return self.minus_month(1)

        @property
        def year_ago(self):
            return self.minus_year

        # Add-on
        @property
        def calendar_week(self) -> int:
            return self._dates._BD.isocalendar().week

    class _ShowStr:
        def __init__(self, dates):
            self._dates = dates

        def _to_str(self, d) -> str:
            return d.strftime("%Y-%m-%d")

        # current
        @property
        def BD(self):
            return self._to_str(self._dates._BD)

        @property
        def month_start(self):
            return self._to_str(self._dates._month_start)

        @property
        def month_end(self):
            return self._to_str(self._dates._month_end)

        @property
        def year_start(self) -> date:
            return self._to_str(self._dates._year_start)

        @property
        def year_end(self) -> date:
            return self._to_str(self._dates._year_end)

        # next
        def plus_day(self, n: int) -> date:
            return self._to_str(self._dates._get_plus_day(n))

        def plus_week(self, n: int):
            return self._dates._get_plus_week(n)

        def plus_month(self, n: int):
            return self._to_str(self._dates._get_plus_month(n))

        def plus_month_start(self, n: int):
            return self._to_str(self._dates._get_plus_month_start(n))

        def plus_month_end(self, n: int):
            return self._to_str(self._dates._get_plus_month_end(n))

        @property
        def plus_year(self):
            return self._to_str(self._dates._plus_year)

        # past
        def minus_day(self, n: int) -> date:
            return self._to_str(self._dates._get_minus_day(n))

        def minus_week(self, n: int) -> date:
            return self._to_str(self._dates._get_minus_week(n))

        def minus_month(self, n: int):
            return self._to_str(self._dates._get_minus_month(n))

        def minus_month_start(self, n: int):
            return self._to_str(self._dates._get_minus_month_start(n))

        def minus_month_end(self, n: int):
            return self._to_str(self._dates._get_minus_month_end(n))

        @property
        def minus_year(self):
            return self._to_str(self._dates._minus_year)

        @property
        def minus_year_start(self) -> date:
            return self._to_str(self._dates._minus_year_start)

        @property
        def minus_year_end(self) -> date:
            return self._to_str(self._dates._minus_year_end)

        @property
        def minus_30days(self) -> date:
            return self._to_str(self._dates._minus_30days)

        @property
        def minus_60days(self) -> date:
            return self._to_str(self._dates._minus_60days)

        @property
        def minus_90days(self) -> date:
            return self._to_str(self._dates._minus_90days)

        ### Aliases ###
        @property
        def tomorrow(self):
            return self.plus_day(1)

        @property
        def next_week(self):
            return self.plus_week

        @property
        def next_month(self):
            return self.plus_month(1)

        @property
        def next_year(self):
            return self.plus_year

        @property
        def yesterday(self):
            return self.minus_day(1)

        @property
        def week_ago(self):
            return self.minus_week(1)

        @property
        def month_ago(self):
            return self.minus_month(1)

        @property
        def year_ago(self):
            return self.minus_year

    class _ShowIntYM:
        def __init__(self, dates):
            self._dates = dates

        def _to_int(self, d) -> int:
            return int(d.strftime("%Y%m"))

        def minus_month(self, n: int):
            return self._to_int(self._dates._get_minus_month(n))

        def plus_month(self, n: int):
            return self._to_int(self._dates._get_plus_month(n))

        ### Aliases ###
        @property
        def current_month(self):
            return self._to_int(self._dates._BD)

        @property
        def next_month(self):
            return self.plus_month(1)

        @property
        def prev_month(self):
            return self.minus_month(1)