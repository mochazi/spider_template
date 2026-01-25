import shutil
from pathlib import Path
import pathspec
import os
import shutil
from setuptools import setup, Extension
from Cython.Build import cythonize

src_dir = Path(__file__).parent.parent.parent / "src"
src_dir = src_dir.resolve()

dst_dir = Path(__file__).parent / "src"

gitignore_path = src_dir / ".gitignore"

print(f"src_dir: {src_dir}")
print(f"dst_dir: {dst_dir}")
print(f"gitignore_path: {gitignore_path}")

# 根据 .gitignore 规则拷贝 src目录过来准备打包
def copy_tree_src():
    with gitignore_path.open() as f:
        spec = pathspec.PathSpec.from_lines(
            pathspec.patterns.GitWildMatchPattern,
            f
        )

    for path in src_dir.rglob("*"):
        rel_path = path.relative_to(src_dir)

        if path.is_dir():
            if spec.match_tree_files(str(rel_path)):
                continue
            target = dst_dir / rel_path
            target.mkdir(parents=True, exist_ok=True)
        else:
            if spec.match_file(str(rel_path)):
                continue
            target = dst_dir / rel_path
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(path, target)

def compile_pyd():
    py_files = []
    # 1. 递归扫描所有 py 文件
    for root, dirs, files in os.walk(dst_dir):
        for file in files:
            if file.endswith(".py") and file != "main.py" and file != "__init__.py":
                # 获取相对于 dst_dir (src) 的路径，用于构建模块名
                rel_path = os.path.relpath(os.path.join(root, file), dst_dir)
                # 将路径 tools/js_executor.py 转换为 tools.js_executor
                module_path = os.path.splitext(rel_path)[0].replace(os.sep, ".")
                py_files.append({
                    "full_path": os.path.join(root, file),
                    "module_path": module_path,
                    "dir": root,
                    "name": os.path.splitext(file)[0]
                })

    if not py_files:
        print("没有发现需要编译的 Python 文件。")
        return

    print(f"准备编译 {len(py_files)} 个文件...")

    for item in py_files:
        print(f"\n>>> 正在处理: {item['module_path']}")
        
        try:
            # 2. 调用 Cython 编译
            # 关键：Extension 的第一个参数必须是完整的包路径
            setup(
                ext_modules=cythonize(
                    Extension(item['module_path'], [item['full_path']]),
                    compiler_directives={'language_level': "3"},
                    quiet=True
                ),
                # --inplace 会根据 Extension 的名字将 pyd 放在对应的子目录中
                script_args=["build_ext", "--inplace"], 
            )

            # 3. 验证并替换
            # 在 item['dir'] 中寻找生成的 .pyd 文件
            pyd_file = None
            for f in os.listdir(item['dir']):
                if f.startswith(item['name']) and f.endswith(".pyd"):
                    pyd_file = f
                    break
            
            if pyd_file:
                # 成功生成 pyd 后，删除原始 py 文件
                os.remove(item['full_path'])
                print(f"[成功] 原位替换完成: {pyd_file}")
            else:
                print(f"[警告] 未在目标目录发现生成的 pyd 文件")
            
        except Exception as e:
            print(f"[错误] 编译失败 {item['full_path']}: {e}")

    # 4. 清理
    clean_garbage(dst_dir)

def clean_garbage(dst_dir):
    print("\n正在清理中间编译文件...")
    for root, dirs, files in os.walk(dst_dir):
        for file in files:
            # 清理生成的 .c 文件
            if file.endswith(".c"):
                os.remove(os.path.join(root, file))
    
    # 清理产生的临时 build 文件夹
    build_dir = os.path.join(os.getcwd(), "build")
    if os.path.exists(build_dir):
        shutil.rmtree(build_dir)
    print("所有中间文件已清理。")

if __name__ == "__main__":
    copy_tree_src()
    compile_pyd()