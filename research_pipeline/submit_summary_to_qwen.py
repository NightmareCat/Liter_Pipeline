import os
from openai import OpenAI
from typing import List
from prompts import final_prompt


def submit_summary_to_qwen(Research_object: str, markdown_chunks: List[str]) -> str:
    """
    将多篇 markdown 总结内容提交给 Qwen-Long 模型，生成一篇综合性调研报告。
    
    Args:
        research_object (str): 调研主题，例如 "提升卫星的接入成功率"
        markdown_chunks (List[str]): 每篇论文对应的Markdown内容

    Returns:
        str: 调研报告的 Markdown 格式文本
    """
    client = OpenAI(
    api_key=os.getenv("QWEN_API_KEY"),
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
    )   
    merged_md = "\n\n".join(markdown_chunks)

    # 构建Prompt
    user_prompt = f"""
        你是一位专业的科研分析员，擅长从多篇学术研究中提炼出针对特定研究课题的关键技术路线和发展趋势。

        研究课题为：{Research_object}

        以下是{len(markdown_chunks)}篇论文的提炼内容，请你据此生成一篇综合性调研报告：
        {merged_md}

        请根据上述内容输出调研报告，结构与格式要求如下：
        ---
            """
    user_prompt = user_prompt + final_prompt

    # 发起 API 请求
    completion = client.chat.completions.create(
        model="qwen-max-latest",
        messages=[
            {'role': 'system', 'content': '你是一个科研分析助手，请以Markdown格式输出调研报告。'},
            {'role': 'user', 'content': user_prompt}
        ]
    )

    return completion.choices[0].message.content # type: ignore
