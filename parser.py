import re
import config


def extract_data(pdf):
    data = {
        'pages': [],
        'full_text': '',
        'tables_bboxes': []
    }

    for i, page in enumerate(pdf.pages):
        text = page.extract_text() or ""
        data['full_text'] += text + "\n"

        words = page.extract_words(x_tolerance=2, y_tolerance=3)

        page_info = {
            'num': i + 1,
            'width': float(page.width),
            'height': float(page.height),
            'text': text,  # ИСПРАВЛЕНО: Добавлено поле text для чекера
            'words': words
        }

        tables = page.find_tables()
        for tbl in tables:
            data['tables_bboxes'].append({
                'page': i + 1,
                'bbox': tbl.bbox,
                'page_height': float(page.height)
            })

        data['pages'].append(page_info)

    return data


def find_figures_in_text(text):
    matches = re.finditer(config.FIG_PATTERN, text)
    nums = []
    for m in matches:
        parts = m.group(0).split()
        if len(parts) > 1 and parts[1].isdigit():
            nums.append(int(parts[1]))
    return nums


def find_fig_refs(text):
    matches = re.finditer(config.FIG_REF_PATTERN, text, re.IGNORECASE)
    refs = []
    for m in matches:
        start_pos = m.start()
        if start_pos == 0 or text[start_pos - 1] == '\n':
            continue

        txt = m.group(0)
        num = re.search(r'\d+', txt)
        if num:
            refs.append(int(num.group(0)))
    return refs


def find_tables_in_text(text):
    matches = re.finditer(config.TABLE_PATTERN, text)
    nums = []
    for m in matches:
        parts = m.group(0).split()
        if len(parts) > 1 and parts[1].isdigit():
            nums.append(int(parts[1]))
    return nums