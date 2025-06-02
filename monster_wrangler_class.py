import pygame, random, os
##from settings import WINDOW_WIDTH, WINDOW_HEIGHT, FPS

ASSET_DIR = "monster_wrangler_assets"
WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 675
FPS = 60

MONSTER_ZONE_TOP = 200
MONSTER_ZONE_BOTTOM = 700
# FPS = 60

class MonsterWranglerGame:
    def __init__(self):
        pygame.init()
        self.display_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Monster Wrangler")
        self.clock = pygame.time.Clock()

        self.background_image = pygame.transform.scale(
            pygame.image.load(os.path.join(ASSET_DIR, "background.png")).convert(),
            (WINDOW_WIDTH, WINDOW_HEIGHT)
        )
        self.treasure_image = pygame.transform.scale(
            pygame.image.load(os.path.join(ASSET_DIR, "treasure.png")), (48, 48)
        )
        self.font = pygame.font.Font(os.path.join(ASSET_DIR, "標楷體.ttf"), 32)
        self.success_sound = pygame.mixer.Sound(os.path.join(ASSET_DIR, "catch.wav"))
        self.next_level_sound = pygame.mixer.Sound(os.path.join(ASSET_DIR, "next_level.wav"))

    def run(self):
        while True:
            # 遊戲開始
            player_group = pygame.sprite.Group()
            player = Player()
            player_group.add(player)

            monster_group = pygame.sprite.Group()
            game = Game(player, monster_group, self.display_surface, self.font,
                        self.background_image, self.treasure_image,
                        self.success_sound, self.next_level_sound)
            game.running = True
            game.start_new_round()

            while game.running:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        return
                    if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                        player.warp()

                self.display_surface.blit(self.background_image, (0, 0))
                player_group.update()
                player_group.draw(self.display_surface)
                monster_group.update()
                monster_group.draw(self.display_surface)
                game.update()
                game.draw()
                pygame.display.update()
                self.clock.tick(FPS)

            # 顯示結果畫面
            self.show_result(game.result)

            # 成功：按任意鍵離開
            # 失敗：按任意鍵重來（自動迴圈）
            if game.result:  # win
                if not self.wait_for_key():
                    break  # 離開遊戲
                else:
                    break
            else:  # lose
                self.wait_for_key()  # 重來一輪

    def show_result(self, result):
        self.display_surface.blit(self.background_image, (0, 0))
        if result:
            text = self.font.render("🎉 恭喜你贏了！按任意鍵結束遊戲", True, (255, 255, 0))
        else:
            text = self.font.render("💀 你失敗了！按任意鍵重新開始", True, (255, 0, 0))
        rect = text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2))
        self.display_surface.blit(text, rect)
        pygame.display.update()

    def wait_for_key(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return False
                if event.type == pygame.KEYDOWN:
                    return True


class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.image.load(os.path.join(ASSET_DIR, "running_man.png"))
        self.image = pygame.transform.scale(self.image, (72, 72))
        self.rect = self.image.get_rect(centerx=WINDOW_WIDTH // 2, top=105)
        self.lives = 5
        self.warps = 2
        self.velocity = 8
        self.die_sound = pygame.mixer.Sound(os.path.join(ASSET_DIR, "die.wav"))
        self.warp_sound = pygame.mixer.Sound(os.path.join(ASSET_DIR, "warp.wav"))

    def update(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and self.rect.left > 0:
            self.rect.x -= self.velocity
        if keys[pygame.K_RIGHT] and self.rect.right < WINDOW_WIDTH:
            self.rect.x += self.velocity
        if keys[pygame.K_UP] and self.rect.top > 0:
            self.rect.y -= self.velocity
        if keys[pygame.K_DOWN] and self.rect.bottom < WINDOW_HEIGHT:
            self.rect.y += self.velocity

    def warp(self):
        if self.warps > 0:
            self.warps -= 1
            self.warp_sound.play()
            self.rect.top = 105

    def reset(self):
        self.rect.centerx = WINDOW_WIDTH // 2
        self.rect.top = 105

class Monster(pygame.sprite.Sprite):
    def __init__(self, x, y, image, monster_type):
        super().__init__()
        self.image = image
        self.rect = self.image.get_rect(topleft=(x, y))
        self.type = monster_type
        self.dx = random.choice([-1, 1])
        self.dy = random.choice([-1, 1])
        self.velocity = random.randint(1, 5)

    def update(self):
        self.rect.x += self.dx * self.velocity
        self.rect.y += self.dy * self.velocity
        if self.rect.left <= 0 or self.rect.right >= WINDOW_WIDTH:
            self.dx *= -1
        if self.rect.top <= MONSTER_ZONE_TOP or self.rect.bottom >= MONSTER_ZONE_BOTTOM:
            self.dy *= -1

class Game():
    def __init__(self, player, monster_group, display_surface, font,
                 background_image, treasure_image, success_sound, next_level_sound):
        self.score = 0
        self.round_number = 0
        self.round_time = 0
        self.frame_count = 0
        self.result = None
        self.running = True

        self.player = player
        self.monster_group = monster_group
        self.display_surface = display_surface
        self.font = font
        self.background_image = background_image
        self.treasure = treasure_image
        self.success_sound = success_sound
        self.next_level_sound = next_level_sound

        self.treasure_collected = 0
        self.treasure_rect = self.treasure.get_rect()
        self.spawn_treasure()

        self.target_monster_images = [
            pygame.transform.scale(pygame.image.load(os.path.join(ASSET_DIR, "monster1.png")), (64, 64)),
            pygame.transform.scale(pygame.image.load(os.path.join(ASSET_DIR, "monster2.png")), (64, 64)),
            pygame.transform.scale(pygame.image.load(os.path.join(ASSET_DIR, "monster3.png")), (64, 64)),
            pygame.transform.scale(pygame.image.load(os.path.join(ASSET_DIR, "monster4.png")), (64, 64))
        ]

        

        self.target_monster_image = self.treasure
        self.target_monster_rect = self.target_monster_image.get_rect(centerx=WINDOW_WIDTH // 2, top=30)

    def spawn_treasure(self):
        self.treasure_rect.x = random.randint(0, WINDOW_WIDTH - 48)
        self.treasure_rect.y = random.randint(MONSTER_ZONE_TOP, MONSTER_ZONE_BOTTOM - 48)

    def update(self):
        self.frame_count += 1
        if self.frame_count == FPS:
            self.round_time += 1
            self.frame_count = 0
        self.check_collisions()

    def draw(self):
        WHITE = (255, 255, 255)
        catch_text = self.font.render("報紙碎片", True, WHITE)
        catch_rect = catch_text.get_rect(centerx=WINDOW_WIDTH // 2, top=5)


        #score_text = self.font.render(f"分數: {self.score}", True, WHITE)
        lives_text = self.font.render(f"剩餘生命: {self.player.lives}", True, WHITE)
        time_text = self.font.render(f"花費時間: {self.round_time}", True, WHITE)
        treasure_text = self.font.render(f"已搜集碎片: {self.treasure_collected}/4", True, WHITE)

        self.display_surface.blit(catch_text, catch_rect)
        #self.display_surface.blit(score_text, score_text.get_rect(left=10, top=10))
        self.display_surface.blit(lives_text, lives_text.get_rect(left=10, top=45))
        self.display_surface.blit(time_text, time_text.get_rect(right=WINDOW_WIDTH - 10, top=10))
        self.display_surface.blit(treasure_text, treasure_text.get_rect(right=WINDOW_WIDTH - 10, top=45))



        self.display_surface.blit(self.target_monster_image, self.target_monster_rect)
        self.display_surface.blit(self.treasure, self.treasu