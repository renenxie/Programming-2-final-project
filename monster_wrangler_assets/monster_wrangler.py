import pygame, random

# Initialize pygame
pygame.init()

# Set display window
WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 700
MONSTER_ZONE_TOP = 200  # Adjusted to make the zone larger upward
MONSTER_ZONE_BOTTOM = 700
display_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Monster Wrangler")

# Load and scale background image
background_image = pygame.transform.scale(pygame.image.load("background.png").convert(), (WINDOW_WIDTH, WINDOW_HEIGHT))

# Set FPS and clock
FPS = 60
clock = pygame.time.Clock()

# Load treasure image
treasure_image = pygame.image.load("treasure.png")
treasure_image = pygame.transform.scale(treasure_image, (48, 48))

class Game():
    def __init__(self, player, monster_group):
        self.score = 0
        self.round_number = 0
        self.round_time = 0
        self.frame_count = 0

        self.player = player
        self.monster_group = monster_group

        self.next_level_sound = pygame.mixer.Sound("next_level.wav")
        self.success_sound = pygame.mixer.Sound("catch.wav")  # New sound
        self.font = pygame.font.Font("Abrushow.ttf", 24)

        self.treasure_collected = 0
        self.treasure = treasure_image
        self.treasure_rect = self.treasure.get_rect()
        self.spawn_treasure()

        blue_image = pygame.image.load("blue_monster.png")
        green_image = pygame.image.load("green_monster.png")
        purple_image = pygame.image.load("purple_monster.png")
        yellow_image = pygame.image.load("yellow_monster.png")
        self.target_monster_images = [blue_image, green_image, purple_image, yellow_image]

        #self.target_monster_type = random.randint(0, 3)
        self.target_monster_image = self.treasure
        self.target_monster_rect = self.target_monster_image.get_rect()
        self.target_monster_rect.centerx = WINDOW_WIDTH // 2
        self.target_monster_rect.top = 30

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
        BRICK_RED = (156, 42, 0)  # Updated frame color

        catch_text = self.font.render("Treasure", True, WHITE)
        catch_rect = catch_text.get_rect(centerx=WINDOW_WIDTH // 2, top=5)

        score_text = self.font.render(f"Score: {self.score}", True, WHITE)
        lives_text = self.font.render(f"Lives: {self.player.lives}", True, WHITE)
        #round_text = self.font.render(f"Current Round: {self.round_number}", True, WHITE)
        time_text = self.font.render(f"Round Time: {self.round_time}", True, WHITE)
        ##warp_text = self.font.render(f"Warps: {self.player.warps}", True, WHITE)
        treasure_text = self.font.render(f"Treasures: {self.treasure_collected}/4", True, WHITE)

        display_surface.blit(catch_text, catch_rect)
        display_surface.blit(score_text, (5, 5))
        display_surface.blit(lives_text, (5, 35))
        #display_surface.blit(round_text, (5, 65))
        display_surface.blit(time_text, (WINDOW_WIDTH - 160, 5))
        ##display_surface.blit(warp_text, (WINDOW_WIDTH - 160, 35))
        display_surface.blit(treasure_text, (WINDOW_WIDTH - 160, 35))

        display_surface.blit(self.target_monster_image, self.target_monster_rect)
        display_surface.blit(self.treasure, self.treasure_rect)
        #pygame.draw.rect(display_surface, BRICK_RED, (WINDOW_WIDTH//2 - 32, 30, 64, 64), 2)
        #pygame.draw.rect(display_surface, (255, 0, 255), (0, MONSTER_ZONE_TOP, WINDOW_WIDTH, MONSTER_ZONE_BOTTOM - MONSTER_ZONE_TOP), 4)

    def check_collisions(self):
        collided_monster = pygame.sprite.spritecollideany(self.player, self.monster_group)
        if collided_monster:
            self.player.die_sound.play()
            self.player.lives -= 1
            if self.player.lives <= 0:
                self.pause_game(f"Final Score: {self.score}", "Press 'Enter' to play again")
                self.reset_game()
            self.player.reset()

        if self.player.rect.colliderect(self.treasure_rect):
            self.success_sound.play()  # Play success sound
            self.score += 500
            self.treasure_collected += 1
            self.increase_difficulty()  # Add more monsters each treasure
            if self.treasure_collected >= 4:
                self.pause_game("You Win!", "Press 'Enter' to play again")
                self.reset_game()
            else:
                self.spawn_treasure()
                self.player.reset()

    def increase_difficulty(self):
        for m_type in range(4):
            self.monster_group.add(Monster(
                random.randint(0, WINDOW_WIDTH - 64),
                random.randint(MONSTER_ZONE_TOP, MONSTER_ZONE_BOTTOM - 64),
                self.target_monster_images[m_type], m_type))

    def start_new_round(self):
        self.score += int(10000 * self.round_number / (1 + self.round_time))
        self.round_time = 0
        self.frame_count = 0
        self.round_number += 1
        self.player.warps += 1
        self.monster_group.empty()
        for i in range(self.round_number):
            for m_type in range(4):
                self.monster_group.add(Monster(
                    random.randint(0, WINDOW_WIDTH - 64),
                    random.randint(MONSTER_ZONE_TOP, MONSTER_ZONE_BOTTOM - 64),
                    self.target_monster_images[m_type], m_type))
        self.choose_new_target()
        self.next_level_sound.play()

    def choose_new_target(self):
        # Always show treasure icon instead of random monster
        self.target_monster_image = self.treasure

    def pause_game(self, main_text, sub_text):
        global running
        WHITE = (255, 255, 255)
        BLACK = (0, 0, 0)
        main_surf = self.font.render(main_text, True, WHITE)
        sub_surf = self.font.render(sub_text, True, WHITE)
        main_rect = main_surf.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2))
        sub_rect = sub_surf.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2 + 64))
        display_surface.fill(BLACK)
        display_surface.blit(main_surf, main_rect)
        display_surface.blit(sub_surf, sub_rect)
        pygame.display.update()
        is_paused = True
        while is_paused:
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                    is_paused = False
                if event.type == pygame.QUIT:
                    is_paused = False
                    running = False

    def reset_game(self):
        self.score = 0
        self.round_number = 0
        self.player.lives = 5
        self.player.warps = 2
        self.player.reset()
        self.treasure_collected = 0
        self.monster_group.empty()
        self.spawn_treasure()
        self.start_new_round()

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.image.load("knight.png")
        self.rect = self.image.get_rect()
        self.rect.centerx = WINDOW_WIDTH // 2
        self.rect.top = 105
        self.lives = 5
        self.warps = 2
        self.velocity = 8
        self.catch_sound = pygame.mixer.Sound("catch.wav")
        self.die_sound = pygame.mixer.Sound("die.wav")
        self.warp_sound = pygame.mixer.Sound("warp.wav")

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

# Main game setup
player_group = pygame.sprite.Group()
player = Player()
player_group.add(player)

monster_group = pygame.sprite.Group()
game = Game(player, monster_group)
game.pause_game("Monster Wrangler", "Press 'Enter' to begin")
game.start_new_round()

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            player.warp()

    display_surface.blit(background_image, (0, 0))
    player_group.update()
    player_group.draw(display_surface)
    monster_group.update()
    monster_group.draw(display_surface)
    game.update()
    game.draw()
    pygame.display.update()
    clock.tick(FPS)

pygame.quit()