import reversi_get_valid_move_python
import reversi_get_valid_move_cython
import time

num = 100000

def run_python():
    playerColor = 1
    board = [[0,0,0,0,0,0,0,0],
              [0,0,0,0,0,0,0,0],
              [0,0,0,1,0,0,0,0],
              [0,0,2,2,2,2,0,0],
              [0,0,0,1,2,0,0,0],
              [0,0,0,0,0,0,0,0],
              [0,0,0,0,0,0,0,0],
              [0,0,0,0,0,0,0,0]]
    pass_info = 0
    for i in range(num):
        reversi_get_valid_move_python.getValidMoves(board, 8, 8, playerColor, pass_info)
    print(reversi_get_valid_move_python.getValidMoves(board, 8, 8, playerColor, pass_info))
        
def run_cython():
    playerColor = 1
    board = [[0,0,0,0,0,0,0,0],
              [0,0,0,0,0,0,0,0],
              [0,0,0,1,0,0,0,0],
              [0,0,2,2,2,2,0,0],
              [0,0,0,1,2,0,0,0],
              [0,0,0,0,0,0,0,0],
              [0,0,0,0,0,0,0,0],
              [0,0,0,0,0,0,0,0]]
    pass_info = 0
    for i in range(num):
        reversi_get_valid_move_cython.getValidMoves(board, 8, 8, playerColor, pass_info)
    print(reversi_get_valid_move_cython.getValidMoves(board, 8, 8, playerColor, pass_info))

    
if __name__=='__main__':
    """
    用Cython加速黑白棋求合法步邏輯，
    時間大約降至38%
    """
    s = time.time()
    run_python()
    python_time = time.time()-s
    print(python_time)
    
    s = time.time()
    run_cython()
    cython_time = time.time()-s
    print(cython_time)
    
    print(f'Time reduce to {cython_time/python_time} %')
