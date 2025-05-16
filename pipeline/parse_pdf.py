import json
import cv2
import numpy as np
from pathlib import Path
from pdf2image import convert_from_path
from paddleocr import PPStructure, draw_structure_result
from utils.table_utils import html_table_to_markdown
from utils.text_utils import clean_text, auto_title_format, smart_paragraph_split


def parse_pdf_to_markdown(config:dict):
    

    # 初始化 PPStructure 引擎
    ocr_engine = PPStructure(
        layout=config.get("layout_analysis", True),
        table=config.get("table", True),
        ocr=config.get("ocr_order", True),
        lang=config.get("lang", "ch")
    )

    # 将 PDF 转为图像
    print(f"[INFO] 正在将 PDF 转为图像: {pdf_path}")
    images = convert_from_path(pdf_path, dpi=300)

    md_lines = []
    seen_paragraphs = set()

    for idx, img in enumerate(images):
        print(f"[INFO] 正在处理第 {idx + 1} 页...")
        img_np = np.array(img)
        img_cv = cv2.cvtColor(img_np, cv2.COLOR_RGB2BGR)

        results = ocr_engine(img_cv)

        # 保存结构图
        structure_img = draw_structure_result(img_cv, results, font_path="simfang.ttf")
        cv2.imwrite(str(output_dir / f"page_{idx+1}_structure.jpg"), structure_img)

        # 暂存块
        text_blocks = []

        for region in results:
            region_type = region["type"]
            res = region.get("res")

            # 标题/正文内容
            if region_type in ["text", "title"] and isinstance(res, list):
                for sub in res:
                    text = clean_text(sub.get("text", ""))
                    if not text.strip():
                        continue
                    text_blocks.append({
                        "type": region_type,
                        "text": text,
                        "y": sub["text_region"][0][1]
                    })

            # 表格
            elif region_type == "table":
                html_text = res.get("html", "") if isinstance(res, dict) else ""
                markdown_table = html_table_to_markdown(html_text)
                text_blocks.append({
                    "type": "table",
                    "text": markdown_table,
                    "y": region["bbox"][1]
                })

            # 图像
            elif region_type == "figure":
                text_blocks.append({
                    "type": "figure",
                    "text": f"[图像区域 第{idx+1}页]",
                    "y": region["bbox"][1]
                })

            # 跳过页眉/页脚等
            elif region_type in ["header", "footer"]:
                continue

        # 按纵坐标排序（确保输出顺序）
        text_blocks = sorted(text_blocks, key=lambda b: b["y"])

        md_lines.append(f"\n---\n第 {idx+1} 页\n---\n\n")

        for block in text_blocks:
            if block["type"] == "table":
                md_lines.append(block["text"] + "\n")
            elif block["type"] == "figure":
                md_lines.append(block["text"] + "\n")
            else:
                text = block["text"]
                if block["type"] == "title":
                    text = auto_title_format(text)
                    md_lines.append(f"\n{text}\n")
                else:
                    for para in smart_paragraph_split(text):
                        if para in seen_paragraphs:
                            continue
                        seen_paragraphs.add(para)
                        md_lines.append(para + "\n")

    # 输出 Markdown 文件
    md_path = output_dir / "output.md"
    with open(md_path, "w", encoding="utf-8") as f:
        f.write("\n".join(md_lines))

    print(f"[✅ 完成] Markdown 输出保存至: {md_path}")



if '__name__' == "__main__":
    
    # 加载配置
    with open("config.json", "r", encoding="utf-8") as f:
        config = json.load(f)

    pdf_path = config["pdf_path"]
    output_dir = Path(config["output_dir"])
    output_dir.mkdir(exist_ok=True, parents=True)
    
    parse_pdf_to_markdown(config)