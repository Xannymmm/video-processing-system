import cv2
import logging

class MainWindow:
    def __init__(self, args):
        """初始化GUI窗口"""
        self.args = args
        self.setup_logger()
        self.logger.info("GUI初始化完成")
        
    def setup_logger(self):
        """配置简单日志系统"""
        self.logger = logging.getLogger("GUI")
        self.logger.setLevel(logging.INFO)
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter('%(name)s - %(levelname)s - %(message)s'))
        self.logger.addHandler(handler)
    
    def run(self):
        """主运行循环"""
        self.logger.info("开始视频采集...")
        
        cap = cv2.VideoCapture(self.args.camera)
        if not cap.isOpened():
            self.logger.error("无法打开摄像头")
            return
            
        try:
            while True:
                ret, frame = cap.read()
                if not ret:
                    self.logger.warning("视频帧读取失败")
                    break
                
                cv2.imshow('视频监控系统', frame)
                
                # 按ESC退出
                if cv2.waitKey(1) == 27:
                    break
                    
        finally:
            cap.release()
            cv2.destroyAllWindows()
            self.logger.info("程序已退出")