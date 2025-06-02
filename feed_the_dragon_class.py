import pygame
import random
import os

# 模組層級資源資料夾路徑
ASSETS_DIR = os.path.join(os.path.dirname(__file__), "feed_the_dragon_assets")

class FeedTheDragonGame:
    def __init__(self):
        pygame.init()

        # 視窗設定
        self.WINDOW_WIDTH = 1200
        self.WINDOW_HEIGHT = 675
        self.display_surface = pygame.display.set_mode((self.WINDOW_WIDTH, self.WINDOW_HEIGHT))
        pygame.display.set_caption("Feed the Dragon")

        # 時間與邏輯
        self.FPS = 60
        self.clock = pygame.time.Clock()
        self.PLAYER_STARTING_LIVES = 5
        self.PLAYER_VELOCITY = 10
        self.COIN_STARTING_VELOCITY = 10
        self.COIN_ACCELERATION = 0.5
        self.BUFFER_DISTANCE = 100

        self.score = 0
        self.player_lives = self.PLAYER_STARTING_LIVES
        self.coin_velocity = self.COIN_STARTING_VELOCITY

        # 顏色
        self.GREEN = (0, 255, 0)
        self.DARKGREEN = (10, 50, 10)
        self.WHITE = (255, 255, 255)
        self.BLACK = (0, 0, 0)

        # 字型與文字物件
        self.font = pygame.font.Font(os.path.join(ASSETS_DIR, 'msjh.ttc'), 32)
        self.title_text = self.font.render("老鼠殺手", True, self.GREEN, self.BLACK)
        self.title_rect = self.title_text.get_rect(centerx=self.WINDOW_WIDTH // 2, y=10)

        self.game_over_text = self.font.render("你輸了", True, self.BLACK, self.DARKGREEN)
        self.win_text = self.font.render("你贏了!", True, self.BLACK, self.DARKGREEN)
        self.continue_text = self.font.render("請按任意鍵繼續", True, self.GREEN, self.DARKGREEN)
        self.game_over_rect = self.game_over_text.get_rect(center=(self.WINDOW_WIDTH // 2, self.WINDOW_HEIGHT // 2))
        self.win_rect = self.win_text.get_rect(center=(self.WINDOW_WIDTH // 2, self.WINDOW_HEIGHT // 2))
        self.continue_rect = self.continue_text.get_rect(center=(self.WINDOW_WIDTH // 2, self.WINDOW_HEIGHT // 2 + 48))

        # 音效與音樂
        self.coin_sound = pygame.mixer.Sound(os.path.join(ASSETS_DIR, "coin_sound.wav"))
        self.miss_sound = pygame.mixer.Sound(os.path.join(ASSETS_DIR, "miss_sound.wav"))
        self.miss_sound.set_volume(0.1)
        pygame.mixer.music.load(os.path.join(ASSETS_DIR, "ftd_background_music.wav"))

        # 圖片載入
        self.background = pygame.transform.scale(
            pygame.image.load(os.path.join(ASSETS_DIR, "background.png")),
            (self.WINDOW_WIDTH, self.WINDOW_HEIGHT)
        )
        self.player_image = pygame.transform.scale(
            pygame.image.load(os.path.join(ASSETS_DIR, "girl.png")), (128, 128)
        )
        self.coin_image = pygame.transform.scale(
            pygame.image.load(os.path.join(ASSETS_DIR, "mouse.png")), (64, 64)
        )

        # 遊戲物件座標
        self.player_rect = self.player_image.get_rect(left=32, centery=self.WINDOW_HEIGHT // 2)
        self.coin_rect = self.coin_image.get_rect()
        self.coin_rect.x = self.WINDOW_WIDTH + self.BUFFER_DISTANCE
        self.coin_rect.y = random.randint(64, self.WINDOW_HEIGHT - 64)

    def update_texts(self):
        score_text = self.font.render("分數: " + str(self.score), True, self.GREEN, self.DARKGREEN)
        lives_text = self.font.render("剩餘生命: " + str(self.player_lives), True, self.GREEN, self.DARKGREEN)
        return score_text, lives_text

    def reset_game(self):
        self.score = 0
        self.player_lives = self.PLAYER_STARTING_LIVES
        self.coin_velocity = self.COIN_STARTING_VELOCITY
        self.player_rect.centery = self.WINDOW_HEIGHT // 2
        self.coin_rect.x = self.WINDOW_WIDTH + self.BUFFER_DISTANCE
        self.coin_rect.y = random.randint(64, self.WINDOW_HEIGHT - 64)
        pygame.mixer.music.play(-1, 0.0)

    def wait_for_key(self):
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT or event.type == pygame.KEYDOWN:
                    waiting = False

    def run(self):
        pygame.mixer.music.play(-1, 0.0)
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            keys = pygame.key.get_pressed()
            if keys[pygame.K_UP]:
                self.player_rect.y -= self.PLAYER_VELOCITY
            if keys[pygame.K_DOWN]:
                self.player_rect.y += self.PLAYER_VELOCITY

            self.player_rect.top = max(64, self.player_rect.top)
            self.player_rect.bottom = min(self.WINDOW_HEIGHT, self.player_rect.bottom)

            # coin 移動
            if self.coin_rect.right < 0:
                self.player_lives -= 1
                self.miss_sound.play()
                self.coin_rect.x = self.WINDOW_WIDTH + self.BUFFER_DISTANCE
                self.coin_rect.y = random.randint(64, self.WINDOW_HEIGHT - 64)
            else:
                self.coin_rect.x -= self.coin_velocity

            # 碰撞偵測
            if self.player_rect.colliderect(self.coin_rect):
                self.score += 1
                self.coin_sound.play()
                self.coin_velocity += self.COIN_ACCELERATION
                self.coin_rect.x = self.WINDOW_WIDTH + self.BUFFER_DISTANCE
                self.coin_rect.y = random.randint(64, self.WINDOW_HEIGHT - 64)

            # 畫面更新
            score_text, lives_text = self.update_texts()
            self.display_surface.blit(self.background, (0, 0))
            self.display_surface.blit(score_text, (10, 10))
            self.display_surface.blit(lives_text, (self.WINDOW_WIDTH - lives_text.get_width() - 10, 10))
            self.display_surface.blit(self.title_text, self.title_rect)
            pygame.draw.line(self.display_surface, self.WHITE, (0, 64), (self.WINDOW_WIDTH, 64), 2)
            self.display_surface.blit(self.player_image, self.player_rect)
            self.display_surface.blit(self.coin_image, self.coin_rect)

            pygame.display.update()
            self.clock.tick(self.FPS)

            # WIN
            if self.score >= 20:
                pygame.mixer.music.stop()
                self.display_surface.blit(self.win_text, self.win_rect)
                self.display_surface.blit(self.continue_text, self.continue_rect)
                pygame.display.update()
                self.wait_for_key()
                running = False

            # LOSE
            if self.player_lives == 0:
                pygame.mixer.music.stop()
                self.display_surface.blit(self.game_over_text, self.game_over_rect)
                self.display_surface.blit(self.continue_text, self.continue_rect)
                pygame.display.update()
                self.wait_for_key()
                self.reset_game()

        pygame.quit()
