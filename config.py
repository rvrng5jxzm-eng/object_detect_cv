"""
Configuration для CV Detection Project
"""
from dataclasses import dataclass, field
from typing import Tuple


@dataclass
class WindowConfig:
    """Настройки окна"""
    width: int = 1920
    height: int = 1080
    title: str = "Real-time Object & Face Detection"
    fps_target: int = 60


@dataclass
class CameraConfig:
    """Настройки камеры"""
    source: int = 0  # 0 для веб-камеры, или URL для IP камеры
    width: int = 1280
    height: int = 720
    flip_horizontal: bool = True  # Эффект зеркала


@dataclass
class DetectionConfig:
    """Настройки детекции"""
    # YOLO
    yolo_model: str = "yolov8n.pt"  # nano для скорости
    yolo_confidence: float = 0.5
    
    # Face Analysis
    face_detection_backend: str = "opencv"  # opencv, ssd, mtcnn, retinaface
    face_analysis_actions: list = field(default_factory=lambda: ['age'])  # ТОЛЬКО ВОЗРАСТ
    
    # Фильтры объектов (какие классы показывать)
    object_classes_filter: list = field(default_factory=lambda: [
        "person", "phone", "laptop", "mouse", "keyboard",
        "bottle", "cup", "book", "scissors", "remote"
    ])


@dataclass
class UIConfig:
    """Настройки UI"""
    # Цвета (R, G, B, A)
    bg_overlay_color: Tuple[int, int, int, int] = (0, 0, 0, 120)  # Полупрозрачный черный
    
    # Bbox цвета
    bbox_person_color: Tuple[int, int, int] = (0, 255, 0)      # Зеленый для людей
    bbox_object_color: Tuple[int, int, int] = (255, 165, 0)    # Оранжевый для объектов
    bbox_thickness: int = 3
    
    # Face info
    face_info_bg: Tuple[int, int, int, int] = (30, 30, 30, 200)
    face_info_text_color: Tuple[int, int, int] = (255, 255, 255)
    
    # Статистика
    stats_panel_width: int = 400
    stats_panel_height: int = 300
    stats_bg: Tuple[int, int, int, int] = (20, 20, 20, 230)
    stats_text_color: Tuple[int, int, int] = (0, 255, 255)  # Cyan
    
    # Шрифты
    font_size_large: int = 32
    font_size_medium: int = 24
    font_size_small: int = 18


@dataclass
class AppConfig:
    """Главная конфигурация"""
    window: WindowConfig = field(default_factory=WindowConfig)
    camera: CameraConfig = field(default_factory=CameraConfig)
    detection: DetectionConfig = field(default_factory=DetectionConfig)
    ui: UIConfig = field(default_factory=UIConfig)
    
    @staticmethod
    def print_summary():
        print("╔" + "═" * 68 + "╗")
        print("║" + " Real-time CV Detection Project ".center(68) + "║")
        print("╠" + "═" * 68 + "╣")
        print(f"║ Window: {Config.window.width}x{Config.window.height}".ljust(69) + "║")
        print(f"║ Camera: {Config.camera.width}x{Config.camera.height}".ljust(69) + "║")
        print(f"║ YOLO Model: {Config.detection.yolo_model}".ljust(69) + "║")
        print(f"║ Face Detection: {Config.detection.face_detection_backend}".ljust(69) + "║")
        print("╚" + "═" * 68 + "╝")


# Глобальный инстанс
Config = AppConfig()