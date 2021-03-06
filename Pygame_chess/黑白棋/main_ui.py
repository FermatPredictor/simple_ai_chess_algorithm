import pygame

import spriteclass as sc
import reversifunc as rf
import globalvar as gv

import os
from datetime import datetime

pygame.init()

screen = pygame.display.set_mode((gv.WIDTH, gv.HEIGHT))
pygame.display.set_caption('Reversi')

def time_now():
    return datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

# menu screen
def Intro():
    gv.P1_ai, gv.P2_ai = 0, 0
    texts = pygame.sprite.Group()
    buttons = pygame.sprite.Group()

    gameTitle = sc.text('REVERSI', gv.NEXT, 110, (260, 50), gv.GOLD)
    chooseDiff = sc.text('Choose Difficulty', gv.HELV, 40, (320, 300), gv.GREY)
    
    my_buttons = [None]*3
    color_dict = {0:gv.GREEN, 1:gv.YELLOW, 2:gv.ORANGE}
    diff_dict = {0:'Easy', 1:'Normal', 2:'Hard'}
    for i in range(3):
        my_buttons[i] = sc.my_button((200*(i+1), 400),(150, 70), color_dict[i], (gv.HELV, 30, gv.BLACK, f'{diff_dict[i]}'))
        buttons.add(my_buttons[i])

    texts.add(gameTitle, chooseDiff)

    while True:
        for evi in pygame.event.get():
            if evi.type == pygame.QUIT:
                pygame.display.quit()
            if evi.type == pygame.MOUSEBUTTONDOWN:
                for i in range(3):
                    if my_buttons[i].rect.collidepoint(pygame.mouse.get_pos()):
                        InGame()
                        
        screen.fill(gv.BROWN)
        buttons.draw(screen)
        texts.draw(screen)
        pygame.display.update()



"""
棋盤座標有兩種表示法:
row_column and x_y，
下棋邏輯統一用row_column，
ui_board統一用x,y座標
"""
def InGame():
    game = rf.reversi_init_game(8,8)

    texts = pygame.sprite.Group()
    buttons = pygame.sprite.Group()
    ui_board = sc.chessBoard(game.get_board())
    
    
    button_setting = [('Retry',gv.YELLOW) ,
                      ('Menu', gv.ORANGE),
                      ('Edit', gv.YELLOW),
                      ('Play', gv.ORANGE),
                      ('Pass', gv.GREEN),
                      ('Back', gv.YELLOW),
                      ('Next', gv.ORANGE),
                      ('Save', gv.YELLOW)]
    btn_num = len(button_setting)
    my_buttons = [None]*btn_num
    for i in range(btn_num):
        text, color = button_setting[i]
        my_buttons[i] = sc.my_button((850, 40+70*i), (150, 60), color, (gv.HELV, 35, gv.BLACK, text))
        buttons.add(my_buttons[i])
        
    def coord(X, Y):
        return (10+75*X, 460+35*Y)
    
    ai_buttons = [[None]*3 for _ in range(2)]
    color_dict = {0:gv.GREEN, 1:gv.YELLOW, 2:gv.ORANGE}
    diff_dict = {0:'E', 1:'N', 2:'H'}
    for i in range(2):
        for j in range(3):
            ai_buttons[i][j] = sc.my_button(coord(j, i),(70, 30), color_dict[j], (gv.HELV, 30, gv.BLACK, f'P{i} {diff_dict[j]}'))
            buttons.add(ai_buttons[i][j])

    blackScore, whiteScore = 2, 2
    click_x, click_y = None, None
    
    MODE = 'play'
    
    
    while True:
        texts.empty()
        
        if MODE == 'play':
            loop = game.game_loop(gv.P1_ai, gv.P2_ai)
            if not loop:
                if blackScore > whiteScore:
                    result = 'BLACK WIN!'
                elif blackScore < whiteScore:
                    result = 'WHITE WIN!'
                else:
                    result = 'DRAW!'
                    
                gameOverText = sc.text('Game OVER!', gv.HELV, 30, (10, 70), gv.BLACK)
                resultText = sc.text(result, gv.NEXT, 30, (10, 100), gv.BLACK)
                texts.add(gameOverText, resultText)
            

        for evg in pygame.event.get():
            if evg.type == pygame.QUIT:
                pygame.display.quit()

            if evg.type == pygame.MOUSEBUTTONDOWN:
                for aTile in sum(ui_board.tiles, []):
                    if aTile.rect.collidepoint(pygame.mouse.get_pos()):
                        click_x, click_y = aTile.xInd, aTile.yInd
                        if MODE == 'edit':
                            game.set_board(click_x, click_y)
                        if MODE == 'play': 
                            game.make_move(click_x, click_y)
                
                if my_buttons[0].rect.collidepoint(pygame.mouse.get_pos()):
                    InGame()

                if my_buttons[1].rect.collidepoint(pygame.mouse.get_pos()):
                    Intro()
                    
                if my_buttons[2].rect.collidepoint(pygame.mouse.get_pos()):
                    MODE = 'edit'

                if my_buttons[3].rect.collidepoint(pygame.mouse.get_pos()):
                    MODE = 'play'
                    game.reset_record()
                    
                if my_buttons[4].rect.collidepoint(pygame.mouse.get_pos()):
                    game.change_turn()
                
                if my_buttons[5].rect.collidepoint(pygame.mouse.get_pos()):
                    game.back_move()
                    
                if my_buttons[6].rect.collidepoint(pygame.mouse.get_pos()):
                    game.next_move()
                
                if my_buttons[7].rect.collidepoint(pygame.mouse.get_pos()):
                    game.save(os.path.join('.\\',time_now()+'.json'))
                    
                for i in range(2):
                    for j in range(3):
                        if ai_buttons[i][j].rect.collidepoint(pygame.mouse.get_pos()):
                            if i==0:
                                gv.P1_ai = 0 if gv.P1_ai else j+2
                            elif i==1:
                                gv.P2_ai = 0 if gv.P2_ai else j+2
        
        blackScore, whiteScore = game.getScoreOfBoard()
        blackText = sc.text(f'BLACK: {blackScore}', gv.HELV, 25, (10, 10), gv.GREY)
        whiteText = sc.text(f'WHITE: {whiteScore}', gv.HELV, 25, (10, 40), gv.GREY)
        clickText = sc.text(f'x: {click_x}, y: {click_y}', gv.HELV, 25, (10, 200), gv.GREY)
        next_move_text = sc.text(f"next: {'black' if game.get_turn()==1 else 'white'}", gv.HELV, 25, (10, 250), gv.GREY)
        mode_text = sc.text(f"game mode: {MODE}", gv.HELV, 25, (10, 300), gv.GREY)
        ai_p1_text = sc.text(f"ai_P1: {'on' if gv.P1_ai else 'off'}", gv.HELV, 25, (10, 350), gv.GREY)
        ai_p2_text = sc.text(f"ai_P2: {'on' if gv.P2_ai else 'off'}", gv.HELV, 25, (10, 400), gv.GREY)
        texts.add(blackText, whiteText, clickText, next_move_text, mode_text, ai_p1_text, ai_p2_text)

        screen.fill(gv.BROWN)
        ui_board.update(game.get_board(), game.get_hint())
        ui_board.draw(screen)
        buttons.draw(screen)
        texts.draw(screen)
        pygame.display.update()


Intro()