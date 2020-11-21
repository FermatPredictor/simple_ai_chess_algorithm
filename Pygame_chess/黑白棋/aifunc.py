import math
import random
import copy
import reversifunc as rf
import globalvar as gv

# the weights of board, big positive value means top priority for opponent
weights = [[ 100, -20,  10,   5,   5,  10, -20, 100],
           [ -20, -50,  -2,  -2,  -2,  -2, -50, -20],
           [  10,  -2,   1,   1,   1,   1,  -2,  10],
           [   5,  -2,   1,   1,   1,   1,  -2,   5],
           [   5,  -2,   1,   1,   1,   1,  -2,   5],
           [  10,  -2,   1,   1,   1,   1,  -2,  10],
           [ -20, -50,  -2,  -2,  -2,  -2, -50, -20],
           [ 100, -20,  10,   5,   5,  10, -20, 100]]

# evaluate score of the opponent for minimax algorithm, based on mobility and positioning of disks
def evalScore(board, turn):
    score = 0

    if turn == gv.P1:
        opp = gv.P2
    elif turn == gv.P2:
        opp = gv.P1

    # positioning of disks
    for x in range(8):
        for y in range(8):
            if board[x][y] == turn:
                score += weights[x][y]
            elif board[x][y] == opp:
                score -= weights[x][y]

    return score

# minimax algorithm with alpha-beta pruning; opponent is maximizing and player is minimizing
def miniMax(board, depth, alpha, beta, isMaxPlayer, turn):
    bestMove = None

    if turn == gv.P1:
        opp = gv.P2
    elif turn == gv.P2:
        opp = gv.P1

    if depth == 0 or len(rf.getValidMoves(board, turn)) == 0:
        return evalScore(board, turn), 1

    # opponent's turn
    if isMaxPlayer:
        maxValue = -math.inf
        moves = rf.getValidMoves(board, turn)

        if len(moves) > 0:
            random.shuffle(moves)

        for aMove in moves:
            tempBoard = copy.deepcopy(board)
            tempBoard = rf.makeMove(tempBoard, turn, aMove[0], aMove[1])
            curScore, move = miniMax(tempBoard, depth-1, alpha, beta, False, turn)

            if curScore > maxValue:
                maxValue = curScore
                bestMove = aMove

            alpha = max(alpha, maxValue)
            if alpha >= beta:
                break

        return maxValue, bestMove

    # player's turn
    else:
        minValue = math.inf
        moves = rf.getValidMoves(board, opp)

        for aMove in moves:
            tempBoard = copy.deepcopy(board)
            tempBoard = rf.makeMove(tempBoard, opp, aMove[0], aMove[1])
            curScore, move = miniMax(tempBoard, depth-1, alpha, beta, True, turn)

            if curScore < minValue:
                minValue = curScore
                bestMove = aMove

            beta = min(beta, minValue)
            if alpha >= beta:
                break

        return minValue, bestMove
