from pathlib import Path
from pipeline.parse_pdf import parse_pdf_to_markdown
# from pipeline.summarize_with_deepseek import summarize_markdown

import shutil

def ensure_dir(path: Path):
    path.mkdir(parents=True, exist_ok=True)

def run_stage1_pdf_to_md():
    src_dir = Path("liter_source")
    out_dir = Path("markdown_out")
    ensure_dir(out_dir)

    for pdf in src_dir.glob("*.pdf"):
        folder_name = pdf.stem
        target_folder = out_dir / folder_name
        if target_folder.exists():
            print(f"[跳过] 已处理过：{folder_name}")
            continue

        print(f"[STEP 1] 处理 PDF → Markdown: {folder_name}")
        ensure_dir(target_folder)

        # 生成 config dict
        config = {
            "pdf_path": str(pdf),
            "output_dir": str(target_folder),
            "lang": "ch",
            "use_angle_cls": True,
            "layout_analysis": True,
            "table": True,
            "ocr_order": True,
            "save_visual": False
        }

        parse_pdf_to_markdown(config)

def run_stage2_md_to_summary():
    md_root = Path("markdown_out")
    emb_root = Path("embedding_out")
    ensure_dir(emb_root)

    for subdir in md_root.iterdir():
        if not subdir.is_dir():
            continue

        folder_name = subdir.name
        if (emb_root / folder_name).exists():
            print(f"[跳过] 已总结过：{folder_name}")
            continue

        md_file = subdir / "output.md"
        if not md_file.exists():
            print(f"[警告] 缺失 Markdown 文件：{md_file}")
            continue

        print(f"[STEP 2] 总结 Markdown via DeepSeek: {folder_name}")
        ensure_dir(emb_root / folder_name)

        # summary_text = summarize_markdown(str(md_file), api_config)
        # with open(emb_root / folder_name / "summary.txt", "w", encoding="utf-8") as f:
        #     f.write(summary_text)

def main():
    run_stage1_pdf_to_md()
    # run_stage2_md_to_summary()

if __name__ == "__main__":
    main()
