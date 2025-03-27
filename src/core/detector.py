import cv2
import numpy as np
from utils.logger import setup_logger
from utils.config import MODELS_DIR

class Detector:
    def __init__(self, detection_type="face"):
        """初始化检测器"""
        self.logger = setup_logger("Detector")
        self.detection_type = detection_type
        self.model = self._load_model()
        self.logger.info(f"{detection_type} 检测器初始化完成")

    def _load_model(self):
        """加载预训练模型"""
        if self.detection_type == "face":
            model_path = os.path.join(MODELS_DIR, "haarcascade_frontalface_default.xml")
            if not os.path.exists(model_path):
                self.logger.error(f"模型文件不存在: {model_path}")
                return None
            return cv2.CascadeClassifier(model_path)
        
        elif self.detection_type in ["object", "vehicle", "person"]:
            # 加载YOLO模型
            weights_path = os.path.join(MODELS_DIR, "yolov3.weights")
            config_path = os.path.join(MODELS_DIR, "yolov3.cfg")
            
            if not os.path.exists(weights_path) or not os.path.exists(config_path):
                self.logger.error("YOLO模型文件缺失")
                return None
                
            net = cv2.dnn.readNet(weights_path, config_path)
            
            # 使用GPU加速（如果可用）
            try:
                net.setPreferableBackend(cv2.dnn.DNN_BACKEND_CUDA)
                net.setPreferableTarget(cv2.dnn.DNN_TARGET_CUDA)
                self.logger.info("使用CUDA加速")
            except:
                self.logger.info("使用CPU模式")
                
            return net
        
        else:
            self.logger.error(f"不支持的检测类型: {self.detection_type}")
            return None

    def detect(self, frame):
        """在帧中检测目标"""
        if self.detection_type == "face":
            return self._detect_faces(frame)
        else:
            return self._detect_objects(frame)

    def _detect_faces(self, frame):
        """人脸检测"""
        if self.model is None:
            return frame
            
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = self.model.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5)
        
        for (x, y, w, h) in faces:
            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
            cv2.putText(frame, "Face", (x, y-10), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        
        return frame

    def _detect_objects(self, frame):
        """目标检测（使用YOLO）"""
        if self.model is None:
            return frame
            
        # 获取YOLO输出层
        layer_names = self.model.getLayerNames()
        output_layers = [layer_names[i[0] - 1] for i in self.model.getUnconnectedOutLayers()]
        
        # 准备输入blob
        blob = cv2.dnn.blobFromImage(frame, 0.00392, (416, 416), (0, 0, 0), True, crop=False)
        self.model.setInput(blob)
        outs = self.model.forward(output_layers)
        
        # 解析检测结果
        class_ids = []
        confidences = []
        boxes = []
        height, width = frame.shape[:2]
        
        for out in outs:
            for detection in out:
                scores = detection[5:]
                class_id = np.argmax(scores)
                confidence = scores[class_id]
                
                if confidence > 0.5:  # 置信度阈值
                    # 检测到的对象
                    center_x = int(detection[0] * width)
                    center_y = int(detection[1] * height)
                    w = int(detection[2] * width)
                    h = int(detection[3] * height)
                    
                    # 矩形坐标
                    x = int(center_x - w / 2)
                    y = int(center_y - h / 2)
                    
                    boxes.append([x, y, w, h])
                    confidences.append(float(confidence))
                    class_ids.append(class_id)
        
        # 非极大值抑制
        indexes = cv2.dnn.NMSBoxes(boxes, confidences, 0.5, 0.4)
        
        # 加载类别标签
        labels_path = os.path.join(MODELS_DIR, "coco.names")
        with open(labels_path, "r") as f:
            classes = [line.strip() for line in f.readlines()]
        
        # 绘制检测结果
        for i in range(len(boxes)):
            if i in indexes:
                x, y, w, h = boxes[i]
                label = str(classes[class_ids[i]])
                confidence = confidences[i]
                
                # 根据检测类型过滤
                if (self.detection_type == "vehicle" and label not in ["car", "truck", "bus"]) or \
                   (self.detection_type == "person" and label != "person"):
                    continue
                
                color = (0, 255, 0)  # BGR
                cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)
                cv2.putText(frame, f"{label} {confidence:.2f}", (x, y - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
        
        return frame