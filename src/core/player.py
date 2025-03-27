import cv2
import os
from utils.logger import setup_logger
from utils.config import VIDEOS_DIR

class VideoPlayer:
    def __init__(self):
        """初始化视频播放器"""
        self.logger = setup_logger("Player")
        self.cap = None
        self.paused = False
        self.logger.info("视频播放器初始化完成")

    def load_video(self, filepath):
        """加载视频文件"""
        if not os.path.exists(filepath):
            self.logger.error(f"视频文件不存在: {filepath}")
            return False
            
        if self.cap is not None:
            self.cap.release()
            
        self.cap = cv2.VideoCapture(filepath)
        if not self.cap.isOpened():
            self.logger.error(f"无法打开视频文件: {filepath}")
            return False
            
        self.logger.info(f"已加载视频: {filepath}")
        return True

    def play(self):
        """播放视频"""
        if self.cap is None or not self.cap.isOpened():
            self.logger.warning("没有可播放的视频")
            return
            
        while True:
            if not self.paused:
                ret, frame = self.cap.read()
                if not ret:
                    self.logger.info("视频播放结束")
                    break
                    
                cv2.imshow("Video Player", frame)
            
            key = cv2.waitKey(25) & 0xFF
            if key == ord(' '):  # 空格键暂停/继续
                self.paused = not self.paused
            elif key == ord('q') or key == 27:  # q或ESC退出
                break
            elif key == ord('f'):  # f键快进10秒
                current_pos = int(self.cap.get(cv2.CAP_PROP_POS_MSEC))
                self.cap.set(cv2.CAP_PROP_POS_MSEC, current_pos + 10000)
        
        self.release()
        cv2.destroyAllWindows()

    def release(self):
        """释放资源"""
        if self.cap is not None:
            self.cap.release()
            self.cap = None
            self.logger.info("视频播放器资源已释放")

    def __del__(self):
        """析构函数确保资源释放"""
        self.release()