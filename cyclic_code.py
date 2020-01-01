import sys
from sympy import Poly, SympifyError, PolynomialError
from sympy.abc import x
import numpy as np
from typing import List, Tuple


class BadPolyError(Exception):
    pass


class CyclicUtil:

    def __init__(self, n, k, g):
        self.n = n
        self.k = k
        self.g = g
        self.h = self.calculate_parity_check_poly()
        self.g_mat = self.create_generator_matrix()
        self.h_mat = self.create_parity_check_matrix()

    def create_generator_matrix(self):
        g_ = np.array(self.g, dtype=int)
        m = np.zeros((self.k, self.n), dtype=int)

        for i in range(0, self.k):
            m[i, i:i + self.n - self.k + 1] = g_

        for i in range(0, self.k - 1):
            for j in range(i+1, self.k):
                if m[i, j]:
                    np.bitwise_xor(m[i, :], m[j, :], out=m[i, :])

        return m

    def create_parity_check_matrix(self):
        parity = np.eye(self.n - self.k, self.n, k=self.k, dtype=int)
        parity[:, :self.k] = self.g_mat[:, self.k:].transpose()
        return parity

    def calculate_parity_check_poly(self) -> str:
        return str(Poly(divide_mod_2(create_x_n_1(self.n), self.g)[0], x).as_expr())

    def encode(self, d: List[int]) -> str:
        return "".join([str(i) for i in np.array(d, dtype=int).dot(self.g_mat) % 2])


def main():
    try:
        main_unsafe()
    except (KeyboardInterrupt, EOFError):
        print("\nExiting the program.")
        sys.exit(0)


def main_unsafe():
    # 0 < k < n
    n = load_number_from_inclusive_range("n", 1, 0)
    k = load_number_from_inclusive_range("k", 1, n - 1)
    g = load_poly_coeffs(n, k)

    cyclic = CyclicUtil(n, k, g)

    print("\nG: ")
    print(cyclic.g_mat)
    print("\nH: ")
    print(cyclic.h_mat)
    print(f"\nh(x) = {cyclic.h}\n")

    d = load_message(k)
    c = cyclic.encode(d)
    print(f"c = {c}")


def load_number_from_inclusive_range(name: str, lower: int, upper: int) -> int:
    while True:
        print(f"{name} = ", end="")

        try:
            i = int(input())
        except ValueError:
            print("Please enter a number")
            continue

        if i < lower:
            print(f"'{name}' must be greater than {lower - 1}")
        elif upper > lower and i > upper:
            print(f"'{name}' must be less than {upper + 1}")
        else:
            return i


def load_poly_coeffs(n: int, k: int) -> List[int]:
    degree = n - k

    while True:
        print("g(x) = ", end="")

        try:
            p = Poly(input(), x)

            if str(p.get_domain()) != "ZZ" or len(p.degree_list()) != 1:
                raise BadPolyError("Too many variables")

            coeffs = [int(i) for i in p.all_coeffs()]
            if len(coeffs) != (degree + 1):
                raise BadPolyError(
                    f"Degree of polynomial must be exactly {degree}")

            for c in coeffs:
                if (c != 0 and c != 1):
                    raise BadPolyError("All coefficients must be 0 or 1")

            if coeffs[-1] != 1:
                raise BadPolyError("Trailing term must be 1")

            if divide_mod_2(create_x_n_1(n), coeffs)[1]:
                raise BadPolyError("Polynomial must be a divisor of x^n - 1")

            return coeffs

        except BadPolyError as e:
            print(e)
        except (ValueError, SyntaxError, SympifyError, PolynomialError):
            print("Invalid polynomial format")


def load_message(length: int) -> List[int]:
    while True:
        print("d = ", end="")

        try:
            s = input()
            d = []
            for i_ in s:
                i = int(i_)
                if (i == 0 or i == 1):
                    d.append(i)
                else:
                    raise ValueError

            if len(d) < length:
                print(f"Message length must be at least {length}")
            else:
                return d[:length]

        except ValueError:
            print("Only characters '0' and '1' are allowed")


def create_x_n_1(n: int) -> List[int]:
    x_n_1 = [0] * (n + 1)
    x_n_1[0] = 1
    x_n_1[-1] = 1
    return x_n_1


def divide_mod_2(a: List[int], b: List[int]) -> Tuple[List[int], List[int]]:
    res = []

    while len(b) <= len(a) and a:
        if a[0] == 1:
            del a[0]
            for j in range(len(b) - 1):
                a[j] ^= b[j + 1]
            if len(a) > 0:
                res.append(1)
        else:
            del a[0]
            res.append(0)

    while a and a[0] == 0:
        del a[0]

    return (res, a)


if __name__ == "__main__":
    main()
