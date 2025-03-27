import cv2
import os
from utils.logger import setup_logger
from utils.config import VIDEO_CONFIG, VIDEOS_DIR, get_video_filename
from utils.helpers import resize_frame

class VideoRecorder:
    def __init__(self, camera, resolution=None, fps=None, format=None):
        """初始化视频录制器"""
        self.logger = setup_logger("Recorder")
        self.camera = camera
        
        # 配置参数
        self.resolution = resolution or VIDEO_CONFIG["default_resolution"]
        self.fps = fps or VIDEO_CONFIG["default_fps"]
        self.format = format or VIDEO_CONFIG["default_format"]
        self.codec = VIDEO_CONFIG["codecs"][self.format]
        
        # 确保视频目录存在
        os.makedirs(VIDEOS_DIR, exist_ok=True)
        
        # 初始化录制状态
        self.writer = None
        self.recording = False
        self.logger.info("视频录制器初始化完成")

    def start_recording(self, filename=None):
        """开始录制视频"""
        if self.recording:
            self.logger.warning("已经在录制中")
            return False
            
        if filename is None:
            filename = get_video_filename(extension=self.format)
        
        filepath = os.path.join(VIDEOS_DIR, filename)
        width, height = VIDEO_CONFIG["resolutions"][self.resolution]
        
        # 创建VideoWriter
        fourcc = cv2.VideoWriter_fourcc(*self.codec)
        self.writer = cv2.VideoWriter(filepath, fourcc, self.fps, (width, height))
        
        if not self.writer.isOpened():
            self.logger.error(f"无法创建视频文件 {filepath}")
            return False
            
        self.recording = True
        self.logger.info(f"开始录制视频: {filepath}")
        return True

    def record_frame(self, frame):
        """录制一帧"""
        if self.recording and self.writer is not None:
            resized_frame = resize_frame(frame, self.resolution)
            self.writer.write(resized_frame)

    def stop_recording(self):
        """停止录制"""
        if self.recording and self.writer is not None:
            self.writer.release()
            self.writer = None
            self.recording = False
            self.logger.info("视频录制已停止")

    def toggle_recording(self, filename=None):
        """切换录制状态"""
        if self.recording:
            self.stop_recording()
        else:
            self.start_recording(filename)

    def __del__(self):
        """析构函数确保资源释放"""
        self.stop_recording()