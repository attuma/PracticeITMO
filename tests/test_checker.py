import unittest

import checker


class CheckerFunctionsTests(unittest.TestCase):
    def test_check_figures_reports_numbering_gap(self):
        data = {
            "text": "Рисунок 1\nРисунок 3",
            "images": [{"page": 1}, {"page": 1}],
        }

        errors = checker.check_figures(data)

        self.assertEqual(len(errors), 1)
        self.assertIn("Рисунок 3: нарушена нумерация (ожидается 2)", errors[0])

    def test_check_fig_refs_returns_empty_when_all_numbers_found(self):
        data = {
            "text": "Рисунок 1\nРисунок 2\nВ тексте есть ссылка только на рис. 1",
        }

        errors = checker.check_fig_refs(data)

        self.assertEqual(errors, [])

    def test_check_ref_order_reports_out_of_order_references(self):
        data = {
            "text": "Сначала [3], потом [1], затем [2]",
        }

        errors = checker.check_ref_order(data)

        self.assertEqual(errors, ["Ссылка [1] идет после [3]: нарушен порядок"])

    def test_check_lists_reports_missing_space_after_marker(self):
        data = {
            "pages": [
                {
                    "num": 1,
                    "text": "-Неправильно\n- Правильно\n•Без пробела",
                }
            ]
        }

        errors = checker.check_lists(data)

        self.assertEqual(len(errors), 2)
        self.assertIn("нет пробела после маркера списка '-'", errors[0])
        self.assertIn("нет пробела после маркера списка '•'", errors[1])

    def test_check_tables_reports_caption_and_object_count_mismatch(self):
        data = {
            "text": "Таблица 1",
            "tables": [
                {"page": 1, "bbox": (0, 0, 100, 100)},
                {"page": 1, "bbox": (0, 0, 100, 100)},
            ],
            "pages": [{"num": 1, "height": 500}],
        }

        errors = checker.check_tables(data)

        self.assertEqual(errors, ["Количество подписей таблиц (1) != количество таблиц (2)"])

    def test_check_indent_returns_empty_for_short_or_lowercase_paragraphs(self):
        data = {
            "pages": [
                {
                    "num": 1,
                    "words": [
                        {"top": 10, "x0": 20, "text": "короткий"},
                        {"top": 20, "x0": 60, "text": "текст"},
                    ]
                }
            ]
        }

        errors = checker.check_indent(data)

        self.assertEqual(errors, [])

    def test_run_all_returns_all_sections(self):
        data = {
            "pages": [
                {
                    "num": 1,
                    "width": 300,
                    "height": 500,
                    "words": [{"x0": 10, "x1": 20, "top": 10, "bottom": 20, "text": "Текст"}],
                    "text": "",
                }
            ],
            "text": "",
            "images": [],
            "tables": [],
        }

        results = checker.run_all(data)

        self.assertEqual(
            set(results.keys()),
            {"margins", "figures", "fig_refs", "ref_order", "tables", "lists", "indent"},
        )


if __name__ == "__main__":
    unittest.main()
