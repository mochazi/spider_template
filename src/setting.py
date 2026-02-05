import os,sys

# 当前分布式任务 ID
QUANTITY_ID = 1
# 分布式数量
QUANTITY_COUNT = 2

# 切换工作路径为当前项目路径
PROJECT_PATH = os.path.abspath(os.path.dirname(__file__))
os.chdir(PROJECT_PATH)  # 切换工作路经
sys.path.insert(0, PROJECT_PATH) # 添加环境变量
if not os.path.exists('logs'):
    os.makedirs('logs')

LOG_NAME = "init_spider"
LOG_PATH = "logs/%s.log" % LOG_NAME  # log存储路径
# LOG_LEVEL = "DEBUG"
LOG_LEVEL = "INFO"
LOG_COLOR = True  # 是否带有颜色
LOG_IS_WRITE_TO_CONSOLE = True  # 是否打印到控制台
LOG_IS_WRITE_TO_FILE = True  # 是否写文件
LOG_MODE = "w"  # 写文件的模式
LOG_MAX_BYTES = 10 * 1024 * 1024  # 每个日志文件的最大字节数
LOG_BACKUP_COUNT = 20  # 日志文件保留数量
LOG_ENCODING = "utf8"  # 日志文件编码
OTHERS_LOG_LEVAL = "ERROR"  # 第三方库的log等级

## 爬虫启动时，重新抓取失败的requests
RETRY_FAILED_REQUESTS = True

SPIDER_SLEEP_TIME = [5, 8] # 请求延迟
SPIDER_MAX_RETRY_TIMES = 3 # 最大重试次数

# 数据库IP
DATABASE_IP = "127.0.0.1"

# Redis
REDISDB_IP_PORTS=f"{DATABASE_IP}:6379"
REDISDB_USER_PASS=""
REDISDB_DB=0

# MySQL
MYSQL_IP=DATABASE_IP
MYSQL_PORT=3306
MYSQL_DB="init_spider"
MYSQL_USER_NAME="root"
MYSQL_USER_PASS="root"
