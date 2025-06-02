import pygame
import os
import sys
import json
from scene_manager import SceneManager
from video_player import VideoPlayer
from settings import SCREEN_WIDTH, SCREEN_HEIGHT
from zoom_animation import ZoomAnimation

from inventory import Inventory
from scene4 import Scene4
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
inventory = Inventory(SCREEN_WIDTH, SCREEN_HEIGHT)

class Scene3:
    def __init__(self, screen, inventory):
        self.screen = screen
        self.inventory = inventory
        self.views = ['front']
        self.current_view = 'front'
        self.load_resources()
        self.load_text_contents()  # 新增方法載入文字內容
        self.delay_time = 23
        self.show_buttons = True
        self.show_images = False
        self.full_scene_complete = False  # 新增標記變量
        self.chess_sussess = False  # 新增變量來標記下棋成功與否
        self.trychess_times = 0  # 重置下棋成功標記
        
        # 互動設定
        self.can_interact = {'front': True}
        self.interact_areas = {
            'front': pygame.Rect(SCREEN_WIDTH//2 - 100, SCREEN_HEIGHT//2 - 100, 200, 200),
        }

        # 新增標記，用來判斷場景是否已初始化
        self.scene_initialized = False
    
    def load_text_contents(self):
        """從 tree0_1.json 載入文字內容"""
        # Default content in case loading fails
        default_contents = {
            "burner": "這是燃燒器的圖片，看起來已經使用很久了，表面有明顯的燒焦痕跡。",
            "midian": "這是一張古老的地圖，描繪著米甸地區的地理特徵，有些地方已經模糊不清。"
        }
        
        try:
            with open('json/tree0_1.json', 'r', encoding='utf-8') as f:
                self.text_contents = json.load(f)
        except FileNotFoundError:
            print("警告: tree0_1.json 檔案未找到，使用預設文字內容")
            self.text_contents = default_contents
        except json.JSONDecodeError:
            print("錯誤: tree0_1.json 格式不正確，使用預設文字內容")
            self.text_contents = default_contents
        except Exception as e:
            print(f"載入文字內容時發生未知錯誤: {e}")
            self.text_contents = default_contents
    
    def load_resources(self):
        """載入所有需要的資源"""
        self.backgrounds = {}
        
        # 載入背景
        tree2_path = os.path.join('images', 'tree2.png')
        self.tree2_img = pygame.transform.scale(
            pygame.image.load(tree2_path).convert_alpha(),
            (SCREEN_WIDTH, SCREEN_HEIGHT)
        )
        
        # 載入彈出圖片
        try:
            burner_path = os.path.join('images', 'burner.jpg')
            self.burner_img = pygame.transform.scale(
                pygame.image.load(burner_path).convert(),
                (SCREEN_WIDTH//3, SCREEN_HEIGHT//2)
            )
            
            midian_path = os.path.join('images', 'Midian.jpg')
            self.midian_img = pygame.transform.scale(
                pygame.image.load(midian_path).convert(),
                (SCREEN_WIDTH//3, SCREEN_HEIGHT//2)
            )
        except Exception as e:
            print(f"載入圖片失敗: {e}")
            self.create_fallback_images()
        
        self.current_bg = self.tree2_img
        self.backgrounds['front'] = (self.current_bg, (0, 0))
    
    def create_fallback_images(self):
        """建立替代圖片並標註錯誤訊息"""
        self.burner_img = pygame.Surface((SCREEN_WIDTH//3, SCREEN_HEIGHT//2))
        self.burner_img.fill((255, 0, 0))
        font = pygame.font.Font(None, 30)
        text = font.render("burner.jpg 載入失敗", True, (255, 255, 255))
        self.burner_img.blit(text, (10, 10))
        
        self.midian_img = pygame.Surface((SCREEN_WIDTH//3, SCREEN_HEIGHT//2))
        self.midian_img.fill((0, 0, 255))
        text = font.render("Midian.jpg 載入失敗", True, (255, 255, 255))
        self.midian_img.blit(text, (10, 10))
    
    def create_rounded_mask(self, size, radius):
        """建立圓角遮罩"""
        mask = pygame.Surface(size, pygame.SRCALPHA)
        pygame.draw.rect(mask, (255, 255, 255, 255), (0, 0, *size), border_radius=radius)
        return mask

    def draw_image_with_border(self, image, pos, radius=20, border_width=5):
        """繪製帶邊框的圓角圖片"""
        img_width, img_height = image.get_size()
        combined_surface = pygame.Surface(
            (img_width + border_width*2, img_height + border_width*2), 
            pygame.SRCALPHA
        )
        
        pygame.draw.rect(
            combined_surface, 
            (255, 255, 255, 255),
            (0, 0, img_width + border_width*2, img_height + border_width*2),
            border_radius=radius
        )
        
        mask = pygame.Surface((img_width, img_height), pygame.SRCALPHA)
        pygame.draw.rect(
            mask,
            (255, 255, 255, 255),
            (0, 0, img_width, img_height),
            border_radius=radius
        )
        
        processed_img = image.copy()
        if not processed_img.get_flags() & pygame.SRCALPHA:
            processed_img = processed_img.convert_alpha()
        
        processed_img.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
        combined_surface.blit(processed_img, (border_width, border_width))
        self.screen.blit(combined_surface, pos)

    def show_text_dialog(self, text_content):
        """顯示文字對話框（優化中文換行和段落顯示）"""
        if isinstance(text_content, tuple):
            text_content = text_content[0]
        
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        
        dialog_width = SCREEN_WIDTH - 200
        dialog_height = SCREEN_HEIGHT - 200
        dialog_x = 50
        dialog_y = 50
        
        font = pygame.font.Font("標楷體.ttf", 28)  # 確保使用支援中文的字體
        line_height = font.get_linesize() + 5  # 增加行距
        text_color = (255, 255, 255)
        paragraph_spacing = 20  # 段落間距
        
        if not isinstance(text_content, str):
            text_content = str(text_content)
        
        # 中文專用換行處理函數
        def wrap_chinese_text(text, font, max_width):
            lines = []
            current_line = ""
            
            # 特殊處理中文標點符號（不會出現在行首）
            punctuation = "，。、；：！？）」】》…"
            
            for char in text:
                test_line = current_line + char
                # 使用font.size獲取渲染後的寬度
                if font.size(test_line)[0] <= max_width:
                    current_line = test_line
                else:
                    # 如果當前字符是標點且不是行首，則允許放在行尾
                    if char in punctuation and current_line:
                        current_line += char
                        lines.append(current_line)
                        current_line = ""
                    else:
                        lines.append(current_line)
                        current_line = char
            
            if current_line:
                lines.append(current_line)
            
            return lines
        
        # 分割段落（保留空行）
        paragraphs = [p for p in text_content.split('\n\n') if p.strip()]
        current_paragraph = 0
        wrapped_lines = []
        text_complete = False
        
        clock = pygame.time.Clock()
        dialog_running = True
        
        while dialog_running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if text_complete:
                        if current_paragraph < len(paragraphs) - 1:
                            current_paragraph += 1
                            wrapped_lines = []
                            text_complete = False
                        else:
                            dialog_running = False
                    else:
                        text_complete = True
            
            self.screen.blit(self.tree2_img, (0, 0))
            if self.show_buttons:
                self.draw_action_buttons()
            
            self.screen.blit(overlay, (0, 0))
            
            pygame.draw.rect(self.screen, (50, 50, 70), (dialog_x, dialog_y, dialog_width, dialog_height), border_radius=15)
            pygame.draw.rect(self.screen, (100, 100, 120), (dialog_x, dialog_y, dialog_width, dialog_height), 3, border_radius=15)
            
            text_area = pygame.Rect(dialog_x + 40, dialog_y + 40, dialog_width - 80, dialog_height - 80)
            
            if not text_complete:
                # 處理當前段落換行
                paragraph = paragraphs[current_paragraph]
                wrapped_lines = wrap_chinese_text(paragraph, font, text_area.width)
                text_complete = True
            
            # 計算總高度（包括段落間距）
            total_height = len(wrapped_lines) * line_height
            
            # 計算起始Y位置（垂直居中）
            start_y = text_area.y + (text_area.height - total_height) // 2
            start_y = max(text_area.y, start_y)  # 確保不會超出頂部
            
            # 渲染文字
            y_pos = start_y
            for line in wrapped_lines:
                rendered_text = font.render(line, True, text_color)
                self.screen.blit(rendered_text, (text_area.x, y_pos))
                y_pos += line_height
                
                # 檢查是否超出底部邊界
                if y_pos + line_height > text_area.y + text_area.height:
                    break
            
            # 顯示提示文字
            if text_complete:
                if current_paragraph < len(paragraphs) - 1:
                    prompt = font.render("點擊繼續下一段...", True, (200, 200, 255))
                    self.screen.blit(prompt, (SCREEN_WIDTH - 250, SCREEN_HEIGHT - 60))
                else:
                    prompt = font.render("點擊關閉...", True, (200, 200, 255))
                    self.screen.blit(prompt, (SCREEN_WIDTH - 200, SCREEN_HEIGHT - 60))
            
            pygame.display.flip()
            clock.tick(60)
    
    def initialize_scenes(self):
        """初始化場景序列，只執行一次"""
        if self.scene_initialized:
            return
            
        current_view = self.current_view
        self.can_interact[current_view] = False  # 禁用當前視角互動
        
        def scene_callback():
            """場景結束後的回調函數"""
            self.current_view = current_view  # 確保回到原視角
            # 如果需要重新啟用互動，取消下面註解
            # self.can_interact[current_view] = True
        
        from scenes import load_scene_resources
        screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        font = pygame.font.Font("標楷體.ttf", 18)
        scene_manager = SceneManager(screen, font)
        
        scenes = [
            {"scene": "scene3_1.json"},
            {"scene": "scene3_2.json"}
        ]
        
        scene_sequence = []
        for scene_data in scenes:
            scene_sequence.append(
                lambda scene=scene_data["scene"]: 
                load_scene_resources(scene)
            )
        
        scene_manager.run_scenes(
            scene_sequence,
            callback=scene_callback
        )
        
        self.scene_initialized = True

    def handle_events(self):
        # 靜止畫面顯示
        clock = pygame.time.Clock()
        static_running = True
        
        while static_running:
            self.screen.blit(self.tree2_img, (0, 0))
            
            if self.show_buttons:
                self.draw_action_buttons()
            
            if self.show_images:
                img_width = self.burner_img.get_width()
                img_height = self.burner_img.get_height()
                
                left_pos = (SCREEN_WIDTH//4 - img_width//2, SCREEN_HEIGHT//2 - img_height//2)
                right_pos = (SCREEN_WIDTH*3//4 - img_width//2, SCREEN_HEIGHT//2 - img_height//2)
                
                self.draw_image_with_border(self.burner_img, left_pos)
                self.draw_image_with_border(self.midian_img, right_pos)
                
                # 繪製繼續按鈕
                continue_btn = pygame.Rect(SCREEN_WIDTH//2 - 100, SCREEN_HEIGHT - 100, 200, 60)
                pygame.draw.rect(self.screen, (100, 100, 200), continue_btn, border_radius=10)
                pygame.draw.rect(self.screen, (150, 150, 250), continue_btn, 2, border_radius=10)
                
                font = pygame.font.Font("標楷體.ttf", 30)
                continue_text = font.render("繼續", True, (255, 255, 255))
                self.screen.blit(continue_text, (continue_btn.centerx - continue_text.get_width()//2, 
                                            continue_btn.centery - continue_text.get_height()//2))
            
            pygame.display.flip()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = pygame.mouse.get_pos()
                    
                    if self.show_images:
                        # 檢查是否點擊了左邊圖片
                        left_img_rect = pygame.Rect(
                            SCREEN_WIDTH//4 - self.burner_img.get_width()//2,
                            SCREEN_HEIGHT//2 - self.burner_img.get_height()//2,
                            self.burner_img.get_width(),
                            self.burner_img.get_height()
                        )
                        
                        # 檢查是否點擊了右邊圖片
                        right_img_rect = pygame.Rect(
                            SCREEN_WIDTH*3//4 - self.midian_img.get_width()//2,
                            SCREEN_HEIGHT//2 - self.midian_img.get_height()//2,
                            self.midian_img.get_width(),
                            self.midian_img.get_height()
                        )
                        
                        # 檢查是否點擊了繼續按鈕
                        continue_btn = pygame.Rect(SCREEN_WIDTH//2 - 100, SCREEN_HEIGHT - 100, 200, 60)
                        
                        if left_img_rect.collidepoint(mouse_pos):
                            self.show_text_dialog(self.text_contents.get('burner', '沒有相關描述'))
                        
                        elif right_img_rect.collidepoint(mouse_pos):
                            self.show_text_dialog(self.text_contents.get('midian', '沒有相關描述'))
                        
                        elif continue_btn.collidepoint(mouse_pos):
                            self.show_images = False
                            self.show_buttons = True
                            static_running = False
                            # 跳出迴圈後執行劇情場景
                            self.full_scene_complete = self.run_full_scene_sequence()
                            if(self.full_scene_complete):
                                return False
                
                elif event.type == pygame.KEYDOWN:
                    if self.show_buttons:
                        if event.key == pygame.K_e:
                            print("坐下喝茶動作觸發")
                            self.show_buttons = False
                            static_running = False
                            # 跳出迴圈後執行劇情場景
                            self.full_scene_complete = self.run_full_scene_sequence()
                            if(self.full_scene_complete):
                                return False
                        
                        elif event.key == pygame.K_f:
                            print("觀察四周動作觸發")
                            self.show_buttons = False
                            self.show_images = True
                    
                    elif event.key == pygame.K_ESCAPE and self.show_images:
                        self.show_images = False
                        self.show_buttons = True
            
            clock.tick(60)
        
        return True

    def run_scene_sequence1(self):
        """執行劇情場景序列"""
        current_view = self.current_view
        self.can_interact[current_view] = False  # 禁用當前視角互動
        
        def scene_callback():
            """場景結束後的回調函數"""
            self.current_view = current_view  # 確保回到原視角
            # 如果需要重新啟用互動，取消下面註解
            # self.can_interact[current_view] = True
        
        from scenes import load_scene_resources
        screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        font = pygame.font.Font("標楷體.ttf", 18)
        scene_manager = SceneManager(screen, font)
        
        scenes = [
            {"scene": "scene3_3.json"},
            {"scene": "scene3_4.json"},
            {"scene": "scene3_5.json"},
            {"scene": "scene3_6.json"},
        ]
        
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
        
        # 載入 tea.png 圖片並調整為全螢幕大小
        try:
            tea_img = pygame.image.load(os.path.join('images', 'tea.png')).convert_alpha()
            # 調整為全螢幕大小，保持原始比例
            img_ratio = tea_img.get_width() / tea_img.get_height()
            screen_ratio = SCREEN_WIDTH / SCREEN_HEIGHT
            
            if img_ratio > screen_ratio:
                # 圖片較寬，以寬度為基準
                new_width = SCREEN_WIDTH
                new_height = int(new_width / img_ratio)
            else:
                # 圖片較高，以高度為基準
                new_height = SCREEN_HEIGHT
                new_width = int(new_height * img_ratio)
            
            tea_img = pygame.transform.scale(tea_img, (SCREEN_WIDTH, SCREEN_HEIGHT))
        except:
            # 如果載入失敗，創建一個全螢幕替代圖片
            tea_img = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            tea_img.fill((255, 255, 255, 128))
            font = pygame.font.Font(None, 60)
            text = font.render("tea.png 載入失敗", True, (0, 0, 0))
            tea_img.blit(text, (SCREEN_WIDTH//2 - text.get_width()//2, 
                            SCREEN_HEIGHT//2 - text.get_height()//2))
        
        # 創建並執行縮放動畫
        zoom_anim = ZoomAnimation()
        zoom_anim.zoom_scale = 3  # 縮放比例調小一點，因為已經是全螢幕
        zoom_anim.duration = 1500  # 動畫時間延長到1.5秒
        zoom_anim.start(tea_img)
        
        # 計算圖片位置（居中）
        image_position = (SCREEN_WIDTH//2 - tea_img.get_width()//2, 
                        SCREEN_HEIGHT//2 - tea_img.get_height()//2)
        
        # 動畫循環
        clock = pygame.time.Clock()
        running = True
        
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                    # 允許按任意鍵或點擊滑鼠跳過動畫
                    running = False
            
            # 清空畫面
            self.screen.fill((0, 0, 0))
            
            # 更新並繪製動畫
            animation_complete = zoom_anim.update(self.screen, image_position)
            
            # 如果動畫完成，結束循環
            if animation_complete:
                running = False
            
            pygame.display.flip()
            clock.tick(60)
        
        self.scene_initialized = True

    def run_scene_sequence2(self):
        """執行劇情場景序列"""
        current_view = self.current_view
        self.can_interact[current_view] = False  # 禁用當前視角互動
        
        def scene_callback():
            """場景結束後的回調函數"""
            self.current_view = current_view  # 確保回到原視角
            # 如果需要重新啟用互動，取消下面註解
            # self.can_interact[current_view] = True
        
        from scenes import load_scene_resources
        screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        font = pygame.font.Font("標楷體.ttf", 18)
        scene_manager = SceneManager(screen, font)
        
        scenes = [
            {"scene": "scene3_7.json"},
            {"scene": "scene3_8.json"},
            {"scene": "scene3_9.json"},
            {"scene": "scene3_10.json"},
            {"scene": "scene3_11.json"},
            {"scene": "scene3_12.json"},
            {"scene": "scene3_13.json"},
            {"scene": "scene3_14.json"},
        ]
        
        scene_sequence = []
        for scene_data in scenes:
            scene_sequence.append(
                lambda scene=scene_data["scene"]: 
                load_scene_resources(scene)
            )
        
        scene_manager.run_scenes(
            scene_sequence,
            callback=scene_callback
        )
        
        self.scene_initialized = True   
    
    def run_full_scene_sequence(self):
        """執行完整的場景序列（包含 sequence1 和 sequence2）"""
        # 執行第一個場景序列
        self.run_scene_sequence1()
        
        # 執行第二個場景序列
        self.run_scene_sequence2()
        
        # 新增：載入並顯示 Zhang.png 圖片（全螢幕）
        try:
            # 載入圖片並調整為全螢幕大小
            zhang_img = pygame.image.load(os.path.join('images', 'Zhang5.png')).convert_alpha()
            zhang_img = pygame.transform.scale(zhang_img, (SCREEN_WIDTH, SCREEN_HEIGHT))
        except:
            # 如果載入失敗，創建全螢幕替代圖片
            zhang_img = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            zhang_img.fill((50, 50, 50))  # 深灰色背景
            font = pygame.font.Font(None, 60)
            text = font.render("Zhang5.png 載入失敗", True, (255, 255, 255))
            zhang_img.blit(text, (SCREEN_WIDTH//2 - text.get_width()//2, 
                                SCREEN_HEIGHT//2 - text.get_height()//2))
        
        # 顯示圖片和互動按鈕
        clock = pygame.time.Clock()
        show_zhang = True
        
        while show_zhang:
            # 繪製全螢幕圖片
            self.screen.blit(zhang_img, (0, 0))
            
            # 繪製半透明黑色遮罩層
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 128))
            self.screen.blit(overlay, (0, 0))
            
            # 繪製互動按鈕
            font = pygame.font.Font("標楷體.ttf", 30)
            
            # 左按鈕：前往還願戲台
            left_btn = pygame.Rect(SCREEN_WIDTH//4 - 150, SCREEN_HEIGHT - 120, 300, 60)
            pygame.draw.rect(self.screen, (180, 70, 60), left_btn, border_radius=10)
            pygame.draw.rect(self.screen, (220, 120, 100), left_btn, 2, border_radius=10)
            left_text = font.render("前往還願戲台 (Q)", True, (255, 255, 255))
            self.screen.blit(left_text, (left_btn.centerx - left_text.get_width()//2, 
                                    left_btn.centery - left_text.get_height()//2))
            # 橢圓形標籤位置（按鈕右上角）
            tag_rect = pygame.Rect(
                left_btn.right - 80,  # 從按鈕右邊往左偏移
                left_btn.top - 15,    # 從按鈕頂部往上偏移
                120, 30               # 寬度和高度
            )

            # 繪製白色橢圓形
            pygame.draw.ellipse(self.screen, (255, 255, 255), tag_rect)
            pygame.draw.ellipse(self.screen, (200, 200, 200), tag_rect, 1)  # 邊框

            # 繪製文字（使用較小的字體）
            small_font = pygame.font.Font("標楷體.ttf", 16)
            tag_text = small_font.render("去了回不來喔", True, (50, 50, 50))
            self.screen.blit(tag_text, (
                tag_rect.centerx - tag_text.get_width()//2,
                tag_rect.centery - tag_text.get_height()//2
            ))
            
            # 右按鈕：與老張下棋
            if not self.chess_sussess:
                right_btn = pygame.Rect(SCREEN_WIDTH*3//4 - 150, SCREEN_HEIGHT - 120, 300, 60)
                pygame.draw.rect(self.screen, (60, 100, 180), right_btn, border_radius=10)
                pygame.draw.rect(self.screen, (100, 150, 220), right_btn, 2, border_radius=10)
                right_text = font.render("與老張下棋 (E)", True, (255, 255, 255))
                self.screen.blit(right_text, (right_btn.centerx - right_text.get_width()//2, 
                                        right_btn.centery - right_text.get_height()//2))
                
                # 如果已經下過一次棋，顯示「再來一次？」標籤
                if self.trychess_times >= 1:
                    # 橢圓形標籤位置（按鈕右上角）
                    tag_rect = pygame.Rect(
                        right_btn.right - 80,  # 從按鈕右邊往左偏移
                        right_btn.top - 15,    # 從按鈕頂部往上偏移
                        100, 30                # 寬度和高度
                    )
                    
                    # 繪製白色橢圓形
                    pygame.draw.ellipse(self.screen, (255, 255, 255), tag_rect)
                    pygame.draw.ellipse(self.screen, (200, 200, 200), tag_rect, 1)  # 邊框
                    
                    # 繪製文字（使用較小的字體）
                    small_font = pygame.font.Font("標楷體.ttf", 16)
                    tag_text = small_font.render("再來一次？", True, (50, 50, 50))
                    self.screen.blit(tag_text, (
                        tag_rect.centerx - tag_text.get_width()//2,
                        tag_rect.centery - tag_text.get_height()//2
                    ))
            
            pygame.display.flip()
            
            # 事件處理
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_q:
                        print("前往還願戲台動作觸發")
                        scene4 = Scene4(screen, inventory)
                        scene4.run()
                        show_zhang = False
                    
                    elif event.key == pygame.K_e:
                        print("與老張下棋動作觸發")
                        self.chess_sussess = False  # 標記下棋成功
                        self.trychess_times += 1
            
            clock.tick(60)
        
        return True

    def draw_action_buttons(self):
        """繪製動作選擇按鈕"""
        font = pygame.font.Font("標楷體.ttf", 30)
        
        tea_btn = pygame.Rect(SCREEN_WIDTH//4 - 150, SCREEN_HEIGHT - 100, 300, 60)
        pygame.draw.rect(self.screen, (50, 150, 50), tea_btn, border_radius=10)
        tea_text = font.render("坐下喝茶 (按 E)", True, (255, 255, 255))
        self.screen.blit(tea_text, (tea_btn.centerx - tea_text.get_width()//2, 
                                  tea_btn.centery - tea_text.get_height()//2))
        
        look_btn = pygame.Rect(SCREEN_WIDTH*3//4 - 150, SCREEN_HEIGHT - 100, 300, 60)
        pygame.draw.rect(self.screen, (50, 100, 200), look_btn, border_radius=10)
        look_text = font.render("觀察四周 (按 F)", True, (255, 255, 255))
        self.screen.blit(look_text, (look_btn.centerx - look_text.get_width()//2, 
                                    look_btn.centery - look_text.get_height()//2))
    
    def draw_ui(self):
        """繪製UI按鈕"""
        self.back_btn = pygame.Rect(30, 30, 80, 40)
        pygame.draw.rect(self.screen, (200, 50, 50), self.back_btn)
        font = pygame.font.Font("標楷體.ttf", 20)
        back_text = font.render("返回", True, (255, 255, 255))
        self.screen.blit(back_text, (45, 35))
    
    def draw(self):
        """繪製場景"""
        self.screen.fill((0, 0, 0))
        bg_img, bg_pos = self.backgrounds[self.current_view]
        self.screen.blit(bg_img, bg_pos)
        # self.draw_ui()
        
        if self.show_buttons:
            self.draw_action_buttons()
        
        pygame.display.flip()
    
    def run(self):
        """執行場景"""
        # 初始化場景序列，只執行一次
        self.initialize_scenes()
        
        clock = pygame.time.Clock()
        running = True
        
        while running:
            running = self.handle_events()
            self.draw()
            clock.tick(60)
        
        return True