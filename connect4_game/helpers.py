def verify_board_state_difference(active, prev_board_state, state):
	count=0
	for i in range(6):
		for j in range(7):
			if(prev_board_state[i*7 + j] != '0') and (state[i*7 + j] != prev_board_state[i*7 + j]):
				return False
			elif (prev_board_state[i*7 + j] == '0') and (state[i*7 + j] != prev_board_state[i*7 + j]):
				if state[i*7 + j] != active:
					return False
				else:
					count=count+1
	return (count == 1)



# check if game finished
def game_finished(user_state):
	return False

# TODO
def ai_move(curr_active, curr_state):
    return curr_state