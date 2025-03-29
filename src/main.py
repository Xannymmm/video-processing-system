import sys
import cv2
import time
import argparse
from pathlib import Path

# ========== 路径配置 ==========
_project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_project_root))

# ========== 模块导入 ==========
try:
    from src.utils.logger import setup_logger
    from src.utils.config import VIDEO_CONFIG
    from src.core.camera import Camera
    from src.core.recorder import VideoRecorder
    from src.core.detector import Detector
    from src.gui.main_window import MainWindow
except ImportError as e:
    print(f"导入失败: {e}")
    print("请检查：")
    print("1. 项目结构是否正确")
    print("2. 是否在项目根目录执行 pip install -e .")
    sys.exit(1)

def parse_arguments():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(
        description="视频流处理系统",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument("--camera", 
                      type=int, 
                      default=VIDEO_CONFIG["default_camera"],
                      help="摄像头索引")
    parser.add_argument("--resolution", 
                      choices=["480p", "720p", "1080p"],
                      default=VIDEO_CONFIG["default_resolution"],
                      help="视频分辨率")
    parser.add_argument("--fps", 
                      type=int, 
                      choices=[15, 30, 60],
                      default=VIDEO_CONFIG["default_fps"],
                      help="帧率(FPS)")
    parser.add_argument("--format", 
                      choices=["mp4", "avi"],
                      default=VIDEO_CONFIG["default_format"],
                      help="视频存储格式")
    parser.add_argument("--detect", 
                      choices=["face", "person", "vehicle"],
                      help="启用目标检测")
    parser.add_argument("--gui", 
                      action="store_true",
                      help="启用GUI界面")
    return parser.parse_args()

def run_cli_mode(args, logger):
    """命令行模式主逻辑"""
    logger.info("启动命令行模式")
    
    camera = Camera(args.camera)
    recorder = VideoRecorder(
        camera=camera,
        resolution=args.resolution,
        fps=args.fps,
        output_format=args.format
    )
    detector = Detector(args.detect) if args.detect else None

    try:
        while True:
            ret, frame = camera.read()
            if not ret:
                logger.warning("无法获取视频帧")
                break
            
            if detector:
                frame = detector.process_frame(frame)
            
            recorder.record_frame(frame)
            cv2.imshow("Video System", frame)
            
            key = cv2.waitKey(1) & 0xFF
            if key == ord('r'):
                recorder.toggle_recording()
                status = "开始录制" if recorder.is_recording else "停止录制"
                logger.info(status)
            elif key == 27:  # ESC退出
                break
                
    except KeyboardInterrupt:
        logger.info("用户中断操作")
    finally:
        camera.release()
        recorder.release()
        cv2.destroyAllWindows()

def main():
    logger = setup_logger("Main")
    
    try:
        args = parse_arguments()
        
        if args.gui:
            logger.info("启动GUI模式")
            app = MainWindow(args)
            app.run()
        else:
            run_cli_mode(args, logger)
            
    except Exception as e:
        logger.error(f"程序崩溃: {str(e)}", exc_info=True)
    finally:
        logger.info("程序退出")

if __name__ == "__main__":
    main()