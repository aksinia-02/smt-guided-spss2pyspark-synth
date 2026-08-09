import re

from smt_types import DateType, DateUnit

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

    TYPE_MAP_3 = {
        "jahr": DateType.TYPE_YEAR,
        "monat": DateType.TYPE_MONTH,
        "tag": DateType.TYPE_DAY,
    }

    @classmethod
    def decode(cls, param_str: str) -> dict:

        found_type = 0
        match = re.match(r"\$P-(plus|minus)(\d+)([a-zA-Z]+)", param_str)
        if match:
            found_type = 1
        else:
            match = re.match(r"\$P-([a-zA-Z]+)(zahl)([a-zA-Z]*)$", param_str)
            if match:
                found_type = 3
            else:
                match = re.match(r"\$P-([a-zA-Z0-9]+)$", param_str)
                if match:
                    found_type = 2
                else:
                    raise ValueError(f"Unrecognized SPSS date parameter format: {param_str}")

        jump = None
        match found_type:
            case 1:
                direction, amount, raw_unit = match.groups()
                print("case1")
            case 2:
                raw_unit = match.group(1)
                lower_unit = raw_unit.lower()
                direction = "minus" if "vor" in lower_unit else "plus" if "next" in lower_unit else None
                jump = "last" if "ultimo" in lower_unit.lower() else None
                jump_add = " year" if "jahr" in lower_unit else " month"
                jump = f"last{jump_add}" if jump else None
                amount = None
            case 3:
                raw_unit, indicator, modifier = match.groups() # e.g. ('jahr', 'zahl', 'NextJahr')
                mod_lower = modifier.lower()
                
                if "next" in mod_lower:
                    direction = "plus"
                    amount = 1
                elif "vor" in mod_lower:
                    direction = "minus"
                    amount = 1
                else: # Handles 'Aktuell' or empty string ''
                    direction = None
                    amount = None

        raw_unit = raw_unit.lower()

        unit = next(
            (
                unit_val for key, unit_val in cls.UNIT_MAP.items() if key in raw_unit
            ),
            raw_unit
        ) if direction else None

        if found_type == 3:

            date_type = next(
                (type_val for key, type_val in cls.TYPE_MAP_3.items() if key in raw_unit),
                None
            )
        else:
            date_type = next(
                (type_val for key, type_val in cls.TYPE_MAP.items() if key in raw_unit),
                None
            )

        amount = 1 if direction and amount is None else amount

        if param_str == "$P-tag":
            date_type = DateType.TYPE_DATE
        
        return {
            k: v
            for k, v in {
                "direction": direction,
                "amount": int(amount) if amount is not None else None,
                "unit": unit,
                "type": date_type,
                "jump": jump,
                #"method_name": f"{direction}_{unit}" if direction and unit else None,
            }.items()
            if v is not None
        }