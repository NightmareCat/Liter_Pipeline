import os
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI

MIN_BLOCK_LENGTH = 100

load_dotenv()  # 从.env文件中读取环境变量

def summarize_markdown(md_path: str, config: dict) -> list[str]:
    """
    将 Markdown 文档通过 DeepSeek API 发送总结，返回多个技术要点 markdown 文件路径。
    
    Args:
        md_path: str, 输入 markdown 文件路径
        config: dict, 包含 model, prompt_template, output_dir 等（API Key 从环境变量读取）
    
    Returns:
        List[str]: 输出的 markdown 文件路径列表
    """
    api_key = config.get("deepseek_api_key") or os.getenv("DEEPSEEK_API_KEY")
    if not api_key:
        raise ValueError("❌ 未提供 DeepSeek API Key，请设置 config['deepseek_api_key'] 或 .env 文件")

    client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com/v1")

    with open(md_path, "r", encoding="utf-8") as f:
        content = f.read()

    prompt = config.get("prompt_template", "")
    full_prompt = prompt + "\n\n" + content

    response = client.chat.completions.create(
        model=config.get("model", "deepseek-chat"),
        messages=[{"role": "user", "content": full_prompt}],
        temperature=0.5,
    )

    result_text = response.choices[0].message.content
    output_dir = Path(config["output_dir"])
    output_dir.mkdir(parents=True, exist_ok=True)

    blocks = result_text.split("---") # type: ignore
    pdf_name = output_dir.name + ".pdf"
    output_paths = []

    n_block = 1
    for i, block in enumerate(blocks):
        block = block.strip()
        if len(block) < MIN_BLOCK_LENGTH:
            # print(f"[跳过] tech_{i+1}.md 内容过短（{len(block)} 字符）")
            continue

        # ✅ 追加“对应文献”信息
        block += f"\n- 对应文献：{pdf_name}"

        out_path = output_dir / f"tech_{n_block}.md"
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(block)
        output_paths.append(str(out_path))
        n_block += 1

    return output_paths