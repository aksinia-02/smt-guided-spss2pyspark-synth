import re

from matplotlib.pylab import number

from enums.smt_types import DateType, DateUnit
from invariants import PrimitiveSemantics

class SPSSDateParamDecoder:
    """
    Parses SPSS parameter strings like '$P-plus1tag' or '$P-minus2monat'
    and translates them into normalized target metadata.
    """
    UNIT_MAP = {
        "jahr": DateUnit.YEAR, "jahre": DateUnit.YEAR, "jahren": DateUnit.YEAR,
        "monat": DateUnit.MONTH, "monate": DateUnit.MONTH, "monaten": DateUnit.MONTH,
        "woche": DateUnit.WEEK, "wochen": DateUnit.WEEK,
        "tag": DateUnit.DAY, "tage": DateUnit.DAY, "tagen": DateUnit.DAY,
    }

    TYPE_MAP = {
        "datum": DateType.TYPE_DATE,
        "8stellig": DateType.TYPE_INT,
        "tag": DateType.TYPE_INT,
        "monat": DateType.TYPE_INT_YM,
    }

    TYPE_MAP_ZAHL = {
        "jahr": DateType.TYPE_YEAR,
        "monat": DateType.TYPE_MONTH,
        "tag": DateType.TYPE_DAY,
    }

    PATTERNS = [
        (re.compile(r"\$P-(plus|minus)(\d+)([a-zA-Z]+)$"), "_parse_offset"),
        (re.compile(r"\$P-([a-zA-Z]+)zahl([a-zA-Z]*)$"), "_parse_zahl"),
        (re.compile(r"\$P-([a-zA-Z0-9]+)$"), "_parse_generic"),
    ]

    @staticmethod
    def _parse_offset(match: re.Match) -> dict:
        direction, amount, raw_unit = match.groups()
        weeks = False
        if int(amount) % 7 == 0:
            weeks_amount = int(int(amount) / 7)
            weeks = True
        return {
            "case": 1,
            "raw_unit": raw_unit,
            "direction": direction,
            "amount": weeks_amount if weeks else int(amount),
            "jump": None,
            "weeks": weeks
        }

    @staticmethod
    def _parse_zahl(match: re.Match) -> dict:
        raw_unit, modifier = match.groups()
        mod_lower = modifier.lower()

        if "next" in mod_lower:
            direction, amount = "plus", 1
        elif "vor" in mod_lower:
            direction, amount = "minus", 1
        else:
            direction, amount = None, None

        return {
            "case": 2,
            "raw_unit": raw_unit,
            "direction": direction,
            "amount": amount,
            "jump": None,
            "weeks": False
        }

    @staticmethod
    def _parse_generic(match: re.Match) -> dict:
        raw_unit = match.group(1)
        lower = raw_unit.lower()

        direction = "minus" if "vor" in lower else "plus" if "next" in lower else None

        jump = None
        if "ultimo" in lower:
            jump = "end year" if "jahr" in lower else "end month"

        return {
            "case": 3,
            "raw_unit": raw_unit,
            "direction": direction,
            "amount": 1 if direction else None,
            "jump": jump,
            "weeks": False
        }

    @classmethod
    def decode(cls, param_str: str) -> dict:

        parsed = None
        for pattern, handler_name in cls.PATTERNS:
            match = pattern.match(param_str)
            if match:
                handler = getattr(cls, handler_name)
                parsed = handler(match)
                break

        if not parsed:
            raise ValueError(f"Unrecognized SPSS date parameter format: {param_str}")

        raw_unit_lower = parsed["raw_unit"].lower()

        unit = next(
            (
                unit_val for key, unit_val in cls.UNIT_MAP.items() if key in raw_unit_lower
            ),
            raw_unit_lower
        ) if parsed["direction"] else None

        unit = "week" if parsed["weeks"] else unit

        mapping = cls.TYPE_MAP_ZAHL if parsed["case"] == 2 else cls.TYPE_MAP

        date_type = next(
            (type_val for key, type_val in mapping.items() if key in raw_unit_lower),
            None
        )

        if param_str == "$P-tag":
            date_type = DateType.TYPE_DATE

        primitive = PrimitiveSemantics(
            target_type=date_type,
            direction=parsed["direction"],
            unit=unit,
            amount=parsed["amount"],
            jump=parsed["jump"]
        )

        return primitive

        # return {
        #     k: v
        #     for k, v in {
        #         "direction": parsed["direction"],
        #         "amount": parsed["amount"],
        #         "unit": unit,
        #         "type": date_type,
        #         "jump": parsed["jump"],
        #     }.items()
        #     if v is not None
        # }