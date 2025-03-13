import pygame
import time



# 角色類別
class Character:
    def __init__(self, image_path, position, dialogues):
        self.image = pygame.image.load(image_path)
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
    """ 逐字顯示文字，支援換行，確保文字無底色，對話框仍然白色 """
    x, y = pos
    lines = text.split("\n")  # 依照 \n 手動換行
    displayed_text = [""] * len(lines)  # 已顯示的部分

    total_chars = sum(len(line) for line in lines)  # 計算所有字數
    current_chars = 0  # 當前顯示的字數
    text_complete = False  # 是否已顯示完整句子
    
    dialogue_box = pygame.Rect(50, 400, 700, 150)  # (x, y, width, height)
    pygame.draw.rect(surface, (255, 255, 255), dialogue_box)  # 白色對話框
    pygame.draw.rect(surface, (0, 0, 0), dialogue_box, 3)  # 黑色外框

    while not text_complete:
        y_offset = y

        for idx, line in enumerate(displayed_text):
            rendered_text = font.render(line, True, text_color)  # **確保文字本身沒有底色**
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
            return  # **回傳，讓 `run_scene()` 決定何時切換角色**




def scene_1():
    """ 第一場景：小明 & 老闆 """
    screen_center_x = 800 // 2  # 螢幕寬度的一半
    character_width = 300  # 角色圖片寬度（假設角色圖片大小是 150x150）
    character_height = 300
    characters = [
        Character("character1.png", (screen_center_x - character_width // 2, 150), [
            "北斗紅磚市場，一座充滿歷史氣息的建築\n"
            "市場裡仍然有老攤販擺攤、柑仔店販售傳統零食！\n" 
            "理髮廳的師傅依舊熟練地為客人修剪頭髮",
            "但奇怪的是，每天市場內的場景都是一模一樣的——攤販賣著同樣的春捲，\n"
            "柑仔店的老闆娘總是找不到某個硬幣\n"
            "理髮師每天在相同的時間擦拭鏡子，低聲說著：「今天又是這一天……」"
        ]),
        Character("shopkeeper.png", (screen_center_x - character_width // 2, 150), [
            "我們這裡的紅磚市場可是百年歷史的地標！",
            "但你有沒有發現……每天都好像重複著同樣的事情？",
            "我每天都在找一枚硬幣，可是它永遠找不到……"
        ])
    ]
    
    background = pygame.image.load("background1.jpg")
    background = pygame.transform.scale(background, (800, 600))
    
    return characters, background  # 回傳角色列表 & 背景


def scene_2():
    """ 第二場景：小美 & 老闆 """
    screen_center_x = 800 // 2  # 螢幕寬度的一半
    character_width = 300  # 角色圖片寬度（假設角色圖片大小是 150x150）
    character_height = 300

    characters = [
        Character("character2.png", (screen_center_x - character_width // 2, 150), [
            "新新理髮廳是一間家傳三代的老理髮店，位於老街的一角", 
            "外頭的招牌早已斑駁褪色，依稀能看出過去燙髮、剃鬍的廣告字樣，\n象徵著那個年代的時髦與興盛", 
            "然而，因為後代無人接手，這家店的故事也即將畫下句點，成為被時光遺忘的角落"
        ]),
        Character("barber.png", (screen_center_x - character_width // 2, 150), [
            "我已經在這間店工作了 40 年，見證了無數客人從年輕變成老爺爺", 
            "每次拿起剃刀，彷彿還能聽見當年的熱鬧聲", 
            "可是，現在的年輕人已經不再來這裡了……"
        ])
    ]
    
    background = pygame.image.load("background2.jpg")
    background = pygame.transform.scale(background, (800, 600))
    
    return characters, background  # 回傳角色列表 & 背景


# 場景列表（可以自由增加新場景）
scenes = [scene_1, scene_2]
