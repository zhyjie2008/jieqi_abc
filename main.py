import random
import sys


class RevealedChess:
    def __init__(self):
        # 初始化棋盘
        self.board = [[None for _ in range(9)] for _ in range(10)]
        # 红方(0)和黑方(1)的已揭示棋子
        self.revealed = [[[False for _ in range(9)] for _ in range(10)] for _ in range(2)]
        # 当前回合(0:红方, 1:黑方)
        self.current_player = 0
        # 游戏是否结束
        self.game_over = False
        # 初始化棋子
        self.setup_pieces()

    def setup_pieces(self):
        """初始化棋子布局"""
        # 红方(下方)和黑方(上方)的棋子类型
        piece_types = [
            ['车', '马', '相', '士', '帅', '士', '相', '马', '车'],
            ['炮', '炮'],
            ['兵', '兵', '兵', '兵', '兵']
        ]

        # 放置红方棋子(背面)
        for i in range(3):
            for j, piece in enumerate(piece_types[i]):
                if i == 0:
                    self.board[9][j] = ('红', piece, True)  # (颜色, 类型, 是否隐藏)
                elif i == 1:
                    self.board[7][1 + j * 7] = ('红', piece, True)
                else:
                    self.board[6][j * 2] = ('红', piece, True)

        # 放置黑方棋子(背面)
        for i in range(3):
            for j, piece in enumerate(piece_types[i]):
                if i == 0:
                    self.board[0][j] = ('黑', piece, True)
                elif i == 1:
                    self.board[2][1 + j * 7] = ('黑', piece, True)
                else:
                    self.board[3][j * 2] = ('黑', piece, True)

        # 随机打乱棋子(除了将帅)
        self.shuffle_pieces()

    def shuffle_pieces(self):
        """随机打乱棋子位置(除了将帅)"""
        # 收集所有可打乱的棋子位置
        red_positions = []
        black_positions = []

        for i in range(10):
            for j in range(9):
                if self.board[i][j] and self.board[i][j][2]:  # 只打乱隐藏的棋子
                    if self.board[i][j][0] == '红' and self.board[i][j][1] != '帅':
                        red_positions.append((i, j))
                    elif self.board[i][j][0] == '黑' and self.board[i][j][1] != '帅':
                        black_positions.append((i, j))

        # 打乱红方棋子
        red_pieces = [self.board[i][j][1] for i, j in red_positions]
        random.shuffle(red_pieces)
        for idx, (i, j) in enumerate(red_positions):
            self.board[i][j] = ('红', red_pieces[idx], True)

        # 打乱黑方棋子
        black_pieces = [self.board[i][j][1] for i, j in black_positions]
        random.shuffle(black_pieces)
        for idx, (i, j) in enumerate(black_positions):
            self.board[i][j] = ('黑', black_pieces[idx], True)

    def print_board(self):
        """打印当前棋盘状态"""
        print("  0 1 2 3 4 5 6 7 8")
        for i in range(10):
            print(i, end=" ")
            for j in range(9):
                piece = self.board[i][j]
                if not piece:
                    print("·", end=" ")
                else:
                    color, piece_type, hidden = piece
                    if hidden:
                        # 对当前玩家已揭示的棋子显示真实信息
                        if self.revealed[self.current_player][i][j]:
                            print(f"\033[1;33m{color[0]}{piece_type}\033[0m", end=" ")  # 黄色显示已知但未移动的棋子
                        else:
                            print("?", end=" ")
                    else:
                        print(f"\033[1;32m{color[0]}{piece_type}\033[0m", end=" ")  # 绿色显示已揭示的棋子
            print()
        print("当前玩家:", "红方" if self.current_player == 0 else "黑方")

    def is_valid_move(self, start, end):
        """检查移动是否合法"""
        sx, sy = start
        ex, ey = end

        # 检查起始位置是否有棋子
        if not self.board[sx][sy]:
            return False

        # 检查是否是当前玩家的棋子
        piece_color = self.board[sx][sy][0]
        if (piece_color == '红' and self.current_player != 0) or (piece_color == '黑' and self.current_player != 1):
            return False

        # 检查目标位置是否是自己的棋子
        if self.board[ex][ey] and self.board[ex][ey][0] == piece_color:
            return False

        # 获取棋子类型(如果已揭示)
        _, piece_type, hidden = self.board[sx][sy]
        if hidden:
            # 如果是隐藏棋子，第一次移动时揭示
            if not self.revealed[self.current_player][sx][sy]:
                # 玩家不知道是什么棋子，只能尝试移动
                # 这里简化处理，允许任何移动，实际游戏可能需要限制
                return True
            else:
                piece_type = self.board[sx][sy][1]

        # 根据棋子类型检查移动规则
        return self.check_piece_rules(piece_type, start, end, piece_color)

    def check_piece_rules(self, piece_type, start, end, color):
        """检查特定棋子的移动规则"""
        sx, sy = start
        ex, ey = end
        dx = ex - sx
        dy = ey - sy

        # 车
        if piece_type == '车':
            if dx != 0 and dy != 0:
                return False
            if dx == 0:  # 横向移动
                step = 1 if dy > 0 else -1
                for y in range(sy + step, ey, step):
                    if self.board[sx][y]:
                        return False
            else:  # 纵向移动
                step = 1 if dx > 0 else -1
                for x in range(sx + step, ex, step):
                    if self.board[x][sy]:
                        return False
            return True

        # 马
        elif piece_type == '马':
            if (abs(dx) == 2 and abs(dy) == 1) or (abs(dx) == 1 and abs(dy) == 2):
                # 检查马脚
                if abs(dx) == 2:
                    if self.board[sx + dx // 2][sy]:
                        return False
                else:
                    if self.board[sx][sy + dy // 2]:
                        return False
                return True
            return False

        # 相/象
        elif piece_type in ['相', '象']:
            if (color == '红' and ex < 5) or (color == '黑' and ex > 4):
                return False  # 不能过河

            if abs(dx) == 2 and abs(dy) == 2:
                # 检查象眼
                if self.board[sx + dx // 2][sy + dy // 2]:
                    return False
                return True
            return False

        # 士
        elif piece_type == '士':
            if (color == '红' and (ex < 7 or ey < 3 or ey > 5)) or \
                    (color == '黑' and (ex > 2 or ey < 3 or ey > 5)):
                return False  # 必须在九宫格内

            return abs(dx) == 1 and abs(dy) == 1

        # 帅/将
        elif piece_type in ['帅', '将']:
            if (color == '红' and (ex < 7 or ey < 3 or ey > 5)) or \
                    (color == '黑' and (ex > 2 or ey < 3 or ey > 5)):
                return False  # 必须在九宫格内

            return (abs(dx) == 1 and dy == 0) or (dx == 0 and abs(dy) == 1)

        # 炮
        elif piece_type == '炮':
            if dx != 0 and dy != 0:
                return False

            obstacle_count = 0
            if dx == 0:  # 横向移动
                step = 1 if dy > 0 else -1
                for y in range(sy + step, ey, step):
                    if self.board[sx][y]:
                        obstacle_count += 1
            else:  # 纵向移动
                step = 1 if dx > 0 else -1
                for x in range(sx + step, ex, step):
                    if self.board[x][sy]:
                        obstacle_count += 1

            # 炮移动需要0个障碍(不吃子)或1个障碍(吃子)
            target_piece = self.board[ex][ey]
            if target_piece:
                return obstacle_count == 1
            else:
                return obstacle_count == 0

        # 兵/卒
        elif piece_type in ['兵', '卒']:
            # 基本移动规则
            if color == '红':
                if dx == -1 and dy == 0:  # 红方向上移动
                    return True
                elif ex < 5:  # 过河后可以横向移动
                    return (dx == 0 and abs(dy) == 1)
            else:  # 黑方
                if dx == 1 and dy == 0:  # 黑方向下移动
                    return True
                elif ex > 4:  # 过河后可以横向移动
                    return (dx == 0 and abs(dy) == 1)
            return False

        return False

    def make_move(self, start, end):
        """执行移动"""
        sx, sy = start
        ex, ey = end

        # 揭示棋子(如果是隐藏的)
        if self.board[sx][sy][2]:  # 隐藏状态
            # 揭示给双方玩家
            self.revealed[0][sx][sy] = True
            self.revealed[1][sx][sy] = True
            # 更新棋盘状态
            color, piece_type, _ = self.board[sx][sy]
            self.board[sx][sy] = (color, piece_type, False)

        # 检查是否吃子
        if self.board[ex][ey]:
            # 检查是否吃将/帅
            if self.board[ex][ey][1] in ['帅', '将']:
                self.game_over = True

        # 移动棋子
        self.board[ex][ey] = self.board[sx][sy]
        self.board[sx][sy] = None

        # 切换玩家
        self.current_player = 1 - self.current_player

    def play(self):
        """主游戏循环"""
        print("欢迎来到揭棋游戏!")
        print("输入移动格式: 起始行 起始列 目标行 目标列 (例如: 7 0 6 0)")

        while not self.game_over:
            self.print_board()

            try:
                # 获取玩家输入
                move = input("请输入你的移动: ").strip()
                if move.lower() == 'exit':
                    break

                sx, sy, ex, ey = map(int, move.split())
                start = (sx, sy)
                end = (ex, ey)

                # 检查移动是否合法
                if self.is_valid_move(start, end):
                    self.make_move(start, end)
                else:
                    print("非法移动，请重试!")
            except ValueError:
                print("输入格式错误，请使用: 起始行 起始列 目标行 目标列")
            except IndexError:
                print("坐标超出范围，请重试!")

        if self.game_over:
            self.print_board()
            winner = "红方" if self.current_player == 0 else "黑方"
            print(f"游戏结束! {winner}获胜!")


if __name__ == "__main__":
    game = RevealedChess()
    game.play()
