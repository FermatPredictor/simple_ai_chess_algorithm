cpdef int count_tile(list board, int height, int width, int tile):
    cdef int score = 0
    cdef int opp = tile^3
    for r in range(height):
        for c in range(width):
            if board[r][c]==tile:
                score += 1
            elif board[r][c]==opp:
                score -= 1
    return score

cpdef int eval_func(list board, int height, int width, int tile, list w_board):
    cdef int score = 0
    cdef int opp = tile^3
    for r in range(height):
        for c in range(width):
            if board[r][c]==tile:
                score += w_board[r][c]
            elif board[r][c]==opp:
                score -= w_board[r][c]
    return score
