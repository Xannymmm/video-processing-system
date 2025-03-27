import os
from datetime import datetime

# 视频配置
VIDEO_CONFIG = {
    "default_camera": 0,  # 默认摄像头索引
    "resolutions": {
        "480p": (640, 480),
        "720p": (1280, 720),
        "1080p": (1920, 1080)
    },
    "default_resolution": "720p",
    "fps_options": [15, 30, 60],
    "default_fps": 30,
    "formats": ["mp4", "avi"],
    "default_format": "mp4",
    "codecs": {
        "mp4": "mp4v",
        "avi": "XVID"
    }
}

# 路径配置
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
MODELS_DIR = os.path.join(BASE_DIR, "models")
DATA_DIR = os.path.join(BASE_DIR, "data")
VIDEOS_DIR = os.path.join(DATA_DIR, "videos")

def get_video_filename(prefix="video", extension="mp4"):
    """生成带时间戳的视频文件名"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"{prefix}_{timestamp}.{extension}"