from cpython cimport array
import array

cdef bint isOnBoard(int r, int c, int H, int W):
    return 0 <= r < H and 0 <= c < W

cpdef getValidMoves(int[:] board, int height, int width, int playerColor, int pass_info):
    """
    回傳字典: {合法棋步座標: 翻轉的對手棋子}
    player_color : int(usually 1 or 2, 0 for empty grid), 下一步換誰下
    pass_info: 上一步pass，0:無pass, 1:黑pass, 2:白pass
    """
    cdef int H = height
    cdef int W = width
    cdef int tile = playerColor
    cdef int opp_tile = playerColor^3
    cdef dict move_dict = {}
    cdef int r,c, dr, dc, di
    cdef list dirs = [(r,c, r*width+c)for r in [-1,0,1] for c in [-1,0,1] if r or c] # 定義八個方向
    cdef int idx = -1 
    cdef int inter_r, inter_c, inter_idx, flip
    
    for r in range(H):
        for c in range(W):
            idx += 1
            if board[idx]!=tile:
                continue
            for dr, dc, di in dirs:
                inter_r = r+dr
                inter_c = c+dc
                inter_idx = idx+di
                flip = 0
                while isOnBoard(inter_r, inter_c, H, W) and board[inter_idx] == opp_tile:
                    inter_r += dr
                    inter_c += dc
                    inter_idx += di
                    flip += 1
                if flip and isOnBoard(inter_r, inter_c, H, W) and board[inter_idx] == 0:
                    # 夾到對手的棋子，回頭記錄
                    if (inter_r, inter_c) not in move_dict:
                        move_dict[(inter_r, inter_c)] = array.array('i',[inter_idx])
                    grid_r, gird_c = inter_r, inter_c
                    for i in range(flip):
                        inter_r -= dr
                        inter_c -= dc
                        inter_idx -= di
                        move_dict[(grid_r, gird_c)].append(inter_idx)
    move_dict = {k: (v,pass_info) for k,v in move_dict.items()}
    return move_dict if move_dict else {'PASS': ('PASS', pass_info)}

cpdef count_tile(int[:] board, int tile):
    cdef int score = 0
    cdef int opp = tile^3
    for e in board:
        if e==tile:
            score += 1
        elif e==opp:
            score -= 1
    return score

cpdef eval_func(int[:] board, int height, int width, int tile, int[:] w_board):
    cdef int score = 0
    cdef int opp = tile^3
    for e, w in zip(board, w_board):
        if e==tile:
            score += w
        elif e==opp:
            score -= w
    return score

