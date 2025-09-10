import os
from pathlib import Path
from dotenv import load_dotenv
from typing import Optional, Dict, Any, List

from config.settings import PROCESSING_CONFIG
from utils.api_clients import api_manager

load_dotenv()  # 从.env文件中读取环境变量

# 从配置中获取最小块长度
MIN_BLOCK_LENGTH = PROCESSING_CONFIG["min_block_length"]

'''
仅离线模式使用,已注释
calling by research_pipeline/research_long_analyse.py
'''

def summarize_markdown(md_path: str, config: Optional[Dict[str, Any]] = None) -> List[str]:
    """
    将 Markdown 文档通过 DeepSeek API 发送总结，返回多个技术要点 markdown 文件路径。
    
    Args:
        md_path: str, 输入 markdown 文件路径
        config: Optional[Dict[str, Any]], 可选配置参数，包含 prompt_template, output_dir 等
    
    Returns:
        List[str]: 输出的 markdown 文件路径列表
    """
    if config is None:
        config = {}
    
    # 获取DeepSeek客户端
    client = api_manager.get_deepseek_client()
    
    # 使用传入的配置或默认值
    final_config = config

    with open(md_path, "r", encoding="utf-8") as f:
        content = f.read()

    prompt = final_config.get("prompt_template", "")
    full_prompt = prompt + "\n\n" + content

    response = client.chat.completions.create(
        model="deepseek-chat",  # 使用默认模型
        messages=[{"role": "user", "content": full_prompt}],
        temperature=0.5,  # 使用默认温度
    )

    result_text = response.choices[0].message.content
    output_dir = Path(final_config["output_dir"])
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
