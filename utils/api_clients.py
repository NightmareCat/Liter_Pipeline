"""
统一的API客户端管理模块
"""

import os
from typing import Optional
from openai import OpenAI
import requests

from config.settings import API_CONFIG

class APIClientManager:
    """统一的API客户端管理器"""
    
    def __init__(self):
        self.clients = {}
        
    def get_qwen_client(self) -> OpenAI:
        """获取Qwen API客户端"""
        if "qwen" not in self.clients:
            self.clients["qwen"] = OpenAI(
                api_key=API_CONFIG["qwen"]["api_key"],
                base_url=API_CONFIG["qwen"]["base_url"]
            )
        return self.clients["qwen"]
    
    def get_deepseek_client(self) -> OpenAI:
        """获取DeepSeek API客户端"""
        if "deepseek" not in self.clients:
            self.clients["deepseek"] = OpenAI(
                api_key=API_CONFIG["deepseek"]["api_key"],
                base_url=API_CONFIG["deepseek"]["base_url"]
            )
        return self.clients["deepseek"]
    
    def get_siliconflow_client(self) -> dict:
        """获取SiliconFlow API配置"""
        return {
            "api_key": API_CONFIG["siliconflow"]["api_key"],
            "base_url": API_CONFIG["siliconflow"]["base_url"]
        }

# 全局客户端实例
api_manager = APIClientManager()

def get_embedding_vectors(text: str, model_type: int = 2) -> list:
    """
    统一的嵌入向量获取函数
    
    Args:
        text: 要嵌入的文本
        model_type: 1-qwen, 2-bge-m3-local, 3-bge-m3-siliconflow
    
    Returns:
        list: 嵌入向量列表
    """
    import numpy as np
    from pipeline.get_embedding_bgem3 import get_embedding_bge_m3
    
    if model_type == 1:
        # Qwen embedding
        client = api_manager.get_qwen_client()
        response = client.embeddings.create(
            input=text,
            model=API_CONFIG["qwen"]["embedding_model"]
        )
        return [np.array(response.data[0].embedding)]
    
    elif model_type == 2:
        # Local BGE-M3
        embedding_tensor = get_embedding_bge_m3(text)
        return [np.array(embedding_tensor.cpu().tolist())]
    
    elif model_type == 3:
        # SiliconFlow BGE-M3
        config = api_manager.get_siliconflow_client()
        payload = {
            "model": API_CONFIG["siliconflow"]["embedding_model"],
            "input": text,
            "encoding_format": "float"
        }
        headers = {
            "Authorization": f"Bearer {config['api_key']}",
            "Content-Type": "application/json"
        }
        
        response = requests.post(config["base_url"] + "/embeddings", 
                               json=payload, headers=headers)
        if response.status_code == 200:
            return [np.array(item["embedding"]) for item in response.json()["data"]]
        else:
            raise Exception(f"API调用失败: {response.status_code} - {response.text}")
    
    else:
        raise ValueError(f"不支持的模型类型: {model_type}")

def wait_for_file_ready(client: OpenAI, file_id: str, max_retries: int = 30, interval: int = 2) -> bool:
    """
    等待文件处理完成
    
    Args:
        client: OpenAI客户端
        file_id: 文件ID
        max_retries: 最大重试次数
        interval: 重试间隔(秒)
    
    Returns:
        bool: 是否处理完成
    """
    import time
    
    for _ in range(max_retries):
        try:
            file_info = client.files.retrieve(file_id)
            if getattr(file_info, "status", "") == "processed":
                return True
        except Exception:
            pass
        time.sleep(interval)
    return False
