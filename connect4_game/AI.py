from .Connect4AI import Solver, GameState
import os

data_filename = os.path.join(os.path.dirname(__file__), 'score_data.txt')
solver = Solver(data_filename)

def ai_move(game_state, height, width, ai_stone):
    GS = GameState()
    GS.play_board_state("".join(game_state), ai_stone)
    score = solver.solve(GS)                     # max score
    mark_col_num = 0

    for col_num in range(width):
        if game_state[col_num] == '0':
            temp_GS = GameState(GS)
            temp_GS.playCol(col_num)
            if score == -(solver.solve(temp_GS)):
                mark_col_num = col_num
                break
    
    mark_row_num = 0
    for row_num in range(height-1, -1, -1):
        if game_state[row_num*width + col_num] == '0':
            mark_row_num = row_num
            break

    game_state[mark_row_num*width + mark_col_num] = ai_stone
    return ("".join(game_state), mark_row_num, mark_col_num)
  

# print the current state in matrix form
def game_state_to_matrix(game_state, rows, cols):
    string = ''
    for row_num in range(rows):
        for col_num in range(cols):
            string += ' ' + game_state[row_num*cols + col_num]
        string += "\n"
    return string
