import unittest
import cv2
import os
from src.core.camera import Camera
from utils.config import VIDEO_CONFIG

class TestCamera(unittest.TestCase):
    def setUp(self):
        """测试前准备"""
        self.camera = Camera()
        
    def test_camera_initialization(self):
        """测试摄像头初始化"""
        self.assertTrue(self.camera.cap.isOpened())
        
    def test_get_frame(self):
        """测试获取帧"""
        frame = self.camera.get_frame()
        self.assertIsNotNone(frame)
        self.assertEqual(len(frame.shape), 3)  # 检查是否为彩色图像
        
    def test_set_resolution(self):
        """测试设置分辨率"""
        for res_name, (width, height) in VIDEO_CONFIG["resolutions"].items():
            self.camera.set_resolution(res_name)
            actual_width = int(self.camera.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            actual_height = int(self.camera.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            self.assertEqual(actual_width, width)
            self.assertEqual(actual_height, height)
            
    def tearDown(self):
        """测试后清理"""
        self.camera.release()

if __name__ == "__main__":
    unittest.main()