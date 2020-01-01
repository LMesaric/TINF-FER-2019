import sys
from sympy import Poly, SympifyError, PolynomialError
from sympy.abc import x
import numpy as np
from typing import List, Tuple


class BadPolyError(Exception):
    pass


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
    g_mat = create_generator_matrix(n, k, g)
    h_mat = create_parity_check_matrix(n, k, g_mat)
    h = calculate_parity_check_poly(n, g)

    print(g_mat)
    print(h_mat)
    print(h)


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


def create_generator_matrix(n: int, k: int, g: List[int]):
    g = np.array(g, dtype=int)
    m = np.zeros((k, n), dtype=int)

    for i in range(0, k):
        m[i, i:i+n-k+1] = g

    for i in range(0, k-1):
        for j in range(i+1, k):
            if m[i, j]:
                np.bitwise_xor(m[i, :], m[j, :], out=m[i, :])

    return m


def create_parity_check_matrix(n: int, k: int, generator_matrix):
    parity = np.eye(n-k, n, k=k, dtype=int)
    parity[:, :k] = generator_matrix[:, k:].transpose()
    return parity


def calculate_parity_check_poly(n: int, g: List[int]):
    return Poly(divide_mod_2(create_x_n_1(n), g)[0], x).as_expr()


if __name__ == "__main__":
    main()
