import pygame
from scenes import draw_text
from scene_change import wait_for_player_input, handle_scene_transition
from functools import partial
from settings import SCREEN_WIDTH, SCREEN_HEIGHT, DIALOGUE_WIDTH, DIALOGUE_HEIGHT

class SceneManager:
    def __init__(self, screen, font):
        self.screen = screen
        self.font = font
        self.current_scene = 0
        self.dialogue_box = pygame.Rect(
            (SCREEN_WIDTH  - DIALOGUE_WIDTH) // 2,
            SCREEN_HEIGHT - 200,
            DIALOGUE_WIDTH,
            DIALOGUE_HEIGHT
        )  # (x, y, width, height)
        
    def fade_transition(self, from_surface, to_surface, duration=200):
        """實現淡出淡入過渡效果"""
        fade_surface = pygame.Surface((self.screen.get_width(), self.screen.get_height()))
        for alpha in range(0, 255, 5):  # 淡出
            fade_surface.fill((0, 0, 0))
            from_surface.set_alpha(255 - alpha)
            fade_surface.blit(from_surface, (0, 0))
            self.screen.blit(fade_surface, (0, 0))
            pygame.display.flip()
            pygame.time.delay(duration // 50)
        
        pygame.time.delay(duration // 2)  # 短暫黑屏
        
        for alpha in range(0, 255, 5):  # 淡入
            fade_surface.fill((0, 0, 0))
            to_surface.set_alpha(alpha)
            fade_surface.blit(to_surface, (0, 0))
            self.screen.blit(fade_surface, (0, 0))
            pygame.display.flip()
            pygame.time.delay(duration // 50)
    
    def play_backgrounds(self, backgrounds, last_background=None):
        """播放多個背景，處理背景切換效果"""
        if not backgrounds:
            return None
            
        # 如果有上一個背景，先執行淡入效果
        if last_background:
            temp_surface = pygame.Surface((self.screen.get_width(), self.screen.get_height()))
            temp_surface.blit(last_background, (0, 0))
            # self.fade_transition(temp_surface, backgrounds[0]["image"])
        
        # 播放每個背景
        for i, bg_info in enumerate(backgrounds):
            self.screen.blit(bg_info["image"], (0, 0))
            pygame.display.flip()
            
            # 如果不是最後一個背景且有設定播放時間，則等待
            if i < len(backgrounds) - 1 and "duration" in bg_info:
                pygame.time.delay(bg_info["duration"])
        
        # 返回最後一個背景供下次使用
        return backgrounds[-1]["image"]
    
    def run_scene(self, scene_func, callback=None, last_background=None):
        """執行單個場景（支援多背景和角色對話）"""
        characters, backgrounds = scene_func()
        
        # 背景設定
        backgroundok = False 
        
        # 如果沒有角色對話，直接結束
        if not characters:
            if callback:
                callback()
            return current_background
        
        # 處理角色對話部分
        current_character = 0
        show_character = True
        running = True
        
        while running:
            # 顯示當前背景
            if not backgroundok:
                current_background = self.play_backgrounds(backgrounds, last_background)
                backgroundok = True
                # 顯示當前角色
                if show_character:
                    characters[current_character].draw(self.screen)

                # 顯示對話
                current_char = characters[current_character]
                draw_text(
                    self.screen, 
                    current_char.get_current_dialogue(), 
                    (self.dialogue_box.x + 20, self.dialogue_box.y + 30), 
                    self.font, 
                    reveal_speed=30
                )
            else:
                self.screen.blit(current_background, (0, 0))
                # 顯示當前角色
                if show_character:
                    characters[current_character].draw(self.screen)

                # 顯示對話
                current_char = characters[current_character]
                draw_text(
                    self.screen, 
                    current_char.get_current_dialogue(), 
                    (self.dialogue_box.x + 20, self.dialogue_box.y + 30), 
                    self.font, 
                    reveal_speed=30
                )
            

            pygame.display.update()

            # 等待玩家輸入
            wait_for_player_input()

            # 處理場景切換
            new_scene, new_character, need_reload = handle_scene_transition(
                current_char, characters, self.current_scene
            )

            # 檢查是否場景完全結束
            if new_scene == -1 and new_character == -1:
                running = False
                break

            # 處理角色切換效果
            if new_character != current_character and new_character < len(characters):
                show_character = False
                pygame.time.delay(500)
                show_character = True

            current_character = new_character

        # 場景完全結束後執行回調
        if callback:
            callback()
        
        return current_background

    def run_scenes(self, scene_sequence, callback=None):
        """
        執行一系列場景，帶有淡出淡入效果
        :param scene_sequence: 場景函數的列表
        :param callback: 所有場景完成後執行的回調函數
        """
        last_background = None
        for i, scene_func in enumerate(scene_sequence):
            # 最後一個場景不需要淡出
            if i == len(scene_sequence) - 1:
                last_background = self.run_scene(scene_func, None, last_background)
            else:
                # 執行場景並保存背景供下一個場景使用
                last_background = self.run_scene(scene_func, None, last_background)
                
                # 創建一個臨時表面用於淡出效果
                temp_surface = pygame.Surface((self.screen.get_width(), self.screen.get_height()))
                temp_surface.blit(last_background, (0, 0))
                
                # 淡出到黑屏
                fade_surface = pygame.Surface((self.screen.get_width(), self.screen.get_height()))
                for alpha in range(0, 255, 5):
                    fade_surface.fill((0, 0, 0))
                    temp_surface.set_alpha(255 - alpha)
                    fade_surface.blit(temp_surface, (0, 0))
                    self.screen.blit(fade_surface, (0, 0))
                    pygame.display.flip()
                    pygame.time.delay(10)
        
        # 所有場景完成後執行回調
        if callback:
            callback()