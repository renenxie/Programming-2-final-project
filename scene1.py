import pygame
import os
import sys
from scene_manager import SceneManager
from transitions import slide_transition
from video_player import VideoPlayer
from settings import SCREEN_WIDTH, SCREEN_HEIGHT

scene1_1 = "scene_1.json"
background1_1 = "black_view.png"
scene1_2 = "scene_2.json"
background1_2 = "background2.jpg"

class Scene1:
    def __init__(self, screen, inventory):
        self.screen = screen
        self.inventory = inventory
        self.views = ['front', 'right', 'back', 'left']
        self.current_view = 'front'
        self.load_resources()
        self.delay_time = 23
        
        # 為每個視角設置獨立的互動開關
        self.can_interact = {
            'front': True,
            'right': True,
            'back': True,
            'left': True
        }
        
        # 各視角的互動區域
        self.interact_areas = {
            'front': pygame.Rect(SCREEN_WIDTH//2 - 100, SCREEN_HEIGHT//2 - 100, 200, 200),
            'right': pygame.Rect(SCREEN_WIDTH//2 - 100, SCREEN_HEIGHT//2 - 100, 200, 200),
            'back': pygame.Rect(SCREEN_WIDTH//2 - 100, SCREEN_HEIGHT//2 - 100, 200, 200),
            'left': pygame.Rect(SCREEN_WIDTH//2 - 100, SCREEN_HEIGHT//2 - 100, 200, 200)
        }
        
        # 修改為可以儲存多個場景的結構
        self.scene_resources = {
            'front': [
                {"scene": "scene_1.json", "background": "black_view.png"},
                {"scene": "scene_2.json", "background": "Red_Brick_Market1.png"}
            ],
            'right': [
                {"scene": "scene_3.json", "background": "background3.jpg"},
                {"scene": "scene_4.json", "background": "background4.jpg"}
            ],
            'back': [
                {"scene": "scene_5.json", "background": "background5.jpg"}
            ],
            'left': [
                {"scene": "scene_6.json", "background": "background6.jpg"},
                {"scene": "scene_7.json", "background": "background7.jpg"},
                {"scene": "scene_8.json", "background": "background8.jpg"}
            ]
        }
        
    def switch_view(self, direction):
        """切換市場視角（帶滑動動畫）"""
        current_idx = self.views.index(self.current_view)
        new_view = self.views[(current_idx + direction) % len(self.views)]
        
        # 獲取當前和新背景圖
        current_img, current_pos = self.backgrounds[self.current_view]
        new_img, new_pos = self.backgrounds[new_view]
        
        # 創建兩個臨時表面用於動畫
        current_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        new_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        
        # 繪製當前畫面到表面
        current_surface.blit(current_img, current_pos)
        # 繪製新畫面到表面
        new_surface.blit(new_img, new_pos)
        
        # 使用 slide_transition 函數
        slide_transition(self.screen, current_surface, new_surface, "right" if direction == 1 else "left")
        
        # 更新當前視角
        self.current_view = new_view
        
    def load_resources(self):
        """載入市場場景資源（調整圖片大小並置中）"""
        self.backgrounds = {}
        self.original_items = {}
        
        # 載入背景並調整大小和位置
        for view in self.views:
            path = os.path.join('images', f'background1_{view}.png')
            original_img = pygame.image.load(path)
            
            # 計算縮放比例並保持寬高比
            img_width, img_height = original_img.get_size()
            scale = max(SCREEN_WIDTH/img_width, SCREEN_HEIGHT/img_height)  # 使用max而不是min
            new_width = int(img_width * scale)
            new_height = int(img_height * scale)
            
            scaled_img = pygame.transform.scale(original_img, (new_width, new_height))
            
            # 計算置中位置
            x = (SCREEN_WIDTH - new_width) // 2
            y = (SCREEN_HEIGHT - new_height) // 2
            
            self.backgrounds[view] = (scaled_img, (x, y))
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    self.switch_view(-1)
                elif event.key == pygame.K_RIGHT:
                    self.switch_view(1)
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                
                # 檢查返回按鈕
                if self.back_btn.collidepoint(mouse_pos):
                    self.inventory.items.clear()
                    self.inventory.selected_index = -1
                    return False
                
                # 檢查左右箭頭按鈕
                if self.left_btn.collidepoint(mouse_pos):
                    self.switch_view(-1)
                elif self.right_btn.collidepoint(mouse_pos):
                    self.switch_view(1)

                # # 檢查當前視角的互動區域
                # current_view = self.current_view
                # if (self.interact_areas[current_view].collidepoint(mouse_pos) and 
                #     self.can_interact[current_view]):
                    
                #     self.can_interact[current_view] = False  # 禁用當前視角互動
                    
                #     def scene_callback():
                #         """場景結束後的回調函數"""
                #         self.current_view = current_view  # 確保回到原視角
                #         # 如果需要重新啟用互動，取消下面註解
                #         # self.can_interact[current_view] = True
                        
                #     from scenes import load_scene_resources
                #     screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
                #     font = pygame.font.Font("標楷體.ttf", 18)
                #     scene_manager = SceneManager(screen, font)
                    
                #     # 獲取當前視角對應的所有場景資源
                #     scenes = self.scene_resources[current_view]
                    
                #     # 創建場景序列
                #     scene_sequence = []
                #     for scene_data in scenes:
                #         scene_sequence.append(
                #             lambda scene=scene_data["scene"], bg=scene_data["background"]: 
                #             load_scene_resources(scene, bg)
                #         )
                    
                #     # 執行場景序列
                #     scene_manager.run_scenes(
                #         scene_sequence,
                #         callback=scene_callback
                #     )

        return True
    
    def draw(self):
        """繪製市場場景（先清空畫面再繪製）"""
        # 清空畫面（隱藏原本視角）
        self.screen.fill((0, 0, 0))
        
        # 繪製背景（使用儲存的圖片和位置）
        bg_img, bg_pos = self.backgrounds[self.current_view]
        self.screen.blit(bg_img, bg_pos)
        
        # 繪製UI元素
        self.draw_ui()
        
        pygame.display.flip()
    
    def draw_ui(self):
        """繪製UI按鈕和提示"""
        # 返回按鈕
        self.back_btn = pygame.Rect(30, 30, 80, 40)
        pygame.draw.rect(self.screen, (200, 50, 50), self.back_btn)
        font = pygame.font.Font("msjh.ttc", 20)
        back_text = font.render("返回", True, (255, 255, 255))
        self.screen.blit(back_text, (45, 35))
        
        # 左右箭頭按鈕
        self.left_btn = pygame.Rect(50, SCREEN_HEIGHT//2 - 25, 50, 50)
        self.right_btn = pygame.Rect(SCREEN_WIDTH - 100, SCREEN_HEIGHT//2 - 25, 50, 50)
        
        pygame.draw.polygon(self.screen, (255, 0, 0), [
            (self.left_btn.right, self.left_btn.top),
            (self.left_btn.left, self.left_btn.centery),
            (self.left_btn.right, self.left_btn.bottom)
        ])
        
        pygame.draw.polygon(self.screen, (255, 0, 0), [
            (self.right_btn.left, self.right_btn.top),
            (self.right_btn.right, self.right_btn.centery),
            (self.right_btn.left, self.right_btn.bottom)
        ])
    
    def run(self):
        """執行市場場景"""
        clock = pygame.time.Clock()
        running = True
        
        while running:
            running = self.handle_events()
            self.draw()
            clock.tick(60)
        
        return True