import pygame

class ZoomAnimation:
    def __init__(self):
        self.active = False
        self.start_time = 0
        self.duration = 1000  # 2秒 (毫秒)
        self.original_image = None
        self.zoomed_image = None
        self.should_trigger_scene = False
        self.zoom_scale = 1.7  # 放大比例

    def start(self, current_image):
        """啟動放大動畫"""
        self.original_image = current_image.copy()
        
        # 創建放大後的圖片
        original_rect = self.original_image.get_rect()
        zoomed_size = (
            int(original_rect.width * self.zoom_scale), 
            int(original_rect.height * self.zoom_scale)
        )
        self.zoomed_image = pygame.transform.scale(self.original_image, zoomed_size)
        
        self.active = True
        self.start_time = pygame.time.get_ticks()
        self.should_trigger_scene = True

    def update(self, screen, image_position):
        """更新並繪製放大動畫"""
        if not self.active:
            return False
        
        current_time = pygame.time.get_ticks()
        elapsed = current_time - self.start_time
        progress = min(elapsed / self.duration, 1.0)  # 0.0 到 1.0
        
        # 計算當前縮放比例
        current_scale = 1.0 + ((self.zoom_scale - 1.0) * progress)
        
        # 計算當前圖片大小
        original_rect = self.original_image.get_rect()
        current_width = int(original_rect.width * current_scale)
        current_height = int(original_rect.height * current_scale)
        
        # 縮放圖片
        scaled_img = pygame.transform.scale(self.original_image, (current_width, current_height))
        
        # 計算位置 (居中)
        x = image_position[0] - (current_width - original_rect.width) // 2
        y = image_position[1] - (current_height - original_rect.height) // 2
        
        # 繪製放大中的圖片
        screen.blit(scaled_img, (x, y))
        
        # 檢查動畫是否完成
        if progress >= 1.0:
            self.active = False
            return True  # 動畫完成
        
        return False  # 動畫未完成

    def reset(self):
        """重置動畫狀態"""
        self.active = False
        self.should_trigger_scene = False