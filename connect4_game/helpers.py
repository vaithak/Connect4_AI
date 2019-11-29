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
	num_of_rows    = 6
	num_of_columns = 7
	connect_num	   = 4

	# check all rows
	for row_num in range(num_of_rows):
		for index in range(num_of_columns - connect_num + 1):
			if (user_state[row_num*num_of_columns + index] != '0') and (user_state[row_num*num_of_columns + index] == user_state[row_num*num_of_columns + index + 1]) and (user_state[row_num*num_of_columns + index + 1] == user_state[row_num*num_of_columns + index + 2]) and (user_state[row_num*num_of_columns + index + 2] == user_state[row_num*num_of_columns + index + 3]):
				return True

	# check all columns
	for column_num in range(num_of_columns):
		for index in range(num_of_rows - connect_num + 1):
			if (user_state[index*num_of_columns + column_num] != '0') and (user_state[index*num_of_columns + column_num] == user_state[(index+1)*num_of_columns + column_num]) and (user_state[(index+1)*num_of_columns + column_num] == user_state[(index+2)*num_of_columns + column_num]) and (user_state[(index+2)*num_of_columns + column_num] == user_state[(index+3)*num_of_columns + column_num]):
				return True

	# check right downward diagonals
	for row_num in range(num_of_rows - connect_num + 1):
		for column_num in range(num_of_columns - connect_num + 1):
			if (user_state[row_num*num_of_columns + column_num] != '0') and (user_state[row_num*num_of_columns + column_num] == user_state[(row_num+1)*num_of_columns + column_num + 1]) and (user_state[(row_num+1)*num_of_columns + column_num + 1] == user_state[(row_num+2)*num_of_columns + column_num + 2]) and (user_state[(row_num + 2)*num_of_columns + column_num + 2] == user_state[(row_num + 3)*num_of_columns + column_num + 3]):
				return True

	# check left downward diagonals
	for row_num in range(num_of_rows - connect_num + 1):
		for column_num in range(connect_num-1, num_of_columns):
			if (user_state[row_num*num_of_columns + column_num] != '0') and (user_state[row_num*num_of_columns + column_num] == user_state[(row_num+1)*num_of_columns + column_num - 1]) and (user_state[(row_num+1)*num_of_columns + column_num - 1] == user_state[(row_num + 2)*num_of_columns + column_num - 2]) and (user_state[(row_num + 2)*num_of_columns + column_num - 2] == user_state[(row_num + 3)*num_of_columns + column_num - 3]):
				return True

	return False

# TODO
def ai_move(curr_active, curr_state):
    return curr_state