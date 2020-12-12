import json

class Recorder():
    
    def __init__(self, board=None):
        if board:
            self.reset(board)
        self.step_stack = []
    
    def record_move(self, r,c):
        self.step_stack.append((r,c))
        print(f"[DEBUG] {self.step_stack}")
        
    def reset(self, board):
        H, W = len(board), len(board[0])
        self.board = [[0]*W for i in range(H)]
        for r in range(H):
            for c in range(W):
                self.board[r][c] = board[r][c]
        self.step_stack = []
        
    def save(self):
        json.dump((self.board, self.step_stack), open(r".\record.json", "w"))
        
    
    def load(self):
        return json.load(open(r".\record.json", "r"))

if __name__ == '__main__':
    r = Recorder()
    step_stack = r.load()
    print(step_stack)
        