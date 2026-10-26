from datetime import date
from datetime import datetime

from .base_registry import BasePrimitiveRegistry
from enums.smt_types import DateType, DateUnit
from enums.categories import Category
from .Semantics import DateSemantics

from primitives.dataparams.dataparams import DatesNamespace

class DatePrimitiveRegistry(BasePrimitiveRegistry):
    """Handles type conversion functions between Date, String, and Int."""
    
    def register_all(self, eval_date: int) -> None:

        today = date.today()
        today_int = today.year * 10000 + today.month * 100 + today.day
        
        self.D = DatesNamespace(eval_date)
        self.init_dateprimitives()

    def init_dateprimitives(self) -> None:
        name = f"D.as_intYM.current_month"
        return_type = DateType.TYPE_INT_YM
        arg_types = []
        category = Category.DATE_NAMESPACE

        pyspark_str = f"D.as_intYM.current_month"

        python_eval = lambda args, _: self.D.as_intYM.current_month

        semantics = DateSemantics(
            name=f"D.as_intYM.current_month",
            target_type=DateType.TYPE_INT_YM,
            direction=None,
            unit=None,
            amount=None,
            jump=None
        )
        self.add_primitive(name, return_type, arg_types, category, semantics, pyspark_str, python_eval)

        for type in [DateType.TYPE_YEAR, DateType.TYPE_MONTH, DateType.TYPE_DAY]:
            name = f"D.as_date.BD.{type.value}"
            return_type = type
            arg_types = []
            category = Category.DATE_NAMESPACE
    
            pyspark_str = f"D.as_date.BD.{type.value}"
            if type.eq_exact(DateType.TYPE_YEAR):
                python_eval = lambda args, _: self.D.as_date.BD.year
            elif type.eq_exact(DateType.TYPE_MONTH):
                python_eval = lambda args, _: self.D.as_date.BD.month
            else:  # TYPE_DAY
                python_eval = lambda args, _: self.D.as_date.BD.day
    
            semantics = DateSemantics(
                name=f"D.as_date.BD.{type.value}",
                target_type=type,
                direction=None,
                unit=None,
                amount=None,
                jump=None
            )
            self.add_primitive(name, return_type, arg_types, category, semantics, pyspark_str, python_eval)


        for type in [DateType.TYPE_YEAR, DateType.TYPE_MONTH, DateType.TYPE_DAY]:
            for direction in ["plus", "minus"]:

                plus_minus = "+" if direction == "plus" else "-"
        
                name = f"D.as_date.BD.{type.value} {plus_minus}"
                return_type = type
                arg_types = [(DateType.TYPE_INT, False)]
                category = Category.DATE_NAMESPACE
        
                pyspark_str = f"(D.as_date.BD.{type.value} {plus_minus} {{0}})"
                python_eval = lambda args, _, t=type.value, d=direction: (
                    getattr(self.D.as_date.BD, t) + args[0] if d == "plus" else getattr(self.D.as_date.BD, t) - args[0]
                )
        
                semantics = DateSemantics(
                    name=f"D.as_date.BD.{type.value} {plus_minus} {{0}}",
                    target_type=type,
                    direction=direction,
                    unit=None,
                    amount=None,
                    jump=None
                )
                self.add_primitive(name, return_type, arg_types, category, semantics, pyspark_str, python_eval)



        for type in [DateType.TYPE_DATE, DateType.TYPE_STRING, DateType.TYPE_INT]:
            name = f"D.as_{type.value}.BD"
            return_type = type
            arg_types = []
            category = Category.DATE_NAMESPACE

            pyspark_str = f"D.as_{type.value}.BD"
            python_eval = lambda args, _, dt=type: getattr(getattr(self.D, f"as_{dt.value}"), "BD")

            semantics = DateSemantics(
                name=f"D.as_{type.value}.BD",
                target_type=type,
                direction=None,
                unit=None,
                amount=None,
                jump=None
            )
            self.add_primitive(name, return_type, arg_types, category, semantics, pyspark_str, python_eval)

            for amount in [30, 60, 90]:
                for direction in [ "minus"]: #"plus",
                    name = f"D.as_{type.value}.{direction}_{amount}days"
                    return_type = type
                    arg_types = []
                    category = Category.DATE_NAMESPACE

                    pyspark_str = f"D.as_{type.value}.{direction}_{amount}days"
                    python_eval = lambda args, _, dt=type, d=direction, a=amount: getattr(getattr(self.D, f"as_{dt.value}"), f"{d}_{a}days")

                    semantics = DateSemantics(
                        name=f"D.as_{type.value}.{direction}_{amount}days",
                        target_type=type,
                        direction=direction,
                        unit=DateUnit.DAY,
                        amount=amount,
                        jump=None
                    )
                    self.add_primitive(name, return_type, arg_types, category, semantics, pyspark_str, python_eval)
                
        for unit in [DateUnit.MONTH, DateUnit.YEAR]:
            for jump in ["start", "end"]:
                for type in [DateType.TYPE_DATE, DateType.TYPE_STRING, DateType.TYPE_INT]:
                    name = f"D.as_{type.value}.{unit.value}_{jump}"
                    return_type = type
                    arg_types = []
                    category = Category.DATE_NAMESPACE

                    pyspark_str = f"D.as_{type.value}.{unit.value}_{jump}"
                    python_eval = lambda args, _, dt=type, u=unit.value, j=jump: getattr(getattr(self.D, f"as_{dt.value}"), f"{u}_{j}")

                    semantics = DateSemantics(
                        name=f"D.as_{type.value}.{unit.value}_{jump}",
                        target_type=type,
                        direction=None,
                        unit=None,
                        amount=None,
                        jump=f"{jump} {unit.value}"
                    )

                    self.add_primitive(name, return_type, arg_types, category, semantics, pyspark_str, python_eval)

        for direction in ["plus", "minus"]:
            for unit in [DateUnit.DAY, DateUnit.WEEK, DateUnit.MONTH, DateUnit.YEAR]:
                for type in [DateType.TYPE_DATE, DateType.TYPE_STRING, DateType.TYPE_INT]:
                    name = f"D.as_{type.value}.{direction}_{unit.value}"
                    return_type = type
                    arg_types = [(DateType.TYPE_INT, False)]
                    category = Category.DATE_NAMESPACE

                    if unit == DateUnit.YEAR:
                        pyspark_str = f"D.as_{type.value}.{direction}_{unit.value}"
                        python_eval = lambda args, _, dt=type, d=direction, u=unit.value: getattr(getattr(self.D, f"as_{dt.value}"), f"{d}_{u}")
                    else:
                        pyspark_str = f"D.as_{type.value}.{direction}_{unit.value}({{0}})"
                        python_eval = lambda args, _, dt=type, d=direction, u=unit.value: getattr(getattr(self.D, f"as_{dt.value}"), f"{d}_{u}")(args[0])

                    semantics = DateSemantics(
                        name=f"D.as_{type.value}.{direction}_{unit.value}({{0}})",
                        target_type=type,
                        direction=direction,
                        unit=unit,
                        amount=None,
                        jump=None
                    )
                    self.add_primitive(name, return_type, arg_types, category, semantics, pyspark_str, python_eval)
        
        for unit in [DateUnit.MONTH, DateUnit.YEAR]:
            for direction in ["minus"]: #"plus", 
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
                        def create_eval(dt, d, u, j):
                            def eval_fn(args, _):
                                attr = getattr(self.D, f"as_{dt.value}")
                                val = getattr(attr, f"{d}_{u}_{j}")
                                return val() if callable(val) else val
                            return eval_fn

                        if unit == DateUnit.MONTH:
                            pyspark_str = f"D.as_{type.value}.{direction}_{unit.value}_{jump}({{0}})"
                            python_eval = lambda args, _, dt=type, d=direction, u=unit.value, j=jump: getattr(getattr(self.D, f"as_{dt.value}"), f"{d}_{u}_{j}")(args[0])
                        else:
                            pyspark_str = f"D.as_{type.value}.{direction}_{unit.value}_{jump}"
                            python_eval = create_eval(type, direction, unit.value, jump)
                        self.add_primitive(name, return_type, arg_types, category, semantics, pyspark_str, python_eval)
        for direction in ["plus", "minus"]:
            name = f"D.as_intYM.{direction}_month"
            return_type = DateType.TYPE_INT_YM
            arg_types = [(DateType.TYPE_INT, False)]
            category = Category.DATE_NAMESPACE

            pyspark_str = f"D.as_intYM.{direction}_month({{0}})"
            python_eval = lambda args, _, d=direction: getattr(self.D.as_intYM, f"{d}_month")(args[0])

            semantics = DateSemantics(
                name=f"D.as_intYM.{direction}_month(_)",
                target_type=DateType.TYPE_INT_YM,
                direction=direction,
                unit=DateUnit.MONTH,
                amount=None,
                jump=None
            )
            self.add_primitive(name, return_type, arg_types, category, semantics, pyspark_str, python_eval)