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
    title: str = "NEURAL VISION SYSTEM"
    fps_target: int = 60


@dataclass
class CameraConfig:
    """Настройки камеры"""
    source: int = 0
    width: int = 1280
    height: int = 720
    flip_horizontal: bool = True


@dataclass
class DetectionConfig:
    """Настройки детекции"""
    yolo_model: str = "yolov8n.pt"  # Основная модель
    yolo_confidence: float = 0.5
    
    # Custom detection (для GPU)
    use_custom_detection: bool = True
    custom_detection_interval: int = 3  # Запускаем custom детектор каждый N-й кадр
    
    # Объекты для детекции
    object_classes_filter: list = field(default_factory=lambda: [
        "person", "laptop", "cell phone", "keyboard", "mouse",
        "bottle", "cup", "book", "chair", "tv", "remote",
        "backpack", "handbag", "bicycle", "car", "motorcycle",
        "clock", "scissors", "teddy bear", "hair drier"
    ])


@dataclass
class UIConfig:
    """Настройки UI - БЕЛАЯ ТЕМА"""
    # Основные цвета
    primary_color: Tuple[int, int, int] = (255, 255, 255)      # БЕЛЫЙ
    accent_color: Tuple[int, int, int] = (0, 255, 136)         # Зеленый акцент
    secondary_accent: Tuple[int, int, int] = (255, 200, 0)     # Желтый
    warning_color: Tuple[int, int, int] = (255, 70, 70)        # Красный
    
    # Bbox - ТОЛСТЫЕ белые контуры
    bbox_color: Tuple[int, int, int] = (255, 255, 255)
    bbox_person_color: Tuple[int, int, int] = (0, 255, 136)    # Зеленый для людей
    bbox_electronics_color: Tuple[int, int, int] = (100, 200, 255)  # Голубой
    bbox_thickness: int = 3  # ТОЛЩЕ
    corner_length: int = 25  # ДЛИННЕЕ углы
    
    # Текст
    text_color: Tuple[int, int, int] = (255, 255, 255)
    text_bg: Tuple[int, int, int, int] = (0, 0, 0, 180)
    
    # HUD
    hud_bg: Tuple[int, int, int, int] = (0, 0, 0, 200)
    
    # Шрифты
    font_size_large: int = 30
    font_size_medium: int = 22
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
        print("╔" + "═" * 50 + "╗")
        print("║" + " NEURAL VISION SYSTEM ".center(50) + "║")
        print("╠" + "═" * 50 + "╣")
        print(f"║ Resolution: {Config.window.width}x{Config.window.height}".ljust(51) + "║")
        print(f"║ Model: {Config.detection.yolo_model}".ljust(51) + "║")
        print(f"║ Custom Detection: {'ON' if Config.detection.use_custom_detection else 'OFF'}".ljust(51) + "║")
        print("╚" + "═" * 50 + "╝")


# ВАЖНО: Глобальный инстанс Config (с большой буквы!)
Config = AppConfig()