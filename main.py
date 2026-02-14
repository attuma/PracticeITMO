import sys
import parser
import checker


def main():
    if len(sys.argv) < 2:
        print("Использование: python main.py <файл.pdf>")
        sys.exit(1)

    path = sys.argv[1]

    try:
        print(f"Загрузка файла: {path}")
        data = parser.load(path)
    except Exception as e:
        print(f"Ошибка при чтении файла: {e}")
        sys.exit(1)

    print(f"Страниц: {len(data['pages'])}")
    print(f"Рисунков (объектов): {len(data['images'])}")
    print(f"Таблиц (объектов): {len(data['tables'])}")
    print("\nПроверка...\n")

    results = checker.run_all(data)

    total = 0

    for name, errors in results.items():
        if errors:
            print(f"--- {name.upper()} ---")
            for e in errors:
                print(f"  ❌ {e}")
            print()
            total += len(errors)

    if total == 0:
        print("✅ Ошибок не найдено!")
    else:
        print(f"Всего ошибок: {total}")


if __name__ == "__main__":
    main()