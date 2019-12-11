def game_state_to_moves(game_state, height, width, ai_stone):
    each_row_red    = []
    each_row_yellow = []

    for row_num in range(height-1, -1, -1):
        for col_num in range(width):
            if game_state[row_num*width + col_num] == 'r':
                each_row_red.append(str(col_num+1))
            elif game_state[row_num*width + col_num] == 'y':
                each_row_yellow.append(str(col_num+1))

    res = []
    if ai_stone == 'r':
        res = [*sum(zip(each_row_yellow, each_row_red),())]
        if len(each_row_yellow) > len(each_row_red):
            res.append(each_row_yellow[-1])
    elif ai_stone == 'y':
        res = [*sum(zip(each_row_red, each_row_yellow),())]
        if len(each_row_red) > len(each_row_yellow):
            res.append(each_row_red[-1])
    
  return "".join(res)
  

# print the current state in matrix form
def game_state_to_matrix(game_state, rows, cols):
    string = ''
    for row_num in range(rows):
        for col_num in range(cols):
            string += ' ' + game_state[row_num*cols + col_num]
        string += "\n"
    return string
