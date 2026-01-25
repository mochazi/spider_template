# -*- coding: utf-8 -*-
import feapder,multiprocessing
from feapder import Response
from feapder.utils.log import log
import curl_cffi, time, os
from urllib.parse import urlparse
from tools.tools import CookieMaster, minimize_console
from tools.js_executor import JSExecutor,js_encode_logic

log.info(f"[当前工作路径] {os.getcwd()}")

class AirSpiderTest(feapder.AirSpider):

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

    def start_requests(self):

        yield feapder.Request(url='https://httpbin.org/get', params={"a":1, "b": 2}, callback=self.parse_get_url)

    # 解析 get_url
    def parse_get_url(self, request, response):
        
        data = response.json['args']
        log.info(f"response.json['args'] = {response.json['args']}")
        yield feapder.Request(url='https://httpbin.org/post', json=data)

    # 校验是否请求成功
    def validate(self, request, response):

        if request.callback_name == 'parse' :
            if response.json['origin']:
                raise Exception("response.json['origin'] is None") 
        return True

    def parse(self, request, response):
        log.info(f"response.json['args'] = {response.json['data']}")

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
