"""飞书项目配置"""

import os

from dotenv import load_dotenv

load_dotenv()

PLUGIN_ID = os.getenv("FEISHU_PLUGIN_ID", "")
PLUGIN_SECRET = os.getenv("FEISHU_PLUGIN_SECRET", "")
API_URL = os.getenv("FEISHU_API_URL", "https://project.feishu.cn")
