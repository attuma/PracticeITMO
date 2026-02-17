import unittest
import parser

class ParserTests(unittest.TestCase):
    def test_find_figures_extracts_numbers(self):
        text = """\
Рисунок 1
Текст
Рисунок 2
"""
        self.assertEqual(parser.find_figures_in_text(text), [1, 2])

    def test_find_fig_refs_extracts_mixed_reference_formats(self):
        text = "Смотри рис. 3 и рисунка 7 в документе"
        self.assertEqual(parser.find_fig_refs(text), [3, 7])

    def test_find_tables_extracts_table_numbers(self):
        text = """\
Таблица 1
данные
Таблица 4
"""
        self.assertEqual(parser.find_tables_in_text(text), [1, 4])

if __name__ == "__main__":
    unittest.main()