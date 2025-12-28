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
    title: str = "Real-time Object Detection"
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
    # YOLO - используем СРЕДНЮЮ модель для лучшей точности
    yolo_model: str = "yolov8m.pt"  # m = medium (было n = nano)
    yolo_confidence: float = 0.35  # Понижаем порог для большей чувствительности
    
    # Расширенный список объектов (только то, что есть в COCO датасете)
    object_classes_filter: list = field(default_factory=lambda: [
        # Люди
        "person",
        
        # Электроника (что ЕСТЬ в COCO)
        "laptop", "cell phone", "keyboard", "mouse", 
        "tv", "remote",
        
        # Аксессуары (что ЕСТЬ в COCO)
        "backpack", "handbag", "suitcase", "umbrella", "tie",
        
        # Транспорт
        "bicycle", "motorcycle", "car", "bus", "train",
        
        # Предметы быта
        "bottle", "wine glass", "cup", "fork", "knife", "spoon", "bowl",
        "book", "clock", "vase", "scissors", "teddy bear", "hair drier",
        "toothbrush",
        
        # Мебель
        "chair", "couch", "bed", "dining table", "toilet",
        
        # Спорт
        "sports ball", "baseball bat", "tennis racket", "skateboard",
        "surfboard", "skis", "snowboard", "frisbee", "kite"
    ])


@dataclass
class UIConfig:
    """Настройки UI - КРАСИВЫЙ БЕЛЫЙ ДИЗАЙН"""
    # Главные цвета (белая тема)
    primary_color: Tuple[int, int, int] = (255, 255, 255)      # Белый
    accent_color: Tuple[int, int, int] = (0, 255, 136)         # Неоново-зеленый
    secondary_accent: Tuple[int, int, int] = (0, 200, 255)     # Голубой
    warning_color: Tuple[int, int, int] = (255, 107, 107)      # Красный
    
    # Bbox цвета (яркие для видео)
    bbox_person_color: Tuple[int, int, int] = (0, 255, 136)    # Неоново-зеленый
    bbox_electronics_color: Tuple[int, int, int] = (0, 200, 255)  # Голубой
    bbox_transport_color: Tuple[int, int, int] = (255, 165, 0)    # Оранжевый
    bbox_accessories_color: Tuple[int, int, int] = (255, 107, 255) # Розовый
    bbox_other_color: Tuple[int, int, int] = (255, 255, 255)   # Белый
    bbox_thickness: int = 3
    
    # Панели (темный фон с прозрачностью)
    panel_bg: Tuple[int, int, int, int] = (15, 15, 25, 220)
    panel_border_color: Tuple[int, int, int] = (80, 80, 100)
    
    # Текст
    text_primary: Tuple[int, int, int] = (255, 255, 255)       # Белый
    text_secondary: Tuple[int, int, int] = (180, 180, 200)     # Серый
    text_accent: Tuple[int, int, int] = (0, 255, 136)          # Неоново-зеленый
    
    # Статистика панель
    stats_panel_width: int = 450
    stats_panel_height: int = 350
    
    # Шрифты
    font_size_title: int = 42
    font_size_large: int = 32
    font_size_medium: int = 24
    font_size_small: int = 18
    
    # Анимация
    animation_speed: float = 0.15  # Скорость плавных переходов


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
        print("║" + " Real-time Object Detection System ".center(68) + "║")
        print("╠" + "═" * 68 + "╣")
        print(f"║ Resolution: {Config.window.width}x{Config.window.height} @ {Config.window.fps_target}fps".ljust(69) + "║")
        print(f"║ Camera: {Config.camera.width}x{Config.camera.height}".ljust(69) + "║")
        print(f"║ Model: {Config.detection.yolo_model}".ljust(69) + "║")
        print(f"║ Objects tracked: {len(Config.detection.object_classes_filter)}".ljust(69) + "║")
        print("╚" + "═" * 68 + "╝")


# Глобальный инстанс
Config = AppConfig()