import unittest
import checker
import config


class CheckerTests(unittest.TestCase):

    def test_check_figures_reports_numbering_gap(self):
        data = {
            "full_text": "Рисунок 1\nРисунок 3",
            "images_count": 2
        }

        errors = checker.check_figures_numbering(data)

        self.assertEqual(len(errors), 1)
        self.assertIn("Нарушена нумерация рисунков: 3 вместо 2", errors[0])

    def test_check_fig_refs_returns_empty_when_all_numbers_found(self):
        data = {
            "full_text": "Рисунок 1\nРисунок 2\nВ тексте есть ссылка только на рис. 1 и рис. 2",
        }

        errors = checker.check_fig_refs(data)
        self.assertEqual(errors, [])

    def test_check_fig_refs_reports_missing_ref(self):
        data = {
            "full_text": "Рисунок 1\nТекст без ссылок",
        }
        errors = checker.check_fig_refs(data)
        self.assertIn("Нет ссылки на рисунок 1", errors[0])

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
        self.assertIn("нет пробела после маркера '-'", errors[0])
        self.assertIn("нет пробела после маркера '•'", errors[1])

    def test_check_tables_reports_numbering_gap(self):
        data = {
            "full_text": "Таблица 1\nТаблица 4",
            "tables_bboxes": []
        }

        errors = checker.check_tables_layout(data)

        self.assertIn("Нарушена нумерация таблиц: 4 вместо 2", errors[0])

    def test_run_all_returns_correct_keys(self):
        data = {
            "pages": [],
            "full_text": "",
            "tables_bboxes": []
        }

        results = checker.run_all(data)

        expected_keys = {"margins", "figures", "fig_refs", "tables", "lists"}
        self.assertEqual(set(results.keys()), expected_keys)


if __name__ == "__main__":
    unittest.main()