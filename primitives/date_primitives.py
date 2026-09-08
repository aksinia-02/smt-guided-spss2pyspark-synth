from .base_registry import BasePrimitiveRegistry
from enums.smt_types import DateType, DateUnit
from enums.categories import Category
from .Semantics import DateSemantics

class DatePrimitiveRegistry(BasePrimitiveRegistry):
    """Handles type conversion functions between Date, String, and Int."""
    
    def register_all(self) -> None:
        self.init_dateprimitives()

    def init_dateprimitives(self) -> None:
        name = f"D.as_intYM.current_month"
        return_type = DateType.TYPE_INT_YM
        arg_types = []
        category = Category.DATE_NAMESPACE

        pyspark_str = f"D.as_intYM.current_month"

        semantics = DateSemantics(
            name=f"D.as_intYM.current_month",
            target_type=DateType.TYPE_INT_YM,
            direction=None,
            unit=None,
            amount=None,
            jump=None
        )
        self.add_primitive(name, return_type, arg_types, category, semantics, pyspark_str)

        for type in [DateType.TYPE_YEAR, DateType.TYPE_MONTH, DateType.TYPE_DAY]:

            name = f"D.as_date.BD.{type.value}"
            return_type = type
            arg_types = []
            category = Category.DATE_NAMESPACE
    
            pyspark_str = f"D.as_date.BD.{type.value}"
    
            semantics = DateSemantics(
                name=f"D.as_date.BD.{type.value}",
                target_type=type,
                direction=None,
                unit=None,
                amount=None,
                jump=None
            )
            self.add_primitive(name, return_type, arg_types, category, semantics, pyspark_str)


        for direction in ["plus", "minus"]:

            plus_minus = "+" if direction == "plus" else "-"
    
            name = f"D.as_date.BD.{type.value} {plus_minus}"
            return_type = DateType.TYPE_YEAR
            arg_types = [(DateType.TYPE_INT, False)]
            category = Category.DATE_NAMESPACE
    
            pyspark_str = f"D.as_date.BD.{DateType.TYPE_YEAR.value} {plus_minus} {{0}}"
    
            semantics = DateSemantics(
                name=f"D.as_date.BD.{DateType.TYPE_YEAR.value} {plus_minus} {{0}}",
                target_type=DateType.TYPE_YEAR,
                direction=direction,
                unit=None,
                amount=None,
                jump=None
            )
            self.add_primitive(name, return_type, arg_types, category, semantics, pyspark_str)



        for type in [DateType.TYPE_DATE, DateType.TYPE_STRING, DateType.TYPE_INT]:
            name = f"D.as_{type.value}.BD"
            return_type = type
            arg_types = []
            category = Category.DATE_NAMESPACE

            pyspark_str = f"D.as_{type.value}.BD"

            semantics = DateSemantics(
                name=f"D.as_{type.value}.BD",
                target_type=type,
                direction=None,
                unit=None,
                amount=None,
                jump=None
            )
            self.add_primitive(name, return_type, arg_types, category, semantics, pyspark_str)

            for amount in [30, 60, 90]:
                for direction in ["plus", "minus"]:
                    name = f"D.as_{type.value}.{direction}_{amount}days"
                    return_type = type
                    arg_types = []
                    category = Category.DATE_NAMESPACE

                    pyspark_str = f"D.as_{type.value}.{direction}_{amount}days"

                    semantics = DateSemantics(
                        name=f"D.as_{type.value}.{direction}_{amount}days",
                        target_type=type,
                        direction=direction,
                        unit=DateUnit.DAY,
                        amount=amount,
                        jump=None
                    )
                    self.add_primitive(name, return_type, arg_types, category, semantics, pyspark_str)
                
        for unit in [DateUnit.MONTH, DateUnit.YEAR]:
            for jump in ["start", "end"]:
                for type in [DateType.TYPE_DATE, DateType.TYPE_STRING, DateType.TYPE_INT]:
                    name = f"D.as_{type.value}.{unit.value}_{jump}"
                    return_type = type
                    arg_types = []
                    category = Category.DATE_NAMESPACE

                    pyspark_str = f"D.as_{type.value}.{unit.value}_{jump}"

                    semantics = DateSemantics(
                        name=f"D.as_{type.value}.{unit.value}_{jump}",
                        target_type=type,
                        direction=None,
                        unit=None,
                        amount=None,
                        jump=f"{jump} {unit.value}"
                    )

                    self.add_primitive(name, return_type, arg_types, category, semantics, pyspark_str)

        for direction in ["plus", "minus"]:
            for unit in [DateUnit.DAY, DateUnit.WEEK, DateUnit.MONTH, DateUnit.YEAR]:
                for type in [DateType.TYPE_DATE, DateType.TYPE_STRING, DateType.TYPE_INT]:
                    name = f"D.as_{type.value}.{direction}_{unit.value}"
                    return_type = type
                    arg_types = [(DateType.TYPE_INT, False)]
                    category = Category.DATE_NAMESPACE

                    pyspark_str = f"D.as_{type.value}.{direction}_{unit.value}({{0}})"

                    semantics = DateSemantics(
                        name=f"D.as_{type.value}.{direction}_{unit.value}({{0}})",
                        target_type=type,
                        direction=direction,
                        unit=unit,
                        amount=None,
                        jump=None
                    )
                    self.add_primitive(name, return_type, arg_types, category, semantics, pyspark_str)
        
        for unit in [DateUnit.MONTH, DateUnit.YEAR]:
            for direction in ["plus", "minus"]:
                for jump in ["start", "end"]:
                    for type in [DateType.TYPE_DATE, DateType.TYPE_STRING, DateType.TYPE_INT]:
                        name = f"D.as_{type.value}.{direction}_{unit}_{jump}"
                        return_type = type
                        arg_types = [(DateType.TYPE_INT, False)] if unit == DateUnit.MONTH else []
                        category = Category.DATE_NAMESPACE
                        semantics = DateSemantics(
                            name=f"D.as_{type.value}.{direction}_{unit.value}_{jump}(_)",
                            target_type=type,
                            direction=direction,
                            unit=unit,
                            amount=None,
                            jump=f"{jump} {unit}"
                        )
                        if unit == DateUnit.MONTH:
                            pyspark_str = f"D.as_{type.value}.{direction}_{unit.value}_{jump}({{0}})"
                        else:
                            pyspark_str = f"D.as_{type.value}.{direction}_{unit.value}_{jump}"
                        self.add_primitive(name, return_type, arg_types, category, semantics, pyspark_str)
        for direction in ["plus", "minus"]:
            name = f"D.as_strYM.{direction}_month"
            return_type = DateType.TYPE_INT_YM
            arg_types = [(DateType.TYPE_INT, False)]
            category = Category.DATE_NAMESPACE

            pyspark_str = f"D.as_strYM.{direction}_month({{0}})"

            semantics = DateSemantics(
                name=f"D.as_strYM.{direction}_month(_)",
                target_type=DateType.TYPE_INT_YM,
                direction=direction,
                unit=DateUnit.MONTH,
                amount=None,
                jump=None
            )
            self.add_primitive(name, return_type, arg_types, category, semantics, pyspark_str)