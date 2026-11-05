
import z3
from typing import List

from primitives.Primitive import Primitive
from enums.categories import Category
from enums.smt_types import PrimitiveType

class Date_Verifier:

    def __init__(self, op: Primitive, children: List[Verifier]):
        print(f'children {children}')

        self.solver = z3.Solver()

        # int date components
        y = z3.Int('year')
        m = z3.Int('month')
        d = z3.Int('day')

        self.year, self.month, self.day = y, m, d

        self.solver.add(y >= 2000, y <= 2100)
        self.solver.add(m >= 1, m <= 12)
        self.solver.add(d >= 1, d <= 31)

        self.solver.add(z3.Implies(z3.Or(m == 4, m == 6, m == 9, m == 11), d <= 30))
        self.solver.add(z3.Implies(m == 2, d <= 29))

        self.base_date_id = y * 365 + m * 30 + d

        self.constraints = []

        self.kb_dates = {}
        #self.build_kb_dates()

        self.add_variable(op, children)

    @classmethod
    def get_assertions(cls):
        return None

    def print_debug(self):
        print(self.solver)
        print(self.expr)

        for assertion in self.solver.assertions():
            print("Assertion:", assertion)

        if self.solver.check() == z3.sat:
            model = self.solver.model()
            print("Model values:", model)

    def add_variable(self, op: Primitive, children):
        print('z3')
        print(op)
        print(children)

        if op.category == Category.LITERAL:
            if op.return_type == PrimitiveType.TYPE_INT:
                self.expr = z3.IntVal(op.z3_rep)
            else:
                self.expr = z3.StringVal(op.z3_rep)

        elif op.category == Category.DATE_NAMESPACE:
            if len(op.arg_types) == 0:
                self.expr = self.get_date_expr(op.z3_rep)
            else:
                print(children)
                self.expr = self.get_date_expr(op.z3_rep, children[0].expr)

        #if op.category == Category.ARITHMETIC:


        self.print_debug()
            #self.constraints.append(z3.IntVal())

    def get_date_expr(self, name: str, param: str):
        pass
        

        

    def build_kb_dates(self):

        new_m = z3.If(self.month == 1, 12, self.month - 1)
        new_y = z3.If(self.month == 1, self.year - 1, self.year)

        self.expr_month_end = self.ordinal(
            new_y,
            new_m,
            self.days_in_month(new_y, new_m)
        )

        self.expr_minus_month_end_minus_5 = self.expr_month_end - 5

        for days in [30, 60, 90]:

            self.kb_dates.update({f'expr_minus_{days}days': self.ordinal(self.year, self.month, self.day) - days})

        #self.solver.add(self.kb_dates['expr_minus_30days'] != self.expr_minus_month_end_minus_5)

        # s = z3.String("s")
        # n = z3.StrToInt(s)
        # self.solver.add(s == "20261028")
        # self.solver.add(n == 20261028)

        #self.solver.add(s != n)

        result = self.solver.check()

        # if result == z3.sat:
        #     model = self.solver.model()
        #     print(f"Counterexample found -> Year: {model[self.year]}, Month: {model[self.month]}, Day: {model[self.day]}")
        # elif result == z3.unsat:
        #     print("PROVED")
        # else:
        #     print("Unknown")

    #def arithmetic(op: str, )
        

    def is_leap(self, y):
        return z3.Or(
            y % 400 == 0,
            z3.And(y % 4 == 0, y % 100 != 0)
        )

    def days_in_month(self, y, m):
        return z3.If(
            z3.Or(m == 4, m == 6, m == 9, m == 11),
            30,
            z3.If(
                m == 2,
                z3.If(self.is_leap(y), 29, 28),
                31
            )
        )

    def ordinal(self, y, m, d):
        prev_y = y - 1
        days_before_year = (
            365 * prev_y
            + prev_y / 4
            - prev_y / 100
            + prev_y / 400
        )

        days_before_month = z3.Sum([
            z3.If(m > i, self.days_in_month(y, i), 0)
            for i in range(1, 13)
        ])

        return days_before_year + days_before_month + d - 1

    def pad2(self, n):
        return z3.If(
            n < 10,
            z3.Concat(z3.StringVal("0"), z3.IntToStr(n)),
            z3.IntToStr(n),
        )

    def date_to_iso(self, y, m, d):
        return z3.Concat(
            z3.IntToStr(y),
            z3.StringVal("-"),
            self.pad2(m),
            z3.StringVal("-"),
            self.pad2(d),
        )

    def date_to_yyyymmdd(self, y, m, d):
        return z3.Concat(
            z3.IntToStr(y),
            self.pad2(m),
            self.pad2(d),
        )