
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
|**MySQL**|**5.x**|
|**Redis**|**3.X**|

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

- 启动推送任务

```bash
uv run push_task.py
```

- 启动消费任务

```bash
uv run main.py
```

# 数据库

## 安装数据库

[phpStudy_64](https://public.xp.cn/upgrades/phpStudy_64.zip) 自带`MySQL` `Redis`的一键安装

[TinyRDM (Redis管理工具)](https://redis.tinycraft.cc)

[DBeaver (MySQL管理工具)](https://dbeaver.io/download)

---

### 导入MySQL数据库

- 账号：root
- 密码：root

切换到 `cmd` 后执行以下指令

```shell
cd sql && mysql -uroot -proot -e "DROP DATABASE IF EXISTS init_spider;CREATE DATABASE init_spider CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci; USE init_spider; SOURCE all.sql;"
```
