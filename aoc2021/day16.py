from typing import NamedTuple, Any, Union
from io import StringIO
import math
import operator


def le_int(binary: list[int]) -> int:
    """Convert a sequence of bits as little endian to an integer"""
    return int("".join(map(str, binary)), 2)


class Value(NamedTuple):
    """A packet containing an integer value"""
    version: int
    type_id: int
    payload: int
    length: int

    @classmethod
    def from_binary(cls, message: list[int]):
        """Parse a Value packet from a binary message"""
        version = le_int(message[:3])
        type_id = le_int(message[3:6])
        digits = []
        for index in range(6, len(message), 5):
            digits += message[index + 1 : index + 5]
            if message[index] == 0:
                break
        return cls(version, type_id, le_int(digits), index + 5)


class Operator(NamedTuple):
    """A packet encoding an operation and containing operators"""
    version: int
    type_id: int
    payloads: list[Any]
    length: int

    @classmethod
    def from_binary(cls, message: list[int]):
        """Parse an Operator packet from a binary message"""
        header = le_int(message[:3]), le_int(message[3:6])
        if message[6] == 0:
            n_bits = le_int(message[6 + 1 : 6 + 16])
            return cls._from_bits(message[6 + 16 : 6 + 16 + n_bits], header)
        else:
            n_payloads = le_int(message[6 + 1 : 6 + 12])
            return cls._from_payloads(message[6 + 12 :], n_payloads, header)

    @classmethod
    def _from_bits(cls, message: list[int], header: tuple[int, int]):
        length = 0
        payloads = []
        while length < len(message):
            payloads.append(parse_packet(message[length:]))
            length += payloads[-1].length
        return cls(*header, payloads, length + 22)

    @classmethod
    def _from_payloads(cls, message: list[int], count: int, header: tuple[int, int]):
        length = 0
        payloads = []
        for _ in range(count):
            payloads.append(parse_packet(message[length:]))
            length += payloads[-1].length
        return cls(*header, payloads, length + 18)


PACKET = Union[Value, Operator]


def parse_packet(message: list[int]) -> PACKET:
    """Parse a packet from a binary message"""
    if message[3:6] == [1, 0, 0]:
        return Value.from_binary(message)
    else:
        return Operator.from_binary(message)


def solve(in_stream: StringIO) -> tuple[object, object]:
    binary_message = to_binary(in_stream.readline().strip())
    root = parse_packet(binary_message)
    return sum_versions(root), evaluate(root)


def to_binary(hex_message: str) -> list[int]:
    """Convert a message from hex digits to binary digits"""
    return [int(bit) for hexdigit in hex_message for bit in f"{int(hexdigit, 16):04b}"]


def sum_versions(root: PACKET):
    """Sum up all version in the packet hierarchy"""
    if isinstance(root, Value):
        return root.version
    else:
        return root.version + sum(map(sum_versions, root.payloads))


# dispatch of operations from the type_id to a function implementing the operation
OPERATORS = {
    0: sum,
    1: math.prod,
    2: min,
    3: max,
    # the `operator.XY` functions take a pair of operators
    # use a lambda to unpack the iterable of operators to a pair of separate operators.
    5: lambda iterator: operator.gt(*iterator),
    6: lambda iterator: operator.lt(*iterator),
    7: lambda iterator: operator.eq(*iterator),
}


def evaluate(root: PACKET):
    """Evaluate the operations in the packet hierarchy"""
    if isinstance(root, Value):
        return root.payload
    else:
        return OPERATORS[root.type_id](map(evaluate, root.payloads))
