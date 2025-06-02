import pygame
from monster_wrangler_class import MonsterWranglerGame
from catch_the_clown_class import CatchTheClownGame
from feed_the_dragon_class import FeedTheDragonGame

def main():
    pygame.init()
    pygame.mixer.init()
   

    # print("▶ 執行 Monster Wrangler")
    # MonsterWranglerGame().run()

    # print("▶ 執行 Catch the Clown")
    # CatchTheClownGame().run()

    print("▶ 執行 Feed the Dragon")
    FeedTheDragonGame().run()

    pygame.quit()
    print("所有遊戲結束")

if __name__ == "__main__":
    main()
