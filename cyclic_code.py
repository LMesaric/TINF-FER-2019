import sys
from sympy import Poly, SympifyError, PolynomialError
from sympy.abc import x
import numpy as np
from typing import List, Tuple


class CyclicUtil:
    """Utility class for calculating `G`, `H` and `h(x)` from `n`, `k` and `g(x)`.

    Enables encoding messages."""

    def __init__(self, n: int, k: int, g: List[int]) -> None:
        """Creates a new instance of `CyclicUtil`.

        Eagerly evaluates `G`, `H` and `h(x)`.

        Args:
            n (int): n
            k (int): k
            g (List[int]): g(x) as list representation
        """

        self.n = n
        self.k = k
        self.g = g
        self.g_mat = self.create_generator_matrix()
        self.h_mat = self.create_parity_check_matrix()
        self.h = self.calculate_parity_check_poly()

    def create_generator_matrix(self) -> np.matrix:
        """Generates and returns a `k × n` generator matrix `G`.

        Returns:
            np.matrix: generator matrix `G`
        """

        g_ = np.array(self.g, dtype=int)
        m = np.zeros((self.k, self.n), dtype=int)

        for i in range(0, self.k):
            m[i, i:i + self.n - self.k + 1] = g_

        for i in range(0, self.k - 1):
            for j in range(i+1, self.k):
                if m[i, j]:
                    np.bitwise_xor(m[i, :], m[j, :], out=m[i, :])

        return m

    def create_parity_check_matrix(self) -> np.matrix:
        """Generates and returns a `(n-k) × n` parity-check matrix `H`.

        Returns:
            np.matrix: parity-check matrix `H`
        """

        parity = np.eye(self.n - self.k, self.n, k=self.k, dtype=int)
        parity[:, :self.k] = self.g_mat[:, self.k:].transpose()
        return parity

    def calculate_parity_check_poly(self) -> str:
        """Generates and returns a formatted string representation of the parity-check polynomial `h(x)`.

        Returns:
            str: parity-check polynomial
        """

        return str(Poly(CyclicUtil.divide_mod_2(CyclicUtil.create_x_n_1(self.n), self.g)[0], x).as_expr())

    def encode(self, d: List[int]) -> str:
        """Encodes message `d` using generator matrix `G`.

        Args:
            d (List[int]): message to encode, length `k`

        Returns:
            str: encoded message
        """

        return "".join([str(i) for i in np.array(d, dtype=int).dot(self.g_mat) % 2])

    @staticmethod
    def create_x_n_1(n: int) -> List[int]:
        """Creates a list representation of the `x^n - 1` polynomial.

        Args:
            n (int): degree of polynomial

        Returns:
            List[int]: `x^n - 1`
        """

        x_n_1 = [0] * (n + 1)
        x_n_1[0] = 1
        x_n_1[-1] = 1
        return x_n_1

    @staticmethod
    def divide_mod_2(a: List[int], b: List[int]) -> Tuple[List[int], List[int]]:
        """Calculates quotient and remainder when dividing polynomials `a` and `b` (mod 2).

        Args:
            a (List[int]): list representation of polynomial `a`
            b (List[int]): list representation of polynomial `b`

        Returns:
            Tuple[List[int], List[int]]: list representations of the quotient and remainder
        """

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


def load_integer_from_inclusive_range(name: str, lower: int, upper: int) -> int:
    """Loads integer from range `[lower, upper]`.

    Repeats requests until user enters a correct number.
    Uses range `[lower, inf)` if `upper < lower`.

    Args:
        name (str): name of parameter to load, used for prompts
        lower (int): lower bound, inclusive
        upper (int): upper bound, inclusive

    Returns:
        int: loaded integer
    """

    while True:
        print(f"{name} = ", end="")

        try:
            i = int(input())
        except ValueError:
            print("Please enter an integer")
            continue

        if i < lower:
            print(f"'{name}' must be greater than {lower - 1}")
        elif upper >= lower and i > upper:
            print(f"'{name}' must be less than {upper + 1}")
        else:
            return i


def load_poly_coeffs(n: int, k: int) -> List[int]:
    """Loads list representation of generator polynomial.

    Repeats requests until user enters a correct polynomial.

    Conditions:
     - polynomial must only be in variable x
     - polynomial must be a factor of x^n - 1
     - all coefficients must be either 0 or 1
     - degree of polynomial must be exactly n-k
     - trailing term must be 1

    Monomials can be entered in any order.
    Exponents can be marked with either `^` or `**`.

    Args:
        n (int): n
        k (int): k

    Returns:
        List[int]: list representation of loaded generator polynomial
    """

    class BadPolyError(Exception):
        '''Custom error class for incorrect polynomial input.'''
        pass

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

            if CyclicUtil.divide_mod_2(CyclicUtil.create_x_n_1(n), coeffs)[1]:
                raise BadPolyError("Polynomial must be a divisor of x^n - 1")

            return coeffs

        except BadPolyError as e:
            print(e)
        except (ValueError, SyntaxError, SympifyError, PolynomialError):
            print("Invalid polynomial format")


def load_message(length: int) -> List[int]:
    """Loads array of bits.

    Repeats requests until user enters a message of length `length` or greater.
    All entered characters must be `0` or `1`.

    Args:
        length (int): minimum length of message

    Returns:
        List[int]: list of first `length` loaded bits
    """

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


def main_unsafe():
    """Internal demonstration entry point which does not handle abrupt script termination.

    Loads `n`, `k` and `g(x)`.
    Prints `G`, `H` and `h(x)`.
    Requires one message and outputs its encoded version.

    Raises:
        KeyboardInterrupt: when Ctrl+C is pressed
        EOFError: when EOF is read from stdin
    """

    # 0 < k < n
    n = load_integer_from_inclusive_range("n", 1, 0)
    k = load_integer_from_inclusive_range("k", 1, n - 1)
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


def main():
    '''Demonstration entry point.'''
    try:
        main_unsafe()
    except (KeyboardInterrupt, EOFError):
        print("\nExiting the program.")
        sys.exit(0)


if __name__ == "__main__":
    main()
