"""
Detection Engine - YOLO + Custom Detection
"""
import cv2
import numpy as np
from ultralytics import YOLO
from typing import List, Tuple
from config import Config


class DetectionResult:
    """Результат детекции одного объекта"""
    def __init__(self, bbox: Tuple[int, int, int, int], 
                 class_name: str, confidence: float):
        self.bbox = bbox  # (x1, y1, x2, y2)
        self.class_name = class_name
        self.confidence = confidence
        self.category = self._get_category()
    
    def _get_category(self) -> str:
        """Определяем категорию объекта для цветовой кодировки"""
        electronics = ["laptop", "cell phone", "keyboard", "mouse", 
                      "tv", "remote", "camera", "headphones (detected)", 
                      "charger (detected)"]
        transport = ["bicycle", "motorcycle", "car", "bus", "train"]
        accessories = ["backpack", "handbag", "suitcase", "umbrella", "tie"]
        
        if self.class_name == "person":
            return "person"
        elif any(e in self.class_name for e in electronics):
            return "electronics"
        elif any(t in self.class_name for t in transport):
            return "transport"
        elif any(a in self.class_name for a in accessories):
            return "accessories"
        else:
            return "other"


class DetectionEngine:
    """
    Движок детекции - YOLO + Custom Detection
    """
    
    def __init__(self):
        print("[DetectionEngine] Инициализация...")
        
        # YOLO model
        print(f"[DetectionEngine] Загрузка YOLO ({Config.detection.yolo_model})...")
        self.yolo = YOLO(Config.detection.yolo_model)
        
        # Греем модель
        print("[DetectionEngine] Прогрев модели...")
        dummy_frame = np.zeros((640, 640, 3), dtype=np.uint8)
        _ = self.yolo(dummy_frame, verbose=False)
        
        # Custom detector для специфичных объектов
        try:
            from custom_detector import CustomObjectDetector
            self.custom_detector = CustomObjectDetector()
            self.use_custom_detection = True
        except ImportError:
            print("[DetectionEngine] Custom detector не найден, используем только YOLO")
            self.use_custom_detection = False
        
        print("[DetectionEngine] ✅ Готов к работе")
    
    def detect_objects(self, frame: np.ndarray) -> List[DetectionResult]:
        """
        Детекция объектов через YOLO + Custom Detection
        """
        detections = []
        
        # 1. YOLO inference
        results = self.yolo(frame, verbose=False, conf=Config.detection.yolo_confidence)[0]
        
        for box in results.boxes:
            # Извлекаем данные
            x1, y1, x2, y2 = map(int, box.xyxy[0].cpu().numpy())
            confidence = float(box.conf[0].cpu().numpy())
            class_id = int(box.cls[0].cpu().numpy())
            class_name = results.names[class_id]
            
            # Фильтруем по классам
            if Config.detection.object_classes_filter:
                if class_name not in Config.detection.object_classes_filter:
                    continue
            
            detections.append(DetectionResult(
                bbox=(x1, y1, x2, y2),
                class_name=class_name,
                confidence=confidence
            ))
        
        # 2. Custom Detection (наушники, зарядники и т.д.)
        if self.use_custom_detection:
            # Детекция наушников
            headphones = self.custom_detector.detect_headphones(frame)
            detections.extend(headphones)
            
            # Детекция зарядников
            chargers = self.custom_detector.detect_charger(frame)
            detections.extend(chargers)
        
        return detections