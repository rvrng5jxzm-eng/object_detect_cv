"""
Detection Engine - YOLO + Оптимизированный Custom Detector
"""
import numpy as np
from ultralytics import YOLO
from typing import List, Tuple
from config import Config


class DetectionResult:
    """Результат детекции"""
    def __init__(self, bbox: Tuple[int, int, int, int], 
                 class_name: str, confidence: float):
        self.bbox = bbox
        self.class_name = class_name
        self.confidence = confidence
        self.category = self._get_category()
    
    def _get_category(self) -> str:
        """Категория для цвета"""
        electronics = ["laptop", "cell phone", "keyboard", "mouse", 
                      "tv", "remote", "headphones", "charger"]
        
        if self.class_name == "person":
            return "person"
        elif any(e in self.class_name for e in electronics):
            return "electronics"
        else:
            return "other"


class DetectionEngine:
    """Быстрый детектор с optional custom detection"""
    
    def __init__(self):
        print("[DetectionEngine] Загрузка YOLO...")
        self.yolo = YOLO(Config.detection.yolo_model)
        
        # Прогрев
        dummy = np.zeros((640, 640, 3), dtype=np.uint8)
        _ = self.yolo(dummy, verbose=False)
        
        # Custom detector (опционально)
        self.custom_detector = None
        if Config.detection.use_custom_detection:
            try:
                from custom_detector import CustomObjectDetector
                self.custom_detector = CustomObjectDetector()
                print("[DetectionEngine] Custom detector включен")
            except ImportError:
                print("[DetectionEngine] Custom detector не найден")
        
        self.frame_count = 0
        
        print("[DetectionEngine] ✅ Готов")
    
    def detect_objects(self, frame: np.ndarray) -> List[DetectionResult]:
        """Быстрая детекция с опциональным custom detector"""
        self.frame_count += 1
        
        detections = []
        
        # 1. YOLO (всегда)
        results = self.yolo(
            frame, 
            verbose=False, 
            conf=Config.detection.yolo_confidence,
            iou=0.5,
            max_det=30
        )[0]
        
        for box in results.boxes:
            x1, y1, x2, y2 = map(int, box.xyxy[0].cpu().numpy())
            confidence = float(box.conf[0].cpu().numpy())
            class_id = int(box.cls[0].cpu().numpy())
            class_name = results.names[class_id]
            
            if Config.detection.object_classes_filter:
                if class_name not in Config.detection.object_classes_filter:
                    continue
            
            detections.append(DetectionResult(
                bbox=(x1, y1, x2, y2),
                class_name=class_name,
                confidence=confidence
            ))
        
        # 2. Custom Detection (только каждый N-й кадр)
        if self.custom_detector is not None:
            if self.frame_count % Config.detection.custom_detection_interval == 0:
                custom_detections = self.custom_detector.detect(frame)
                detections.extend(custom_detections)
        
        return detections