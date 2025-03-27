import cv2
import time
import argparse
from utils.logger import setup_logger
from utils.config import VIDEO_CONFIG, get_video_filename
from utils.helpers import calculate_fps, draw_fps
from core.camera import Camera
from core.recorder import VideoRecorder
from core.detector import Detector
from core.player import VideoPlayer
from gui.main_window import MainWindow  # 可选GUI

def main():
    # 设置日志
    logger = setup_logger("Main")
    
    # 解析命令行参数
    parser = argparse.ArgumentParser(description="视频流处理系统")
    parser.add_argument("--camera", type=int, default=VIDEO_CONFIG["default_camera"],
                       help="摄像头索引")
    parser.add_argument("--resolution", type=str, default=VIDEO_CONFIG["default_resolution"],
                       help="视频分辨率 (480p, 720p, 1080p)")
    parser.add_argument("--fps", type=int, default=VIDEO_CONFIG["default_fps"],
                       help="帧率 (15, 30, 60)")
    parser.add_argument("--format", type=str, default=VIDEO_CONFIG["default_format"],
                       help="视频格式 (mp4, avi)")
    parser.add_argument("--detect", type=str, choices=["face", "person", "vehicle", "object"],
                       help="启用目标检测")
    parser.add_argument("--gui", action="store_true", help="启用GUI界面")
    args = parser.parse_args()
    
    try:
        if args.gui:
            # GUI模式
            app = MainWindow(args)
            app.run()
        else:
            # 命令行模式
            logger.info("启动视频流处理系统 (命令行模式)")
            
            # 初始化组件
            camera = Camera(args.camera)
            recorder = VideoRecorder(camera, args.resolution, args.fps, args.format)
            detector = Detector(args.detect) if args.detect else None
            player = VideoPlayer()
            
            # 主循环
            start_time = time.time()
            frame_count = 0
            
            while True:
                frame = camera.get_frame()
                if frame is None:
                    break
                
                # 目标检测
                if detector:
                    frame = detector.detect(frame)
                
                # 录制视频
                recorder.record_frame(frame)
                
                # 计算并显示FPS
                frame_count += 1
                fps = calculate_fps(start_time, frame_count)
                frame = draw_fps(frame, fps)
                
                # 显示视频
                cv2.imshow("Video Processing System", frame)
                
                # 键盘控制
                key = cv2.waitKey(1) & 0xFF
                if key == ord('r'):  # 开始/停止录制
                    recorder.toggle_recording()
                elif key == ord('p'):  # 播放最近录制的视频
                    player.load_video(recorder.get_last_recording())
                    player.play()
                elif key == 27:  # ESC退出
                    break
            
            # 释放资源
            camera.release()
            recorder.release()
            cv2.destroyAllWindows()
            
    except Exception as e:
        logger.error(f"程序异常: {str(e)}")
    finally:
        logger.info("程序退出")

if __name__ == "__main__":
    main()