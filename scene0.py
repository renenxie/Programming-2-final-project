import pygame
import os
import sys
from scene_manager import SceneManager
from settings import SCREEN_WIDTH, SCREEN_HEIGHT

class Scene0:
    def __init__(self, screen, inventory):
        self.screen = screen
        self.inventory = inventory
        self.views = ['front']
        self.current_view = 'front'
        self.delay_time = 23
        
        # 為每個視角設置獨立的互動開關
        self.can_interact = {
            'front': True,
        }
        
        # 各視角的互動區域
        self.interact_areas = {
            'front': pygame.Rect(SCREEN_WIDTH//2 - 100, SCREEN_HEIGHT//2 - 100, 200, 200),
        }

    def handle_events(self):
        
        # 檢查當前視角的互動區域
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
                    
        # 獲取當前視角對應的所有場景資源
        scenes = [
            {"scene": "scene0_1.json"},
            {"scene": "scene0_2.json"},
            {"scene": "scene0_3.json"},
            {"scene": "scene0_4.json"},
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

        from video_player import VideoPlayer
        # 建立播放器實例
        player = VideoPlayer()

        # 播放影片
        player.play_video(
            video_file="videos/black_shadow.mp4",
            mirror=True,     # 可選: 是否鏡像翻轉
            auto_play=True,  # 可選: 是否自動播放
            window_title="自訂標題"  # 可選: 視窗標題
        )

        # 獲取當前視角對應的所有場景資源
        scenes = [
            {"scene": "scene0_5.json"},
            {"scene": "scene0_6.json"},
            {"scene": "scene0_7.json"},
            {"scene": "scene0_8.json"},
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
    
    def draw(self):
        """繪製市場場景（先清空畫面再繪製）"""
        # 清空畫面（隱藏原本視角）
        self.screen.fill((0, 0, 0))
        
        # 繪製背景（使用儲存的圖片和位置）
        bg_img, bg_pos = self.backgrounds[self.current_view]
        self.screen.blit(bg_img, bg_pos)
        
        # 繪製UI元素
        # self.draw_ui()
        
        pygame.display.flip()
    
    def run(self):
        """執行市場場景"""
        clock = pygame.time.Clock()
        running = True
        
        while running:
            running = self.handle_events()
            # self.draw()
            clock.tick(60)
        
        return True