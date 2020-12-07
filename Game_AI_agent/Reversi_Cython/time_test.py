import eval_func_python
import eval_func_cython
import time

num = 100000

def run_python():
    tile = 1
    board = [[0,0,0,0,0,0,0,0],
              [0,0,0,0,0,0,0,0],
              [0,0,0,1,0,0,0,0],
              [0,0,2,2,2,2,0,0],
              [0,0,0,1,2,0,0,0],
              [0,0,0,0,0,0,0,0],
              [0,0,0,0,0,0,0,0],
              [0,0,0,0,0,0,0,0]]
    for i in range(num):
        eval_func_python.count_tile(board, 8, 8, tile)
    print(eval_func_python.count_tile(board, 8, 8, tile))
        
def run_cython():
    tile = 1
    board = [[0,0,0,0,0,0,0,0],
              [0,0,0,0,0,0,0,0],
              [0,0,0,1,0,0,0,0],
              [0,0,2,2,2,2,0,0],
              [0,0,0,1,2,0,0,0],
              [0,0,0,0,0,0,0,0],
              [0,0,0,0,0,0,0,0],
              [0,0,0,0,0,0,0,0]]
    for i in range(num):
        eval_func_cython.count_tile(board, 8, 8, tile)
    print(eval_func_cython.count_tile(board, 8, 8, tile))

    
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
