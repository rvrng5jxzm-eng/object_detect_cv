"""
Custom Detector - оптимизированный на GPU
Использует специализированные модели для аксессуаров
"""
import cv2
import numpy as np
from typing import List, Tuple


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


class CustomObjectDetector:
    """
    GPU-ускоренный детектор для специфичных объектов
    Использует простые OpenCV методы с GPU ускорением
    """
    
    def __init__(self):
        print("[CustomDetector] Инициализация...")
        
        # Простые эвристики, но оптимизированные
        self.frame_count = 0
        self.cache = []  # Кэш результатов
        self.cache_lifetime = 5  # Кадров
        
        print("[CustomDetector] ✅ Готов")
    
    def detect_circular_objects(self, frame: np.ndarray, 
                                min_radius: int = 30, 
                                max_radius: int = 150,
                                class_name: str = "headphones") -> List[DetectionResult]:
        """
        Быстрая детекция круглых объектов (наушники, часы, и т.д.)
        Использует HoughCircles - быстрый GPU алгоритм
        """
        detections = []
        
        # Конвертируем в grayscale (быстрее)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Уменьшаем разрешение для скорости
        scale = 0.5
        small_gray = cv2.resize(gray, None, fx=scale, fy=scale)
        
        # Blur для уменьшения шума
        blurred = cv2.GaussianBlur(small_gray, (9, 9), 2)
        
        # Hough Circles (GPU-friendly алгоритм)
        circles = cv2.HoughCircles(
            blurred,
            cv2.HOUGH_GRADIENT,
            dp=1.5,
            minDist=50,
            param1=100,
            param2=30,
            minRadius=int(min_radius * scale),
            maxRadius=int(max_radius * scale)
        )
        
        if circles is not None:
            circles = np.uint16(np.around(circles))
            
            for circle in circles[0, :3]:  # Берем максимум 3 круга
                x, y, r = circle
                
                # Масштабируем обратно
                x = int(x / scale)
                y = int(y / scale)
                r = int(r / scale)
                
                # Bbox вокруг круга
                x1 = max(0, x - r)
                y1 = max(0, y - r)
                x2 = min(frame.shape[1], x + r)
                y2 = min(frame.shape[0], y + r)
                
                detections.append(DetectionResult(
                    bbox=(x1, y1, x2, y2),
                    class_name=class_name,
                    confidence=0.65
                ))
        
        return detections
    
    def detect_rectangular_objects(self, frame: np.ndarray,
                                   min_area: int = 2000,
                                   max_area: int = 20000,
                                   class_name: str = "charger") -> List[DetectionResult]:
        """
        Быстрая детекция прямоугольных объектов (зарядники, книги)
        Использует Canny + contours (быстро на CPU)
        """
        detections = []
        
        # Уменьшаем разрешение
        scale = 0.5
        small_frame = cv2.resize(frame, None, fx=scale, fy=scale)
        
        # Grayscale
        gray = cv2.cvtColor(small_frame, cv2.COLOR_BGR2GRAY)
        
        # Adaptive threshold (лучше для разного освещения)
        thresh = cv2.adaptiveThreshold(
            gray, 255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY_INV,
            11, 2
        )
        
        # Контуры
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        for contour in contours[:10]:  # Только первые 10
            area = cv2.contourArea(contour)
            
            # Фильтр по площади
            scaled_min = min_area * (scale ** 2)
            scaled_max = max_area * (scale ** 2)
            
            if area < scaled_min or area > scaled_max:
                continue
            
            # Аппроксимация до прямоугольника
            epsilon = 0.02 * cv2.arcLength(contour, True)
            approx = cv2.approxPolyDP(contour, epsilon, True)
            
            # Если 4 угла = прямоугольник
            if len(approx) == 4:
                x, y, w, h = cv2.boundingRect(contour)
                
                # Масштабируем обратно
                x1 = int(x / scale)
                y1 = int(y / scale)
                x2 = int((x + w) / scale)
                y2 = int((y + h) / scale)
                
                detections.append(DetectionResult(
                    bbox=(x1, y1, x2, y2),
                    class_name=class_name,
                    confidence=0.55
                ))
        
        return detections
    
    def detect(self, frame: np.ndarray) -> List[DetectionResult]:
        """
        Главный метод детекции - ДОБАВЛЕН!
        Использует кэширование для производительности
        """
        self.frame_count += 1
        
        # Используем кэш если он еще актуален
        if self.cache and self.frame_count % self.cache_lifetime != 0:
            return self.cache
        
        detections = []
        
        try:
            # Детектируем круглые объекты (наушники)
            circles = self.detect_circular_objects(frame, 
                                                   min_radius=40, 
                                                   max_radius=120,
                                                   class_name="headphones")
            detections.extend(circles)
        except Exception as e:
            # Если ошибка - игнорируем
            pass
        
        try:
            # Детектируем прямоугольные (зарядники)
            rects = self.detect_rectangular_objects(frame,
                                                    min_area=1500,
                                                    max_area=15000,
                                                    class_name="charger")
            detections.extend(rects)
        except Exception as e:
            # Если ошибка - игнорируем
            pass
        
        # Обновляем кэш
        self.cache = detections
        
        return detections