
# 爬虫模板

# 一键安装环境

## Windows

双击 `package\windows\build.bat`

- 检测`WinRAR` `msvc` `uv` `node`环境并且安装
- 利用`cython`将`python文件`编译成`pyd`
- 利用`WinRAR`自解压运行的功能，将`pyd` `uv` `node`打入压缩包，双击`exe`自动安装`uv`环境

# 手动安装环境

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
|**Windows10**|**22H2**|
|**python**|**3.11.12**|

## 一键启动

- **Windows双击`src\run.bat`**

## 手动启动

- 同步 pyproject.toml 环境

```bash
uv sync
```

- 导出成 requirements.txt

```bash
uv pip freeze > requirements.txt
```

- 启动主函数

```bash
uv run main.py
```
