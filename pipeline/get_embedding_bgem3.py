from transformers import AutoTokenizer, AutoModel # type: ignore
import torch

# 加载模型（自动下载到 ~/.cache/huggingface）
model_name = "BAAI/bge-m3"
cache_dir = "./model_cache"  # 自定义路径

tokenizer = AutoTokenizer.from_pretrained(model_name, cache_dir=cache_dir)
model = AutoModel.from_pretrained(model_name, cache_dir=cache_dir)

device = torch.device("cpu")
model = model.to(device)


# 向量生成
def get_embedding_bge_m3(texts):
    """
    使用BGE-M3模型生成文本的向量表示
    
    参数:
        texts (str or list): 输入的文本字符串或文本列表
        
    返回:
        torch.Tensor: 归一化后的文本向量表示，形状为(batch_size, embedding_dim)
    """
    if isinstance(texts, str):
        texts = [texts]
    inputs = tokenizer(texts, return_tensors="pt", truncation=True, padding=True)
    with torch.no_grad():
        outputs = model(**{k: v.to(device) for k, v in inputs.items()})
        emb = outputs.last_hidden_state[:, 0]
        return torch.nn.functional.normalize(emb, p=2, dim=1)