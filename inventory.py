import pygame

class Inventory:
    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.items = []
        self.selected_index = -1
        self.slot_size = 40  # 每個物品格的大小
        self.slot_margin = 15  # 物品格之間的間距
        self.item_ids = []  # 新增：儲存物品ID
        self.item_names = []  # 儲存物品名稱
        
        # 計算物品欄的總寬度（基於最大容量 6 個物品）
        self.max_items = 3
        total_width = self.max_items * (self.slot_size + self.slot_margin) - self.slot_margin + 20  # 20 是左右 padding
        
        # 設定物品欄的 rect（置中於螢幕底部）
        self.rect = pygame.Rect(
            (screen_width - total_width) // 2,  # x 置中
            screen_height - self.slot_size - 20,  # y 位於底部
            total_width,  # 寬度
            self.slot_size + 20  # 高度
        )

        self.font = pygame.font.Font("msjh.ttc", 20)
    
    def add_item(self, item_image, item_id, item_name):
        """添加物品到物品欄（新增item_id參數）"""
        if len(self.items) < self.max_items:
            scaled_item = pygame.transform.scale(item_image, (self.slot_size-10, self.slot_size-10))
            self.items.append(scaled_item)
            self.item_ids.append(item_id)  # 記錄物品ID
            self.item_names.append(item_name)  # 記錄物品名稱
            return True
        return False
    
    def handle_click(self, pos):
        """處理物品欄點擊事件"""
        if not self.rect.collidepoint(pos):
            self.selected_index = -1
            return
        
        x_offset = pos[0] - self.rect.x
        self.selected_index = x_offset // (self.slot_size + self.slot_margin)
        
        if self.selected_index >= len(self.items):
            self.selected_index = -1
    
    def draw(self, screen):
        """繪製物品欄（縮小置中版）"""
        inventory_surface = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
        
        # 陰影參數
        shadow_offset = 5
        border_radius = 10
        
        # 繪製陰影效果（半透明黑色）
        shadow_rect = pygame.Rect(
            shadow_offset, 
            shadow_offset, 
            self.rect.width, 
            self.rect.height
        )
        pygame.draw.rect(
            inventory_surface, 
            (0, 0, 0, 100),  # 半透明黑色
            shadow_rect, 
            border_radius=border_radius
        )
        ########################################
        # 繪製背景（縮小後的矩形）
        # 繪製半透明背景 (RGBA顏色，A=150)
        pygame.draw.rect(
            inventory_surface, 
            (120, 120, 140, 150),  # 半透明背景色
            (0, 0, self.rect.width, self.rect.height),
            border_radius=border_radius
        )
        
        # 繪製邊框 (半透明深灰色)
        pygame.draw.rect(
            inventory_surface, 
            (80, 80, 100, 200),  # 半透明深灰色邊框
            (0, 0, self.rect.width, self.rect.height),
            width=2, 
            border_radius=border_radius
        )
        screen.blit(inventory_surface, (self.rect.x, self.rect.y))

        ##############################
        # 繪製物品格
        for i in range(self.max_items):  # 繪製 6 個格子（即使沒有物品）
            x = self.rect.x + 10 + i * (self.slot_size + self.slot_margin)
            y = self.rect.y + 10
            slot_rect = pygame.Rect(x, y, self.slot_size, self.slot_size)
            
            # 繪製物品格邊框 (半透明)
            pygame.draw.rect(
                screen, 
                (80, 80, 100, 200),  # 半透明邊框
                slot_rect, 
                width=2
            )
            
            # 如果有物品，繪製物品圖標
            if i < len(self.items):
                # 注意：物品圖標需要處理透明度
                item_with_alpha = self.items[i].copy()
                item_with_alpha.set_alpha(200)  # 設置物品圖標透明度
                screen.blit(item_with_alpha, (x + 5, y + 5))  # 物品圖標稍微內縮
                
                # 繪製選中框 (半透明白色)
                if i == self.selected_index:
                    border_rect = pygame.Rect(x-3, y-3, self.slot_size+6, self.slot_size+6)
                    pygame.draw.rect(
                        screen, 
                        (255, 255, 255, 200),  # 半透明白色
                        border_rect, 
                        width=3
                    )            
        # 繪製選中物品的名稱（左下角）
        if 0 <= self.selected_index < len(self.item_names):
            item_name = self.item_names[self.selected_index]
            text_surface = self.font.render(item_name, True, (255, 255, 255))
            text_rect = text_surface.get_rect(bottomleft=(10, self.screen_height - 10))
            pygame.draw.rect(screen, (0, 0, 0, 128), text_rect.inflate(10, 5))  # 半透明背景
            screen.blit(text_surface, text_rect)
            
    def clear(self):
        """清空物品欄中的所有物品（包括名稱和ID）"""
        self.items = []
        self.item_ids = []
        self.item_names = []
        self.selected_index = -1