## 安装流程

- 拉取分支

```bash
git clone https://github.com/NightmareCat/Liter_Pipeline.git 
```

环境配置
- 如需要本地OCR部署，需要通过Anaconda配置MinerU环境
- 安装配置Python环境，推荐3.10.x

```bash
pip install -r requirements.txt
```

- 本地环境配置

  - 本地环境包获取

    - bgem3缓存

      ``` bash
      python ./pipeline/get_embedding_bgem3.py
      ```

      运行后将/model_cache下文件存起来（约4.5GB）

    - pip环境包存储

      ```bash
      pip download -r requirements.txt -d packages
      ```

  - 本地环境包配置

    - 将/model_cache放在同样位置

    - pip环境包安装

      - 将packages放到目的文件夹根目录下

      ```bash
      pip install --no-index --find-links=packages -r requirements.txt
      ```
