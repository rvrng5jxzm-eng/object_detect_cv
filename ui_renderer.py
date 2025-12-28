"""
UI Renderer - красивый интерфейс поверх видео
"""
import pygame
import numpy as np
from typing import List, Dict
from config import Config
from detection_engine import DetectionResult, FaceAnalysisResult


class UIRenderer:
    """
    Рендеринг красивого UI поверх видеопотока
    """
    
    def __init__(self, screen: pygame.Surface):
        self.screen = screen
        self.width = Config.window.width
        self.height = Config.window.height
        
        # Шрифты
        self.font_large = pygame.font.Font(None, Config.ui.font_size_large)
        self.font_medium = pygame.font.Font(None, Config.ui.font_size_medium)
        self.font_small = pygame.font.Font(None, Config.ui.font_size_small)
        
        # Статистика
        self.stats = {
            'fps': 0,
            'objects_detected': 0,
            'faces_detected': 0,
            'object_counts': {}
        }
        
        print("[UIRenderer] ✅ Инициализация завершена")
    
    def draw_bbox(self, surface: pygame.Surface, bbox: tuple, 
                  color: tuple, label: str, confidence: float = None):
        """
        Рисуем bounding box с лейблом
        """
        x1, y1, x2, y2 = bbox
        
        # Масштабируем координаты из камеры (720p) в окно (1080p)
        scale_x = self.width / Config.camera.width
        scale_y = self.height / Config.camera.height
        
        x1 = int(x1 * scale_x)
        y1 = int(y1 * scale_y)
        x2 = int(x2 * scale_x)
        y2 = int(y2 * scale_y)
        
        # Рисуем прямоугольник
        pygame.draw.rect(surface, color, (x1, y1, x2 - x1, y2 - y1), 
                        Config.ui.bbox_thickness)
        
        # Лейбл с confidence
        if confidence is not None:
            label_text = f"{label} {confidence:.2f}"
        else:
            label_text = label
        
        # Фон для текста
        text_surface = self.font_small.render(label_text, True, (255, 255, 255))
        text_rect = text_surface.get_rect()
        
        # Позиция над bbox
        text_bg_rect = pygame.Rect(x1, y1 - text_rect.height - 8, 
                                   text_rect.width + 10, text_rect.height + 6)
        
        # Рисуем фон
        bg_surface = pygame.Surface((text_bg_rect.width, text_bg_rect.height))
        bg_surface.set_alpha(200)
        bg_surface.fill(color)
        surface.blit(bg_surface, text_bg_rect.topleft)
        
        # Рисуем текст
        surface.blit(text_surface, (x1 + 5, y1 - text_rect.height - 5))
    
    def draw_face_info(self, surface: pygame.Surface, face: FaceAnalysisResult):
        """
        Рисуем информацию о лице (ТОЛЬКО ВОЗРАСТ)
        """
        x1, y1, x2, y2 = face.bbox
        
        # Масштабируем
        scale_x = self.width / Config.camera.width
        scale_y = self.height / Config.camera.height
        
        x1 = int(x1 * scale_x)
        y1 = int(y1 * scale_y)
        x2 = int(x2 * scale_x)
        y2 = int(y2 * scale_y)
        
        # Bbox для лица (зеленый)
        pygame.draw.rect(surface, Config.ui.bbox_person_color, 
                        (x1, y1, x2 - x1, y2 - y1), 
                        Config.ui.bbox_thickness)
        
        # Информационная панель (справа от лица)
        info_width = 150
        info_height = 60
        info_x = x2 + 10
        info_y = y1
        
        # Если выходит за границы - рисуем слева
        if info_x + info_width > self.width:
            info_x = x1 - info_width - 10
        
        # Фон панели
        info_bg = pygame.Surface((info_width, info_height), pygame.SRCALPHA)
        info_bg.fill(Config.ui.face_info_bg)
        surface.blit(info_bg, (info_x, info_y))
        
        # Текст - только возраст
        y_offset = info_y + 15
        
        # Возраст
        age_text = self.font_medium.render(f"Age: {face.age}", True, 
                                        Config.ui.face_info_text_color)
        surface.blit(age_text, (info_x + 10, y_offset))
        
        # Аксессуары (если будут добавлены позже)
        if face.has_glasses:
            y_offset += 30
            glasses_text = self.font_small.render("👓 Glasses", True, (255, 255, 0))
            surface.blit(glasses_text, (info_x + 10, y_offset))
    
    def draw_objects(self, surface: pygame.Surface, objects: List[DetectionResult]):
        """
        Рисуем все обнаруженные объекты
        """
        for obj in objects:
            # Цвет в зависимости от класса
            if obj.class_name == "person":
                color = Config.ui.bbox_person_color
            else:
                color = Config.ui.bbox_object_color
            
            # Рисуем bbox
            self.draw_bbox(surface, obj.bbox, color, 
                          obj.class_name, obj.confidence)
    
    def draw_faces(self, surface: pygame.Surface, faces: List[FaceAnalysisResult]):
        """
        Рисуем всю информацию о лицах
        """
        for face in faces:
            self.draw_face_info(surface, face)
    
    def draw_stats_panel(self, surface: pygame.Surface):
        """
        Рисуем панель статистики (верхний правый угол)
        """
        panel_x = self.width - Config.ui.stats_panel_width - 20
        panel_y = 20
        
        # Фон панели
        panel_bg = pygame.Surface((Config.ui.stats_panel_width, 
                                   Config.ui.stats_panel_height), 
                                 pygame.SRCALPHA)
        panel_bg.fill(Config.ui.stats_bg)
        surface.blit(panel_bg, (panel_x, panel_y))
        
        # Заголовок
        y_offset = panel_y + 15
        title = self.font_large.render("Statistics", True, (0, 255, 255))
        surface.blit(title, (panel_x + 15, y_offset))
        y_offset += 40
        
        # Линия
        pygame.draw.line(surface, (100, 100, 100), 
                        (panel_x + 15, y_offset), 
                        (panel_x + Config.ui.stats_panel_width - 15, y_offset), 2)
        y_offset += 15
        
        # FPS
        fps_text = self.font_medium.render(f"FPS: {self.stats['fps']}", True, 
                                          Config.ui.stats_text_color)
        surface.blit(fps_text, (panel_x + 15, y_offset))
        y_offset += 30
        
        # Faces detected
        faces_text = self.font_medium.render(
            f"Faces: {self.stats['faces_detected']}", True, 
            (0, 255, 0))
        surface.blit(faces_text, (panel_x + 15, y_offset))
        y_offset += 30
        
        # Objects detected
        objects_text = self.font_medium.render(
            f"Objects: {self.stats['objects_detected']}", True, 
            (255, 165, 0))
        surface.blit(objects_text, (panel_x + 15, y_offset))
        y_offset += 40
        
        # Object counts (детальная статистика)
        if self.stats['object_counts']:
            counts_title = self.font_small.render("Detected:", True, (200, 200, 200))
            surface.blit(counts_title, (panel_x + 15, y_offset))
            y_offset += 25
            
            for obj_class, count in sorted(self.stats['object_counts'].items()):
                count_text = self.font_small.render(f"  {obj_class}: {count}", 
                                                    True, (180, 180, 180))
                surface.blit(count_text, (panel_x + 20, y_offset))
                y_offset += 22
    
    def draw_header(self, surface: pygame.Surface):
        """
        Рисуем заголовок приложения (верхний левый угол)
        """
        header_bg = pygame.Surface((600, 60), pygame.SRCALPHA)
        header_bg.fill((20, 20, 20, 200))
        surface.blit(header_bg, (20, 20))
        
        # Текст заголовка
        title = self.font_large.render("🎥 Real-time CV Detection", True, (0, 255, 0))
        surface.blit(title, (30, 30))
    
    def draw_controls_hint(self, surface: pygame.Surface):
        """
        Подсказка по управлению (нижний левый угол)
        """
        hints = [
            "SPACE - Pause",
            "D - Toggle Stats",
            "ESC - Exit"
        ]
        
        y_offset = self.height - 120
        
        for hint in hints:
            hint_text = self.font_small.render(hint, True, (150, 150, 150))
            surface.blit(hint_text, (20, y_offset))
            y_offset += 25
    
    def update_stats(self, fps: int, objects: List[DetectionResult], 
                    faces: List[FaceAnalysisResult]):
        """
        Обновляем статистику для отображения
        """
        self.stats['fps'] = fps
        self.stats['faces_detected'] = len(faces)
        self.stats['objects_detected'] = len(objects)
        
        # Подсчитываем объекты по классам
        object_counts = {}
        for obj in objects:
            if obj.class_name in object_counts:
                object_counts[obj.class_name] += 1
            else:
                object_counts[obj.class_name] = 1
        
        self.stats['object_counts'] = object_counts
    
    def render(self, objects: List[DetectionResult], 
               faces: List[FaceAnalysisResult], show_stats: bool = True):
        """
        Главный метод рендеринга - рисуем всё
        """
        # Объекты
        self.draw_objects(self.screen, objects)
        
        # Лица
        self.draw_faces(self.screen, faces)
        
        # UI элементы
        self.draw_header(self.screen)
        
        if show_stats:
            self.draw_stats_panel(self.screen)
        
        self.draw_controls_hint(self.screen)
    
    @staticmethod
    def _get_emotion_emoji(emotion: str) -> str:
        """Возвращаем эмодзи для эмоции"""
        emotion_map = {
            'happy': '😊',
            'sad': '😢',
            'angry': '😠',
            'surprise': '😲',
            'fear': '😨',
            'disgust': '🤢',
            'neutral': '😐'
        }
        return emotion_map.get(emotion.lower(), '😐')