import json
import pygame
import os

# 直接從當前目錄載入設定
with open('images.json', 'r') as f:
    config = json.load(f)

# 畫面設定
WINDOW_WIDTH = config['screen']['width']
WINDOW_HEIGHT = config['screen']['height']
FPS = 60

# 對話框設定
DIALOGUE_WIDTH = config['dialogue_box']['width']
DIALOGUE_HEIGHT = config['dialogue_box']['height']

# 按鈕設定
BUTTON_WIDTH = config['buttons']['width']
BUTTON_HEIGHT = config['buttons']['height']

# 圖片路徑
IMAGE_PATHS = config['images']

