import config
import parser


def check_margins(data):
    errors = []
    for page in data['pages']:
        words = page['words']
        if not words: continue

        page_h = page['height']
        content_words = [w for w in words if 0.05 * page_h < w['top'] < 0.95 * page_h]
        if not content_words: continue

        min_x = min(w['x0'] for w in content_words)
        max_x = max(w['x1'] for w in content_words)
        min_y = min(w['top'] for w in content_words)
        max_y = max(w['bottom'] for w in content_words)

        left_mm = min_x / config.POINTS_PER_MM
        right_mm = (page['width'] - max_x) / config.POINTS_PER_MM
        top_mm = min_y / config.POINTS_PER_MM
        bottom_mm = (page['height'] - max_y) / config.POINTS_PER_MM

        if abs(left_mm - config.MARGIN_LEFT) > config.TOLERANCE_MM:
            errors.append(f"Стр {page['num']}: левое поле {left_mm:.1f}мм")
        if abs(right_mm - config.MARGIN_RIGHT) > config.TOLERANCE_MM:
            errors.append(f"Стр {page['num']}: правое поле {right_mm:.1f}мм")
        if top_mm < config.MARGIN_TOP - config.TOLERANCE_MM:
            errors.append(f"Стр {page['num']}: верхнее поле {top_mm:.1f}мм")
        if bottom_mm < config.MARGIN_BOTTOM - config.TOLERANCE_MM:
            errors.append(f"Стр {page['num']}: нижнее поле {bottom_mm:.1f}мм")
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


def run_all(data):
    return {
        'margins': check_margins(data),
        'figures': check_figures_numbering(data),
        'fig_refs': check_fig_refs(data),
        'tables': check_tables_layout(data),
        'lists': check_lists(data)
    }