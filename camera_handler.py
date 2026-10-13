"""
Camera Handler - работа с видеопотоком
Адаптировано из hand_tracking.py
"""
import cv2
import  as np
from config import Config


class CameraHandler:
    """
    Обработка видеопотока с камеры
    """
    
    def __init__(self):
        print("[CameraHandler] Инициализация камеры...")
        
        self.cap = cv2.VideoCapture(Config.camera.source)
        
        if not self.cap.isOpened():
            raise RuntimeError("❌ Не удалось открыть камеру!")
        
        # Устанавливаем разрешение
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, Config.camera.width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, Config.camera.height)
        
        # Проверяем реальное разрешение
        actual_width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        actual_height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        
        print(f"[CameraHandler] ✅ Камера открыта: {actual_width}x{actual_height}")
        
        self.frame = None
        self.frame_count = 0
    
    def read_frame(self) -> bool:
        """
        Читаем кадр с камеры
        Returns: True если кадр успешно прочитан
        """
        ret, frame = self.cap.read()
        
        if not ret:
            print("[CameraHandler] ⚠️ Не удалось прочитать кадр")
            return False
        
        # Flip для эффекта зеркала
        if Config.camera.flip_horizontal:
            frame = cv2.flip(frame, 1)
        
        self.frame = frame
        self.frame_count += 1
        
        return True
    
    def get_frame(self) -> np.ndarray:
        """Возвращает текущий кадр"""
        return self.frame
    
    def get_frame_rgb(self) -> np.ndarray:
        """Возвращает кадр в RGB (для pygame/PIL)"""
        if self.frame is None:
            return None
        return cv2.cvtColor(self.frame, cv2.COLOR_BGR2RGB)
    
    def release(self):
        """Освобождаем ресурсы"""
        if self.cap is not None:
            self.cap.release()
            print("[CameraHandler] 🧹 Камера закрыта")