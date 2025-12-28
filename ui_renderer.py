"""
UI Renderer - БЕЛЫЕ ТОЛСТЫЕ КОНТУРЫ
"""
import pygame
import time
from typing import List, Tuple
from config import Config
from detection_engine import DetectionResult


class UIRenderer:
    """Белый минималистичный HUD"""
    
    def __init__(self, screen: pygame.Surface):
        self.screen = screen
        self.width = Config.window.width
        self.height = Config.window.height
        
        pygame.font.init()
        self.font_large = pygame.font.SysFont('Arial', Config.ui.font_size_large, bold=True)
        self.font_medium = pygame.font.SysFont('Arial', Config.ui.font_size_medium, bold=True)
        self.font_small = pygame.font.SysFont('Arial', Config.ui.font_size_small)
        
        self.fps = 0
        self.object_count = 0
        
        print("[UIRenderer] ✅ Готов")
    
    def _get_bbox_color(self, detection: DetectionResult) -> Tuple[int, int, int]:
        """Цвет в зависимости от категории"""
        if detection.category == "person":
            return Config.ui.bbox_person_color
        elif detection.category == "electronics":
            return Config.ui.bbox_electronics_color
        else:
            return Config.ui.bbox_color
    
    def draw_target_box(self, surface: pygame.Surface, bbox: tuple, 
                        label: str, confidence: float, color: tuple):
        """
        ТОЛСТЫЕ БЕЛЫЕ контуры с четкими углами
        """
        x1, y1, x2, y2 = bbox
        
        # Масштабируем
        scale_x = self.width / Config.camera.width
        scale_y = self.height / Config.camera.height
        
        x1 = int(x1 * scale_x)
        y1 = int(y1 * scale_y)
        x2 = int(x2 * scale_x)
        y2 = int(y2 * scale_y)
        
        thickness = Config.ui.bbox_thickness
        corner_len = Config.ui.corner_length
        
        # УГЛЫ (ТОЛСТЫЕ)
        # Верхний левый
        pygame.draw.line(surface, color, (x1, y1), (x1 + corner_len, y1), thickness)
        pygame.draw.line(surface, color, (x1, y1), (x1, y1 + corner_len), thickness)
        
        # Верхний правый
        pygame.draw.line(surface, color, (x2, y1), (x2 - corner_len, y1), thickness)
        pygame.draw.line(surface, color, (x2, y1), (x2, y1 + corner_len), thickness)
        
        # Нижний левый
        pygame.draw.line(surface, color, (x1, y2), (x1 + corner_len, y2), thickness)
        pygame.draw.line(surface, color, (x1, y2), (x1, y2 - corner_len), thickness)
        
        # Нижний правый
        pygame.draw.line(surface, color, (x2, y2), (x2 - corner_len, y2), thickness)
        pygame.draw.line(surface, color, (x2, y2), (x2, y2 - corner_len), thickness)
        
        # Label с фоном
        label_text = f"{label.upper()}"
        text_surf = self.font_medium.render(label_text, True, Config.ui.text_color)
        text_rect = text_surf.get_rect()
        
        # Позиция
        text_x = x1
        text_y = y1 - text_rect.height - 10
        
        if text_y < 0:
            text_y = y1 + 5
        
        # Фон для текста
        bg_padding = 8
        bg_rect = pygame.Rect(
            text_x - bg_padding, 
            text_y - bg_padding,
            text_rect.width + bg_padding * 2,
            text_rect.height + bg_padding * 2
        )
        
        bg_surface = pygame.Surface((bg_rect.width, bg_rect.height), pygame.SRCALPHA)
        bg_surface.fill(Config.ui.text_bg)
        surface.blit(bg_surface, bg_rect.topleft)
        
        # Текст
        surface.blit(text_surf, (text_x, text_y))
        
        # Confidence (маленько)
        conf_text = f"{confidence:.0%}"
        conf_surf = self.font_small.render(conf_text, True, color)
        surface.blit(conf_surf, (x2 - 50, text_y))
    
    def draw_hud(self, surface: pygame.Surface):
        """Минималистичный HUD"""
        hud_x = 30
        hud_y = 30
        
        # Фон HUD
        hud_lines = [
            f"NEURAL VISION",
            f"FPS: {self.fps}",
            f"OBJECTS: {self.object_count}"
        ]
        
        # Вычисляем размер фона - ИСПРАВЛЕНО!
        max_width = max([self.font_medium.size(line)[0] for line in hud_lines]) + 30
        hud_height = len(hud_lines) * 35 + 20
        
        # Рисуем фон
        hud_bg = pygame.Surface((max_width, hud_height), pygame.SRCALPHA)
        hud_bg.fill(Config.ui.hud_bg)
        surface.blit(hud_bg, (hud_x - 15, hud_y - 10))
        
        # Текст
        y_offset = hud_y
        
        for i, line in enumerate(hud_lines):
            color = Config.ui.accent_color if i == 0 else Config.ui.text_color
            text_surf = self.font_medium.render(line, True, color)
            surface.blit(text_surf, (hud_x, y_offset))
            y_offset += 35
    
    def update_stats(self, fps: int, objects: List[DetectionResult]):
        """Обновляем статистику"""
        self.fps = fps
        self.object_count = len(objects)
    
    def render(self, objects: List[DetectionResult]):
        """Главный рендеринг"""
        # Target boxes
        for obj in objects:
            color = self._get_bbox_color(obj)
            self.draw_target_box(self.screen, obj.bbox, 
                               obj.class_name, obj.confidence, color)
        
        # HUD
        self.draw_hud(self.screen)