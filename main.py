from pathlib import Path
from pipeline.parse_pdf import parse_pdf_to_markdown
from pipeline.summarize_with_deepseek import summarize_markdown
from concurrent.futures import ThreadPoolExecutor, as_completed

path_liter = Path("liter_source")       # 文档目录
path_markdown = Path("markdown_out")    # MD目录
path_embedding = Path("embedding_out")  # embedding目录

def ensure_dir(path: Path):
    path.mkdir(parents=True, exist_ok=True)

def run_stage1_pdf_to_md():
    src_dir = path_liter
    out_dir = path_markdown
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
    markdown_root = path_markdown
    summary_root = path_embedding
    max_workers = 8  # 可根据 CPU 核心和网络能力调整

    tasks = []
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        for subdir in markdown_root.iterdir():
            if not subdir.is_dir():
                continue

            md_files = list(subdir.glob("*.md"))
            if not md_files:
                continue

            target_dir = summary_root / subdir.name
            if target_dir.exists():
                print(f"[跳过] 已存在总结目录：{target_dir}")
                continue

            md_file = md_files[0]  # 每个子目录只取一个 md 文件处理
            out_dir = summary_root / subdir.name
            #  动态传入配置（不写入 config.json）
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
                    "7.需要有完整的技术原理——验证方案——实现效果的才可看做为一个完整的技术要点，否则不输出。"
                    "8.所有内容请使用Markdown格式,多项间用“---”分隔。"
                ),
                "output_dir": str(out_dir)
            }

            
            print(f"[提交] 总结任务：{md_file}")
            tasks.append(
                executor.submit(summarize_markdown, str(md_file), summarize_cfg)
            )

        for future in as_completed(tasks):
            try:
                result = future.result()
                print(f"[完成] {result}")
            except Exception as e:
                print(f"[错误] 总结失败：{e}")

def main():
    run_stage1_pdf_to_md()
    run_stage2_md_to_summary()

if __name__ == "__main__":
    main()
