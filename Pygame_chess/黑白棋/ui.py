import pygame

import spriteclass as sc
import reversifunc as rf
import globalvar as gv
import aifunc as af

import math
import time

# 創建顏色(三個參數為RGB)
GREEN = (128,255,0)
BLACK = (0,0,0)
YELLOW = (255,225,0)
ORANGE = (255,135,0)

pygame.init()

screen = pygame.display.set_mode((gv.WIDTH, gv.HEIGHT))
pygame.display.set_caption('Reversi')

# menu screen
def Intro():
    texts = pygame.sprite.Group()
    buttons = pygame.sprite.Group()

    gameTitle = sc.text('REVERSI', gv.NEXT, 110, (260, 50), gv.GOLD)
    chooseDiff = sc.text('Choose Difficulty', gv.HELV, 40, (320, 300), gv.GREY)
    
    easyButton = sc.my_button((200, 400), (150, 70), GREEN, (gv.HELV, 30, gv.BLACK, 'Easy'))
    normButton = sc.my_button((400, 400), (150, 70), YELLOW, (gv.HELV, 30, gv.BLACK, 'Normal'))
    hardButton = sc.my_button((600, 400), (150, 70), ORANGE, (gv.HELV, 30, gv.BLACK, 'Hard'))
    aiButton = sc.my_button((780, 625), (150, 70), ORANGE, (gv.HELV, 30, gv.BLACK, 'AI Mode'))

    texts.add(gameTitle, chooseDiff)
    buttons.add(easyButton, normButton, hardButton, aiButton)

    while True:
        for evi in pygame.event.get():
            if evi.type == pygame.QUIT:
                pygame.display.quit()

            if evi.type == pygame.MOUSEBUTTONDOWN:
                if easyButton.rect.collidepoint(pygame.mouse.get_pos()):
                    gv.diff = 2
                    gv.aiMode = False
                    InGame()
                if normButton.rect.collidepoint(pygame.mouse.get_pos()):
                    gv.diff = 3
                    gv.aiMode = False
                    InGame()
                if hardButton.rect.collidepoint(pygame.mouse.get_pos()):
                    gv.diff = 4
                    gv.aiMode = False
                    InGame()
                if aiButton.rect.collidepoint(pygame.mouse.get_pos()):
                    AiMode()

        screen.fill(gv.BROWN)
        buttons.draw(screen)
        texts.draw(screen)
        pygame.display.update()

def AiMode():
    texts = pygame.sprite.Group()
    buttons = pygame.sprite.Group()

    aiTitle = sc.text('AI Mode', gv.NEXT, 110, (260, 50), gv.GOLD)
    
    def coord(X, Y):
        return (200+200*X, 200+125*Y)
    
    my_buttons = [[None]*3 for _ in range(3)]
    color_dict = {0:GREEN, 1:YELLOW, 2:ORANGE}
    diff_dict = {0:'E', 1:'N', 2:'H'}
    for i in range(3):
        for j in range(3):
            my_buttons[i][j] = sc.my_button(coord(j, i),(150, 70), color_dict[i], (gv.HELV, 30, gv.BLACK, f'{diff_dict[i]} v {diff_dict[j]}'))
            buttons.add(my_buttons[i][j])
    backButton = sc.my_button((780, 625),(150, 70), ORANGE, (gv.HELV, 30, gv.BLACK, 'Back'))

    texts.add(aiTitle)
    buttons.add(backButton)

    while True:
        for eva in pygame.event.get():
            if eva.type == pygame.QUIT:
                pygame.display.quit()

            if eva.type == pygame.MOUSEBUTTONDOWN:
                for i in range(3):
                    for j in range(3):
                        if my_buttons[i][j].rect.collidepoint(pygame.mouse.get_pos()):
                            gv.aiPlay = i+2
                            gv.diff = j+2
                            gv.aiMode = True
                            InGame()
                if backButton.rect.collidepoint(pygame.mouse.get_pos()):
                    Intro()

        screen.fill(gv.BROWN)
        buttons.draw(screen)
        texts.draw(screen)
        pygame.display.update()

# gameplay
def InGame():
    game = rf.Reversi_Gmae()
    #curBoard = [['.' for x in range(8)] for y in range(8)]
    #noMoves = 0
    #curBoard = rf.initializeBoard(curBoard)
   # curTurn = gv.P1

    texts = pygame.sprite.Group()
    buttons = pygame.sprite.Group()
    ui_board = sc.chessBoard(game.get_board())
    
    retryButton = sc.my_button((800, 100), (150, 70), YELLOW, (gv.HELV, 35, gv.BLACK, 'Retry'))
    backButton = sc.my_button((800, 190), (150, 70), ORANGE, (gv.HELV, 35, gv.BLACK, 'Back'))
    buttons.add(retryButton, backButton)

    blackScore, whiteScore = 2, 2
    click_x, click_y = None, None
    while True:
        texts.empty()
        if not game.is_terminal():
            if game.get_turn()==1 and gv.aiMode or game.get_turn()==2:
                game.ai_action()
        else:
            if blackScore > whiteScore:
                result = 'BLACK WIN!'
            elif blackScore < whiteScore:
                result = 'WHITE WIN!'
            else:
                result = 'DRAW!'
                
            gameOverText = sc.text('Game OVER!', gv.HELV, 30, (10, 70), gv.BLACK)
            resultText = sc.text(result, gv.NEXT, 30, (10, 100), gv.BLACK)
            texts.add(gameOverText)
            texts.add(resultText)
            
            
        # if not game.is_terminal():
        #     validPos = rf.getValidMoves(curBoard, curTurn)
        #     if len(validPos) > 0:
        #         noMoves = 0
        #         if curTurn == gv.P1 and gv.aiMode or curTurn == gv.P2 and gv.diff:
        #             depth = gv.aiPlay if curTurn == gv.P1 else gv.diff
        #             value, oppMove = af.miniMax(curBoard, depth, -math.inf, math.inf, True, curTurn)
        #             if oppMove in validPos:
        #                 curBoard = rf.makeMove(curBoard, curTurn, oppMove[0], oppMove[1])
        #                 curTurn = gv.P2 if curTurn == gv.P1 else gv.P1
        #     else:
        #         curTurn = gv.P2 if curTurn == gv.P1 else gv.P1
        #         noMoves += 1
            
        # if noMoves>0:
        #     TEXT = 'No moves for WHITE' if curTurn == gv.P1 else 'No moves for BLACK'
        #     noText = sc.text(TEXT, gv.HELV, 25, (730, 10), gv.GREY)
        #     texts.add(noText)
        
        # if rf.getEmptyTiles(curBoard) == 0 or noMoves == 2:
            
        #     if blackScore > whiteScore:
        #         result = 'BLACK WIN!'
        #     elif blackScore < whiteScore:
        #         result = 'WHITE WIN!'
        #     else:
        #         result = 'DRAW!'
                
        #     gameOverText = sc.text('Game OVER!', gv.HELV, 30, (10, 70), gv.BLACK)
        #     resultText = sc.text(result, gv.NEXT, 30, (10, 100), gv.BLACK)
        #     texts.add(gameOverText)
        #     texts.add(resultText)

        for evg in pygame.event.get():
            if evg.type == pygame.QUIT:
                pygame.display.quit()

            if evg.type == pygame.MOUSEBUTTONDOWN:
                for aTile in sum(ui_board.tiles, []):
                    if aTile.rect.collidepoint(pygame.mouse.get_pos()):  
                        click_x, click_y = aTile.xInd, aTile.yInd
                        game.make_move(click_x, click_y)
                        # curBoard = rf.makeMove(curBoard, curTurn, aTile.xInd, aTile.yInd)
                        # curTurn = gv.P2 if curTurn == gv.P1 else gv.P1
                        # aiThink = sc.text('AI is thinking...', gv.HELV, 25, (770, 10), gv.GREY)
                        
                if retryButton.rect.collidepoint(pygame.mouse.get_pos()):
                    InGame()

                if backButton.rect.collidepoint(pygame.mouse.get_pos()):
                    Intro()
        
        blackScore, whiteScore = game.getScoreOfBoard()
        blackText = sc.text(f'BLACK: {blackScore}', gv.HELV, 25, (10, 10), gv.GREY)
        whiteText = sc.text(f'WHITE: {whiteScore}', gv.HELV, 25, (10, 40), gv.GREY)
        clickText = sc.text(f'x: {click_x}, y: {click_y}', gv.HELV, 25, (10, 200), gv.GREY)
        next_move_text = sc.text(f"next: {'black' if game.get_turn()==1 else 'white'}", gv.HELV, 25, (10, 250), gv.GREY)
        texts.add(blackText, whiteText, clickText, next_move_text)

        screen.fill(gv.BROWN)
        ui_board.update(game.get_board())
        ui_board.draw(screen)
        buttons.draw(screen)
        texts.draw(screen)
        pygame.display.update()


Intro()