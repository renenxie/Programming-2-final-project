import pygame
import os
import sys
from settings import SCREEN_WIDTH, SCREEN_HEIGHT

class Scene2:
    def __init__(self, screen, inventory):
        self.screen = screen
        self.inventory = inventory
        self.current_view = 'front'
        self.items_collected = {'front': []}
        
        # 物品屬性設定 (名稱、寬度、高度)
        self.item_properties = {
            'item1': {'name': '金球', 'width': 50, 'height': 50},
            'item2': {'name': '魔法書', 'width': 50, 'height': 50},
            'item3': {'name': '寶石', 'width': 50, 'height': 50},
            'item4': {'name': '鑰匙', 'width': 50, 'height': 50}
        }
        
        # 任務視窗相關變數
        self.show_task_window = True
        self.task_completed = False
        self.game_started = False
        
        # 遮罩相關變數
        self.show_mask = True
        self.mask_shown = False
        self.mask_start_time = 0
        
        self.load_resources()
        self.setup_items()
        
        # 初始化UI按鈕
        self.back_btn = pygame.Rect(30, 30, 80, 40)
        
        self.item_use_positions = {
            'item1': [{'direction': 'front', 'x': SCREEN_WIDTH//2, 'y': SCREEN_HEIGHT//2}],
            'item2': [{'direction': 'front', 'x': SCREEN_WIDTH//2, 'y': SCREEN_HEIGHT//2}],
            'item3': [{'direction': 'front', 'x': SCREEN_WIDTH//2, 'y': SCREEN_HEIGHT//2}],
            'item4': [{'direction': 'front', 'x': SCREEN_WIDTH//2, 'y': SCREEN_HEIGHT//2}]
        }
        
    def load_resources(self):
        """載入所有資源並根據設定調整大小"""
        self.backgrounds = {}
        self.original_items = {}
        
        # 載入front背景圖片 - 改為medicine_store.png
        path = os.path.join('images', 'medicine_store.png')
        original_img = pygame.image.load(path)
        
        # 保持比例縮放背景
        img_width, img_height = original_img.get_size()
        scale = max(SCREEN_WIDTH/img_width, SCREEN_HEIGHT/img_height)
        new_width = int(img_width * scale)
        new_height = int(img_height * scale)
        
        scaled_img = pygame.transform.scale(original_img, (new_width, new_height))
        x = (SCREEN_WIDTH - new_width) // 2
        y = (SCREEN_HEIGHT - new_height) // 2
        
        self.backgrounds['front'] = (scaled_img, (x, y))
        
        # 載入物品圖片並根據設定調整大小
        for item_id, props in self.item_properties.items():
            path = os.path.join('images', f'{item_id}.png')
            original_img = pygame.image.load(path)
            self.original_items[item_id] = pygame.transform.scale(
                original_img, 
                (props['width'], props['height'])
            )
    
    def setup_items(self):
        """設定物品初始位置"""
        bg_x, bg_y = self.backgrounds['front'][1]  # 使用背景的偏移量
        
        self.item_positions = {
            'front': [
                {'id': 'item1', 'pos': (bg_x + 150, bg_y + 200), 'collected': False},
                {'id': 'item2', 'pos': (bg_x + 350, bg_y + 180), 'collected': False},
                {'id': 'item3', 'pos': (bg_x + 550, bg_y + 220), 'collected': False},
                {'id': 'item4', 'pos': (bg_x + 250, bg_y + 150), 'collected': False}
            ]
        }
    
    def draw_task_window(self):
        """繪製任務視窗"""
        if not self.show_task_window:
            return
        
        # 創建半透明背景
        s = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        s.fill((0, 0, 0, 180))
        self.screen.blit(s, (0, 0))
        
        # 視窗大小和位置
        window_width = SCREEN_WIDTH * 0.7
        window_height = SCREEN_HEIGHT * 0.6
        window_x = (SCREEN_WIDTH - window_width) // 2
        window_y = (SCREEN_HEIGHT - window_height) // 2
        
        # 繪製視窗背景
        window_rect = pygame.Rect(window_x, window_y, window_width, window_height)
        pygame.draw.rect(self.screen, (50, 50, 50), window_rect, border_radius=10)
        pygame.draw.rect(self.screen, (200, 200, 200), window_rect, 2, border_radius=10)
        
        # 繪製標題
        title_font = pygame.font.Font("msjh.ttc", 30)
        title_text = title_font.render("任務說明", True, (255, 255, 255))
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH//2, window_y + 40))
        self.screen.blit(title_text, title_rect)
        
        # 繪製任務內容
        content_font = pygame.font.Font("msjh.ttc", 24)
        task_text = [
            "藥房探索任務",
            "",
            "遊戲說明:",
            "1. 在藥房中尋找隱藏的物品",
            "2. 收集所有關鍵物品",
            "3. 使用物品解開謎題"
        ]
        
        y_offset = window_y + 80
        for line in task_text:
            text_surface = content_font.render(line, True, (255, 255, 255))
            self.screen.blit(text_surface, (window_x + 30, y_offset))
            y_offset += 35
        
        # 繪製開始遊戲按鈕
        button_rect = pygame.Rect(
            SCREEN_WIDTH//2 - 100,
            window_y + window_height - 80,
            200,
            50
        )
        pygame.draw.rect(self.screen, (70, 70, 70), button_rect, border_radius=5)
        pygame.draw.rect(self.screen, (200, 200, 200), button_rect, 2, border_radius=5)
        
        button_font = pygame.font.Font("msjh.ttc", 24)
        button_text = button_font.render("進入遊戲", True, (255, 255, 255))
        button_text_rect = button_text.get_rect(center=button_rect.center)
        self.screen.blit(button_text, button_text_rect)
        
        return button_rect
    
    def handle_events(self):
        # 處理遮罩計時
        if self.show_mask and not self.mask_shown:
            self.mask_start_time = pygame.time.get_ticks()
            self.mask_shown = True
        
        # 如果遮罩正在顯示且超過2秒，則關閉遮罩
        if self.mask_shown and self.show_mask:
            current_time = pygame.time.get_ticks()
            if current_time - self.mask_start_time >= 2000:  # 2秒 = 2000毫秒
                self.show_mask = False
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
                return False
            
            # 如果遮罩正在顯示，則不處理其他事件
            if self.show_mask:
                return True
                
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                
                # 檢查任務視窗中的按鈕點擊
                if self.show_task_window:
                    button_rect = self.draw_task_window()
                    if button_rect.collidepoint(mouse_pos):
                        self.show_task_window = False
                        from catch_the_clown_class import CatchTheClownGame
                        CatchTheClownGame().run()
                        self.game_started = True
                    continue
                
                # 檢查返回按鈕
                if self.back_btn.collidepoint(mouse_pos):
                    self.inventory.clear()
                    self.inventory.selected_index = -1
                    return False
                
                # 檢查物品點擊 (只有遊戲開始後才能點擊)
                if self.game_started:
                    if self.inventory.selected_index == -1:
                        for item in self.item_positions[self.current_view]:
                            if not item['collected']:
                                item_id = item['id']
                                props = self.item_properties[item_id]
                                item_rect = pygame.Rect(
                                    item['pos'][0], 
                                    item['pos'][1], 
                                    props['width'], 
                                    props['height']
                                )
                                if item_rect.collidepoint(mouse_pos):
                                    if self.inventory.add_item(
                                        self.original_items[item_id],
                                        item_id,
                                        props['name']
                                    ):
                                        item['collected'] = True
                    else:
                        # 檢查物品使用
                        self.try_use_item(mouse_pos)
                    
                    # 處理物品欄點擊
                    self.inventory.handle_click(mouse_pos)
        
        return True

    def try_use_item(self, mouse_pos):
        """嘗試使用選中的物品"""
        if self.inventory.selected_index == -1 or self.inventory.selected_index >= len(self.inventory.items):
            return False

        # 直接從物品欄獲取物品ID
        item_id = self.inventory.item_ids[self.inventory.selected_index]
        
        # 檢查使用位置
        for use_pos in self.item_use_positions.get(item_id, []):
            if (use_pos['direction'] == self.current_view and
                abs(mouse_pos[0] - use_pos['x']) < 30 and
                abs(mouse_pos[1] - use_pos['y']) < 30):
                
                # 使用成功，移除物品和對應ID
                self.inventory.items.pop(self.inventory.selected_index)
                self.inventory.item_ids.pop(self.inventory.selected_index)
                self.inventory.selected_index = -1
                return True
        
        return False
    
    def draw(self):
        """繪製場景（先清空畫面再繪製）"""
        # 清空畫面
        self.screen.fill((0, 0, 0))
        
        # 繪製背景（使用儲存的圖片和位置）
        bg_img, bg_pos = self.backgrounds[self.current_view]
        self.screen.blit(bg_img, bg_pos)
        
        # 繪製遮罩（如果正在顯示）
        if hasattr(self, 'show_mask') and self.show_mask:
            # 創建半透明背景
            s = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            s.fill((0, 0, 0, 180))  # 半透明黑色
            self.screen.blit(s, (0, 0))
            
            # 繪製中央方塊
            mask_width = SCREEN_WIDTH * 0.7
            mask_height = SCREEN_HEIGHT * 0.3
            mask_rect = pygame.Rect(
                (SCREEN_WIDTH - mask_width) // 2,
                (SCREEN_HEIGHT - mask_height) // 2,
                mask_width,
                mask_height
            )
            pygame.draw.rect(self.screen, (50, 50, 50, 230), mask_rect, border_radius=10)
            pygame.draw.rect(self.screen, (200, 200, 200), mask_rect, 2, border_radius=10)
            
            # 繪製文字
            font = pygame.font.Font("msjh.ttc", 30)
            text = font.render("歡迎來到藥房場景", True, (255, 255, 255))
            text_rect = text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
            self.screen.blit(text, text_rect)
        
        # 繪製任務視窗
        if self.show_task_window:
            self.draw_task_window()
        else:
            # 只有遊戲開始後才繪製物品和物品欄
            if self.game_started:
                # 繪製物品（未收集的）
                for item in self.item_positions[self.current_view]:
                    if not item['collected']:
                        self.screen.blit(
                            pygame.transform.scale(self.original_items[item['id']], (50, 50)),
                            item['pos']
                        )
                
                # 繪製物品欄
                self.inventory.draw(self.screen)
        
        # 繪製UI元素
        self.draw_ui()
        
        pygame.display.flip()
    
    def draw_ui(self):
        """繪製UI按鈕和提示"""
        # 返回按鈕 (只有遊戲開始後才顯示)
        if self.game_started:
            self.back_btn = pygame.Rect(30, 30, 80, 40)
            pygame.draw.rect(self.screen, (200, 50, 50), self.back_btn)
            font = pygame.font.Font("msjh.ttc", 20)
            back_text = font.render("返回", True, (255, 255, 255))
            self.screen.blit(back_text, (45, 35))
    
    def run(self):
        """執行場景"""
        clock = pygame.time.Clock()
        running = True
        
        while running:
            running = self.handle_events()
            self.draw()
            clock.tick(60)
        
        return True