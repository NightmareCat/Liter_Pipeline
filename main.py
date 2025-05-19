from pathlib import Path
from pipeline.parse_pdf import parse_pdf_to_markdown
from pipeline.summarize_with_deepseek import summarize_markdown

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

    for subdir in md_root.iterdir():
        if not subdir.is_dir():
            continue

        folder_name = subdir.name
        md_file = subdir / "output.md"
        out_dir = emb_root / folder_name

        if out_dir.exists():
            print(f"[跳过] 已总结过：{folder_name}")
            continue
        if not md_file.exists():
            print(f"[警告] 缺失 Markdown 文件：{md_file}")
            continue

        print(f"[STEP 2] 总结 Markdown via DeepSeek: {folder_name}")

        # ✅ 动态传入配置（不写入 config.json）
        summarize_cfg = {
            "model": "deepseek-chat",
            "prompt_template": (
                "请你从以下论文内容中提取出所有具有完整描述的“技术要点”，并逐个输出，格式如下：\\n\\n"
                "## 技术要点 N\\n"
                "### 技术名称\\n……\\n"
                "### 技术背景\\n……\\n"
                "### 技术原理\\n……\\n"
                "### 验证方案\\n……\\n"
                "### 实现效果\\n……\\n"
                "### 对应章节/页码（如可判断）\\n……\\n\\n"
                "要求:"
                "1.所有内容需基于原文，适度总结，不添加虚构信息；"
                "2.若无法判断某项，请保留标题，写“未明确提及”；"
                "3.除名称外，每一项输出尤其是技术原理要求尽量详尽，描述清楚;"
                "4.技术原理部分需要尽量包含设计模型、依赖技术、方案的适用性与局限性、原理推导的诸多核心公式、预期解决问题等,如没有满足要求的描述可以跳过"
                "5.当涉及到引用文献时,尽量将引用文献的标题也写出;"
                "6.原理描述尽量使用公式进行描述,所用latex公式、变量均使用'$'包起来以满足latex输出格式,每个$格式中不要包含无关文字;"
                "7.所有内容请使用Markdown格式,多项间用“---”分隔。"
            ),
            "output_dir": str(out_dir)
        }

        summarize_markdown(str(md_file), summarize_cfg)

def main():
    run_stage1_pdf_to_md()
    run_stage2_md_to_summary()

if __name__ == "__main__":
    main()
