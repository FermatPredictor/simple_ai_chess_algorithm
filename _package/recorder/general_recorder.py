import json

class Recorder():
    """
    用來記錄棋局過程，必要記錄的三項東西:
    「下一步換誰走」、「初始盤面」、「棋局棋步」(可以做為state的getValidMoves()函數的key值去走棋的)
    目前假設一定是黑白交錯進行(如有輪空規則，記錄裡要寫'PASS')
    """
    
    def __init__(self, state, debug=False):
        self.reset(state)
        self.debug = debug
    
    def record_move(self, move):
        self.step_stack.append(move)
        self.step_pt += 1
        
    def reset(self, state):
        """
        被call時機: 棋盤被重新編輯過，因此需重設初始盤面
        """
        self.state = state
        self.board = state.to_board()
        self.playerColor = state.playerColor
        self.step_stack = []
        self.step_pt = 0
        
    def refresh(self):
        """
        被call時機: 此函數接水至game_engine，每當game_engine走棋時檢查，
        self.step_pt 並非最後一步時，將self.step_stack截斷至等同於self.step_pt長度
        """
        if len(self.step_stack)<self.step_pt:
            raise Exception('The recorder has too long step_pt.')
        if len(self.step_stack)>self.step_pt:
            self.step_stack = self.step_stack[:self.step_pt]
    
    def __goto_move(self, n):
        if self.debug:
            print(f'[DEBUG] step_pt:{self.step_pt}, step_stack: {self.step_stack}')
        # 從初始盤面開始擺n手棋
        self.state.__init__(self.board, self.playerColor)
        step_stack = self.step_stack
        for i in range(self.step_pt):
            valid_moves = self.state.getValidMoves()
            move = step_stack[i]
            if isinstance(move, list):
                # 存檔成json檔時會將tuple轉型為list，所以轉型回tuple
                move = tuple(move)
            if move in valid_moves:
                self.state.makeMove(valid_moves[move])
            elif move == 'PASS':
                self.state.passMove()                
            else:
                raise Exception('catch a non-valid move.')
    
    def back_move(self):
        self.step_pt = max(0, self.step_pt-1)
        self.__goto_move(self.step_pt)
        return self.state
    
    def next_move(self):
        self.step_pt = min(len(self.step_stack), self.step_pt+1)
        self.__goto_move(self.step_pt)
        return self.state
    
    def get_last_move(self):
        if self.step_stack:
            return self.step_stack[-1]
        
    def is_last_move(self)-> bool:
        return len(self.step_stack)==self.step_pt
        
    def save(self, path):
        json.dump((self.playerColor, self.board, self.step_stack), open(path, "w"))
        
    
    def load(self, path):
        self.playerColor, self.board, self.step_stack = json.load(open(path, "r"))
        
        