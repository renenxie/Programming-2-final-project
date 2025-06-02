import pygame
from settings import SCREEN_WIDTH, SCREEN_HEIGHT
delaytime = 23

def slide_transition(screen, current_image, new_image, direction):
    slide_speed = 20
    current_rect = current_image.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
    new_rect = new_image.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))

    if direction == "right":
        new_rect.left = SCREEN_WIDTH
        while new_rect.centerx > SCREEN_WIDTH // 2:
            screen.fill((255, 255, 255))
            screen.blit(current_image, current_rect)
            screen.blit(new_image, new_rect)
            pygame.display.flip()
            current_rect.x -= slide_speed
            new_rect.x -= slide_speed
            pygame.time.delay(delaytime)
    elif direction == "left":
        new_rect.right = 0
        while new_rect.centerx < SCREEN_WIDTH // 2:
            screen.fill((255, 255, 255))
            screen.blit(current_image, current_rect)
            screen.blit(new_image, new_rect)
            pygame.display.flip()
            current_rect.x += slide_speed
            new_rect.x += slide_speed
            pygame.time.delay(delaytime)

    # 最終位置
    screen.blit(new_image, (0, 0))
    pygame.display.flip()