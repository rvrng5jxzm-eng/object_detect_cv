"""
Main Application - Минималистичная версия для скорости
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
    """Быстрое приложение"""
    
    def __init__(self):
        print("=" * 52)
        print(" NEURAL VISION SYSTEM - INITIALIZING ".center(52))
        print("=" * 52)
        Config.print_summary()
        
        pygame.init()
        self.screen = pygame.display.set_mode((Config.window.width, Config.window.height))
        pygame.display.set_caption(Config.window.title)
        
        self.camera = CameraHandler()
        self.detector = DetectionEngine()
        self.ui = UIRenderer(self.screen)
        
        self.running = True
        self.paused = False
        
        self.clock = pygame.time.Clock()
        self.fps = 0
        self.frame_count = 0
        self.last_fps_time = time.time()
        
        self.current_objects = []
        
        print("\n✅ SYSTEM READY")
        print("CONTROLS: SPACE=pause | ESC=exit\n")
    
    def process_frame(self):
        """Обработка кадра"""
        if not self.camera.read_frame():
            return
        
        frame = self.camera.get_frame()
        
        if not self.paused:
            self.current_objects = self.detector.detect_objects(frame)
        
        self.ui.update_stats(self.fps, self.current_objects)
    
    def render_frame(self):
        """Рендеринг"""
        frame_rgb = self.camera.get_frame_rgb()
        if frame_rgb is None:
            return
        
        # Масштабируем
        frame_resized = cv2.resize(frame_rgb, (Config.window.width, Config.window.height))
        
        # В pygame surface
        frame_surface = pygame.surfarray.make_surface(np.transpose(frame_resized, (1, 0, 2)))
        
        # Фон
        self.screen.blit(frame_surface, (0, 0))
        
        # UI поверх (БЕЗ show_stats параметра!)
        self.ui.render(self.current_objects)
        
        # Пауза
        if self.paused:
            pause_text = self.ui.font_large.render("[PAUSED]", True, Config.ui.warning_color)
            rect = pause_text.get_rect(center=(Config.window.width // 2, 50))
            self.screen.blit(pause_text, rect)
        
        pygame.display.flip()
    
    def handle_events(self):
        """События"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT or \
               (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                self.running = False
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    self.paused = not self.paused
                    print(f"{'[PAUSED]' if self.paused else '[RUNNING]'}")
    
    def update_fps(self):
        """FPS"""
        self.frame_count += 1
        current_time = time.time()
        
        if current_time - self.last_fps_time >= 1.0:
            self.fps = self.frame_count
            self.frame_count = 0
            self.last_fps_time = current_time
    
    def run(self):
        """Главный цикл"""
        print("\n▶️  STARTING MAIN LOOP...\n")
        
        while self.running:
            self.handle_events()
            self.process_frame()
            self.render_frame()
            self.update_fps()
            self.clock.tick(Config.window.fps_target)
        
        self.cleanup()
    
    def cleanup(self):
        """Очистка"""
        print("\n🧹 Cleanup...")
        self.camera.release()
        pygame.quit()
        print("✅ Done")


def main():
    try:
        app = CVDetectionApp()
        app.run()
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()