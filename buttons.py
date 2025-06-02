import pygame
import os
from settings import SCREEN_WIDTH, SCREEN_HEIGHT, BUTTON_WIDTH, BUTTON_HEIGHT

# 初始化 Pygame 和視窗
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

# 載入箭頭圖片（假設圖片存在於相同目錄下）
try:
    left_arrow_img = pygame.image.load("images/left_arrow.png").convert_alpha()
    right_arrow_img = pygame.image.load("images/right_arrow.png").convert_alpha()
    # 調整圖片大小以符合按鈕尺寸
    left_arrow_img = pygame.transform.scale(left_arrow_img, (BUTTON_WIDTH, BUTTON_HEIGHT))
    right_arrow_img = pygame.transform.scale(right_arrow_img, (BUTTON_WIDTH, BUTTON_HEIGHT))
    use_images = True
except:
    print("無法載入箭頭圖片，將使用預設的紅色箭頭")
    use_images = False

def draw_arrow_button(screen, rect, direction):
    if use_images:
        # 使用圖片繪製箭頭
        if direction == "left":
            screen.blit(left_arrow_img, rect)
        else:  # right
            screen.blit(right_arrow_img, rect)
    else:
        # 保留原有的紅色箭頭程式碼作為備用
        color = (255, 0, 0)  # 紅色箭頭
        if direction == "left":
            points = [(rect.right, rect.top), (rect.left, rect.centery), (rect.right, rect.bottom)]
        else:  # right
            points = [(rect.left, rect.top), (rect.right, rect.centery), (rect.left, rect.bottom)]
        pygame.draw.polygon(screen, color, points)

def create_buttons():
    left_rect = pygame.Rect(
        50, 
        SCREEN_HEIGHT // 2 - BUTTON_HEIGHT // 2,
        BUTTON_WIDTH,
        BUTTON_HEIGHT
    )
    right_rect = pygame.Rect(
        SCREEN_WIDTH - 50 - BUTTON_WIDTH,
        SCREEN_HEIGHT // 2 - BUTTON_HEIGHT // 2,
        BUTTON_WIDTH,
        BUTTON_HEIGHT
    )
    return left_rect, right_rect