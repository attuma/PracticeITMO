import sys
import pdfplumber
import parser
import checker


def main():
    if len(sys.argv) < 2:
        return

    path = sys.argv[1]

    try:
        with pdfplumber.open(path) as pdf:
            data = parser.extract_data(pdf)
            results = checker.run_all(data)

        total = sum(len(errs) for errs in results.values())

        if total == 0:
            print("OK")
        else:
            print(f"Errors: {total}")
            for k, v in results.items():
                if v:
                    print(f"{k}: {v}")

    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()