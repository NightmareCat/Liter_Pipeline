"""
项目配置文件 - 集中管理所有配置项
支持从.env文件读取敏感配置（如API密钥）
"""

from pathlib import Path
from typing import Dict, Any
import os
from dotenv import load_dotenv

# 加载.env文件
load_dotenv()

# 基础路径配置
BASE_DIR = Path(__file__).parent.parent

# 数据目录配置
DATA_PATHS = {
    "liter_source": BASE_DIR / "liter_source",
    "markdown_out": BASE_DIR / "markdown_out", 
    "embedding_out": BASE_DIR / "embedding_out",
    "embedding_qwen_long": BASE_DIR / "embedding_qwen_long",
    "research_output": BASE_DIR / "research_output",
    "model_cache": BASE_DIR / "model_cache"
}

# API配置 - 从环境变量读取API密钥
API_CONFIG = {
    "qwen": {
        "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
        "embedding_model": "text-embedding-v3",
        "chat_model": "qwen-long-latest",
        "api_key": os.getenv("QWEN_API_KEY", "your_qwen_api_key_here")  # 从环境变量读取
    },
    "deepseek": {
        "base_url": "https://api.deepseek.com/v1", 
        "chat_model": "deepseek-chat",
        "api_key": os.getenv("DEEPSEEK_API_KEY", "your_deepseek_api_key_here")  # 从环境变量读取
    },
    "siliconflow": {
        "base_url": "https://api.siliconflow.cn/v1",
        "embedding_model": "BAAI/bge-m3",
        "api_key": os.getenv("SOLID_API_KEY", "your_siliconflow_api_key_here")  # 从环境变量读取
    }
}

# 模型选择配置
MODEL_SELECTION = {
    "embedding": 2,  # 1-qwen, 2-bge-m3-local, 3-bge-m3-siliconflow
    "summary": 2,    # 1-qwen, 2-deepseek
    "default_top_k": 10
}

# 处理参数配置
PROCESSING_CONFIG = {
    "max_workers": 8,
    "min_block_length": 100,
    "max_retries": 30,
    "retry_interval": 2
}

# 确保所有目录存在
def ensure_directories():
    """确保所有必要的目录都存在"""
    for path in DATA_PATHS.values():
        path.mkdir(parents=True, exist_ok=True)

# 初始化时确保目录存在
ensure_directories()
