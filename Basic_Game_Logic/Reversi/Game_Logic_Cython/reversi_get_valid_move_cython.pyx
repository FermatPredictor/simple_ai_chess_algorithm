cdef bint isOnBoard(int r, int c, int H, int W):
    return 0 <= r < H and 0 <= c < W

cpdef dict getValidMoves(list board, int height, int width, int playerColor, int pass_info):
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
    cdef list dirs = [[0, 1], [1, 1], [1, 0], [1, -1], [0, -1], [-1, -1], [-1, 0], [-1, 1]] # 定義八個方向
    cdef int _r, _c, flip
    for r in range(H):
        for c in range(W):
            if board[r][c]!=tile:
                continue
            for dr, dc in dirs:
                _r, _c, flip = r+dr, c+dc, 0
                while isOnBoard(_r, _c, H, W) and board[_r][_c] == opp_tile:
                    _r, _c, flip = _r+dr, _c+dc, flip+1
                if flip and isOnBoard(_r, _c, H, W) and board[_r][_c] == 0:
                    # 夾到對手的棋子，回頭記錄
                    if (_r, _c) not in move_dict:
                        move_dict[(_r, _c)] = [(_r, _c)] 
                    grid_r, gird_c = _r, _c
                    for i in range(flip):
                        _r, _c = _r-dr, _c-dc
                        move_dict[(grid_r, gird_c)].append((_r, _c))
    move_dict = {k:(v, pass_info) for k,v in move_dict.items()}
    return move_dict if move_dict else {'PASS': ('PASS', pass_info)}
