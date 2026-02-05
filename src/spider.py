# -*- coding: utf-8 -*-
import feapder,multiprocessing
from feapder import Response
from feapder.utils.log import log
import curl_cffi, time, os, random
from urllib.parse import urlparse
from tools.tools import CookieMaster, minimize_console
from tools.js_executor import JSExecutor,js_encode_logic
from setting import QUANTITY_ID, QUANTITY_COUNT

log.info(f"[当前工作路径] {os.getcwd()}")
log.info(f"[分布式ID] {QUANTITY_ID}")
log.info(f"[分布式数量] {QUANTITY_COUNT}")

class TaskSpiderTest(feapder.TaskSpider):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.end_time = None
        self.cookies = {}
        self.headers = {}
        self.cookie_master = CookieMaster()
        self.js_executor = JSExecutor()
    
    def download_midware(self, request):
        # ------------通用转发中间件------------
        if not hasattr(request, 'cookies'):
            request.cookies = self.cookies
        if not hasattr(request, 'headers'):
            request.headers = self.headers

        params = None
        if hasattr(request, 'params'):
            params = request.params
        if hasattr(request, 'data'):
            response = curl_cffi.requests.request(method='POST', url=request.url, params=params, data=request.data, headers=request.headers, cookies=request.cookies)
            self.cookies.update(response.cookies.get_dict())
        elif hasattr(request, 'json'):
            response = curl_cffi.requests.request(method='POST', url=request.url, params=params, json=request.json, headers=request.headers, cookies=request.cookies)
            self.cookies.update(response.cookies.get_dict())
        else:
            response = curl_cffi.requests.request(method='GET', url=request.url, params=params, headers=request.headers, cookies=request.cookies)
            self.cookies.update(response.cookies.get_dict())

        request.cookies = self.cookies

        parsed = urlparse(request.url)
        domain = f"{parsed.scheme}://{parsed.netloc}"
        if hasattr(request, 'encoding'):
            response = Response.from_text(text=response.text, url=domain, cookies=request.cookies, encoding=request.encoding, headers=response.headers)
        else:
            response = Response.from_text(text=response.text, url=domain, cookies=request.cookies, headers=response.headers)

        return request, response

    def add_task(self):
        sql = f"INSERT INTO spider_task (url, state, parser_name, quantity_id) VALUES (%s, %s, %s, %s) ON DUPLICATE KEY UPDATE state = IF({self._task_condition}, VALUES(state), state)"
        sqls = []
        for index in range(50):
            sqls.append([
                f'https://httpbin.org/get?params={index}',
                0,
                self.__class__.__name__,
                random.randint(1, QUANTITY_COUNT)
            ])

        self._mysqldb.add_batch(sql, sqls)

    def start_requests(self, task):
        
        task_id = task.get('id')
        yield feapder.Request(url=task.url, 
                              callback=self.parse,
                              task_id=task_id)

    # 校验是否请求成功
    def validate(self, request, response):

        if request.callback_name == 'parse':
            if response.json.get('origin') is None :
                raise Exception("response.json.get('origin') is None") 
        return True

    def parse(self, request, response):
        log.info(f"response.json['args'] = {response.json['args']}")

        email = "123456@qq.com"
        password = "123456"

        tasks = [
            {"email": email, "password": password}
        ]

        log.info("开始批量执行任务...")
        results = self.js_executor.map_tasks(js_encode_logic, tasks)
        log.info(f"异步任务结果: {results}")

        log.info("异步提交单个任务...")
        future = self.js_executor.submit_task(js_encode_logic, email=email, password=password)
        log.info(f"异步任务结果: {future.result()}")

        # 标记MySQL完成任务
        yield self.update_task_batch(request.task_id)
