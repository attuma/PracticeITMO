import sys
import pdfplumber
import parser
import checker


def main():
    if len(sys.argv) < 2:
        print("Использование: python main.py <путь_к_файлу.pdf>")
        sys.exit(1)

    path = sys.argv[1]

    try:
        with pdfplumber.open(path) as pdf:
            data = parser.extract_data(pdf)
            results = checker.run_all(data)

        total = sum(len(errs) for errs in results.values())

        if total == 0:
            print("OK: Ошибок не найдено")
        else:
            print(f"Найдено ошибок: {total}")
            for k, v in results.items():
                if v:
                    print(f"[{k.upper()}]:")
                    for e in v:
                        print(f"  - {e}")
    except Exception as e:
        print(f"Ошибка: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()