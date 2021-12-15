from importlib import import_module
from io import StringIO


def plugin(year, day, data):
    mod = import_module(f".day{day}", __package__)
    in_stream = StringIO(data)
    return mod.solve(in_stream)
