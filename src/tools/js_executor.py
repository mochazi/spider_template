import subprocess
import tempfile
import os
import multiprocessing
import json
import shutil
from feapder.utils.log import log
from concurrent.futures import ProcessPoolExecutor
from functools import partial

# 将 bin 目录添加到 PATH 第一位
PROJECT_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
os.environ["PATH"] = os.path.join(PROJECT_PATH, "bin") + os.pathsep + os.environ.get("PATH", "")

def js_encode_logic(email, password, timeout_sec=30):

    try:
        tmp_path = None
        with open('./js/encode.js', 'r', encoding='utf-8') as f_read:
            js_template = f_read.read()
            js_code = js_template.replace('python_email', email)
            js_code = js_code.replace('python_password', password)
            
        # 创建临时文件
        with tempfile.NamedTemporaryFile(mode='w', suffix='.js', delete=False) as tmp:
            tmp.write(js_code)
            tmp_path = tmp.name

        # 调用 Node.js 执行
        result = subprocess.run(
            ['node', tmp_path], 
            capture_output=True, 
            text=True, 
            timeout=timeout_sec
        )
        result = result.stdout.strip()
        return dict(email=email, password=password, value=json.loads(result), status="success")

    except subprocess.TimeoutExpired:
        log.exception("JS 执行超时")
    except Exception as e:
        log.exception("JS 执行异常")
    finally:
        # 清理临时文件
        if tmp_path and os.path.exists(tmp_path):
            try:
                os.remove(tmp_path)
            except:
                pass

# ==========================================
# 通用并发执行引擎 (单例类)
# ==========================================
def _jsexecutor_dict_wrapper(task_dict, func, timeout_sec=30):
    """
    字典参数中转器: partial序列化必须放在外面, 用于支持 map 传字典列表
    """
    return func(**task_dict, timeout_sec=timeout_sec)

class JSExecutor:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            if not shutil.which("node"):
                log.error("未检测到 Node.js 环境，请检查 PATH 变量")
                raise RuntimeError("Node.js not found.")

            cls._instance = super(JSExecutor, cls).__new__(cls)
            
            cores = max(1, multiprocessing.cpu_count() - 1)
            cls._instance.executor = ProcessPoolExecutor(max_workers=cores)
            
            log.debug(f"[JSExecutor] 初始化成功，工作进程数: {cores}")
        return cls._instance

    @property
    def is_active(self):
        """检测是否存活"""
        return self.executor is not None

    def submit_task(self, func, **kwargs):
        """异步提交单个任务"""
        if not self.is_active:
            return None
        try:
            return self.executor.submit(func, **kwargs)
        except RuntimeError: # 拦截解释器关闭异常
            return None

    def map_tasks(self, func, dict_params_list, timeout_sec=30):
        """批量提交字典列表"""
        if not self.is_active:
            return []
        try:
            wrapper_func = partial(_jsexecutor_dict_wrapper, func=func, timeout_sec=timeout_sec)
            return list(self.executor.map(wrapper_func, dict_params_list))
        except RuntimeError:
            return []

    def shutdown(self):
        """手动优雅退出"""
        if self.executor:
            log.debug("[JSExecutor] 正在执行手动关闭...")
            try:
                self.executor.shutdown(wait=True)
            finally:
                self.executor = None
                log.info("[JSExecutor] 进程池已完全关闭")

if __name__ == '__main__':
    # Windows 环境下必须加这句
    multiprocessing.freeze_support()

    # 获取单例
    js_executor = JSExecutor()

    email = "123456@qq.com"
    password = "123456"

    tasks = [
        {"email": email, "password": password}
    ]

    log.info("开始批量执行任务...")
    results = js_executor.map_tasks(js_encode_logic, tasks)
    log.info(f"异步任务结果: {results}")

    log.info("异步提交单个任务...")
    future = js_executor.submit_task(js_encode_logic, email=email, password=password)
    log.info(f"异步任务结果: {future.result()}")

    if js_executor.is_active:
        js_executor.shutdown()