"""
Custom Detector - дополнительная детекция для объектов, которых нет в COCO
"""
import cv2
import numpy as np
from typing import List, Tuple
from detection_engine import DetectionResult


class CustomObjectDetector:
    """
    Детектор для объектов, которых нет в стандартной YOLO
    Использует простые эвристики (цвет, форма, контуры)
    """
    
    def __init__(self):
        print("[CustomDetector] Инициализация детектора специфичных объектов...")
        self.min_contour_area = 5000  # Минимальная площадь контура
    
    def detect_headphones(self, frame: np.ndarray) -> List[DetectionResult]:
        """
        Детекция наушников по форме (два круга рядом)
        """
        # Конвертируем в HSV для поиска черных объектов
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        
        # Маска для темных объектов (наушники обычно черные/темные)
        lower_dark = np.array([0, 0, 0])
        upper_dark = np.array([180, 255, 80])
        mask = cv2.inRange(hsv, lower_dark, upper_dark)
        
        # Морфологические операции для очистки
        kernel = np.ones((5, 5), np.uint8)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
        
        # Ищем контуры
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        detections = []
        
        # Ищем круглые объекты
        for contour in contours:
            area = cv2.contourArea(contour)
            if area < self.min_contour_area:
                continue
            
            # Проверяем круглость
            perimeter = cv2.arcLength(contour, True)
            if perimeter == 0:
                continue
            
            circularity = 4 * np.pi * area / (perimeter * perimeter)
            
            # Если объект круглый (circularity близко к 1)
            if 0.6 < circularity < 1.3:
                x, y, w, h = cv2.boundingRect(contour)
                
                # Проверяем aspect ratio (должно быть близко к квадрату)
                aspect_ratio = float(w) / h if h > 0 else 0
                
                if 0.7 < aspect_ratio < 1.3:  # Примерно квадратный
                    detections.append(DetectionResult(
                        bbox=(x, y, x + w, y + h),
                        class_name="headphones (detected)",
                        confidence=0.7
                    ))
        
        return detections
    
    def detect_charger(self, frame: np.ndarray) -> List[DetectionResult]:
        """
        Детекция зарядного устройства (маленький прямоугольный объект)
        """
        # Аналогично наушникам, но ищем прямоугольные объекты
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray, 50, 150)
        
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        detections = []
        
        for contour in contours:
            area = cv2.contourArea(contour)
            if area < 1000 or area > 15000:  # Зарядник обычно небольшой
                continue
            
            # Аппроксимируем контур
            epsilon = 0.02 * cv2.arcLength(contour, True)
            approx = cv2.approxPolyDP(contour, epsilon, True)
            
            # Если 4 угла - это прямоугольник
            if len(approx) == 4:
                x, y, w, h = cv2.boundingRect(contour)
                aspect_ratio = float(w) / h if h > 0 else 0
                
                # Зарядник обычно квадратный или слегка прямоугольный
                if 0.5 < aspect_ratio < 2.0:
                    detections.append(DetectionResult(
                        bbox=(x, y, x + w, y + h),
                        class_name="charger (detected)",
                        confidence=0.6
                    ))
        
        return detections