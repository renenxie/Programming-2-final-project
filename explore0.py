import pygame
import os
import sys
import json
from scene_manager import SceneManager
from video_player import VideoPlayer
from settings import SCREEN_WIDTH, SCREEN_HEIGHT

class Explore0:
    def __init__(self, screen, inventory):
        self.screen = screen
        self.inventory = inventory
        self.views = ['front']
        self.current_view = 'front'
        self.items_collected = {view: [] for view in self.views}
        
        # 載入物品描述
        with open('json/explore0_1.json', 'r', encoding='utf-8') as f:
            self.item_descriptions = json.load(f)
        
        self.item_properties = {
            'stick': {'name': '木架', 'width': 173 * SCREEN_WIDTH / 800, 'height': 341 * SCREEN_HEIGHT / 600},
            'doll': {'name': '燒焦布袋戲偶', 'width': 278 * SCREEN_WIDTH / 800, 'height': 117 * SCREEN_HEIGHT / 600},
            'newspaper': {'name': '報紙', 'width': 227 * SCREEN_WIDTH / 800, 'height': 238 * SCREEN_HEIGHT / 600},
        }
        
        # 文字顯示相關變數
        self.current_description = ""
        self.current_item_to_show = 'stick'  # 初始顯示木棍描述
        self.show_discraption = True
        
        # 報紙點擊相關變數
        self.newspaper_clicked = False
        self.newspaper_timer = 0
        self.newspaper_delay = 180
        
        # 任務視窗相關變數
        self.show_task_window = False
        self.task_completed = False
        self.show_completion_window = False
        
        # 合成相關變數
        self.show_combine_result = False
        self.cancel_click = False
        self.combine_result_timer = 0
        self.combine_result_duration = 180
        
        # old_paper 相關變數
        self.show_old_paper = False
        self.old_paper_img = None
        self.old_paper_rect = None
        
        self.load_resources()
        self.setup_items()
        
        self.interact_areas = {
            'front': pygame.Rect(SCREEN_WIDTH//2 - 100, SCREEN_HEIGHT//2 - 100, 200, 200),
        }

    def load_resources(self):
        """載入所有資源並根據設定調整大小"""
        self.backgrounds = {}
        self.original_items = {}
        
        # 載入背景圖片
        for view in self.views:
            path = os.path.join('images', f'explore0.png')
            original_img = pygame.image.load(path)
            
            img_width, img_height = original_img.get_size()
            scale = max(SCREEN_WIDTH/img_width, SCREEN_HEIGHT/img_height)
            new_width = int(img_width * scale)
            new_height = int(img_height * scale)
            
            scaled_img = pygame.transform.scale(original_img, (new_width, new_height))
            x = (SCREEN_WIDTH - new_width) // 2
            y = (SCREEN_HEIGHT - new_height) // 2
            
            self.backgrounds[view] = (scaled_img, (x, y))
        
        # 載入物品圖片
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
        self.font = pygame.font.Font("標楷體.ttf", 24)

    def setup_items(self):
        """設定物品初始位置和狀態"""
        self.item_positions = {
            'front': [
                {'id': 'stick', 'pos': (SCREEN_WIDTH * 267 // 800, SCREEN_HEIGHT * 100 // 600), 'collected': False, 'touch': False},
                {'id': 'doll', 'pos': (SCREEN_WIDTH * 225 // 800, SCREEN_HEIGHT * 475 // 600), 'collected': False, 'touch': False},
                {'id': 'newspaper', 'pos': (SCREEN_WIDTH * 580 // 800, SCREEN_HEIGHT * 321 // 600), 'collected': False, 'touch': False}
            ],
        }
        
        # 物品收集順序
        self.item_order = ['stick', 'doll', 'newspaper']
        self.current_item_to_show = self.item_order[0]  # 初始顯示第一個物品的描述

    def update_item_touch_status(self):
        """更新物品的可點擊狀態"""
        for i in range(len(self.item_order)):
            current_item_id = self.item_order[i]
            
            for item in self.item_positions[self.current_view]:
                if item['id'] == current_item_id:
                    if i == 0:
                        break
                    
                    prev_item_id = self.item_order[i-1]
                    prev_item_collected = False
                    
                    for prev_item in self.item_positions[self.current_view]:
                        if prev_item['id'] == prev_item_id:
                            prev_item_collected = prev_item['collected']
                            break
                    
                    item['touch'] = prev_item_collected
                    
                    # 如果前一個物品已收集，則更新當前要顯示的描述
                    if prev_item_collected and not item['collected']:
                        self.current_item_to_show = current_item_id
                    break

    def draw_description(self):
        """繪製當前應該顯示的物品描述"""
        # 如果點擊到了報紙碎片
        if self.show_discraption == False:
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
        
        # 計算右上角位置
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
        title_font = pygame.font.Font("標楷體.ttf", 30)
        title_text = title_font.render("任務說明", True, (255, 255, 255))
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH//2, window_y + 40))
        self.screen.blit(title_text, title_rect)
        
        # 繪製任務內容
        content_font = pygame.font.Font("標楷體.ttf", 24)
        task_text = [
            "收集報紙碎片",
            "",
            "遊戲說明:",
            "1. 使用上下左右鍵移動角色",
            "2. 收集所有報紙碎片",
            "3. 避開鬼影"
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
        
        button_font = pygame.font.Font("標楷體.ttf", 24)
        button_text = button_font.render("進入遊戲", True, (255, 255, 255))
        button_text_rect = button_text.get_rect(center=button_rect.center)
        self.screen.blit(button_text, button_text_rect)
        
        return button_rect

    def draw_completion_window(self):
        """繪製任務完成視窗"""
        if not self.show_completion_window:
            return
        
        # 創建半透明背景
        s = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        s.fill((0, 0, 0, 180))
        self.screen.blit(s, (0, 0))
        
        # 視窗大小和位置
        window_width = SCREEN_WIDTH * 0.7
        window_height = SCREEN_HEIGHT * 0.5
        window_x = (SCREEN_WIDTH - window_width) // 2
        window_y = (SCREEN_HEIGHT - window_height) // 2
        
        # 繪製視窗背景
        window_rect = pygame.Rect(window_x, window_y, window_width, window_height)
        pygame.draw.rect(self.screen, (50, 50, 50), window_rect, border_radius=10)
        pygame.draw.rect(self.screen, (200, 200, 200), window_rect, 2, border_radius=10)
        
        # 繪製標題
        title_font = pygame.font.Font("標楷體.ttf", 30)
        title_text = title_font.render("任務完成", True, (255, 255, 255))
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH//2, window_y + 40))
        self.screen.blit(title_text, title_rect)
        
        # 繪製內容
        content_font = pygame.font.Font("標楷體.ttf", 24)
        content_text = [
            "恭喜收集所有的報紙碎片！",
            "是否要合成報紙？"
        ]
        
        y_offset = window_y + 80
        for line in content_text:
            text_surface = content_font.render(line, True, (255, 255, 255))
            text_rect = text_surface.get_rect(center=(SCREEN_WIDTH//2, y_offset))
            self.screen.blit(text_surface, text_rect)
            y_offset += 40
        
        # 繪製按鈕
        button_width = 150
        button_height = 50
        
        # 合成按鈕
        combine_button_rect = pygame.Rect(
            SCREEN_WIDTH//2 - button_width - 20,
            window_y + window_height - 80,
            button_width,
            button_height
        )
        pygame.draw.rect(self.screen, (70, 70, 70), combine_button_rect, border_radius=5)
        pygame.draw.rect(self.screen, (200, 200, 200), combine_button_rect, 2, border_radius=5)
        
        button_font = pygame.font.Font("標楷體.ttf", 24)
        combine_text = button_font.render("合成", True, (255, 255, 255))
        combine_text_rect = combine_text.get_rect(center=combine_button_rect.center)
        self.screen.blit(combine_text, combine_text_rect)
        
        # 取消按鈕
        cancel_button_rect = pygame.Rect(
            SCREEN_WIDTH//2 + 20,
            window_y + window_height - 80,
            button_width,
            button_height
        )
        pygame.draw.rect(self.screen, (70, 70, 70), cancel_button_rect, border_radius=5)
        pygame.draw.rect(self.screen, (200, 200, 200), cancel_button_rect, 2, border_radius=5)
        
        cancel_text = button_font.render("取消", True, (255, 255, 255))
        cancel_text_rect = cancel_text.get_rect(center=cancel_button_rect.center)
        self.screen.blit(cancel_text, cancel_text_rect)
        
        return combine_button_rect, cancel_button_rect

    def show_explore0_3_content(self):
        """使用 SceneManager 執行 explore0_3.json 的場景"""
        def scene_callback():
            """場景結束後的回調函數"""
            # 將報紙加入物品欄
            # for item in self.item_positions[self.current_view]:
            #     if item['id'] == 'newspaper' and not item['collected']:
            #         if self.inventory.add_item(
            #             self.original_items['newspaper'],
            #             'newspaper',
            #             self.item_properties['newspaper']['name']
            #         ):
            #             item['collected'] = True
            #             self.update_item_touch_status()
            
            # 顯示合成結果
            self.show_combine_result = True
            self.combine_result_timer = self.combine_result_duration

        # 設置場景管理器
        from scenes import load_scene_resources
        screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        font = pygame.font.Font("標楷體.ttf", 18)
        scene_manager = SceneManager(screen, font)
        
        # 獲取當前視角對應的所有場景資源
        scenes = [
            {"scene": "explore0_3.json"},
            {"scene": "explore0_4.json"},
        ]
        
        # 創建場景序列
        scene_sequence = []
        for scene_data in scenes:
            scene_sequence.append(
                lambda scene=scene_data["scene"]: 
                load_scene_resources(scene)
            )
        
        # 執行場景序列
        scene_manager.run_scenes(
            scene_sequence,
            callback=scene_callback
        )
        
    def handle_events(self):
        # 檢查是否已經顯示過遮罩
        if not hasattr(self, 'mask_shown'):
            self.mask_shown = False
            self.mask_start_time = 0
            self.show_mask = True  # 控制是否顯示遮罩
            
        # 處理遮罩計時
        if self.show_mask and not self.mask_shown:
            self.mask_start_time = pygame.time.get_ticks()
            self.mask_shown = True
        
        # 如果遮罩正在顯示且超過2秒，則關閉遮罩並啟用木棍
        if self.mask_shown and self.show_mask:
            current_time = pygame.time.get_ticks()
            if current_time - self.mask_start_time >= 2000:  # 2秒 = 2000毫秒
                self.show_mask = False
                # 啟用木棍的觸碰狀態
                for item in self.item_positions[self.current_view]:
                    if item['id'] == 'stick':
                        item['touch'] = True
                # 更新物品觸碰狀態
                self.update_item_touch_status()

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
                
                # 檢查是否所有物品都已收集
                # all_collected = all(item['collected'] for item in self.item_positions[self.current_view])
                
                # 如果所有物品都已收集且點擊了中間區域
                # if all_collected and self.interact_areas[self.current_view].collidepoint(mouse_pos):
                #     self.inventory.clear()
                #     return False
                
                # 如果取消物品合成且點擊了中間區域
                if self.cancel_click and self.interact_areas[self.current_view].collidepoint(mouse_pos):
                    self.inventory.clear()
                    return False
                
                # 處理合成結果視窗
                if self.show_combine_result:
                    self.show_combine_result = False
                    return True
                
                # 處理任務完成視窗中的按鈕點擊
                if self.show_completion_window:
                    combine_rect, cancel_rect = self.draw_completion_window()
                    
                    if combine_rect.collidepoint(mouse_pos):
                        self.show_completion_window = False
                        # 使用 SceneManager 執行 explore0_3.json 的內容
                        self.inventory.clear()
                        self.show_explore0_3_content()
                        return False
                    
                    elif cancel_rect.collidepoint(mouse_pos):
                        self.cancel_click = True
                        self.show_completion_window = False
                        return True
                
                # 處理任務視窗中的按鈕點擊
                if self.show_task_window:
                    button_rect = self.draw_task_window()
                    if button_rect.collidepoint(mouse_pos):
                        self.show_task_window = False
                        # 啟動遊戲
                        from monster_wrangler_class import MonsterWranglerGame
                        MonsterWranglerGame().run()
                        self.task_completed = True  # 假設任務完成
                        
                        # 如果任務完成，顯示完成視窗
                        if self.task_completed:
                            self.show_completion_window = True
                    continue
                
                # 檢查是否點擊了非物品欄範圍且 old_paper 正在顯示
                if self.show_old_paper:
                    if not self.old_paper_rect.collidepoint(mouse_pos):
                        self.show_old_paper = False
                        self.inventory.selected_index = -1
                    continue
                
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
                                if item_id == 'newspaper' and not self.task_completed:
                                    # 顯示任務視窗而不是直接收集報紙
                                    self.show_task_window = True
                                    self.show_discraption = False
                                else:
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
                    selected_item = self.inventory.items[self.inventory.selected_index]
                    self.show_old_paper = True

        return True

    def update(self):
        """更新遊戲狀態"""
        if self.show_combine_result:
            self.combine_result_timer -= 1
            if self.combine_result_timer <= 0:
                self.show_combine_result = False

    def draw(self):
        """繪製場景"""
        self.screen.fill((0, 0, 0))
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
            font = pygame.font.Font("標楷體.ttf", 30)
            text = font.render("請根據提示詞，找到對應的物件", True, (255, 255, 255))
            text_rect = text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
            self.screen.blit(text, text_rect)
        else:
            # 繪製物品欄
            self.inventory.draw(self.screen)
            
            # 繪製當前應該顯示的物品描述
            self.draw_description()
            
            # 繪製 old_paper (如果有顯示)
            if self.show_old_paper and self.old_paper_img is not None:
                s = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
                s.fill((0, 0, 0, 180))
                self.screen.blit(s, (0, 0))
                self.screen.blit(self.old_paper_img, self.old_paper_rect)
                
                if self.inventory.selected_index != -1:
                    if hasattr(self.inventory, 'selected_index') and self.inventory.selected_index < len(self.item_order):
                        item_id = self.item_order[self.inventory.selected_index]
                    
                        if item_id in self.original_items:
                            item_img = self.original_items[item_id]
                            item_props = self.item_properties[item_id]
                            
                            left_third_rect = pygame.Rect(
                                self.old_paper_rect.right - self.old_paper_rect.width // 3,
                                self.old_paper_rect.bottom - self.old_paper_rect.height // 2,
                                self.old_paper_rect.width // 3,
                                self.old_paper_rect.height // 2
                            )
                            
                            original_width = item_props['width']
                            original_height = item_props['height']
                            
                            max_width = left_third_rect.width - 60
                            max_height = left_third_rect.height - 60
                            
                            width_ratio = max_width / original_width
                            height_ratio = max_height / original_height
                            scale = min(width_ratio, height_ratio)
                            
                            scaled_width = int(original_width * scale)
                            scaled_height = int(original_height * scale)
                            
                            scaled_img = pygame.transform.smoothscale(item_img, (scaled_width, scaled_height))
                            
                            item_x = left_third_rect.left
                            item_y = left_third_rect.bottom - scaled_height - 30
                            
                            self.screen.blit(scaled_img, (item_x, item_y))
                        
                        if not hasattr(self, 'text_data'):
                            try:
                                with open('json/explore0_2.json', 'r', encoding='utf-8') as f:
                                    self.text_data = json.load(f)
                            except:
                                self.text_data = {}
                        
                        if item_id in self.text_data:
                            if not hasattr(self, 'text_display_vars'):
                                self.text_display_vars = {
                                    'current_chars': 0,
                                    'displayed_text': [],
                                    'start_time': pygame.time.get_ticks(),
                                    'text_complete': False
                                }
                            
                            if not hasattr(self, 'last_item_id') or self.last_item_id != item_id:
                                self.last_item_id = item_id
                                self.text_display_vars = {
                                    'current_chars': 0,
                                    'displayed_text': [],
                                    'start_time': pygame.time.get_ticks(),
                                    'text_complete': False
                                }
                            
                            text_content = self.text_data[item_id]
                            lines = text_content.split('\n')
                            
                            if len(self.text_display_vars['displayed_text']) == 0:
                                self.text_display_vars['displayed_text'] = [''] * len(lines)
                            
                            right_two_thirds_rect = pygame.Rect(
                                self.old_paper_rect.left + 100,
                                self.old_paper_rect.top + 70,
                                self.old_paper_rect.width * 2 // 3 - 40,
                                self.old_paper_rect.height - 80
                            )
                            
                            font = pygame.font.Font("標楷體.ttf", 20)
                            text_color = (101, 67, 33)
                            line_spacing = 10
                            reveal_speed = 30
                            
                            current_time = pygame.time.get_ticks()
                            if current_time - self.text_display_vars['start_time'] > reveal_speed and not self.text_display_vars['text_complete']:
                                self.text_display_vars['start_time'] = current_time
                                
                                total_chars = sum(len(line) for line in lines)
                                if self.text_display_vars['current_chars'] < total_chars:
                                    for i in range(len(lines)):
                                        if len(self.text_display_vars['displayed_text'][i]) < len(lines[i]):
                                            self.text_display_vars['displayed_text'][i] = lines[i][:len(self.text_display_vars['displayed_text'][i]) + 1]
                                            self.text_display_vars['current_chars'] += 1
                                            break
                                else:
                                    self.text_display_vars['text_complete'] = True
                            
                            y_pos = right_two_thirds_rect.top
                            for line in self.text_display_vars['displayed_text']:
                                if line.strip():
                                    text_surface = font.render(line, True, text_color)
                                    self.screen.blit(text_surface, (right_two_thirds_rect.left, y_pos))
                                y_pos += font.get_height() + line_spacing
        
        # 繪製任務視窗
        if self.show_task_window:
            self.draw_task_window()
        
        # 繪製任務完成視窗
        if self.show_completion_window:
            self.draw_completion_window()
        
        # # 繪製合成結果
        # if self.show_combine_result:
        #     # 創建半透明背景
        #     s = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        #     s.fill((0, 0, 0, 180))
        #     self.screen.blit(s, (0, 0))
            
        #     # 視窗大小和位置
        #     window_width = SCREEN_WIDTH * 0.7
        #     window_height = SCREEN_HEIGHT * 0.5
        #     window_x = (SCREEN_WIDTH - window_width) // 2
        #     window_y = (SCREEN_HEIGHT - window_height) // 2
            
        #     # 繪製視窗背景
        #     window_rect = pygame.Rect(window_x, window_y, window_width, window_height)
        #     pygame.draw.rect(self.screen, (50, 50, 50), window_rect, border_radius=10)
        #     pygame.draw.rect(self.screen, (200, 200, 200), window_rect, 2, border_radius=10)
            
        #     # 繪製標題
        #     title_font = pygame.font.Font("標楷體.ttf", 30)
        #     title_text = title_font.render("合成完成", True, (255, 255, 255))
        #     title_rect = title_text.get_rect(center=(SCREEN_WIDTH//2, window_y + 40))
        #     self.screen.blit(title_text, title_rect)
            
        #     # 繪製內容
        #     content_font = pygame.font.Font("標楷體.ttf", 24)
        #     content_text = [
        #         "報紙已成功合成！",
        #         "已將完整的報紙加入物品欄"
        #     ]
            
        #     y_offset = window_y + 80
        #     for line in content_text:
        #         text_surface = content_font.render(line, True, (255, 255, 255))
        #         text_rect = text_surface.get_rect(center=(SCREEN_WIDTH//2, y_offset))
        #         self.screen.blit(text_surface, text_rect)
        #         y_offset += 40
        
        # 如果所有物品都已收集，顯示提示文字
        # if all(item['collected'] for item in self.item_positions[self.current_view]):
        #     font = pygame.font.Font("標楷體.ttf", 30)
        #     text = font.render("點擊中間區域繼續", True, (255, 255, 255))
        #     text_rect = text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT - 50))
        #     self.screen.blit(text, text_rect)

        # 如果取消合成，則顯示提示文字
        if self.cancel_click:
            font = pygame.font.Font("標楷體.ttf", 30)
            text = font.render("點擊中間區域繼續", True, (255, 255, 255))
            text_rect = text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT - 50))
            self.screen.blit(text, text_rect)
        
        pygame.display.flip()
    
    def run(self):
        """執行場景"""
        clock = pygame.time.Clock()
        running = True
        
        while running:
            running = self.handle_events()
            self.update()
            self.draw()
            clock.tick(60)
        
        return True