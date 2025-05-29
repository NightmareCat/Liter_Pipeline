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
    if isinstance(texts, str):
        texts = [texts]
    inputs = tokenizer(texts, return_tensors="pt", truncation=True, padding=True)
    with torch.no_grad():
        outputs = model(**{k: v.to(device) for k, v in inputs.items()})
        emb = outputs.last_hidden_state[:, 0]
        return torch.nn.functional.normalize(emb, p=2, dim=1)