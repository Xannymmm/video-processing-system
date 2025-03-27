import cv2
from utils.logger import setup_logger
from utils.config import VIDEO_CONFIG

class Camera:
    def __init__(self, camera_index=None):
        """初始化摄像头"""
        self.logger = setup_logger("Camera")
        
        # 设置摄像头索引
        self.camera_index = camera_index if camera_index is not None else VIDEO_CONFIG["default_camera"]
        
        # 打开摄像头
        self.cap = cv2.VideoCapture(self.camera_index)
        if not self.cap.isOpened():
            self.logger.error(f"无法打开摄像头 {self.camera_index}")
            raise IOError(f"摄像头 {self.camera_index} 初始化失败")
            
        # 设置默认分辨率
        self.set_resolution(VIDEO_CONFIG["default_resolution"])
        self.logger.info(f"摄像头 {self.camera_index} 初始化成功")

    def set_resolution(self, resolution):
        """设置摄像头分辨率"""
        if resolution in VIDEO_CONFIG["resolutions"]:
            width, height = VIDEO_CONFIG["resolutions"][resolution]
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
            self.logger.info(f"设置分辨率为 {resolution} ({width}x{height})")
        else:
            self.logger.warning(f"不支持的分辨率: {resolution}")

    def get_frame(self):
        """获取当前帧"""
        ret, frame = self.cap.read()
        if not ret:
            self.logger.warning("获取帧失败")
            return None
        return frame

    def release(self):
        """释放摄像头资源"""
        if self.cap.isOpened():
            self.cap.release()
            self.logger.info("摄像头资源已释放")

    def __del__(self):
        """析构函数确保资源释放"""
        self.release()