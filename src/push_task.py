from setting import QUANTITY_ID
from spider import *

if __name__ == "__main__":

    # Windows 环境下必须加这句
    multiprocessing.freeze_support()

    # 控制台最小化
    # minimize_console()

    spider = TaskSpiderTest(
        task_table="spider_task",
        task_keys=["id", "url"],
        redis_key=f"feapder:spider_task_{QUANTITY_ID}",
        keep_alive=True,
        delete_keys="*z_requests",
        task_condition=f"quantity_id={QUANTITY_ID}"
    )
    spider.start_monitor_task()

    # 检测 3次
    for _ in range(3):
        while spider.all_thread_is_done() is False:
            time.sleep(1)
        time.sleep(1)
    
    js_executor = JSExecutor()
    if js_executor.is_active:
        js_executor.shutdown()