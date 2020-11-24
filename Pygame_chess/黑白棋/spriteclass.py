import pygame

def ini_sprite(Sprite, ini_pos, simple_obj=None, pic_path=None, font_obj=None):
    """
    初始化pygame.sprite.Sprite物件
    Sprite: 必順是繼承pygame.sprite.Sprite的class
    simple_obj(tuple): (物件之矩形框大小(tuple of 2), 物件顏色(RGB))
    ini_pos(tuple): 初始x,y座標(左上角)
    picture_path: 若存在，則讀取指定圖檔
    font_obj(tuple): (字型, 字體大小, 文字顏色(RGB), 文字內容)
    """
    pygame.sprite.Sprite.__init__(Sprite)
    if simple_obj:
        size, color = simple_obj
        Sprite.image = pygame.Surface(size)
        Sprite.image.fill(color)
    if pic_path:
        Sprite.image = pygame.image.load(pic_path)
    if font_obj:
        font, font_size, font_color, text = font_obj
        Sprite.font = pygame.font.Font(font, font_size)
        Sprite.image = Sprite.font.render(text, True, font_color)
    Sprite.image.convert()
    Sprite.rect = Sprite.image.get_rect()
    Sprite.rect.topleft = ini_pos
    
# text display for UI
class text(pygame.sprite.Sprite):
    def __init__(self, text, font, size, pos, color):
        ini_sprite(self, pos, font_obj=(font, size, color, text))
        
# buttons for UI
class my_button(pygame.sprite.Sprite):
    def __init__(self, pos, size, color, font_obj):
        """
        font_obj(tuple): (字型, 字體大小, 文字顏色(RGB), 文字內容)
        """
        ini_sprite(self, pos, simple_obj=(size, color))
        pygame.draw.rect(self.image, (0,0,0), (0, 0, *size), 1) #繪製黑色邊框
        font, font_size, font_color, text = font_obj
        my_font = pygame.font.Font(font, font_size)
        msg = my_font.render(text, True, font_color)
        
        msg_rect = msg.get_rect()
        msg_rect.center = self.image.get_rect().center
        self.image.blit(msg, msg_rect.topleft)  #繪製訊息，自動將文字置中



# board tiles
class tile(pygame.sprite.Sprite):
    def __init__(self, xInd, yInd, stone_type='.'):
        self.xInd, self.yInd = xInd, yInd
        ini_sprite(self, self.__tile_coord(xInd, yInd), pic_path= "sprites/tile.png")
        if stone_type!=0:
            disks = {1: "sprites/b_disk.png", 2:"sprites/w_disk.png"}
            image = pygame.image.load(disks[stone_type])
            self.image.blit(image, (4,4))
    
    def __tile_coord(self, x,y):
        return (236+x*72, 72+y*72)

    def update(self, stone_type):
        image = pygame.image.load("sprites/tile.png")
        self.image.blit(image, (0,0))
        disks = {1: "sprites/b_disk.png", 2:"sprites/w_disk.png"}
        if stone_type!=0:
            image = pygame.image.load(disks[stone_type])
            self.image.blit(image, (4,4))
            
    def draw_hint(self):
        center = self.image.get_size()[0]//2
        pygame.draw.circle(self.image, (0,0,0), (center, center), center, 1) #繪製黑色邊框
    

class chessBoard():
    def __init__(self, board):
        self.tiles_group = pygame.sprite.Group()
        self.width, self.height = len(board[0]), len(board)
        self.tiles = [[tile(i, j, board[i][j]) for j in range(self.width)] for i in range(self.height)]
        self.tiles_group.add(self.tiles)
                    
    def update(self, board, hints = None):
        for i in range(self.height):
            for j in range(self.width):
                self.tiles[i][j].update(board[i][j])
        if hints:
            for x,y in hints:
                self.tiles[x][y].draw_hint()
    
    def draw(self, screen):
        self.tiles_group.draw(screen)
        