import reversi_python
import reversi_cython
import time

from array import array

num = 50000

def run_python(board):
    playerColor = 1
    pass_info = 0
    for i in range(num):
        reversi_python.getValidMoves(board, 8, 8, playerColor, pass_info)
    print(reversi_python.getValidMoves(board, 8, 8, playerColor, pass_info))
        
def run_cython(board):
    playerColor = 1
    pass_info = 0
    for i in range(num):
        reversi_cython.getValidMoves(board, 8, 8, playerColor, pass_info)
    print(reversi_cython.getValidMoves(board, 8, 8, playerColor, pass_info))

def run_python_ef(board):
    tile = 1
    for i in range(num):
        reversi_python.count_tile(board, tile)
    print(reversi_python.count_tile(board, tile))
        
def run_cython_ef(board):
    tile = 1
    for i in range(num):
        reversi_cython.count_tile(board, tile)
    print(reversi_cython.count_tile(board, tile))
    
if __name__=='__main__':
    """
    用Cython加速黑白棋求合法步邏輯及求盤面估值，
    時間大約降至20%
    """
    board = [[0,0,0,0,0,0,0,0],
              [0,0,0,0,0,0,0,0],
              [0,0,0,1,0,0,0,0],
              [0,0,2,2,2,2,0,0],
              [0,0,0,1,2,0,0,0],
              [0,0,0,0,0,0,0,0],
              [0,0,0,0,0,0,0,0],
              [0,0,0,0,0,0,0,0]]
    board = array('i',sum(board,[]))
    
    s = time.time()
    run_python(board)
    python_time = time.time()-s
    print(python_time)
    
    s = time.time()
    run_cython(board)
    cython_time = time.time()-s
    print(cython_time)
    
    print(f'Time reduce to {cython_time/python_time} %')
    
        
    s = time.time()
    run_python_ef(board)
    python_time = time.time()-s
    print(python_time)
    
    s = time.time()
    run_cython_ef(board)
    cython_time = time.time()-s
    print(cython_time)
    
    print(f'Time reduce to {cython_time/python_time} %')
