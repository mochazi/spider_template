from spider import *

if __name__ == "__main__":

    # Windows 环境下必须加这句
    multiprocessing.freeze_support()

    # 控制台最小化
    # minimize_console()

    spider = AirSpiderTest()
    spider.start()

    # 检测 3次
    for _ in range(3):
        while spider.all_thread_is_done() is False:
            time.sleep(1)
        time.sleep(1)
    
    js_executor = JSExecutor()
    if js_executor.is_active:
        js_executor.shutdown()