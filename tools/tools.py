import pickle,os,time,curl_cffi,platform,ctypes

# 最小化当前窗口
def minimize_console():
    if platform.system() == "Windows":
        # 获取当前控制台窗口句柄
        whnd = ctypes.windll.kernel32.GetConsoleWindow()
        if whnd != 0:
            # 6 表示最小化窗口 (SW_MINIMIZE)
            ctypes.windll.user32.ShowWindow(whnd, 6)

class CookieMaster:

    # https://curl-cffi.readthedocs.io/en/stable/cookies.html
    def __init__(self):
        self.cookies_path = self.set_current_path('cookies.pk')

    def set_current_path(self, path) -> str:
        return os.path.join(os.path.dirname(__file__), path)

    def save_cookies(self, client):
        """
            client = curl_cffi.Session()
            cookie_master = CookieMaster()
            client.get("https://httpbin.org/cookies/set/foo/bar")
            cookie_master.save_cookies(client)
        """
        with open(self.cookies_path, "wb") as f:
            pickle.dump(client.cookies.jar._cookies, f)

    def load_cookies(self):
        """
            client = curl_cffi.Session()
            cookie_master = CookieMaster()
            client.cookies.jar._cookies.update(cookie_master.load_cookies())
            print(client.cookies.get_dict())
        """
        if not os.path.isfile(self.cookies_path):
            return None
        with open(self.cookies_path, "rb") as f:
            return pickle.load(f)

    # 检测 cookie 是否需要更新
    def check_token_expiry(self, cookie_name: str = "zsxq_access_token") -> bool:
        """
            cookie_master = CookieMaster()
            print(cookie_master.check_token_expiry())
        """
        client = curl_cffi.Session()
        cookies = self.load_cookies()

        # 不存在 cookies.pk 
        if cookies is None:
            return True

        client.cookies.jar._cookies.update(cookies)

        target_cookie = None
        for cookie in client.cookies.jar:
            if cookie.name == cookie_name:
                target_cookie = cookie
                break
        
        # 未找到cookie
        if not target_cookie:
            return True

        expires_timestamp = target_cookie.expires
        
        if expires_timestamp is None:
            return False

        # 提前三天, 判断cookie过期
        now = time.time()
        one_day_later = now + (3 * 24 * 60 * 60)
        
        if one_day_later >= expires_timestamp:
            return True
        else:
            return False
