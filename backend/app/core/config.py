"""
配置管理模块
"""
from pydantic_settings import BaseSettings
from functools import lru_cache
from pathlib import Path


class Settings(BaseSettings):
    """应用配置"""
    
    # 应用基础配置
    app_name: str = "OCR PNG to Excel"
    app_version: str = "1.0.0"
    debug: bool = True
    app_host: str = "0.0.0.0"
    app_port: int = 8000
    
    # 数据库配置
    db_type: str = "sqlite"  # sqlite 或 mysql
    db_host: str = "localhost"
    db_port: int = 3306
    db_user: str = "root"
    db_password: str = ""
    db_name: str = "ocr_pngtoexcel"
    db_sqlite_path: str = "../data/ocr_pngtoexcel.db"
    
    # OCR 服务配置
    ocr_base_url: str = "http://10.119.133.236:8806"
    ocr_token: str = ""
    
    # 文件存储配置
    data_dir: str = "../data"
    max_upload_size: int = 10485760  # 10MB
    
    class Config:
        env_file = ".env"
        case_sensitive = False
    
    @property
    def database_url(self) -> str:
        """构造数据库连接URL"""
        if self.db_type == "sqlite":
            return f"sqlite://{self.db_sqlite_path}"
        else:
            return f"mysql://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}"
    
    @property
    def data_paths(self) -> dict:
        """获取所有数据目录路径"""
        base_dir = Path(self.data_dir)
        return {
            "images": base_dir / "images",
            "ocr_json": base_dir / "ocr_json",
            "excel": base_dir / "excel",
            "temp": base_dir / "temp",
        }


@lru_cache()
def get_settings() -> Settings:
    """获取配置单例"""
    return Settings()
