import datetime as dt
import pytest

from dataparams import DatesNamespace


def test_dataparam():
    # Pass dt.date as YYYYMMDD integer
    D = DatesNamespace(20260807)

    # 1. Test Base Properties & Direct Access Types
    assert D.as_date.BD == dt.date(2026, 8, 7)
    assert D.as_int.BD == 20260807
    assert D.as_str.BD == "2026-08-07"
    assert D.as_strYM.current_month == "202608"

    # 2. Test Month/Year Bounds (as string available)
    assert D.as_date.month_start == dt.date(2026, 8, 1)
    assert D.as_date.month_end == dt.date(2026, 8, 31)
    assert D.as_date.year_start == dt.date(2026, 1, 1)
    assert D.as_date.year_end == dt.date(2026, 12, 31)

    # future
    assert D.as_date.plus_day(1) == dt.date(2026, 8, 8)
    assert D.as_date.plus_week == dt.date(2026, 8, 14)
    assert D.as_date.plus_month(2) == dt.date(2026, 10, 7)
    assert D.as_date.plus_month_start(3) == dt.date(2026, 11, 1)
    assert D.as_date.plus_month_end(1) == dt.date(2026, 9, 30)
    assert D.as_date.plus_year == dt.date(2027, 8, 7)


    # past
    assert D.as_date.minus_day(1) == dt.date(2026, 8, 6)
    assert D.as_date.minus_week(1) == dt.date(2026, 7, 31)
    assert D.as_date.minus_month(1) == dt.date(2026, 7, 7)
    assert D.as_date.minus_month_start(1) == dt.date(2026, 7, 1)
    assert D.as_date.minus_month_end(1) == dt.date(2026, 7, 31)
    assert D.as_date.minus_year == dt.date(2025, 8, 7)
    assert D.as_date.minus_year_start == dt.date(2025, 1, 1)
    assert D.as_date.minus_year_end == dt.date(2025, 12, 31)

    assert D.as_date.minus_30days == dt.date(2026, 7, 8)
    assert D.as_date.minus_60days == dt.date(2026, 6, 8)
    assert D.as_date.minus_90days == dt.date(2026, 5, 9)

    # 3. Test Direct Aliases (also as dates available)
    assert D.as_str.tomorrow == "2026-08-08"
    assert D.as_str.next_week == "2026-08-14"
    assert D.as_str.next_month == "2026-09-07"
    assert D.as_str.next_year == "2027-08-07"

    assert D.as_str.yesterday == "2026-08-06"
    assert D.as_str.week_ago == "2026-07-31"
    assert D.as_str.month_ago == "2026-07-07"
    assert D.as_str.year_ago == "2025-08-07"

    # 4. Test Dynamic Offset Methods
    assert D.as_str.plus_day(5) == "2026-08-12"
    assert D.as_str.minus_day(3) == "2026-08-04"
    assert D.as_str.plus_month(2) == "2026-10-07"
    assert D.as_str.minus_month(3) == "2026-05-07"

    # 5. Test Additional Features (e.g. ISO Calendar Week)
    assert D.as_int.calendar_week == 32

    # 6. Test Input Validation & Bounds
    with pytest.raises(ValueError, match="n must be between 1 and 10"):
        D.as_date.plus_day(15)

    with pytest.raises(ValueError, match="n must be between 1 and 18"):
        D.as_date.minus_month(20)

    assert D.as_strYM.current_month == "202608"
    assert D.as_strYM.plus_month(1) == "202609"
    assert D.as_strYM.minus_month(2) == "202606"
    assert D.as_strYM.prev_month == "202607"
    assert D.as_strYM.next_month == "202609"