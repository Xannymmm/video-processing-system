import os
import logging
from pathlib import Path

def setup_logger(name, log_file='app.log'):
    """配置日志系统"""
    BASE_DIR = Path(__file__).parent.parent.parent  # 项目根目录
    
    # 确保日志目录存在
    log_dir = BASE_DIR / 'logs'
    log_dir.mkdir(exist_ok=True)
    
    log_path = log_dir / log_file
    
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    
    # 文件处理器
    file_handler = logging.FileHandler(log_path, encoding='utf-8')
    file_handler.setFormatter(
        logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    )
    
    # 控制台处理器（移除emoji避免编码问题）
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(
        logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    )
    
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger