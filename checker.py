import config
import parser


def check_margins(data):
    margins = parser.get_margins(data)
    errors = []
    tol = 5 * config.MM

    for m in margins:
        if abs(m['left'] - config.MARGIN_LEFT * config.MM) > tol:
            errors.append(f"Стр {m['page']}: левое поле {m['left'] / config.MM:.1f}мм (норма {config.MARGIN_LEFT}мм)")

        if abs(m['right'] - config.MARGIN_RIGHT * config.MM) > tol:
            errors.append(
                f"Стр {m['page']}: правое поле {m['right'] / config.MM:.1f}мм (норма {config.MARGIN_RIGHT}мм)")

        if abs(m['top'] - config.MARGIN_TOP * config.MM) > tol:
            errors.append(f"Стр {m['page']}: верхнее поле {m['top'] / config.MM:.1f}мм (норма {config.MARGIN_TOP}мм)")

        if abs(m['bottom'] - config.MARGIN_BOTTOM * config.MM) > tol:
            errors.append(
                f"Стр {m['page']}: нижнее поле {m['bottom'] / config.MM:.1f}мм (норма {config.MARGIN_BOTTOM}мм)")

    return errors


def check_figures(data):
    errors = []
    text = data['text']

    figs = parser.find_figures(text)
    imgs = data['images']

    if len(figs) != len(imgs):
        pass

    for i, num in enumerate(figs):
        if num != i + 1:
            errors.append(f"Рисунок {num}: нарушена нумерация (ожидается {i + 1})")

    return errors


def check_fig_refs(data):
    errors = []
    text = data['text']

    figs = set(parser.find_figures(text))
    refs = set(parser.find_fig_refs(text))

    missing = figs - refs
    for num in missing:
        errors.append(f"Рисунок {num}: нет ссылки в тексте")

    return errors


def check_ref_order(data):
    errors = []
    text = data['text']

    refs = parser.find_refs(text)

    seen = []
    for r in refs:
        if r not in seen:
            seen.append(r)

    for i in range(1, len(seen)):
        if seen[i] < seen[i - 1]:
            errors.append(f"Ссылка [{seen[i]}] идет после [{seen[i - 1]}]: нарушен порядок")

    return errors


def check_tables(data):
    errors = []
    text = data['text']

    tbls = parser.find_tables(text)
    tbl_objs = data['tables']

    if len(tbls) != len(tbl_objs):
        errors.append(f"Количество подписей таблиц ({len(tbls)}) != количество таблиц ({len(tbl_objs)})")

    for tbl in tbl_objs:
        page_data = next(p for p in data['pages'] if p['num'] == tbl['page'])
        page_h = page_data['height']
        bbox = tbl['bbox']

        if bbox[3] > page_h - (config.MARGIN_BOTTOM * config.MM):
            errors.append(f"Стр {tbl['page']}: таблица выходит за нижнее поле")

    return errors


def check_lists(data):
    errors = []

    for page in data['pages']:
        lines = page['text'].split('\n')

        for i, line in enumerate(lines):
            stripped = line.strip()

            if not stripped:
                continue

            for marker in config.LIST_MARKERS:
                if stripped.startswith(marker):
                    if len(stripped) > 1 and stripped[len(marker)] != ' ':
                        errors.append(f"Стр {page['num']}: нет пробела после маркера списка '{marker}'")
                    break

    return errors


def check_indent(data):
    errors = []
    paras = parser.get_paragraphs(data)

    if not paras:
        return errors

    indents = [p['indent'] for p in paras]
    min_indent = min(indents) if indents else 0

    target_indent = config.INDENT * 10 * config.MM

    for p in paras:
        if len(p['text']) < 60:
            continue

        if not p['text'][0].isupper():
            continue

        current_indent = p['indent'] - min_indent

        if abs(current_indent) < 2:
            continue

        if abs(current_indent - target_indent) > 5 * config.MM:
            errors.append(
                f"Стр {p['page']}: абзацный отступ {current_indent / config.MM:.2f}мм (норма {config.INDENT * 10:.1f}мм)")

    return errors


def run_all(data):
    results = {
        'margins': check_margins(data),
        'figures': check_figures(data),
        'fig_refs': check_fig_refs(data),
        'ref_order': check_ref_order(data),
        'tables': check_tables(data),
        'lists': check_lists(data),
        'indent': check_indent(data)
    }
    return results