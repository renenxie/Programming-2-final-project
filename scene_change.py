import pygame

def wait_for_player_input():
    """等待玩家按下 Enter 或滑鼠點擊"""
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                waiting = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                waiting = False

def handle_scene_transition(current_char, characters, current_scene):
    """
    處理角色和場景的切換
    返回: (新的場景索引, 新的角色索引, 是否需要重新載入場景)
    """
    if not current_char.next_dialogue():  # 如果當前角色對話結束
        current_character_index = characters.index(current_char) + 1
        
        if current_character_index < len(characters):  # 還有下一個角色
            return current_scene, current_character_index, False
        else:  # 所有角色對話結束
            return -1, -1, False  # 使用 -1 表示場景完全結束
    
    return current_scene, characters.index(current_char), False