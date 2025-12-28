"""
UI Renderer - КРАСИВЫЙ БЕЛЫЙ ДИЗАЙН для видео
"""
import pygame
import numpy as np
from typing import List, Dict, Tuple  # ДОБАВИЛИ Tuple
from config import Config
from detection_engine import DetectionResult
import time


class AnimatedValue:
    """Плавная анимация для числовых значений"""
    def __init__(self, initial_value: float = 0.0):
        self.current = initial_value
        self.target = initial_value
    
    def set_target(self, value: float):
        self.target = value
    
    def update(self):
        # Плавное приближение к целевому значению
        self.current += (self.target - self.current) * Config.ui.animation_speed
    
    def get(self) -> float:
        return self.current


class UIRenderer:
    """
    Рендеринг красивого UI поверх видеопотока
    """
    
    def __init__(self, screen: pygame.Surface):
        self.screen = screen
        self.width = Config.window.width
        self.height = Config.window.height
        
        # Шрифты
        pygame.font.init()
        self.font_title = pygame.font.Font(None, Config.ui.font_size_title)
        self.font_large = pygame.font.Font(None, Config.ui.font_size_large)
        self.font_medium = pygame.font.Font(None, Config.ui.font_size_medium)
        self.font_small = pygame.font.Font(None, Config.ui.font_size_small)
        
        # Статистика с анимацией
        self.stats = {
            'fps': AnimatedValue(0),
            'objects_detected': AnimatedValue(0),
            'object_counts': {}
        }
        
        # Для плавных переходов панелей
        self.panel_alpha = AnimatedValue(0)
        self.show_time = time.time()
        
        print("[UIRenderer] ✅ Инициализация завершена")
    
    def _get_category_color(self, category: str) -> Tuple[int, int, int]:
        """Цвет bbox в зависимости от категории"""
        color_map = {
            'person': Config.ui.bbox_person_color,
            'electronics': Config.ui.bbox_electronics_color,
            'transport': Config.ui.bbox_transport_color,
            'accessories': Config.ui.bbox_accessories_color,
            'other': Config.ui.bbox_other_color
        }
        return color_map.get(category, Config.ui.bbox_other_color)
    
    def draw_bbox(self, surface: pygame.Surface, bbox: tuple, 
                  color: tuple, label: str, confidence: float):
        """
        Рисуем КРАСИВЫЙ bounding box с градиентом и тенью
        """
        x1, y1, x2, y2 = bbox
        
        # Масштабируем координаты
        scale_x = self.width / Config.camera.width
        scale_y = self.height / Config.camera.height
        
        x1 = int(x1 * scale_x)
        y1 = int(y1 * scale_y)
        x2 = int(x2 * scale_x)
        y2 = int(y2 * scale_y)
        
        width = x2 - x1
        height = y2 - y1
        
        # Тень для глубины
        shadow_offset = 4
        shadow_rect = pygame.Rect(x1 + shadow_offset, y1 + shadow_offset, width, height)
        shadow_surface = pygame.Surface((width, height), pygame.SRCALPHA)
        shadow_surface.fill((0, 0, 0, 40))
        surface.blit(shadow_surface, shadow_rect.topleft)
        
        # Главный bbox с углами
        thickness = Config.ui.bbox_thickness
        corner_length = 20
        
        # Верхние углы
        pygame.draw.line(surface, color, (x1, y1), (x1 + corner_length, y1), thickness)
        pygame.draw.line(surface, color, (x1, y1), (x1, y1 + corner_length), thickness)
        pygame.draw.line(surface, color, (x2, y1), (x2 - corner_length, y1), thickness)
        pygame.draw.line(surface, color, (x2, y1), (x2, y1 + corner_length), thickness)
        
        # Нижние углы
        pygame.draw.line(surface, color, (x1, y2), (x1 + corner_length, y2), thickness)
        pygame.draw.line(surface, color, (x1, y2), (x1, y2 - corner_length), thickness)
        pygame.draw.line(surface, color, (x2, y2), (x2 - corner_length, y2), thickness)
        pygame.draw.line(surface, color, (x2, y2), (x2, y2 - corner_length), thickness)
        
        # Лейбл с красивым фоном
        label_text = f"{label.upper()} {confidence:.0%}"
        text_surface = self.font_medium.render(label_text, True, (255, 255, 255))
        text_rect = text_surface.get_rect()
        
        # Позиция над bbox
        label_padding = 10
        label_bg_width = text_rect.width + label_padding * 2
        label_bg_height = text_rect.height + label_padding
        
        label_x = x1
        label_y = y1 - label_bg_height - 5
        
        # Если выходит за верхнюю границу - рисуем внутри
        if label_y < 0:
            label_y = y1 + 5
        
        # Фон лейбла с градиентом
        label_bg = pygame.Surface((label_bg_width, label_bg_height), pygame.SRCALPHA)
        
        # Градиент от цвета к полупрозрачному
        for i in range(label_bg_height):
            alpha = int(220 - (i / label_bg_height) * 50)
            gradient_color = (*color, alpha)
            pygame.draw.line(label_bg, gradient_color, 
                           (0, i), (label_bg_width, i))
        
        surface.blit(label_bg, (label_x, label_y))
        
        # Текст лейбла
        surface.blit(text_surface, (label_x + label_padding, label_y + label_padding // 2))
    
    def draw_objects(self, surface: pygame.Surface, objects: List[DetectionResult]):
        """
        Рисуем все обнаруженные объекты
        """
        for obj in objects:
            color = self._get_category_color(obj.category)
            self.draw_bbox(surface, obj.bbox, color, obj.class_name, obj.confidence)
    
    def draw_stats_panel(self, surface: pygame.Surface):
        """
        КРАСИВАЯ панель статистики (правый верхний угол)
        """
        panel_x = self.width - Config.ui.stats_panel_width - 30
        panel_y = 30
        panel_w = Config.ui.stats_panel_width
        panel_h = Config.ui.stats_panel_height
        
        # Фон с закругленными углами
        panel_surface = pygame.Surface((panel_w, panel_h), pygame.SRCALPHA)
        pygame.draw.rect(panel_surface, Config.ui.panel_bg, 
                        (0, 0, panel_w, panel_h), border_radius=15)
        
        # Граница
        pygame.draw.rect(panel_surface, Config.ui.panel_border_color, 
                        (0, 0, panel_w, panel_h), 2, border_radius=15)
        
        surface.blit(panel_surface, (panel_x, panel_y))
        
        # Контент панели
        y_offset = panel_y + 25
        x_padding = panel_x + 25
        
        # Заголовок
        title = self.font_large.render("STATISTICS", True, Config.ui.text_accent)
        surface.blit(title, (x_padding, y_offset))
        y_offset += 50
        
        # Линия разделитель
        pygame.draw.line(surface, Config.ui.panel_border_color,
                        (x_padding, y_offset), 
                        (panel_x + panel_w - 25, y_offset), 2)
        y_offset += 20
        
        # FPS с иконкой
        fps_value = int(self.stats['fps'].get())
        fps_color = Config.ui.accent_color if fps_value >= 30 else Config.ui.warning_color
        fps_text = self.font_medium.render(f"FPS:", True, Config.ui.text_secondary)
        fps_value_text = self.font_large.render(f"{fps_value}", True, fps_color)
        
        surface.blit(fps_text, (x_padding, y_offset))
        surface.blit(fps_value_text, (x_padding + 100, y_offset - 5))
        y_offset += 50
        
        # Objects detected
        objects_count = int(self.stats['objects_detected'].get())
        obj_text = self.font_medium.render(f"Detected:", True, Config.ui.text_secondary)
        obj_value = self.font_large.render(f"{objects_count}", True, Config.ui.secondary_accent)
        
        surface.blit(obj_text, (x_padding, y_offset))
        surface.blit(obj_value, (x_padding + 100, y_offset - 5))
        y_offset += 60
        
        # Breakdown по категориям
        if self.stats['object_counts']:
            breakdown_title = self.font_small.render("BREAKDOWN:", True, Config.ui.text_secondary)
            surface.blit(breakdown_title, (x_padding, y_offset))
            y_offset += 30
            
            # Сортируем по количеству
            sorted_counts = sorted(self.stats['object_counts'].items(), 
                                  key=lambda x: x[1], reverse=True)
            
            for obj_class, count in sorted_counts[:6]:  # Топ 6
                # Прогресс бар
                max_count = max(self.stats['object_counts'].values())
                bar_width = int((count / max_count) * 200)
                
                # Фон бара
                pygame.draw.rect(surface, (40, 40, 50, 150),
                               (x_padding, y_offset, 200, 20), border_radius=3)
                
                # Заполненная часть
                category_color = self._get_category_color(
                    DetectionResult((0,0,0,0), obj_class, 0).category
                )
                pygame.draw.rect(surface, (*category_color, 180),
                               (x_padding, y_offset, bar_width, 20), border_radius=3)
                
                # Текст
                count_text = self.font_small.render(f"{obj_class}: {count}", 
                                                    True, Config.ui.text_primary)
                surface.blit(count_text, (x_padding + 210, y_offset))
                
                y_offset += 28
    
    def draw_header(self, surface: pygame.Surface):
        """
        Минималистичный заголовок (левый верхний угол)
        """
        header_w = 650
        header_h = 80
        header_x = 30
        header_y = 30
        
        # Фон
        header_bg = pygame.Surface((header_w, header_h), pygame.SRCALPHA)
        pygame.draw.rect(header_bg, Config.ui.panel_bg,
                        (0, 0, header_w, header_h), border_radius=15)
        pygame.draw.rect(header_bg, Config.ui.panel_border_color,
                        (0, 0, header_w, header_h), 2, border_radius=15)
        surface.blit(header_bg, (header_x, header_y))
        
        # Текст
        title = self.font_title.render("OBJECT DETECTION", True, Config.ui.text_primary)
        surface.blit(title, (header_x + 20, header_y + 20))
        
        # Подзаголовок
        subtitle = self.font_small.render("Real-time AI Vision System", 
                                         True, Config.ui.text_secondary)
        surface.blit(subtitle, (header_x + 22, header_y + 50))
    
    def draw_legend(self, surface: pygame.Surface):
        """
        Легенда категорий (нижний левый угол)
        """
        legend_x = 30
        legend_y = self.height - 200
        
        categories = [
            ("Person", Config.ui.bbox_person_color),
            ("Electronics", Config.ui.bbox_electronics_color),
            ("Transport", Config.ui.bbox_transport_color),
            ("Accessories", Config.ui.bbox_accessories_color),
            ("Other", Config.ui.bbox_other_color)
        ]
        
        for i, (name, color) in enumerate(categories):
            y_pos = legend_y + i * 35
            
            # Цветной квадрат
            pygame.draw.rect(surface, color, (legend_x, y_pos, 25, 25), border_radius=5)
            pygame.draw.rect(surface, (255, 255, 255, 100), 
                           (legend_x, y_pos, 25, 25), 2, border_radius=5)
            
            # Текст
            text = self.font_small.render(name, True, Config.ui.text_primary)
            surface.blit(text, (legend_x + 35, y_pos + 3))
    
    def update_stats(self, fps: int, objects: List[DetectionResult]):
        """
        Обновляем статистику с плавными анимациями
        """
        # Обновляем целевые значения
        self.stats['fps'].set_target(fps)
        self.stats['objects_detected'].set_target(len(objects))
        
        # Подсчитываем объекты по классам
        object_counts = {}
        for obj in objects:
            if obj.class_name in object_counts:
                object_counts[obj.class_name] += 1
            else:
                object_counts[obj.class_name] = 1
        
        self.stats['object_counts'] = object_counts
        
        # Обновляем анимации
        self.stats['fps'].update()
        self.stats['objects_detected'].update()
    
    def render(self, objects: List[DetectionResult], show_stats: bool = True):
        """
        Главный метод рендеринга
        """
        # Объекты
        self.draw_objects(self.screen, objects)
        
        # UI элементы
        self.draw_header(self.screen)
        
        if show_stats:
            self.draw_stats_panel(self.screen)
        
        self.draw_legend(self.screen)