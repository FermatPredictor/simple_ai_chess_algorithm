def count_tile(board, height, width, tile):
    score, opp = 0, tile^3
    for r in range(height):
        for c in range(width):
            if board[r][c]==tile:
                score += 1
            elif board[r][c]==opp:
                score -= 1
    return score

def eval_func(board, height, width, tile, w_board):
    score, opp = 0, tile^3
    for r in range(height):
        for c in range(width):
            if board[r][c]==tile:
                score += w_board[r][c]
            elif board[r][c]==opp:
                score -= w_board[r][c]
    return score