import pygame
import os
import sys
import json
from transitions import slide_transition
from settings import SCREEN_WIDTH, SCREEN_HEIGHT

from buttons import draw_arrow_button, create_buttons
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
left_btn, right_btn = create_buttons()

class Scene4:
    def __init__(self, screen, inventory):
        self.screen = screen
        self.inventory = inventory
        self.views = ['palace', 'stage']
        self.current_view = 'palace'
        self.items_collected = {view: [] for view in self.views}
        
        # 載入物品描述
        with open('json/scene4_1.json', 'r', encoding='utf-8') as f:
            self.item_descriptions = json.load(f)
        
        # 物品屬性設定 (名稱、寬度、高度)
        self.item_properties = {
            'palace': {'name': '香爐', 'width': 612*1.9, 'height': 408*1.9},
            'incense': {'name': '香', 'width': 1415//3.5, 'height': 1138//3.5},
            'stage': {'name': '戲台', 'width': 612*1.93, 'height': 408*1.93},
        }
        
        # 文字顯示相關變數
        self.current_description = ""
        self.current_item_to_show = 'palace'  # 初始顯示香爐描述
        
        # old_paper 相關變數
        self.show_old_paper = False
        self.old_paper_img = None
        self.old_paper_rect = None
        
        self.load_resources()
        self.setup_items()
        
        # 初始化UI按鈕
        self.back_btn = pygame.Rect(30, 30, 80, 40)
        self.left_btn = pygame.Rect(50, SCREEN_HEIGHT//2 - 25, 50, 50)
        self.right_btn = pygame.Rect(SCREEN_WIDTH - 100, SCREEN_HEIGHT//2 - 25, 50, 50)
        
        # 轉場動畫標誌
        self.is_transitioning = False
        
    def load_resources(self):
        """載入所有資源並根據設定調整大小"""
        self.backgrounds = {}
        self.original_items = {}
        
        # 載入背景圖片
        for view in self.views:
            path = os.path.join('images', f'background_{view}.png')
            original_img = pygame.image.load(path)
            
            # 保持比例縮放背景
            img_width, img_height = original_img.get_size()
            scale = max(SCREEN_WIDTH/img_width, SCREEN_HEIGHT/img_height)
            new_width = int(img_width * scale)
            new_height = int(img_height * scale)
            
            scaled_img = pygame.transform.scale(original_img, (new_width, new_height))
            x = (SCREEN_WIDTH - new_width) // 2
            y = (SCREEN_HEIGHT - new_height) // 2
            
            self.backgrounds[view] = (scaled_img, (x, y))
        
        # 載入物品圖片並根據設定調整大小
        for item_id, props in self.item_properties.items():
            path = os.path.join('images', f'{item_id}.png')
            original_img = pygame.image.load(path)
            self.original_items[item_id] = pygame.transform.scale(
                original_img, 
                (props['width'], props['height'])
            )
        
        # 載入 old_paper 圖片
        old_paper_path = os.path.join('images', 'old_paper.png')
        if os.path.exists(old_paper_path):
            old_paper_img = pygame.image.load(old_paper_path)
            paper_width = int(SCREEN_WIDTH * 0.8)
            paper_height = int(SCREEN_HEIGHT * 0.8)
            self.old_paper_img = pygame.transform.scale(old_paper_img, (paper_width, paper_height))
            self.old_paper_rect = self.old_paper_img.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
        
        # 載入字型
        self.font = pygame.font.Font("msjh.ttc", 20)
    
    def setup_items(self):
        """設定物品初始位置和狀態"""
        bg_x, bg_y = self.backgrounds['palace'][1]  # 使用背景的偏移量
        
        self.item_positions = {
            'palace': [
                {'id': 'palace', 'pos': (10,-50), 'collected': False, 'touch': True}
            ],
            'stage': [
                {'id': 'incense', 'pos': (280,406+50), 'collected': False, 'touch': False},
                {'id': 'stage', 'pos': (18,-350), 'collected': False, 'touch': False}
            ],
        }
        
        # 物品收集順序
        self.item_order = ['palace', 'incense', 'stage']
        self.current_item_to_show = self.item_order[0]  # 初始顯示第一個物品的描述
    
    def update_item_touch_status(self):
        """更新物品的可點擊狀態"""
        for i in range(len(self.item_order)):
            current_item_id = self.item_order[i]
            
            for view in self.item_positions.values():
                for item in view:
                    if item['id'] == current_item_id:
                        if i == 0:  # 第一個物品總是可點擊
                            item['touch'] = True
                            break
                        
                        prev_item_id = self.item_order[i-1]
                        prev_item_collected = False
                        
                        # 檢查前一個物品是否已收集
                        for prev_view in self.item_positions.values():
                            for prev_item in prev_view:
                                if prev_item['id'] == prev_item_id:
                                    prev_item_collected = prev_item['collected']
                                    break
                            if prev_item_collected:
                                break
                        
                        item['touch'] = prev_item_collected
                        
                        # 如果前一個物品已收集，則更新當前要顯示的描述
                        if prev_item_collected and not item['collected']:
                            self.current_item_to_show = current_item_id
                        break
    
    def draw_description(self):
        """繪製當前應該顯示的物品描述"""
        # 如果所有物品都已收集，則不顯示描述
        if all(item['collected'] for view in self.item_positions.values() for item in view):
            return
        
        # 獲取當前應該顯示的物品描述
        description = self.item_descriptions.get(self.current_item_to_show, "")
        
        font_size = 20
        line_spacing = 10
        padding = 70
        
        font = pygame.font.Font("標楷體.ttf", font_size)
        lines = description.split('\n')
        
        line_height = font.get_linesize()
        text_height = len(lines) * (line_height + line_spacing) + 2 * 20
        text_width = max(font.size(line)[0] for line in lines) + 2 * 20 if lines else 0
        
        max_width = SCREEN_WIDTH // 3  # 限制最大寬度
        text_width = min(text_width, max_width)
        
        # 計算左上角位置
        desc_rect = pygame.Rect(
            padding,
            padding,
            text_width,
            text_height
        )
        
        # 繪製背景
        pygame.draw.rect(self.screen, (0, 0, 0, 180), desc_rect, border_radius=10)
        pygame.draw.rect(self.screen, (255, 255, 255), desc_rect, 2, border_radius=10)
        
        # 繪製文字
        y_pos = desc_rect.y + 10
        for line in lines:
            if line.strip():
                text_surface = font.render(line, True, (255, 255, 255))
                self.screen.blit(text_surface, (desc_rect.x + 10, y_pos))
            y_pos += line_height + line_spacing
    
    def switch_view(self, direction):
        """切換視角（帶滑動動畫）"""
        if self.is_transitioning:
            return
            
        self.is_transitioning = True
        
        current_idx = self.views.index(self.current_view)
        new_view = self.views[(current_idx + direction) % len(self.views)]
        
        # 獲取當前和新背景圖
        current_img, current_pos = self.backgrounds[self.current_view]
        new_img, new_pos = self.backgrounds[new_view]
        
        # 創建臨時表面用於動畫
        current_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        new_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        
        # 繪製當前畫面（包括物品）
        current_surface.blit(current_img, current_pos)
        # for item in self.item_positions[self.current_view]:
        #     if not item['collected'] and item['touch']:
        #         item_id = item['id']
        #         current_surface.blit(self.original_items[item_id], item['pos'])
        
        # 繪製新畫面（包括物品）
        new_surface.blit(new_img, new_pos)
        # for item in self.item_positions[new_view]:
        #     if not item['collected'] and item['touch']:
        #         item_id = item['id']
        #         new_surface.blit(self.original_items[item_id], item['pos'])
        
        # 執行轉場動畫
        slide_transition(
            self.screen, 
            current_surface, 
            new_surface, 
            "right" if direction == 1 else "left"
        )
        
        self.current_view = new_view
        self.update_item_touch_status()
        self.is_transitioning = False
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
                return False
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    self.switch_view(-1)
                elif event.key == pygame.K_RIGHT:
                    self.switch_view(1)
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if self.is_transitioning:
                    continue
                    
                mouse_pos = pygame.mouse.get_pos()
                
                # # 檢查返回按鈕
                # if self.back_btn.collidepoint(mouse_pos):
                #     self.inventory.items.clear()
                #     self.inventory.selected_index = -1
                #     return False
                
                # 檢查是否點擊了非物品欄範圍且 old_paper 正在顯示
                if self.show_old_paper:
                    if not self.old_paper_rect.collidepoint(mouse_pos):
                        self.show_old_paper = False
                        self.inventory.selected_index = -1
                    continue
                
                # 檢查方向按鈕
                if self.left_btn.collidepoint(mouse_pos):
                    self.switch_view(-1)
                    continue  # 跳過後續處理
                elif self.right_btn.collidepoint(mouse_pos):
                    self.switch_view(1)
                    continue  # 跳過後續處理
                
                # 處理物品欄點擊
                clicked_inventory = self.inventory.handle_click(mouse_pos)
                
                # 檢查物品點擊
                if self.inventory.selected_index == -1 and not clicked_inventory:
                    for item in self.item_positions[self.current_view]:
                        if not item['collected'] and item['touch']:
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
                                    self.update_item_touch_status()
                                    # 更新當前要顯示的描述
                                    if item_id == self.current_item_to_show:
                                        next_item_index = self.item_order.index(item_id) + 1
                                        if next_item_index < len(self.item_order):
                                            self.current_item_to_show = self.item_order[next_item_index]
                
                # 如果有物品被選取且點擊了非物品欄區域，則顯示 old_paper
                if self.inventory.selected_index != -1 and not clicked_inventory:
                    selected_item_id = self.inventory.item_ids[self.inventory.selected_index]
                    self.show_old_paper = True

        return True
    
    def draw_old_paper(self):
        """繪製 old_paper 和相關內容（包含文字逐字顯示效果）"""
        if not self.show_old_paper or self.old_paper_img is None:
            return
        
        # 繪製半透明背景
        s = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        s.fill((0, 0, 0, 180))
        self.screen.blit(s, (0, 0))
        
        # 繪製 old_paper
        self.screen.blit(self.old_paper_img, self.old_paper_rect)
        
        # 如果有選取的物品，顯示對應的文字和物品圖片
        if self.inventory.selected_index != -1 and self.inventory.selected_index < len(self.inventory.item_ids):
            item_id = self.inventory.item_ids[self.inventory.selected_index]
            
            # 載入物品圖片
            if item_id in self.original_items:
                item_img = self.original_items[item_id]
                item_props = self.item_properties[item_id]
                
                # 計算物品顯示位置（左側1/3區域）
                left_third_rect = pygame.Rect(
                    self.old_paper_rect.right - self.old_paper_rect.width // 3,
                    self.old_paper_rect.bottom - self.old_paper_rect.height // 2,
                    self.old_paper_rect.width // 3,
                    self.old_paper_rect.height // 2
                )
                
                # 計算縮放比例
                original_width = item_props['width']
                original_height = item_props['height']
                
                max_width = left_third_rect.width - 60
                max_height = left_third_rect.height - 60
                
                width_ratio = max_width / original_width
                height_ratio = max_height / original_height
                scale = min(width_ratio, height_ratio)
                
                scaled_width = int(original_width * scale)
                scaled_height = int(original_height * scale)
                
                # 縮放圖片並繪製
                scaled_img = pygame.transform.smoothscale(item_img, (scaled_width, scaled_height))
                item_x = left_third_rect.left
                item_y = left_third_rect.bottom - scaled_height - 30
                self.screen.blit(scaled_img, (item_x, item_y))
            
            # 載入物品描述文字
            if not hasattr(self, 'text_data'):
                try:
                    with open('json/scene4_2.json', 'r', encoding='utf-8') as f:
                        self.text_data = json.load(f)
                except:
                    self.text_data = {}
            
            if item_id in self.text_data:
                # 初始化文字顯示變數
                if not hasattr(self, 'text_display_vars'):
                    self.text_display_vars = {
                        'current_chars': 0,
                        'displayed_text': [],
                        'start_time': pygame.time.get_ticks(),
                        'text_complete': False,
                        'last_item_id': None
                    }
                
                # 如果切換了物品，重置文字顯示狀態
                if self.text_display_vars['last_item_id'] != item_id:
                    self.text_display_vars = {
                        'current_chars': 0,
                        'displayed_text': [],
                        'start_time': pygame.time.get_ticks(),
                        'text_complete': False,
                        'last_item_id': item_id
                    }
                
                # 獲取文字內容
                text_content = self.text_data[item_id]
                lines = text_content.split('\n')
                
                # 初始化顯示文字列表
                if len(self.text_display_vars['displayed_text']) == 0:
                    self.text_display_vars['displayed_text'] = [''] * len(lines)
                
                # 設定文字顯示區域（右側2/3區域）
                text_area_rect = pygame.Rect(
                    self.old_paper_rect.left + 100,
                    self.old_paper_rect.top + 70,
                    self.old_paper_rect.width * 2 // 3 - 40,
                    self.old_paper_rect.height - 80
                )
                
                # 文字顯示參數
                font = pygame.font.Font("標楷體.ttf", 20)  # 使用 標楷體.ttf 字型
                text_color = (101, 67, 33)  # 棕色文字
                line_spacing = 10
                reveal_speed = 10  # 文字顯示速度（毫秒）
                
                # 更新文字顯示（逐字顯示效果）
                current_time = pygame.time.get_ticks()
                if current_time - self.text_display_vars['start_time'] > reveal_speed and not self.text_display_vars['text_complete']:
                    self.text_display_vars['start_time'] = current_time
                    
                    # 計算總字符數
                    total_chars = sum(len(line) for line in lines)
                    
                    # 如果還有字符未顯示，逐字增加
                    if self.text_display_vars['current_chars'] < total_chars:
                        for i in range(len(lines)):
                            if len(self.text_display_vars['displayed_text'][i]) < len(lines[i]):
                                self.text_display_vars['displayed_text'][i] = lines[i][:len(self.text_display_vars['displayed_text'][i]) + 1]
                                self.text_display_vars['current_chars'] += 1
                                break
                    else:
                        self.text_display_vars['text_complete'] = True
                
                # 繪製已顯示的文字
                y_pos = text_area_rect.top
                for line in self.text_display_vars['displayed_text']:
                    if line.strip():
                        text_surface = font.render(line, True, text_color)
                        self.screen.blit(text_surface, (text_area_rect.left, y_pos))
                    y_pos += font.get_height() + line_spacing
    
    def draw_ui(self):
        """繪製UI按鈕和提示"""
        # 返回按鈕
        # pygame.draw.rect(self.screen, (200, 50, 50), self.back_btn)
        # font = pygame.font.Font("msjh.ttc", 20)
        # back_text = font.render("返回", True, (255, 255, 255))
        # self.screen.blit(back_text, (self.back_btn.x + 20, self.back_btn.y + 10))
        
        # 左右箭頭按鈕
        draw_arrow_button(screen, left_btn, "left")
        draw_arrow_button(screen, right_btn, "right")
        
        # # 如果所有物品都已收集，顯示提示文字
        # if all(item['collected'] for view in self.item_positions.values() for item in view):
        #     font = pygame.font.Font("msjh.ttc", 30)
        #     text = font.render("點擊返回按鈕繼續", True, (255, 255, 255))
        #     text_rect = text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT - 50))
        #     self.screen.blit(text, text_rect)
    
    def draw(self):
        """繪製場景"""
        self.screen.fill((0, 0, 0))
        
        # 繪製背景
        bg_img, bg_pos = self.backgrounds[self.current_view]
        self.screen.blit(bg_img, bg_pos)
        
        # 繪製物品（未收集且可點擊的）
        # for item in self.item_positions[self.current_view]:
        #     if not item['collected'] and item['touch']:
        #         item_id = item['id']
        #         self.screen.blit(
        #             self.original_items[item_id],
        #             item['pos']
        #         )
        
        # 繪製描述文字
        self.draw_description()
        
        # 繪製UI元素
        self.draw_ui()
        
        # 繪製物品欄
        self.inventory.draw(self.screen)
        
        # 最後繪製 old_paper（確保在最上層）
        self.draw_old_paper()
        
        pygame.display.flip()
    
    def run(self):
        """執行場景"""
        clock = pygame.time.Clock()
        running = True
        
        # 初始更新物品觸碰狀態
        self.update_item_touch_status()
        
        while running:
            running = self.handle_events()
            self.draw()
            clock.tick(60)
        
        return True