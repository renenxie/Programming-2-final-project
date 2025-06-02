import pygame, random, os
from pygame.transform import scale

WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 675
FPS = 60

ASSET_DIR = "catch_the_clown_assets"

PLAYER_STARTING_LIVES = 5
CLOWN_STARTING_VELOCITY = 7  # 加快初速
CLOWN_ACCELERATION = 1.2     # 增加每次加速幅度

class CatchTheClownGame:
    def __init__(self):
        pygame.init()
        pygame.mixer.init()
        self.display_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Catch the Clown")

        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(os.path.join(ASSET_DIR, "msjh.ttc"), 32)
        self.title_text = self.font.render("抓取你要的中藥材", True, (1, 175, 209))
        self.title_rect = self.title_text.get_rect(topleft=(50, 10))
        self.background_image = scale(pygame.image.load(os.path.join(ASSET_DIR, "background.png")).convert_alpha(), (WINDOW_WIDTH, WINDOW_HEIGHT))
        self.background_rect = self.background_image.get_rect(topleft=(0, 0))
        self.medicine_images = [scale(pygame.image.load(os.path.join(ASSET_DIR, f"medicine{i+1}.png")).convert_alpha(), (128, 128)) for i in range(8)]
        self.medicine_icons = [scale(pygame.image.load(os.path.join(ASSET_DIR, f"medicine{i+1}.png")).convert_alpha(), (64, 64)) for i in range(8)]
        self.poison_images = [scale(pygame.image.load(os.path.join(ASSET_DIR, f"poison{i+1}.png")).convert_alpha(), (128, 128)) for i in range(2)]
        self.click_sound = pygame.mixer.Sound(os.path.join(ASSET_DIR, "click_sound.wav"))
        self.miss_sound = pygame.mixer.Sound(os.path.join(ASSET_DIR, "miss_sound.wav"))
        pygame.mixer.music.load(os.path.join(ASSET_DIR, "ctc_background_music.wav"))

    def show_message(self, text):
        msg = self.font.render(text, True, (255, 255, 0))
        rect = msg.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2))
        self.display_surface.blit(self.background_image, self.background_rect)
        self.display_surface.blit(msg, rect)
        pygame.display.update()
        pygame.time.wait(2000)

    def play_level(self, level):
        hints = {
            1: "第一關：尋找酸梅潤喉糕配方！",
            2: "第二關：尋找胡椒仙楂丸配方！",
            3: "第三關：尋找八仙果茶凍配方"
        }
        self.show_message(hints.get(level, "開始新關卡"))
        score = 0
        lives = PLAYER_STARTING_LIVES

        # 調整速度與圖片切換時間
        if level == 1:
            velocity = CLOWN_STARTING_VELOCITY
            image_switch_interval = 2000
        elif level == 2:
            velocity = CLOWN_STARTING_VELOCITY + 2
            image_switch_interval = 1500
        else:
            velocity = CLOWN_STARTING_VELOCITY + 4
            image_switch_interval = 800  # 第三關非常快

        dx, dy = random.choice([-1,1]), random.choice([-1,1])

        if level == 1:
            target_images = self.medicine_images[0:3]
            target_icons = self.medicine_icons[0:3]
        elif level == 2:
            target_images = self.medicine_images[3:6]
            target_icons = self.medicine_icons[3:6]
        else:
            target_images = self.medicine_images[6:8]
            target_icons = self.medicine_icons[6:8]

        target_count = len(target_images)
        all_images = target_images + self.poison_images
        collected = [False] * target_count

        clown_index = random.randint(0, len(all_images) - 1)
        clown_image = all_images[clown_index]
        clown_rect = clown_image.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2))
        last_switch_time = pygame.time.get_ticks()

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                    return "quit"
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    x, y = event.pos
                    if clown_rect.collidepoint(x, y):
                        if clown_index < target_count:
                            if not collected[clown_index]:
                                collected[clown_index] = True
                                score += 1
                                velocity += CLOWN_ACCELERATION
                                self.click_sound.play()
                            else:
                                self.click_sound.play()
                        else:
                            self.miss_sound.play()
                            lives -= 1
                    else:
                        self.miss_sound.play()
                        lives -= 1

                    if all(collected):
                        return "pass"
                    if lives <= 0:
                        return "fail"

                    clown_index = random.randint(0, len(all_images) - 1)
                    clown_image = all_images[clown_index]
                    clown_rect = clown_image.get_rect(center=clown_rect.center)
                    last_switch_time = pygame.time.get_ticks()

            if pygame.time.get_ticks() - last_switch_time >= image_switch_interval:
                clown_index = random.randint(0, len(all_images) - 1)
                clown_image = all_images[clown_index]
                clown_rect = clown_image.get_rect(center=clown_rect.center)
                last_switch_time = pygame.time.get_ticks()

            clown_rect.x += dx * velocity
            clown_rect.y += dy * velocity
            if clown_rect.left <= 0 or clown_rect.right >= WINDOW_WIDTH:
                dx *= -1
            if clown_rect.top <= 0 or clown_rect.bottom >= WINDOW_HEIGHT:
                dy *= -1

            self.display_surface.blit(self.background_image, self.background_rect)
            self.display_surface.blit(self.title_text, self.title_rect)
            score_text = self.font.render(f"已收集: {score}/{target_count}", True, (248,231,28))
            lives_text = self.font.render("生命: " + str(lives), True, (248,231,28))
            self.display_surface.blit(score_text, (WINDOW_WIDTH - 200, 10))
            self.display_surface.blit(lives_text, (WINDOW_WIDTH - 200, 50))
            for i, got in enumerate(collected):
                if got:
                    self.display_surface.blit(target_icons[i], (10 + i * 70, 100))
            self.display_surface.blit(clown_image, clown_rect)

            pygame.display.update()
            self.clock.tick(FPS)

    def run(self):
        pygame.mixer.music.play(-1, 0.0)

        for level in range(1, 4):
            while True:
                result = self.play_level(level)
                if result == "pass":
                    self.show_message(f"成功收集第 {level} 類素材！")
                    break
                elif result == "quit":
                    pygame.mixer.music.stop()
                    return
                elif result == "fail":
                    self.show_message("失敗！重新挑戰本關！")

        self.show_message("恭喜完成全部素材收集！")
        pygame.mixer.music.stop()
        pygame.time.wait(2000)
