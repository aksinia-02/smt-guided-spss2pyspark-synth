
import z3
from typing import List

from EGraph.ENode import ENode

from primitives.Primitive import Primitive
from enums.categories import Category
from enums.smt_types import PrimitiveType

class Verifier:

    date_solver = z3.Solver()
    year = z3.Int('year')
    month = z3.Int('month')
    day = z3.Int('day')

    base_date_id = year * 365 + month * 30 + day

    date_solver.add(year >= 1998, year <= 2015)
    date_solver.add(month >= 1, month <= 12)
    date_solver.add(day >= 1, day <= 31)

    date_solver.add(z3.Implies(z3.Or(month == 4, month == 6, month == 9, month == 11), day <= 30))
    date_solver.add(z3.Implies(month == 2, day <= 29))

    kb_dates = {}

    def __init__(self, op: Primitive, children_ver: List[Verifier], children_nodes: List[ENode]):

        self.solver = z3.Solver()

        self.expr = None
        self.constants = {}
        self.assertions = {}

        self.add_variable(op, children_ver, children_nodes)

    def print_debug(self):
        print(f'Expression: {self.expr}')

        for assertion in self.solver.assertions():
            print("Assertion:", assertion)

        for assertion in Verifier.date_solver.assertions():
            print("Date Assertion:", assertion)

        if self.solver.check() == z3.sat:
            model = self.solver.model()
            print("Model values:", model)

        if Verifier.date_solver.check() == z3.sat:
            date_model = Verifier.date_solver.model()
            print("Date Model values:", date_model)

    def add_variable(self, op: Primitive, children_ver, children_nodes):
        print('--------------------')
        print('z3')
        print(f'Operation: {op}')
        print(f'Children: {children_ver}')
        print(f'Child Nodes: {children_nodes}')

        if op.category == Category.LITERAL:
            if op.return_type == PrimitiveType.TYPE_INT:
                self.expr = z3.IntVal(op.z3_rep)
            else:
                self.expr = z3.StringVal(op.z3_rep)

        elif op.category == Category.DATE_NAMESPACE:

            found = Verifier.kb_dates.get(op.z3_rep)

            if callable(found):
                if op.z3_rep == 'bd':
                    self.expr = found(Verifier.year * 10000 + Verifier.month * 100 + Verifier.day, op.return_type.value)
                else:
                    if op.z3_rep == 'dif_30_90':
                        self.expr = found(op, op.semantics.amount)
                    else:
                        self.expr = found(op, children_ver[0].expr)

            else:
                self.expr = found
            self.constants[op.name] = self.expr

        elif op.category == Category.CAST_TYPE:

            child = children_nodes[0].op
            child_ver = children_ver[0]

            z3_rep = op.z3_rep

            print(f'child Expr: {child_ver.expr}, {child.z3_rep}')

            if child.category == Category.DATE_NAMESPACE:
                if z3_rep in ('year', 'month', 'day'):
                    if z3_rep == 'year':
                        self.expr = child_ver.expr / 10000
                    elif z3_rep == 'month':
                        self.expr = (child_ver.expr / 100) % 100
                    elif z3_rep == 'day':
                        self.expr = child_ver.expr % 100
                else:
                    found = Verifier.kb_dates.get(child.z3_rep)
                    print(f'Found for casting: {found}')

                    if callable(found):
                        old_type = child.return_type
                        child.return_type = op.return_type

                        if child.z3_rep == 'bd':
                            self.expr = found(Verifier.year * 10000 + Verifier.month * 100 + Verifier.day, child.return_type.value)
                        else:
                            if child.z3_rep == 'dif_30_90':
                                self.expr = found(child, child.semantics.amount)
                            else:
                                self.expr = found(child, children_ver[0].expr)
                        child.return_type = old_type

            else:
                if child.return_type == op.return_type:
                    self.expr = child_ver.expr
                elif z3_rep == 'to_string':
                    self.expr = z3.IntToStr(children_ver[0].expr)
                elif z3_rep == 'to_int':
                    self.expr = z3.StrToInt(children_ver[0].expr)
                else:
                    print(f"Unhandled cast operation: {op.name} with z3_rep: {z3_rep}")

        elif op.category == Category.ARITHMETIC:
            left_expr = children_ver[0].expr
            right_expr = children_ver[1].expr

            if op.name == '+':
                self.expr = left_expr + right_expr
            elif op.name == '-':
                self.expr = left_expr - right_expr


        self.print_debug()
        print('--------------------')
            #self.constraints.append(z3.IntVal())

    def merge(self, other_ver):

        print("Merging Verifiers:")

        merged_ver = Verifier.__new__(Verifier)
        merged_ver.solver = z3.Solver()
        merged_ver.expr = other_ver.expr
        # merged_ver.constants = {**self.constants, **other_ver.constants}
        # merged_ver.assertions = {**self.assertions, **other_ver.assertions}

        for assertion in self.date_solver.assertions():
            merged_ver.solver.add(assertion)

        for assertion in other_ver.solver.assertions():
            merged_ver.solver.add(assertion)

        for assertion in self.solver.assertions():
            merged_ver.solver.add(assertion)

        merged_ver.solver.add(self.expr != other_ver.expr)
        
        result = merged_ver.solver.check()

        if result == z3.sat:
            model = merged_ver.solver.model()
            print(f"Counterexample found -> Year: {model[merged_ver.year]}, Month: {model[merged_ver.month]}, Day: {model[merged_ver.day]}")
            return False
        elif result == z3.unsat:
            print("PROVED")
            for assertion in other_ver.solver.assertions():
                self.solver.add(assertion)
            self.solver.add(self.expr != other_ver.expr)
            return True
        else:
            print("Unknown")

        return False

    def get_date_expr(self, name: str, param: str):
        print(name)

    @classmethod
    def date_to_yyyy_mm_dd(cls, p: int):
        y = p / 10000
        m = (p / 100) % 100
        d = p % 100
        return cls.date_to_iso(y, m, d)

    @classmethod
    def date_to_yyyymmdd_str(cls, p):
        """Returns Z3 String in 'yyyyMMdd' format (String type)"""
        y = p / 10000
        m = (p / 100) % 100
        d = p % 100
        return cls.date_to_yyyymmdd(y, m, d)

    @classmethod
    def cast_to_type(cls, yyyymmdd_int: int, d_type: str):

        if d_type == 'int':
            return yyyymmdd_int
        elif d_type == 'str':
            return cls.date_to_yyyymmdd_str(yyyymmdd_int)
        elif d_type == 'date':
            return cls.date_to_yyyy_mm_dd(yyyymmdd_int)
        
    @classmethod
    def build_kb_dates(cls):

        cls.kb_dates = {
            "current_month": cls.year * 100 + cls.month,
            "bd_year": cls.year,
            "bd_month": cls.month,
            "bd_day": cls.day,

            "plus_minus_unit": lambda op, p: cls.plus_minus_unit(op, p),
            "bd": lambda value, d_type: cls.cast_to_type(value, d_type),
            "dif_30_90": lambda op, p: cls.dif_30_90(op, p),
            "unit_end_start": lambda op, p: cls.unit_end_start(op, p),
            "unit_plus_minus": lambda op, p: cls.unit_plus_minus(op, p),
            "unit_plus_minus_end_start": lambda op, p: cls.unit_plus_minus_end_start(op, p)
        }

        cls.casts = {
            "int_to_date": lambda p: cls.cast_to_type(p, 'date'),
            "int_to_str": lambda p: cls.cast_to_type(p, 'str'),
            "str_to_int": lambda p: cls.cast_to_type(int(p), 'int')
        }

        # self.expr_minus_month_end_minus_5 = self.expr_month_end - 5

        # for days in [30, 60, 90]:

        #     self.kb_dates.update({f'expr_minus_{days}days': self.ordinal(self.year, self.month, self.day) - days})

        #self.solver.add(self.kb_dates['expr_minus_30days'] != self.expr_minus_month_end_minus_5)

        # s = z3.String("s")
        # n = z3.StrToInt(s)
        # self.solver.add(s == "20261028")
        # self.solver.add(n == 20261028)

        #self.solver.add(s != n)

        # result = self.solver.check()

        # if result == z3.sat:
        #     model = self.solver.model()
        #     print(f"Counterexample found -> Year: {model[self.year]}, Month: {model[self.month]}, Day: {model[self.day]}")
        # elif result == z3.unsat:
        #     print("PROVED")
        # else:
        #     print("Unknown")

    #def arithmetic(op: str, )

    @classmethod
    def plus_minus_unit(cls, op: Primitive, p: int):

        cls_units = {
            'year': cls.year,
            'month': cls.month,
            'day': cls.day
        }

        if op.semantics.direction == 'plus':
            return cls_units.get(op.return_type.value) + p
        if op.semantics.direction == 'minus':
            return cls_units.get(op.return_type.value) - p

    @classmethod
    def dif_30_90(cls, op:Primitive, p: int):
        target_y, target_m, target_d = cls.calculate_plus_minus(op.semantics.direction, 'days', op.semantics.amount)
        result = target_y * 10000 + target_m * 100 + target_d
        return cls.cast_to_type(result, op.return_type.value)

    @classmethod
    def unit_end_start(cls, op:Primitive, p: int):

        if op.semantics.unit == "month":
            if op.semantics.jump == "end":
                new_m = z3.If(cls.month == 1, 12, cls.month - 1)
                new_y = z3.If(cls.month == 1, cls.year - 1, cls.year)

                result = cls.ordinal(
                    new_y,
                    new_m,
                    cls.days_in_month(new_y, new_m)
                )
            else:
                result = cls.ordinal(cls.year, cls.month, 1)
        else:
            if op.semantics.jump == "end":
                result = cls.ordinal(cls.year, 12, cls.days_in_month(cls.year, 12))
            else:
                result = cls.ordinal(cls.year, 1, 1)
        return cls.cast_to_type(result, op.return_type.value)

    @classmethod
    def unit_plus_minus(cls, op:Primitive, p: int):
        target_y, target_m, target_d = cls.calculate_plus_minus(op.semantics.direction, op.semantics.unit, p)
        result = target_y * 10000 + target_m * 100 + target_d
        return cls.cast_to_type(result, op.return_type.value)

    @classmethod
    def unit_plus_minus_end_start(cls, op:Primitive, p:int):
        result = cls.date_plus_minus_start_end(op.semantics.direction, op.semantics.unit, op.semantics.jump, p)
        return cls.cast_to_type(result, op.return_type.value)

    @classmethod
    def calculate_plus_minus(cls, direction: str, unit: str, p: int):
        target_y = cls.year
        target_m = cls.month
        target_d = cls.day

        if unit == 'year':
            if direction == 'plus':
                target_y = cls.year + p
            else:
                target_y = cls.year - p
            target_d = z3.If(
                z3.And(cls.month == 2, cls.day == 29, z3.Not(cls.is_leap(target_y))),
                28,
                cls.day
            )
        elif unit == 'month':
            if direction == 'plus':
                total_months = cls.month + p
            else:
                total_months = cls.month - p

            target_y = cls.year + (total_months - 1) // 12
            target_m = ((total_months - 1) % 12) + 1
            
            max_days = cls.days_in_month(target_y, target_m)
            target_d = z3.If(cls.day > max_days, max_days, cls.day)

        if unit in ('day', 'week'):
            days_to_add = p if unit == 'day' else p * 7
            current_ord = cls.ordinal(cls.year, cls.month, cls.day)

            if direction == 'plus':
                new_ord = current_ord + days_to_add
            else:
                new_ord = current_ord - days_to_add

            target_y = z3.Int(f'res_y_{unit}_{p}')
            target_m = z3.Int(f'res_m_{unit}_{p}')
            target_d = z3.Int(f'res_d_{unit}_{p}')

            cls.date_solver.add(target_y >= 1998, target_y <= 2015)
            cls.date_solver.add(target_m >= 1, target_m <= 12)
            cls.date_solver.add(target_d >= 1, target_d <= 31)
            cls.date_solver.add(z3.Implies(z3.Or(target_m == 4, target_m == 6, target_m == 9, target_m == 11), target_d <= 30))
            cls.date_solver.add(z3.Implies(target_m == 2, target_d <= 29))

            cls.date_solver.add(cls.ordinal(target_y, target_m, target_d) == new_ord)

        return target_y, target_m, target_d


    @classmethod
    def date_plus_minus_start_end(cls, direction: str, unit: str, jump: str, p: int):
        target_y, target_m, target_d = cls.calculate_plus_minus(direction, unit, p)

        new_m = z3.If(target_m == 1, 12, target_m - 1)
        new_y = z3.If(target_m == 1, target_y - 1, target_y)

        if unit == 'month':
            if jump == 'end':
                result = cls.ordinal(
                    new_y,
                    new_m,
                    cls.days_in_month(new_y, new_m)
                )
            else:
                result = cls.ordinal(cls.year, cls.month, 1)
        else:
            if jump == 'end':
                result = cls.ordinal(cls.year, 12, cls.days_in_month(cls.year, 12))
            else:
                result = cls.ordinal(cls.year, 1, 1)

        return result
        

    @classmethod
    def is_leap(cls, y):
        return z3.Or(
            y % 400 == 0,
            z3.And(y % 4 == 0, y % 100 != 0)
        )

    @classmethod
    def days_in_month(cls, y, m):
        return z3.If(
            z3.Or(m == 4, m == 6, m == 9, m == 11),
            30,
            z3.If(
                m == 2,
                z3.If(cls.is_leap(y), 29, 28),
                31
            )
        )

    @classmethod
    def ordinal(cls, y, m, d):
        prev_y = y - 1
        days_before_year = (
            365 * prev_y
            + prev_y / 4
            - prev_y / 100
            + prev_y / 400
        )

        days_before_month = z3.Sum([
            z3.If(m > i, cls.days_in_month(y, i), 0)
            for i in range(1, 13)
        ])

        return days_before_year + days_before_month + d - 1

    @classmethod
    def pad2(cls, n):
        return z3.If(
            n < 10,
            z3.Concat(z3.StringVal("0"), z3.IntToStr(n)),
            z3.IntToStr(n),
        )

    @classmethod
    def date_to_iso(cls, y, m, d):
        return z3.Concat(
            z3.IntToStr(y),
            z3.StringVal("-"),
            cls.pad2(m),
            z3.StringVal("-"),
            cls.pad2(d),
        )

    @classmethod
    def date_to_yyyymmdd(cls, y, m, d):
        return z3.Concat(
            z3.IntToStr(y),
            cls.pad2(m),
            cls.pad2(d),
        )

Verifier.build_kb_dates()