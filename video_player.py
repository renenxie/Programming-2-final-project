import pygame
import cv2
import numpy as np
import os
import sys
import time
from pygame.locals import *
from moviepy.editor import VideoFileClip
from settings import SCREEN_WIDTH, SCREEN_HEIGHT

class VideoPlayer:
    def __init__(self):
        """初始化播放器"""
        pygame.init()
        pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=4096)
        self.target_width = SCREEN_WIDTH
        self.target_height = SCREEN_HEIGHT
        self.screen = None
        self.temp_audio = "temp_audio.wav"
        self.cleanup_required = False
        self._pygame_initialized = False

    def init_pygame(self):
        """初始化Pygame顯示"""
        if not self._pygame_initialized:
            self.screen = pygame.display.set_mode((self.target_width, self.target_height))
            self._pygame_initialized = True

    def play_video(self, video_file, mirror=False, auto_play=True, window_title="影片播放器"):
        """
        播放影片函數
        
        參數:
            video_file (str): 影片檔案路徑
            mirror (bool): 是否水平鏡像翻轉 (預設False)
            auto_play (bool): 是否自動播放 (預設True)
            window_title (str): 視窗標題 (預設"影片播放器")
        
        返回:
            bool: 是否成功播放完整個影片
        """
        # 初始化Pygame顯示
        self.init_pygame()
        pygame.display.set_caption(window_title)

        # 檢查影片檔案是否存在
        if not os.path.exists(video_file):
            raise FileNotFoundError(f"找不到影片檔案: {video_file}")

        # 開啟影片
        cap = cv2.VideoCapture(video_file)
        if not cap.isOpened():
            raise IOError("無法開啟影片檔案")

        # 取得影片資訊
        original_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        original_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = cap.get(cv2.CAP_PROP_FPS)
        
        # 計算縮放比例
        ratio = min(self.target_width / original_width, self.target_height / original_height)
        new_width = int(original_width * ratio)
        new_height = int(original_height * ratio)

        # 提取音訊
        audio_loaded = self._extract_audio(video_file)

        # 自動播放或等待點擊
        if auto_play:
            if audio_loaded:
                pygame.mixer.music.play()
            start_time = time.time()
        else:
            if not self._show_waiting_screen():
                cap.release()
                return False
            start_time = time.time()
            if audio_loaded:
                pygame.mixer.music.play()

        # 主播放循環
        completed = self._playback_loop(cap, new_width, new_height, fps, mirror, audio_loaded, start_time)

        # 清理資源但不退出Pygame
        self._cleanup(cap, keep_pygame=True)
        return completed

    def _extract_audio(self, video_file):
        """提取影片中的音訊"""
        try:
            if os.path.exists(self.temp_audio):
                os.remove(self.temp_audio)
                
            video_clip = VideoFileClip(video_file)
            video_clip.audio.write_audiofile(self.temp_audio, fps=44100, ffmpeg_params=["-ac", "2"])
            pygame.mixer.music.load(self.temp_audio)
            self.cleanup_required = True
            return True
        except Exception as e:
            print(f"音訊處理警告: {e}")
            return False

    def _show_waiting_screen(self):
        """顯示等待畫面，返回是否繼續播放"""
        waiting = True
        clock = pygame.time.Clock()
        
        while waiting:
            for event in pygame.event.get():
                if event.type == QUIT:
                    return False
                elif event.type == MOUSEBUTTONDOWN or event.type == KEYDOWN:
                    return True
            
            self.screen.fill((0, 0, 0))
            font = pygame.font.SysFont(None, 36)
            text = font.render("點擊任意位置開始播放影片", True, (255, 255, 255))
            text_rect = text.get_rect(center=(self.target_width//2, self.target_height//2))
            self.screen.blit(text, text_rect)
            pygame.display.flip()
            clock.tick(30)

    def _playback_loop(self, cap, new_width, new_height, fps, mirror, audio_loaded, start_time):
        """主播放循環，返回是否播放完成"""
        playing = True
        paused = False
        clock = pygame.time.Clock()
        
        while playing and cap.isOpened():
            if not paused:
                ret, frame = cap.read()
                if not ret:
                    return True  # 影片播放完成
                
                # 音畫同步
                if audio_loaded:
                    current_time = time.time() - start_time
                    video_pos = cap.get(cv2.CAP_PROP_POS_MSEC) / 1000.0
                    if abs(current_time - video_pos) > 0.1:
                        cap.set(cv2.CAP_PROP_POS_MSEC, current_time * 1000)

            # 事件處理
            for event in pygame.event.get():
                if event.type == QUIT:
                    return False
                elif event.type == KEYDOWN:
                    if event.key == K_ESCAPE:
                        return False
                    elif event.key == K_SPACE:
                        paused = not paused
                        if audio_loaded:
                            if paused:
                                pygame.mixer.music.pause()
                            else:
                                pygame.mixer.music.unpause()
                                start_time = time.time() - (cap.get(cv2.CAP_PROP_POS_MSEC) / 1000.0)

            if paused:
                self._show_pause_screen()
                clock.tick(30)
                continue

            # 處理影片幀
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            if mirror:
                frame = cv2.flip(frame, 1)
            frame = cv2.resize(frame, (new_width, new_height))
            frame_surface = pygame.surfarray.make_surface(np.rot90(frame))
            
            # 顯示幀
            self.screen.fill((0, 0, 0))
            self.screen.blit(frame_surface, ((self.target_width - new_width) // 2, (self.target_height - new_height) // 2))
            pygame.display.flip()
            
            clock.tick(fps)
        
        return False

    def _show_pause_screen(self):
        """顯示暫停畫面"""
        self.screen.fill((0, 0, 0))
        font = pygame.font.SysFont(None, 48)
        text = font.render("已暫停 (按空格鍵繼續)", True, (255, 255, 255))
        text_rect = text.get_rect(center=(self.target_width//2, self.target_height//2))
        self.screen.blit(text, text_rect)
        pygame.display.flip()

    def _cleanup(self, cap, keep_pygame=False):
        """清理資源"""
        cap.release()
        if self.cleanup_required and os.path.exists(self.temp_audio):
            try:
                pygame.mixer.music.stop()
                os.remove(self.temp_audio)
            except:
                pass
        if not keep_pygame:
            pygame.quit()
        else:
            # 重置混音器以便下次使用
            pygame.mixer.music.stop()
            pygame.mixer.quit()
            pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=4096)

    def quit(self):
        """手動退出Pygame"""
        pygame.quit()
        self._pygame_initialized = False


# 使用範例 - 整合到遊戲主循環
if __name__ == "__main__":
    # 建立播放器實例
    player = VideoPlayer()
    
    # 範例遊戲主循環
    running = True
    while running:
        # 播放影片
        try:
            completed = player.play_video(
                video_file="your_video.mp4",  # 替換為你的影片路徑
                mirror=True,                # 水平鏡像翻轉
                auto_play=True,             # 自動播放
                window_title="遊戲過場動畫"
            )
            
            # 影片播放後的遊戲邏輯
            if completed:
                print("影片播放完成，繼續遊戲...")
                
                # 這裡可以加入遊戲的其他邏輯
                # 例如顯示遊戲選單或開始遊戲關卡
                
                # 簡單的範例：顯示一個訊息然後退出
                player.screen.fill((0, 0, 0))
                font = pygame.font.SysFont(None, 48)
                text = font.render("影片播放完畢，按任意鍵退出", True, (255, 255, 255))
                text_rect = text.get_rect(center=(player.target_width//2, player.target_height//2))
                player.screen.blit(text, text_rect)
                pygame.display.flip()
                
                # 等待用戶按鍵
                waiting = True
                while waiting:
                    for event in pygame.event.get():
                        if event.type == QUIT or event.type == KEYDOWN:
                            waiting = False
                            running = False
                    pygame.time.delay(50)
            else:
                print("影片播放被中斷")
                running = False
                
        except Exception as e:
            print(f"播放錯誤: {e}")
            running = False
    
    # 退出時清理
    player.quit()