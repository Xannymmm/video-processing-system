import tkinter as tk
from tkinter import ttk, filedialog
from PIL import Image, ImageTk
import cv2
import threading
from utils.logger import setup_logger
from core.camera import Camera
from core.recorder import VideoRecorder
from core.detector import Detector
from core.player import VideoPlayer
from utils.config import VIDEO_CONFIG

class MainWindow:
    def __init__(self, args):
        """初始化主窗口"""
        self.logger = setup_logger("GUI")
        self.args = args
        
        # 创建主窗口
        self.root = tk.Tk()
        self.root.title("视频流处理系统")
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        
        # 初始化组件
        self.camera = None
        self.recorder = None
        self.detector = None
        self.player = None
        self.recording = False
        self.thread = None
        self.stop_event = threading.Event()
        
        # 创建UI
        self.create_widgets()
        self.logger.info("GUI界面初始化完成")

    def create_widgets(self):
        """创建界面控件"""
        # 视频显示区域
        self.video_label = tk.Label(self.root)
        self.video_label.pack()
        
        # 控制面板
        control_frame = ttk.Frame(self.root)
        control_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # 摄像头选择
        ttk.Label(control_frame, text="摄像头:").grid(row=0, column=0)
        self.camera_combobox = ttk.Combobox(
            control_frame, 
            values=[f"摄像头 {i}" for i in range(3)],  # 假设最多3个摄像头
            state="readonly"
        )
        self.camera_combobox.current(self.args.camera)
        self.camera_combobox.grid(row=0, column=1)
        
        # 分辨率选择
        ttk.Label(control_frame, text="分辨率:").grid(row=0, column=2)
        self.resolution_combobox = ttk.Combobox(
            control_frame,
            values=list(VIDEO_CONFIG["resolutions"].keys()),
            state="readonly"
        )
        self.resolution_combobox.current(
            list(VIDEO_CONFIG["resolutions"].keys()).index(self.args.resolution)
        )
        self.resolution_combobox.grid(row=0, column=3)
        
        # 录制按钮
        self.record_btn = ttk.Button(
            control_frame, 
            text="开始录制", 
            command=self.toggle_recording
        )
        self.record_btn.grid(row=0, column=4, padx=5)
        
        # 检测选项
        ttk.Label(control_frame, text="检测类型:").grid(row=1, column=0)
        self.detect_combobox = ttk.Combobox(
            control_frame,
            values=["无", "人脸", "行人", "车辆", "所有目标"],
            state="readonly"
        )
        self.detect_combobox.current(0)
        if self.args.detect:
            index = {"face":1, "person":2, "vehicle":3, "object":4}[self.args.detect]
            self.detect_combobox.current(index)
        self.detect_combobox.grid(row=1, column=1)
        
        # 播放按钮
        self.play_btn = ttk.Button(
            control_frame,
            text="播放视频",
            command=self.play_video
        )
        self.play_btn.grid(row=1, column=2)
        
        # FPS显示
        self.fps_label = ttk.Label(control_frame, text="FPS: 0.00")
        self.fps_label.grid(row=1, column=3)
        
        # 状态栏
        self.status_var = tk.StringVar()
        self.status_var.set("就绪")
        ttk.Label(self.root, textvariable=self.status_var).pack(side=tk.BOTTOM, fill=tk.X)
        
        # 启动摄像头
        self.init_camera()

    def init_camera(self):
        """初始化摄像头"""
        try:
            camera_index = self.camera_combobox.current()
            self.camera = Camera(camera_index)
            
            # 设置分辨率
            resolution = self.resolution_combobox.get()
            self.camera.set_resolution(resolution)
            
            # 初始化录制器
            self.recorder = VideoRecorder(
                self.camera,
                resolution,
                self.args.fps,
                self.args.format
            )
            
            # 启动视频更新线程
            self.stop_event.clear()
            self.thread = threading.Thread(target=self.update_video, daemon=True)
            self.thread.start()
            
            self.status_var.set("摄像头已启动")
            
        except Exception as e:
            self.status_var.set(f"摄像头初始化失败: {str(e)}")
            self.logger.error(f"摄像头初始化失败: {str(e)}")

    def update_video(self):
        """更新视频帧"""
        start_time = time.time()
        frame_count = 0
        
        while not self.stop_event.is_set():
            try:
                frame = self.camera.get_frame()
                if frame is None:
                    continue
                
                # 目标检测
                detect_type = self.detect_combobox.get()
                if detect_type != "无":
                    if not self.detector or self.detector.detection_type != detect_type:
                        self.detector = Detector({
                            "人脸": "face",
                            "行人": "person",
                            "车辆": "vehicle",
                            "所有目标": "object"
                        }[detect_type])
                    frame = self.detector.detect(frame)
                
                # 录制视频
                if self.recording:
                    self.recorder.record_frame(frame)
                
                # 计算FPS
                frame_count += 1
                fps = frame_count / (time.time() - start_time)
                self.fps_label.config(text=f"FPS: {fps:.2f}")
                
                # 显示视频
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                img = Image.fromarray(frame)
                imgtk = ImageTk.PhotoImage(image=img)
                self.video_label.imgtk = imgtk
                self.video_label.config(image=imgtk)
                
            except Exception as e:
                self.logger.error(f"视频更新错误: {str(e)}")
                break
        
        self.logger.info("视频更新线程结束")

    def toggle_recording(self):
        """切换录制状态"""
        if not self.recording:
            self.recording = self.recorder.start_recording()
            if self.recording:
                self.record_btn.config(text="停止录制")
                self.status_var.set("正在录制...")
        else:
            self.recording = False
            self.recorder.stop_recording()
            self.record_btn.config(text="开始录制")
            self.status_var.set("录制已停止")

    def play_video(self):
        """播放视频文件"""
        filepath = filedialog.askopenfilename(
            title="选择视频文件",
            filetypes=[("视频文件", "*.mp4 *.avi")]
        )
        if filepath:
            self.player = VideoPlayer()
            if self.player.load_video(filepath):
                play_thread = threading.Thread(target=self.player.play, daemon=True)
                play_thread.start()
                self.status_var.set(f"正在播放: {filepath}")

    def on_close(self):
        """关闭窗口事件处理"""
        self.stop_event.set()
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=1)
        
        if self.camera:
            self.camera.release()
        if self.recorder:
            self.recorder.release()
        
        self.root.destroy()
        self.logger.info("应用程序关闭")

    def run(self):
        """运行主循环"""
        self.root.mainloop()