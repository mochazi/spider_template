
# 爬虫模板

# 环境

## 前端

### 环境

|   **环境**   |**版本号**|
|:----------:|:----:|
| **NodeJS** |**v20.19.5**|

### 安装nvm（nodejs管理器）

[nvm发行版](https://github.com/coreybutler/nvm-windows/releases)

#### 安装nodeJS

```bash
nvm install v20.19.5
```
#### 切换nodeJS

```bash
nvm use v20.19.5
```

#### 设置淘宝镜像源

```bash
npm config set registry http://registry.npmmirror.com
```

#### 查看镜像源

```bash
npm config get registry
```

# 后端

---

|**运行环境**|**项目使用版本**|
|:----:|:--------:|
|**python**|**3.11.5**|

```bash
pip install uv
```

```bash
uv venv --python 3.11.5
```

```bash
.venv\Scripts\activate
```

- 同步 pyproject.toml 环境

```bash
uv sync
```

- 导出成 requirements.txt

```bash
uv pip freeze > requirements.txt
```

```bash
uv run spider.py
```
