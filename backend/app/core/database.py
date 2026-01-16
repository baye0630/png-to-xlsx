"""
数据库连接管理模块
"""
from tortoise import Tortoise
from app.core.config import get_settings


settings = get_settings()


# Tortoise ORM 配置
TORTOISE_ORM = {
    "connections": {
        "default": settings.database_url
    },
    "apps": {
        "models": {
            "models": ["app.models.task", "aerich.models"],
            "default_connection": "default",
        }
    },
    "use_tz": False,
    "timezone": "Asia/Shanghai"
}


async def init_db():
    """初始化数据库连接"""
    await Tortoise.init(config=TORTOISE_ORM)
    # 生成数据库表结构（开发环境）
    if settings.debug:
        await Tortoise.generate_schemas()


async def close_db():
    """关闭数据库连接"""
    await Tortoise.close_connections()
