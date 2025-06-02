import pygame
import time
import json
import os
from settings import SCREEN_WIDTH, SCREEN_HEIGHT, DIALOGUE_WIDTH, DIALOGUE_HEIGHT

# 角色類別
class Character:
    def __init__(self, image_path, position, dialogues):
        full_path = os.path.join('images', image_path)
        self.image = pygame.image.load(full_path)
        self.image = pygame.transform.scale(self.image, (300, 300))
        self.rect = self.image.get_rect(topleft=position)
        self.dialogues = dialogues  # 該角色的所有對話
        self.current_dialogue_index = 0  # 當前對話索引

    def draw(self, screen):
        """ 繪製角色 """
        screen.blit(self.image, self.rect.topleft)

    def get_current_dialogue(self):
        """ 取得當前角色的對話 """
        return self.dialogues[self.current_dialogue_index]

    def next_dialogue(self):
        """ 切換到下一句對話，若超過則返回 False """
        self.current_dialogue_index += 1
        if self.current_dialogue_index >= len(self.dialogues):  # 若對話結束
            return False
        return True




def draw_text(surface, text, pos, font, reveal_speed=50, text_color=(0, 0, 0)):
    """改進的文字顯示函數：動畫只播放一次，點擊後才繼續"""
    x, y = pos
    lines = text.split("\n")
    displayed_text = [""] * len(lines)
    total_chars = sum(len(line) for line in lines)
    current_chars = 0
    text_complete = False
    
    # 對話框設定
    # 對話框設定
    dialogue_box = pygame.Rect(
        (SCREEN_WIDTH  - DIALOGUE_WIDTH) // 2,
        SCREEN_HEIGHT - 200,
        DIALOGUE_WIDTH,
        DIALOGUE_HEIGHT
    )  # (x, y, width, height)
    border_radius = 15  # 圓角半徑
    shadow_offset = 5  # 陰影偏移量
    
    # 創建一個帶有alpha通道的Surface來實現半透明
    dialog_surface = pygame.Surface((dialogue_box.width, dialogue_box.height), pygame.SRCALPHA)
    
    # 繪製陰影效果（半透明黑色）
    shadow_rect = pygame.Rect(
        shadow_offset, 
        shadow_offset, 
        dialogue_box.width, 
        dialogue_box.height
    )
    pygame.draw.rect(
        dialog_surface, 
        (0, 0, 0, 100),  # 半透明黑色
        shadow_rect, 
        border_radius=border_radius
    )
    
    # 繪製半透明白色對話框 (RGBA顏色，A=200)
    pygame.draw.rect(
        dialog_surface, 
        (255, 255, 255, 150),  # 半透明白色
        (0, 0, dialogue_box.width, dialogue_box.height),
        border_radius=border_radius
    )
    
    # 繪製邊框 (半透明深灰色)
    pygame.draw.rect(
        dialog_surface, 
        (50, 50, 50, 200),  # 半透明深灰色邊框
        (0, 0, dialogue_box.width, dialogue_box.height),
        width=3, 
        border_radius=border_radius
    )
    
    # 將對話框Surface繪製到主畫面上
    surface.blit(dialog_surface, (dialogue_box.x, dialogue_box.y))

    while not text_complete:
        y_offset = y

        # 在對話框上繪製文字
        for idx, line in enumerate(displayed_text):
            rendered_text = font.render(line, True, text_color)
            # 文字位置要考慮對話框的偏移
            surface.blit(rendered_text, (x, y_offset))
            y_offset += font.get_height()

        pygame.display.update()

        # 逐字顯示
        if current_chars < total_chars:
            for i in range(len(lines)):  # 遍歷每一行
                if len(displayed_text[i]) < len(lines[i]):  # 確保還有字要顯示
                    displayed_text[i] = lines[i][:len(displayed_text[i]) + 1]  # 增加一個字
                    current_chars += 1
                    pygame.time.delay(reveal_speed)  # 控制顯示速度
                    break  # 一次只顯示一個字
        else:
            text_complete = True  # 文字完全顯示完畢
            return

def draw_text2(surface, text, pos, font, reveal_speed=50, text_color=(0, 0, 0)):
    """改進的文字顯示函數：動畫只播放一次，點擊後才繼續"""
    x, y = pos
    lines = text.split("\n")
    displayed_text = [""] * len(lines)
    total_chars = sum(len(line) for line in lines)
    current_chars = 0
    text_complete = False
    
    # 對話框設定
    dialogue_box = pygame.Rect(
        (SCREEN_WIDTH  - DIALOGUE_WIDTH) // 2,
        SCREEN_HEIGHT - 200,
        DIALOGUE_WIDTH,
        DIALOGUE_HEIGHT
    )  # (x, y, width, height)
    border_radius = 15  # 圓角半徑
    shadow_offset = 5  # 陰影偏移量
    
    # 創建一個帶有alpha通道的Surface來實現半透明
    dialog_surface = pygame.Surface((dialogue_box.width, dialogue_box.height), pygame.SRCALPHA)
    
    # 繪製陰影效果（半透明黑色）
    shadow_rect = pygame.Rect(
        shadow_offset, 
        shadow_offset, 
        dialogue_box.width, 
        dialogue_box.height
    )
    pygame.draw.rect(
        dialog_surface, 
        (0, 0, 0, 100),  # 半透明黑色
        shadow_rect, 
        border_radius=border_radius
    )
    
    # 繪製半透明白色對話框 (RGBA顏色，A=200)
    pygame.draw.rect(
        dialog_surface, 
        (255, 255, 255, 150),  # 半透明白色
        (0, 0, dialogue_box.width, dialogue_box.height),
        border_radius=border_radius
    )
    
    # 繪製邊框 (半透明深灰色)
    pygame.draw.rect(
        dialog_surface, 
        (50, 50, 50, 200),  # 半透明深灰色邊框
        (0, 0, dialogue_box.width, dialogue_box.height),
        width=3, 
        border_radius=border_radius
    )
    
    # 將對話框Surface繪製到主畫面上
    surface.blit(dialog_surface, (dialogue_box.x, dialogue_box.y))

    while not text_complete:
        y_offset = y

        # 在對話框上繪製文字
        for idx, line in enumerate(displayed_text):
            rendered_text = font.render(line, True, text_color)
            # 文字位置要考慮對話框的偏移
            surface.blit(rendered_text, (x, y_offset))
            y_offset += font.get_height()

        pygame.display.update()

        # 繪製所有文字（不再逐字顯示）
    y_offset = y
    for line in lines:
        rendered_text = font.render(line, True, text_color)
        surface.blit(rendered_text, (x, y_offset))
        y_offset += font.get_height()
    
    pygame.display.update()
    return True  # 表示文字已完整顯示
        
        
def load_scene_resources(scene_json):
    """ 載入場景資源的共用函數，從 JSON 檔案讀取角色和多個背景 """
    # 從 json/ 資料夾讀取 JSON 檔案
    json_path = os.path.join('json', scene_json)
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    screen_center_x = SCREEN_WIDTH // 2
    character_width = 300
    characters = []
    
    # 載入角色
    for i, char_data in enumerate(data["characters"]):
        image_path = char_data["name"]
        dialogues = char_data["dialogues"]
        pos_x = screen_center_x - character_width // 2 + i * 50
        pos = (pos_x, 150)
        characters.append(Character(image_path, pos, dialogues))

    # 載入多個背景（每個背景包含圖片路徑和播放時間）
    backgrounds = []
    for bg_data in data.get("background", []):
        bg_info = {
            "image": None,
            "duration": bg_data.get("duration", 0)  # 預設播放時間為0
        }
        
        bg_path = os.path.join('images', bg_data["image"])
        try:
            bg_info["image"] = pygame.image.load(bg_path)
            bg_info["image"] = pygame.transform.scale(bg_info["image"], (SCREEN_WIDTH, SCREEN_HEIGHT))
        except pygame.error:
            print(f"無法載入背景圖片: {bg_path}")
            bg_info["image"] = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            bg_info["image"].fill((0, 0, 100))  # 深藍色背景
        
        backgrounds.append(bg_info)
    
    # 如果沒有背景，使用預設背景
    if not backgrounds:
        default_bg = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        default_bg.fill((0, 0, 100))
        backgrounds.append({"image": default_bg, "duration": 0})
    
    return characters, backgrounds
