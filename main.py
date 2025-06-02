import pygame
import sys
from settings import SCREEN_WIDTH, SCREEN_HEIGHT, init_images, VIEW_ORDER
from buttons import draw_arrow_button, create_buttons
from transitions import slide_transition
from scene_manager import SceneManager
from scene0 import Scene0
from explore0 import Explore0
from scene1 import Scene1
from scene2 import Scene2
from scene3 import Scene3
from inventory import Inventory
from zoom_animation import ZoomAnimation


# 初始化
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
inventory = Inventory(SCREEN_WIDTH, SCREEN_HEIGHT)
pygame.display.set_caption("北斗紅磚市場的無錯循環")

# 載入資源
images = init_images()
left_btn, right_btn = create_buttons()
current_view = 'front'

# 載入店主圖片
shopkeeper_img = pygame.image.load("images/shopkeeper.png").convert_alpha()
# 調整大小並居中
shopkeeper_img = pygame.transform.scale(shopkeeper_img, (400, 400))
shopkeeper_rect = shopkeeper_img.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2))

# 場景系統初始化
# 設定字型（支援繁體中文）
font = pygame.font.Font("標楷體.ttf", 24)
scene_manager = SceneManager(screen, font)

def get_next_view(current, direction):
    idx = VIEW_ORDER.index(current)
    if direction == "right":
        return VIEW_ORDER[(idx + 1) % len(VIEW_ORDER)]
    else:
        return VIEW_ORDER[(idx - 1) % len(VIEW_ORDER)]

def check_shopkeeper_click(mouse_pos):
    """檢查是否點擊了店主圖片"""
    return shopkeeper_rect.collidepoint(mouse_pos)

def check_scene_trigger(mouse_pos):
    """檢查是否點擊了觸發場景的區域"""
    center_rect = pygame.Rect(
        SCREEN_WIDTH//2 - 100, 
        SCREEN_HEIGHT//2 - 100,
        200, 200
    )
    return center_rect.collidepoint(mouse_pos)

test = True

# 主循環
clock = pygame.time.Clock()
running = True
scene0_completed = False | test  # 新增標記變量
explore0_completed = False | test
scene2_completed = False | test
scene3_completed = False  # 初始為未完成

zoom_animator = ZoomAnimation()  # 這行很重要，要在主循環外初始化
arrows_unlocked = False  # 箭頭是否解鎖
show_unlock_message = False  # 是否顯示解鎖訊息
message_timer = 0  # 訊息顯示計時器


# 遊戲開始時先執行 Scene0
if not scene0_completed:
    scene0 = Scene0(screen, inventory)
    scene0_completed = scene0.run()

if scene0_completed and not explore0_completed:
    explore0 = Explore0(screen, inventory)
    explore0_completed = explore0.run()

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        # 只有在 scene0 完成後才偵測點擊事件
        elif explore0_completed and event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            zoom_animator = ZoomAnimation()

            if not arrows_unlocked and check_shopkeeper_click(mouse_pos) and current_view == 'front':
                arrows_unlocked = True
                show_unlock_message = True
                message_timer = 60  # 約3秒 (60 FPS)
                
            elif arrows_unlocked and left_btn.collidepoint(mouse_pos):
                new_view = get_next_view(current_view, "left")
                slide_transition(
                    screen, 
                    images[current_view]['image'], 
                    images[new_view]['image'], 
                    "left"
                )
                current_view = new_view
                
            elif arrows_unlocked and right_btn.collidepoint(mouse_pos):
                new_view = get_next_view(current_view, "right")
                slide_transition(
                    screen,
                    images[current_view]['image'],
                    images[new_view]['image'],
                    "right"
                )
                current_view = new_view

            # elif check_scene_trigger(mouse_pos) and current_view == 'front':
            #     scene1 = Scene1(screen, inventory)
            #     scene1.run()

            elif check_scene_trigger(mouse_pos) and current_view == 'right':
                scene2 = Scene2(screen, inventory)
                scene2_completed = scene2.run()   

            elif check_scene_trigger(mouse_pos) and current_view == 'back' and scene2_completed:
                if not zoom_animator.active:
                    zoom_animator.start(images['back']['image'])      

    # 更新計時器
    if message_timer > 0:
        message_timer -= 1
    else:
        show_unlock_message = False

    # 繪製
    screen.fill((255, 255, 255))

    if zoom_animator.active and current_view == 'back':
        animation_completed = zoom_animator.update(screen, images['back']['position'])
        if animation_completed and zoom_animator.should_trigger_scene:
            scene3 = Scene3(screen, inventory)
            scene3_completed = scene3.run()
            zoom_animator.reset()
    else:
        current_image_data = images[current_view]
        screen.blit(current_image_data['image'], current_image_data['position'])
        
        # 在front視角顯示店主圖片
        if current_view == 'front':
            screen.blit(shopkeeper_img, shopkeeper_rect)

        # 在back視角顯示解鎖提示（如果未解鎖）
        if current_view == 'back' and not scene2_completed:
            back_lock_font = pygame.font.Font("標楷體.ttf", 36)  # 專門用於back視角解鎖提示的字型

            # 創建更大的半透明表面 (600x300)
            overlay_width, overlay_height = 600, 300
            overlay = pygame.Surface((overlay_width, overlay_height), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))  # 半透明黑色背景
            
            # 添加邊框效果
            border_size = 5
            pygame.draw.rect(overlay, (100, 100, 100, 200), 
                        (0, 0, overlay_width, overlay_height), border_size)
            
            # 繪製到屏幕上（居中）
            screen.blit(overlay, (SCREEN_WIDTH//2 - overlay_width//2, 
                                SCREEN_HEIGHT//2 - overlay_height//2))
            
            # 繪製更大的文字
            text = back_lock_font.render("此區域尚未解鎖", True, (255, 255, 255))
            text_rect = text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
            
            # 為文字添加陰影效果
            shadow = back_lock_font.render("此區域尚未解鎖", True, (0, 0, 0, 150))
            screen.blit(shadow, (text_rect.x + 3, text_rect.y + 3))
            
            screen.blit(text, text_rect)
    
    # 只有在解鎖後才顯示箭頭
    if arrows_unlocked:
        draw_arrow_button(screen, left_btn, "left")
        draw_arrow_button(screen, right_btn, "right")
    
    # 顯示解鎖訊息
    if show_unlock_message:
        message = font.render("新增兩個探索區域", True, (255, 255, 255))
        message_rect = message.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT - 50))
        # 添加背景框
        pygame.draw.rect(screen, (0, 0, 0), (message_rect.x - 10, message_rect.y - 10, 
                                           message_rect.width + 20, message_rect.height + 20))
        screen.blit(message, message_rect)
    
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()
# import pygame
# from monster_wrangler_class import MonsterWranglerGame
# from catch_the_clown_class import CatchTheClownGame
# from feed_the_dragon_class import FeedTheDragonGame

# def main():
#     pygame.init()
#     pygame.mixer.init()
   

#     # print("▶ 執行 Monster Wrangler")
#     # MonsterWranglerGame().run()

#     # print("▶ 執行 Catch the Clown")
#     # CatchTheClownGame().run()

#     print("▶ 執行 Feed the Dragon")
#     FeedTheDragonGame().run()

#     pygame.quit()
#     print("所有遊戲結束")



if __name__ == "__main__":
    main()

