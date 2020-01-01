import sys


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


def load_number_from_inclusive_range(name: str, lower: int, upper: int) -> int:
    while True:
        print(f"{name} = ", end="")

        try:
            x = int(input())
        except ValueError:
            print("Please enter a number")
            continue

        if x < lower:
            print(f"'{name}' must be greater than {lower - 1}")
        elif upper > lower and x > upper:
            print(f"'{name}' must be less than {upper + 1}")
        else:
            return x


if __name__ == "__main__":
    main()
