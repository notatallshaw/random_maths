"""
Author: Damian (Twitter: @notatallshaw)
"""

import string
from collections import deque

# Global Variable
LEFT = object()
RIGHT = object()
_low_primes = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79,
               83, 89, 97, 101, 103, 107, 109, 113, 127, 131, 137, 139, 149, 151, 157, 163, 167,
               173, 179, 181, 191, 193, 197, 199, 211, 223, 227, 229, 233, 239, 241, 251, 257, 263,
               269, 271, 277, 281, 283, 293, 307, 311, 313, 317, 331, 337, 347, 349, 353, 359, 367,
               373, 379, 383, 389, 397, 401, 409, 419, 421, 431, 433, 439, 443, 449, 457, 461, 463,
               467, 479, 487, 491, 499, 503, 509, 521, 523, 541, 547, 557, 563, 569, 571, 577, 587,
               593, 599, 601, 607, 613, 617, 619, 631, 641, 643, 647, 653, 659, 661, 673, 677, 683,
               691, 701, 709, 719, 727, 733, 739, 743, 751, 757, 761, 769, 773, 787, 797, 809, 811,
               821, 823, 827, 829, 839, 853, 857, 859, 863, 877, 881, 883, 887, 907, 911, 919, 929,
               937, 941, 947, 953, 967, 971, 977, 983, 991, 997]
LOW_PRIMES = {p: None for p in _low_primes}  # A dict in CPython 3.6+ has fast lookup and is ordered
MAX_LOW_PRIMES = max(_low_primes)
# https://arxiv.org/abs/1509.00864
MILLER_RABIN_OPTIMIZATION = (3_317_044_064_679_887_385_961_981,
                             (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41))

# Choices:
SIDE = LEFT
BASE = 10
PRINT_EACH_LEAF = True


class _ArbitraryBase(int):
    "Class Factory for creating int-like objects with arbitrary base"
    ALL_DIGITS = string.digits + string.ascii_letters

    def __new__(cls, base: int, digits: tuple):
        cls.base = base
        cls.digits = digits
        cls.number = cls.calculate_number(base, digits)
        return int.__new__(cls, cls.number)

    def __call__(self, *args, **kwargs):
        # Bring Class variables down to instance variable (hacky!)
        self.base = self.base
        self.digits = self.digits
        self.number = self.number
        return self

    @staticmethod
    def calculate_number(base:int, digits: tuple):
        number = 0
        for position, digit in enumerate(reversed(digits)):
            if digit >= base:
                raise ValueError(f"Digit {digit} in position {position} is greater or equal to base {base}")
            number += digit * base**position

        return number

    def append_digit(self, digit):
        return _ArbitraryBase.__new__(_ArbitraryBase, self.base, (*self.digits, digit))()

    def prepend_digit(self, digit):
        return _ArbitraryBase.__new__(_ArbitraryBase, self.base, (digit, *self.digits))()

    def __repr__(self):
        return f'arbitrary_base({self.base}, {self.digits})'

    def __str__(self):
        if self.base > 62:
            return self.__repr__()

        if self.base == 10:
            return str(self.number)

        if self.number == 0:
            return '0'

        base_digits = deque()
        number = self.number

        if number < 0:
            base_digits.append('-')
            number *= -1

        while number:
            next_digit = self.ALL_DIGITS[int(number % self.base)]
            base_digits.appendleft(next_digit)
            number = int(number / self.base)

        return ''.join(base_digits)


def arbitrary_base(base, digits):
    "Helper function for creating int-like arbitrary base object"
    if type(digits) is int:
        digits = (digits, )
    else:
        digits = tuple(digits)

    class_int = _ArbitraryBase.__new__(_ArbitraryBase, base, digits)
    return class_int()


def rabin_miller(num: int):
    s = num - 1
    t = 0
    while s % 2 == 0:
        s = s // 2
        t += 1

    if num < MILLER_RABIN_OPTIMIZATION[0]:
        test_a = MILLER_RABIN_OPTIMIZATION[1]
    else:
        max_a = 3 * ((num.bit_length() + 1) ** 2)
        test_a = range(2, max_a + 1)

    for a in test_a:
        v = pow(a, s, num)
        if v == 1:
            continue

        i = 0
        while v != (num - 1):
            if i == t - 1:
                return False
            else:
                i += 1
                v = pow(v, 2, num)
    return True


def is_prime(num):
    if num in LOW_PRIMES:
        return True
    elif num < MAX_LOW_PRIMES:
        return False

    for prime in LOW_PRIMES:
        if num % prime == 0:
            return False

    return rabin_miller(num)


def find_deletable_primes(tree, side, base):
    leaf_collection = []
    for parent in tree:
        for new_digit in range(1, base):
            if side is RIGHT:
                new_number = parent.append_digit(new_digit)
            else:
                new_number = parent.prepend_digit(new_digit)

            if is_prime(new_number):
                tree[parent][new_number] = {}

        if tree[parent]:
            leaves = find_deletable_primes(tree[parent], side, base)
            leaf_collection.extend(leaves)
        else:
            leaf_collection.append(parent)
            if PRINT_EACH_LEAF:
                print(f'Leaf: {parent}')

    return leaf_collection


def main():
    # Set-up initial tree
    tree = {}
    for x in range(BASE):
        number = arbitrary_base(BASE, x)
        if is_prime(number):
            tree[number] = {}

    # Recursive function to find all leaf nodes of LEFT or RIGHT deletable primes
    leaves = find_deletable_primes(tree, SIDE, BASE)
    print(f'Largest leaf: {max(leaves)}')


if __name__ == '__main__':
    main()
