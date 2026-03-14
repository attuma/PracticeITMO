import config
import parser

import config


def check_margins(data):
    errors = []
    RELAXED_TOLERANCE = config.TOLERANCE_MM + 2.0

    for page in data['pages']:
        words = page['words']
        if not words: continue

        page_h = page['height']

        content_words = [w for w in words if 0.10 * page_h < w['top'] < 0.90 * page_h]
        if not content_words: continue

        min_x = min(w['x0'] for w in content_words)
        max_x = max(w['x1'] for w in content_words)
        min_y = min(w['top'] for w in content_words)
        max_y = max(w['bottom'] for w in content_words)

        left_mm = min_x / config.POINTS_PER_MM
        right_mm = (page['width'] - max_x) / config.POINTS_PER_MM
        top_mm = min_y / config.POINTS_PER_MM
        bottom_mm = (page['height'] - max_y) / config.POINTS_PER_MM

        if left_mm < config.MARGIN_LEFT - RELAXED_TOLERANCE:
            errors.append(
                f"Стр {page['num']}: текст залезает на левое поле ({left_mm:.1f}мм, минимум {config.MARGIN_LEFT})")

        if right_mm < config.MARGIN_RIGHT - RELAXED_TOLERANCE:
            errors.append(
                f"Стр {page['num']}: текст залезает на правое поле ({right_mm:.1f}мм, минимум {config.MARGIN_RIGHT})")

        if top_mm < config.MARGIN_TOP - RELAXED_TOLERANCE:
            errors.append(
                f"Стр {page['num']}: текст залезает на верхнее поле ({top_mm:.1f}мм, минимум {config.MARGIN_TOP})")

        if bottom_mm < config.MARGIN_BOTTOM - RELAXED_TOLERANCE:
            errors.append(
                f"Стр {page['num']}: текст залезает на нижнее поле ({bottom_mm:.1f}мм, минимум {config.MARGIN_BOTTOM})")

    return errors


def check_figures_numbering(data):
    errors = []
    figs = parser.find_figures_in_text(data['full_text'])
    for i, num in enumerate(figs):
        if num != i + 1:
            errors.append(f"Нарушена нумерация рисунков: {num} вместо {i + 1}")
            break
    return errors


def check_fig_refs(data):
    errors = []
    figs = set(parser.find_figures_in_text(data['full_text']))
    refs = set(parser.find_fig_refs(data['full_text']))
    missing = figs - refs
    for num in missing:
        errors.append(f"Нет ссылки на рисунок {num}")
    return errors


def check_tables_layout(data):
    errors = []
    tbl_nums = parser.find_tables_in_text(data['full_text'])
    for i, num in enumerate(tbl_nums):
        if num != i + 1:
            errors.append(f"Нарушена нумерация таблиц: {num} вместо {i + 1}")
            break
    for tbl in data['tables_bboxes']:
        bottom_y = tbl['bbox'][3]
        limit = tbl['page_height'] - (config.MARGIN_BOTTOM * config.POINTS_PER_MM)
        if bottom_y > limit + 5:
            errors.append(f"Стр {tbl['page']}: таблица выходит за нижнее поле")
    return errors


def check_lists(data):
    errors = []
    for page in data['pages']:
        page_text = page.get('text', "")
        if not page_text: continue

        lines = page_text.split('\n')
        for line in lines:
            stripped = line.strip()
            if not stripped: continue
            for marker in config.LIST_MARKERS:
                if stripped.startswith(marker):
                    if len(stripped) > 1 and stripped[len(marker)] != ' ':
                        errors.append(f"Стр {page['num']}: нет пробела после маркера '{marker}'")
    return errors


def check_ref_order(data):
    errors = []
    refs = parser.find_references(data['full_text'])
    expected_next = 1
    seen = set()
    for ref in refs:
        if ref not in seen:
            if ref != expected_next:
                errors.append(f"Нарушен порядок литературы: ожидалась ссылка [{expected_next}], но встретилась [{ref}]")
                expected_next = ref + 1
            else:
                expected_next += 1
            seen.add(ref)
    return errors


def check_indents(data):
    errors = []
    import config
    for page in data['pages']:
        words = page['words']
        if not words: continue

        page_h = page['height']
        # Исключаем колонтитулы для чистоты расчетов
        content_words = [w for w in words if 0.05 * page_h < w['top'] < 0.95 * page_h]
        if not content_words: continue

        # Находим ФАКТИЧЕСКИЙ левый край текста на странице
        base_left_pt = min(w['x0'] for w in content_words)

        lines = {}
        for w in content_words:
            line_y = round(w['top'] / 4) * 4
            if line_y not in lines:
                lines[line_y] = []
            lines[line_y].append(w)

        for line_y, line_words in lines.items():
            line_words.sort(key=lambda x: x['x0'])
            first_word = line_words[0]

            # Теперь считаем сдвиг первого слова от реального края текста
            shift_mm = (first_word['x0'] - base_left_pt) / config.POINTS_PER_MM

            # Эвристика: если слово сдвинуто от 5 до 25 мм, проверяем его по ГОСТу
            if 5.0 < shift_mm < 25.0:
                if abs(shift_mm - config.INDENT_SIZE) > config.TOLERANCE_MM:
                    errors.append(f"Стр {page['num']}: неверный абзацный отступ {shift_mm:.1f}мм (по ГОСТу {config.INDENT_SIZE}мм)")
    return errors

def run_all(data):
    return {
        'margins': check_margins(data),
        'figures': check_figures_numbering(data),
        'fig_refs': check_fig_refs(data),
        'ref_order': check_ref_order(data),
        'tables': check_tables_layout(data),
        'lists': check_lists(data),
        'indent': check_indents(data)
    }