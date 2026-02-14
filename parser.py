import pdfplumber
import re
import config


def load(path):
    pdf = pdfplumber.open(path)
    data = {
        'pages': [],
        'text': '',
        'images': [],
        'tables': []
    }

    for i, page in enumerate(pdf.pages):
        w = float(page.width)
        h = float(page.height)

        txt = page.extract_text() or ''
        data['text'] += txt + '\n'

        page_data = {
            'num': i + 1,
            'width': w,
            'height': h,
            'text': txt,
            'obj': page,
            'words': page.extract_words(x_tolerance=2, y_tolerance=3)
        }

        imgs = page.images
        for img in imgs:
            data['images'].append({
                'page': i + 1,
                'x0': img['x0'],
                'y0': img['y0'],
                'x1': img['x1'],
                'y1': img['y1']
            })

        tbls = page.find_tables()
        for tbl in tbls:
            data['tables'].append({
                'page': i + 1,
                'bbox': tbl.bbox
            })

        data['pages'].append(page_data)

    pdf.close()
    return data


def get_margins(data):
    margins = []

    for page in data['pages']:
        words = page['words']
        if not words:
            continue

        xs = [w['x0'] for w in words]
        x1s = [w['x1'] for w in words]
        ys = [w['top'] for w in words]
        bottoms = [w['bottom'] for w in words]

    left = min(xs) if xs else 0
    right = page['width'] - max(x1s) if x1s else 0
    top = min(ys) if ys else 0

    main_text_bottoms = [b for b in bottoms if b < page['height'] * 0.9]
    if main_text_bottoms:
        bottom = page['height'] - max(main_text_bottoms)
    else:
        bottom = page['height'] - max(bottoms) if bottoms else 0

    margins.append({
        'page': page['num'],
        'left': left,
        'right': right,
        'top': top,
        'bottom': bottom
    })


    return margins


def get_paragraphs(data):
    paras = []

    for page in data['pages']:
        words = page['words']
        if not words:
            continue

        lines = {}
        for w in words:
            y = round(w['top'])
            if y not in lines:
                lines[y] = []
            lines[y].append(w)

        sorted_ys = sorted(lines.keys())

        for y in sorted_ys:
            line_words = sorted(lines[y], key=lambda x: x['x0'])
            if not line_words:
                continue

            first_word = line_words[0]
            text_content = " ".join([w['text'] for w in line_words])

            paras.append({
                'page': page['num'],
                'text': text_content,
                'indent': first_word['x0']
            })

    return paras


def find_figures(text):
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
        txt = m.group(0)
        num = re.search(r'\d+', txt)
        if num:
            refs.append(int(num.group(0)))
    return refs


def find_refs(text):
    matches = re.finditer(config.REF_PATTERN, text)
    return [int(m.group(1)) for m in matches]


def find_tables(text):
    matches = re.finditer(config.TABLE_PATTERN, text)
    nums = []
    for m in matches:
        parts = m.group(0).split()
        if len(parts) > 1 and parts[1].isdigit():
            nums.append(int(parts[1]))
    return nums