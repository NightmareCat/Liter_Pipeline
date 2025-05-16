# utils/table_utils.py

from bs4 import BeautifulSoup

def pad_row(row, max_len):
    return row + [""] * (max_len - len(row))

def html_table_to_markdown(html_text):
    soup = BeautifulSoup(html_text, 'html.parser')
    table = soup.find('table')
    if not table:
        return "[无法解析HTML表格]"

    rows = []
    for tr in table.find_all('tr'):
        cells = [td.get_text(strip=True) for td in tr.find_all(['td', 'th'])]
        rows.append(cells)

    if not rows:
        return "[空表格]"

    max_len = max(len(r) for r in rows)
    rows = [pad_row(r, max_len) for r in rows]

    header = rows[0]
    markdown = "| " + " | ".join(header) + " |\n"
    markdown += "| " + " | ".join(["---"] * len(header)) + " |\n"

    for row in rows[1:]:
        markdown += "| " + " | ".join(row) + " |\n"

    return markdown
