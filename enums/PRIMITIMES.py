from typing import List, Any
from smt_types import DateType

from smt_types import DateType, DateUnit

PRIMITIVES_TYPES = [
    {
        "name": "as_date",
        "return_type": DateType.TYPE_DATE,
        "arg_types": [],
    }

]

PRIMITIVES = [
    # Primitive(Name, ReturnType, ArgTypes, GeneratorFunc)
    {
        "name": "D.as_date.offset",
        "return_type": DateType.TYPE_DATE,
        "arg_types": [DateType.TYPE_INT, DateType.TYPE_STRING, DateType.TYPE_STRING], 
        "format": lambda args: f"F.lit(D.as_date.{args[1]}_{args[2]}({args[0]}))"
    },
    {
        "name": "D.as_str.offset",
        "return_type": DateType.TYPE_STRING,
        "arg_types": [DateType.TYPE_INT, DateType.TYPE_STRING, DateType.TYPE_STRING], #days, week, year, month; minus/plus
        "format": lambda args: f"F.lit(D.as_str.{args[1]}_{args[2]}({args[0]}))"
    },
    {
        "name": "D.as_int.offset",
        "return_type": DateType.TYPE_INT, 
        "arg_types": [DateType.TYPE_INT, DateType.TYPE_STRING, DateType.TYPE_STRING], #days, week, year, month
        "format": lambda args: f"F.lit(D.as_int.{args[1]}_{args[2]}({args[0]}))"
    },
    {
        "name": "D.as_strYM.offset",
        "return_type": DateType.TYPE_INT, #YYYMM 
        "arg_types": [DateType.TYPE_INT, DateType.TYPE_STRING, DateType.TYPE_STRING], #days, week, year, month
        "format": lambda args: f"F.lit(D.as_strYM.{args[1]}_{args[2]}({args[0]}))"
    },
    {
        "name": "F.to_date",
        "return_type": DateType.TYPE_DATE,
        "arg_types": [DateType.TYPE_STRING],
        "format": lambda args: f"F.to_date({args[0]})"
    },
    {
        "name": "F.concat",
        "return_type": DateType.TYPE_STRING,
        "arg_types": [DateType.TYPE_STRING, DateType.TYPE_STRING],
        "format": lambda args: f"F.concat({args[0]}, {args[1]})"
    },
    {
        "name": "F.substring",
        "return_type": DateType.TYPE_STRING,
        "arg_types": [DateType.TYPE_STRING, DateType.TYPE_INT, DateType.TYPE_INT],
        "format": lambda args: f"F.substring({args[0]}, {args[1]}, {args[2]})"
    }
]