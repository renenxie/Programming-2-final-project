import json
import pygame
import os

# 直接從當前目錄載入設定
with open('images.json', 'r') as f:
    config = json.load(f)

# 畫面設定
SCREEN_WIDTH = config['screen']['width']
SCREEN_HEIGHT = config['screen']['height']

# 對話框設定
DIALOGUE_WIDTH = config['dialogue_box']['width']
DIALOGUE_HEIGHT = config['dialogue_box']['height']

# 按鈕設定
BUTTON_WIDTH = config['buttons']['width']
BUTTON_HEIGHT = config['buttons']['height']

# 圖片路徑
IMAGE_PATHS = config['images']

def init_images():
    """初始化圖片，保持原始比例縮放並置中於畫面中心"""
    images = {}
    for view, path in IMAGE_PATHS.items():
        # 修改路徑，加上 images/ 前綴
        image_path = os.path.join('images', path)
        original_image = pygame.image.load(image_path)
        
        # 計算保持原始比例的縮放尺寸
        original_width, original_height = original_image.get_size()
        ratio = max(SCREEN_WIDTH / original_width, SCREEN_HEIGHT / original_height)
        new_width = int(original_width * ratio)
        new_height = int(original_height * ratio)
        
        # 縮放圖片
        scaled_image = pygame.transform.scale(original_image, (new_width, new_height))
        
        # 計算置中位置
        x = (SCREEN_WIDTH - new_width) // 2
        y = (SCREEN_HEIGHT - new_height) // 2
        
        # 儲存圖片和位置
        images[view] = {
            'image': scaled_image,
            'position': (x, y),
            'size': (new_width, new_height)  # 儲存縮放後的尺寸
        }
          
    return images

# 視角順序 (循環切換)
VIEW_ORDER = ['front', 'right', 'back']