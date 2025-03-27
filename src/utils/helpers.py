import cv2
import time
from datetime import datetime
from utils.config import VIDEO_CONFIG

def resize_frame(frame, resolution):
    """调整帧分辨率"""
    if resolution in VIDEO_CONFIG["resolutions"]:
        width, height = VIDEO_CONFIG["resolutions"][resolution]
        return cv2.resize(frame, (width, height))
    return frame

def calculate_fps(start_time, frame_count):
    """计算实时FPS"""
    elapsed_time = time.time() - start_time
    return frame_count / elapsed_time if elapsed_time > 0 else 0

def draw_fps(frame, fps):
    """在帧上绘制FPS信息"""
    cv2.putText(frame, f"FPS: {fps:.2f}", (10, 30), 
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
    return frame