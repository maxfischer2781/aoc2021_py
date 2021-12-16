from typing import NamedTuple, Any, Union
from io import StringIO
import math


def le_int(binary: list[int]) -> int:
    return int(''.join(map(str, binary)), 2)


def multiple(num: int, of: int) -> int:
    for pad in range(0, of):
        if (num + pad) % of == 0:
            return num + pad


class Packet(NamedTuple):
    version: int
    type_id: int
    payload: "Union[Value, Operator]"

    @property
    def length(self):
        return self.payload.length + 6

    @classmethod
    def from_binary(cls, message: list[int]):
        version = le_int(message[:3])
        type_id = le_int(message[3:6])
        if type_id == 4:
            return cls(version, type_id, Value.from_binary(message[6:]))
        else:
            return cls(version, type_id, Operator.from_binary(message[6:]))


class Value(NamedTuple):
    payload: int
    length: int

    @classmethod
    def from_binary(cls, message: list[int]):
        digits = []
        for count, index in enumerate(range(0, len(message), 5), start=1):
            digits += message[index+1:index+5]
            if message[index] == 0:
                break
        return cls(le_int(digits), 5 * count)


class Operator(NamedTuple):
    payloads: list[Any]
    length: int

    @classmethod
    def from_binary(cls, message: list[int]):
        if message[0] == 0:
            n_bits = le_int(message[1:16])
            return cls.from_bitrange(message[16:16+n_bits])
        else:
            n_payloads = le_int(message[1:12])
            return cls.from_payload_range(message[12:], n_payloads)

    @classmethod
    def from_bitrange(cls, bits: list[int]):
        length = 0
        payloads = []
        while length < len(bits):
            payloads.append(Packet.from_binary(bits[length:]))
            length += payloads[-1].length
        return cls(payloads, length + 16)

    @classmethod
    def from_payload_range(cls, bits: list[int], count: int):
        length = 0
        payloads = []
        for _ in range(count):
            payloads.append(Packet.from_binary(bits[length:]))
            length += payloads[-1].length
        return cls(payloads, length + 12)


def solve(in_stream: StringIO) -> tuple[object, object]:
    binary_message = to_binary(in_stream.readline().strip())
    root = Packet.from_binary(binary_message)
    return sum_versions(root), evaluate(root)


def to_binary(message: str) -> list[int]:
    return [int(bit) for hexdigit in message for bit in f"{int(hexdigit, 16):04b}"]


def sum_versions(root: Packet):
    if isinstance(root.payload, Value):
        return root.version
    else:
        return root.version + sum(map(sum_versions, root.payload.payloads))


OPERATORS = {
    0: sum,
    1: math.prod,
    2: min,
    3: max,
    5: lambda lr: next(lr) > next(lr),
    6: lambda lr: next(lr) < next(lr),
    7: lambda lr: next(lr) == next(lr),
}


def evaluate(root: Packet):
    if isinstance(root.payload, Value):
        return root.payload.payload
    else:
        operation = OPERATORS[root.type_id]
        return operation(map(evaluate, root.payload.payloads))
