import pygame
from scenes import scenes, draw_text  # 從 scenes.py 匯入場景函數 & 工具函數

# 初始化 Pygame
pygame.init()

# 設定畫面大小
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("北斗紅磚市場的無錯循環")

# 設定字型（支援繁體中文）
font = pygame.font.Font("msjh.ttc", 18)  # 使用支援繁體字的字型

# 設定對話框
dialogue_box = pygame.Rect(50, 400, 700, 150)  # (x, y, width, height)

current_scene = 0  # 當前場景索引


def run_scene(scene_id):
    """ 執行指定場景（支援逐字顯示 & 角色切換） """
    global current_scene
    characters, background = scenes[scene_id]()  # 取得該場景的角色列表與背景
    current_character = 0  # 當前角色索引
    show_character = True  # 是否顯示當前角色

    running = True
    while running:
        screen.blit(background, (0, 0))  # 顯示背景

        # 只顯示當前角色
        if show_character:
            characters[current_character].draw(screen)
        '''''
        # 繪製對話框
        pygame.draw.rect(screen, (255, 255, 255), dialogue_box)  # 白色對話框
        pygame.draw.rect(screen, (0, 0, 0), dialogue_box, 3)  # 黑色外框
        '''''
        # 取得當前角色的對話，並逐字顯示
        current_char = characters[current_character]
        draw_text(screen, current_char.get_current_dialogue(), (dialogue_box.x + 20, dialogue_box.y + 30), font, reveal_speed=30)

        pygame.display.update()

        # **等待玩家按下 Enter 才切換角色**
        waiting_for_enter = True
        while waiting_for_enter:
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                    waiting_for_enter = False  # `Enter` 按下後繼續
                elif event.type == pygame.QUIT:
                    pygame.quit()
                    exit()

        # **處理角色切換**
        if not current_char.next_dialogue():  # 如果當前角色對話結束
            current_character += 1  # 切換到下一個角色
            if current_character < len(characters):  # 若還有下一個角色
                show_character = False  # 先隱藏角色
                pygame.time.delay(500)  # 延遲 0.5 秒，模擬消失效果
                show_character = True  # 顯示新角色
            else:  # 所有角色對話結束，進入下一場景
                current_scene += 1  
                if current_scene >= len(scenes):  # 循環回到第一場景
                    current_scene = 0
                run_scene(current_scene)  # 進入下一個場景
                return


# 運行第一個場景
run_scene(current_scene)
pygame.quit()