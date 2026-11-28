"""项目公共配置与日志入口。"""

from base.config import Config, config
from base.logger import logger, setup_logger

__all__ = ["Config", "config", "logger", "setup_logger"]
