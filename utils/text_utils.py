# utils/text_utils.py

import re

def clean_text(text):
    return re.sub(r'\s+', ' ', text).strip()

def auto_title_format(text):
    if re.match(r'^\d+(\.\d+)*[\s\-、.．]', text):
        return f"## {text}"
    elif any(kw in text for kw in ["摘要", "引言", "参考文献", "关键词"]):
        return f"## {text}"
    return text

def smart_paragraph_split(text: str) -> list[str]:
    """
    根据句号/冒号/换行符智能拆分段落
    """
    raw_lines = text.split('\n')
    result = []

    for line in raw_lines:
        line = line.strip()
        if not line:
            continue
        segments = re.split(r'[。！？；]\s*', line)
        for seg in segments:
            if len(seg.strip()) > 10:
                result.append(seg.strip() + "。")
    return result

def merge_text_blocks(blocks, max_distance=50):
    """
    合并相邻文本块
    """
    merged = []
    prev = None

    for block in sorted(blocks, key=lambda b: b["bbox"][1]):
        if prev is None:
            prev = block
        else:
            y_dist = block["bbox"][1] - prev["bbox"][3]
            if y_dist < max_distance and block["type"] == prev["type"] == "text":
                prev["text"] += " " + block["text"]
                prev["bbox"][3] = max(prev["bbox"][3], block["bbox"][3])
            else:
                merged.append(prev)
                prev = block
    if prev:
        merged.append(prev)
    return merged
