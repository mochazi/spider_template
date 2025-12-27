import subprocess
import tempfile
import os
import multiprocessing
import atexit
import json
import shutil
from feapder.utils.log import log
from concurrent.futures import ProcessPoolExecutor
from functools import partial

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

            node_path = shutil.which("node")
            if not node_path:
                log.exception("未检测到 Node.js 环境，请先安装 Node.js 并将其添加到环境变量 PATH 中！")
            
            cls._instance = super(JSExecutor, cls).__new__(cls)
            # 运算密集型推荐核心数；I/O 密集型推荐核心数*2
            # 这里取逻辑核心数作为 max_workers
            # 留1个核心避免卡死
            cores = multiprocessing.cpu_count() - 1
            cls._instance.executor = ProcessPoolExecutor(max_workers=cores)
            # 注册程序退出时的自动关闭钩子
            atexit.register(cls._instance.shutdown)
            log.debug(f"[JSExecutor] 单例初始化成功，工作进程数: {cores}")
        return cls._instance

    def submit_task(self, func, **kwargs):
        """
        异步提交单个任务
        用法: handler.submit_task(js_encode_logic, param1="A", param2="B", timeout_sec=15)
        """
        if not self.executor:
            raise RuntimeError("进程池已关闭")
        return self.executor.submit(func, **kwargs)

    def map_tasks(self, func, dict_params_list):
        """
        批量提交字典任务列表
        用法: handler.map_tasks(js_encode_logic, [{"param1":"A", "param2":"B"}, {...}])
        """
        if not self.executor:
            raise RuntimeError("进程池已关闭")
        
        # 使用 partial 包装，使其支持 map 批量处理字典
        wrapper_func = partial(_jsexecutor_dict_wrapper, func=func)
        return list(self.executor.map(wrapper_func, dict_params_list))

    def shutdown(self):
        """优雅关闭进程池"""
        if self.executor:
            log.debug("[JSExecutor] 正在关闭进程池并清理资源...")
            self.executor.shutdown(wait=True)
            self.executor = None
            log.debug("[JSExecutor] 关闭进程池完毕")

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