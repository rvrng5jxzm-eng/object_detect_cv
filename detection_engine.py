"""
Detection Engine - YOLO + Face Analysis
"""
import cv2
import numpy as np
from ultralytics import YOLO
from deepface import DeepFace
from typing import List, Dict, Tuple, Optional
from config import Config


class DetectionResult:
    """Результат детекции одного объекта"""
    def __init__(self, bbox: Tuple[int, int, int, int], 
                 class_name: str, confidence: float):
        self.bbox = bbox  # (x1, y1, x2, y2)
        self.class_name = class_name
        self.confidence = confidence


class FaceAnalysisResult:
    """Результат анализа лица"""
    def __init__(self, bbox: Tuple[int, int, int, int], age: int):
        self.bbox = bbox
        self.age = age
        
        # Детекция аксессуаров (будет добавлено позже если нужно)
        self.has_glasses = False
        self.has_mask = False


class DetectionEngine:
    """
    Движок детекции - YOLO для объектов + DeepFace для лиц
    """
    
    def __init__(self):
        print("[DetectionEngine] Инициализация...")
        
        # YOLO model
        print(f"[DetectionEngine] Загрузка YOLO ({Config.detection.yolo_model})...")
        self.yolo = YOLO(Config.detection.yolo_model)
        
        # DeepFace настройки
        self.face_backend = Config.detection.face_detection_backend
        
        # Кэш для face analysis (чтобы не анализировать каждый кадр)
        self.face_analysis_cache = {}
        self.face_cache_frames = 15  # Обновляем раз в 15 кадров (реже = быстрее)
        self.current_frame = 0
        
        print("[DetectionEngine] ✅ Готов к работе")
    
    def detect_objects(self, frame: np.ndarray) -> List[DetectionResult]:
        """
        Детекция объектов через YOLO
        """
        results = self.yolo(frame, verbose=False)[0]
        
        detections = []
        
        for box in results.boxes:
            # Извлекаем данные
            x1, y1, x2, y2 = map(int, box.xyxy[0].cpu().numpy())
            confidence = float(box.conf[0].cpu().numpy())
            class_id = int(box.cls[0].cpu().numpy())
            class_name = results.names[class_id]
            
            # Фильтруем по confidence
            if confidence < Config.detection.yolo_confidence:
                continue
            
            # Фильтруем по классам
            if Config.detection.object_classes_filter:
                if class_name not in Config.detection.object_classes_filter:
                    continue
            
            detections.append(DetectionResult(
                bbox=(x1, y1, x2, y2),
                class_name=class_name,
                confidence=confidence
            ))
        
        return detections
    
    def analyze_faces(self, frame: np.ndarray) -> List[FaceAnalysisResult]:
        """
        Анализ лиц через DeepFace (ТОЛЬКО ВОЗРАСТ)
        """
        self.current_frame += 1
        
        # Используем кэш для производительности
        if self.current_frame % self.face_cache_frames != 0:
            return list(self.face_analysis_cache.values())
        
        try:
            # DeepFace анализ
            analysis = DeepFace.analyze(
                frame,
                actions=Config.detection.face_analysis_actions,  # Только ['age']
                detector_backend=self.face_backend,
                enforce_detection=False,
                silent=True
            )
            
            # DeepFace может вернуть list или dict
            if not isinstance(analysis, list):
                analysis = [analysis]
            
            # Обновляем кэш
            self.face_analysis_cache.clear()
            
            results = []
            for idx, face in enumerate(analysis):
                # Извлекаем bbox
                region = face.get('region', {})
                x, y, w, h = region.get('x', 0), region.get('y', 0), \
                            region.get('w', 100), region.get('h', 100)
                
                # Извлекаем только возраст
                age = face.get('age', 0)
                
                result = FaceAnalysisResult(
                    bbox=(x, y, x + w, y + h),
                    age=int(age)
                )
                
                results.append(result)
                self.face_analysis_cache[idx] = result
            
            return results
            
        except Exception as e:
            # Если лиц нет или ошибка - возвращаем пустой список
            return []
    
    def process_frame(self, frame: np.ndarray) -> Tuple[List[DetectionResult], List[FaceAnalysisResult]]:
        """
        Обрабатываем кадр: детекция объектов + анализ лиц
        Returns: (objects, faces)
        """
        objects = self.detect_objects(frame)
        faces = self.analyze_faces(frame)
        
        return objects, faces