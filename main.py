"""
Main Application - Real-time Object Detection (БЕЗ face analysis)
"""
import pygame
import time
import cv2
import numpy as np
from config import Config
from camera_handler import CameraHandler
from detection_engine import DetectionEngine
from ui_renderer import UIRenderer


class CVDetectionApp:
    """
    Главное приложение для real-time детекции объектов
    """
    
    def __init__(self):
        print("=" * 70)
        print("🎥 Real-time Object Detection")
        print("=" * 70)
        Config.print_summary()
        
        # === 1. Pygame initialization ===
        print("\n[1/4] Инициализация Pygame...")
        pygame.init()
        
        self.window_size = (Config.window.width, Config.window.height)
        self.screen = pygame.display.set_mode(self.window_size)
        pygame.display.set_caption(Config.window.title)
        
        print(f"✅ Окно создано: {Config.window.width}x{Config.window.height}")
        
        # === 2. Camera ===
        print("\n[2/4] Инициализация камеры...")
        self.camera = CameraHandler()
        
        # === 3. Detection Engine ===
        print("\n[3/4] Инициализация Detection Engine...")
        self.detector = DetectionEngine()
        
        # === 4. UI Renderer ===
        print("\n[4/4] Инициализация UI Renderer...")
        self.ui = UIRenderer(self.screen)
        
        # === State ===
        self.running = True
        self.paused = False
        self.show_stats = True
        
        # === Timing ===
        self.clock = pygame.time.Clock()
        self.fps = 0
        self.frame_count = 0
        self.last_fps_time = time.time()
        
        # === Detection results ===
        self.current_objects = []
        
        print("\n" + "=" * 70)
        print("✅ Инициализация завершена!")
        print("=" * 70)
        print("\n🎮 Управление:")
        print("  SPACE - Пауза")
        print("  D     - Статистика вкл/выкл")
        print("  ESC   - Выход")
        print("\n🎯 Покажите объекты перед камерой!\n")
    
    def process_frame(self):
        """
        Обрабатываем кадр: детекция объектов
        """
        # Читаем кадр с камеры
        if not self.camera.read_frame():
            return
        
        frame = self.camera.get_frame()
        
        # Детекция (если не на паузе)
        if not self.paused:
            self.current_objects = self.detector.detect_objects(frame)
        
        # Обновляем статистику
        self.ui.update_stats(self.fps, self.current_objects)
    
    def render_frame(self):
        """
        Рендерим кадр с UI
        """
        # Получаем кадр в RGB для pygame
        frame_rgb = self.camera.get_frame_rgb()
        
        if frame_rgb is None:
            return
        
        # Масштабируем кадр до размера окна
        frame_resized = cv2.resize(frame_rgb, self.window_size)
        
        # Конвертируем в pygame surface
        frame_surface = pygame.surfarray.make_surface(
            np.transpose(frame_resized, (1, 0, 2))
        )
        
        # Рисуем кадр как фон
        self.screen.blit(frame_surface, (0, 0))
        
        # Рисуем UI поверх
        self.ui.render(self.current_objects, self.show_stats)
        
        # Если пауза - показываем индикатор
        if self.paused:
            self._draw_pause_indicator()
        
        # Обновляем экран
        pygame.display.flip()
    
    def _draw_pause_indicator(self):
        """Индикатор паузы"""
        pause_bg = pygame.Surface((300, 100), pygame.SRCALPHA)
        pygame.draw.rect(pause_bg, (15, 15, 25, 220), (0, 0, 300, 100), border_radius=15)
        pygame.draw.rect(pause_bg, (80, 80, 100), (0, 0, 300, 100), 2, border_radius=15)
        
        pause_x = (self.window_size[0] - 300) // 2
        pause_y = 100
        
        self.screen.blit(pause_bg, (pause_x, pause_y))
        
        # Текст
        pause_text = self.ui.font_large.render("⏸ PAUSED", True, (255, 255, 0))
        text_rect = pause_text.get_rect(center=(self.window_size[0] // 2, pause_y + 50))
        self.screen.blit(pause_text, text_rect)
    
    def handle_events(self):
        """Обработка событий"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT or \
               (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                self.running = False
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    self.paused = not self.paused
                    print(f"\n{'⏸️  ПАУЗА' if self.paused else '▶️  ЗАПУСК'}")
                
                elif event.key == pygame.K_d:
                    self.show_stats = not self.show_stats
                    print(f"\n📊 Статистика: {'вкл' if self.show_stats else 'выкл'}")
    
    def update_fps(self):
        """Обновление FPS счетчика"""
        self.frame_count += 1
        current_time = time.time()
        
        if current_time - self.last_fps_time >= 1.0:
            self.fps = self.frame_count
            self.frame_count = 0
            self.last_fps_time = current_time
    
    def run(self):
        """Главный цикл приложения"""
        print("\n▶️  Запуск главного цикла...\n")
        
        while self.running:
            # Обработка событий
            self.handle_events()
            
            # Обработка кадра
            self.process_frame()
            
            # Рендеринг
            self.render_frame()
            
            # FPS
            self.update_fps()
            
            # Ограничение FPS
            self.clock.tick(Config.window.fps_target)
        
        # Cleanup
        self.cleanup()
    
    def cleanup(self):
        """Очистка ресурсов"""
        print("\n🧹 Очистка ресурсов...")
        self.camera.release()
        pygame.quit()
        print("✅ Завершено!")


def main():
    """Entry point"""
    try:
        app = CVDetectionApp()
        app.run()
    except Exception as e:
        print(f"\n❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()