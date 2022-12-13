from cmath import inf
from copy import deepcopy
import random
import time
import pygame
import math

class connect4Player(object):
	def __init__(self, position, seed=0):
		self.position = position
		self.opponent = None
		self.seed = seed
		random.seed(seed)

	def play(self, env, move):
		move = [-1]

class human(connect4Player):

	def play(self, env, move):
		move[:] = [int(input('Select next move: '))]
		while True:
			if int(move[0]) >= 0 and int(move[0]) <= 6 and env.topPosition[int(move[0])] >= 0:
				break
			move[:] = [int(input('Index invalid. Select next move: '))]

class human2(connect4Player):

	def play(self, env, move):
		done = False
		while(not done):
			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					sys.exit()

				if event.type == pygame.MOUSEMOTION:
					pygame.draw.rect(screen, BLACK, (0,0, width, SQUARESIZE))
					posx = event.pos[0]
					if self.position == 1:
						pygame.draw.circle(screen, RED, (posx, int(SQUARESIZE/2)), RADIUS)
					else: 
						pygame.draw.circle(screen, YELLOW, (posx, int(SQUARESIZE/2)), RADIUS)
				pygame.display.update()

				if event.type == pygame.MOUSEBUTTONDOWN:
					posx = event.pos[0]
					col = int(math.floor(posx/SQUARESIZE))
					move[:] = [col]
					done = True

class randomAI(connect4Player):

	def play(self, env, move):
		possible = env.topPosition >= 0
		indices = []
		for i, p in enumerate(possible):
			if p: indices.append(i)
		move[:] = [random.choice(indices)]

class stupidAI(connect4Player):

	def play(self, env, move):
		possible = env.topPosition >= 0
		indices = []
		for i, p in enumerate(possible):
			if p: indices.append(i)
		if 3 in indices:
			move[:] = [3]
		elif 2 in indices:
			move[:] = [2]
		elif 1 in indices:
			move[:] = [1]
		elif 5 in indices:
			move[:] = [5]
		elif 6 in indices:
			move[:] = [6]
		else:
			move[:] = [0]

class minimaxAI(connect4Player):

	def simulateMove(self, env, move, player):
		env.board[env.topPosition[move]][move] = player
		env.topPosition[move] -= 1
		env.history[0].append(move)
		return env

	# Counting score in a given window for a player
	def window_score(self, window, player_piece):
		score = 0

		if window.count(player_piece) == 4:
			score += 1000
		if window.count(player_piece) == 3 and window.count(0) == 1:
			score += 100 
		elif window.count(player_piece) == 2 and window.count(0) == 2:
			score += 10
		elif window.count(player_piece) == 1 and window.count(0) == 3:
			score += 1

		return score	

	# Evaluation function
	def eval(self, state):
		player_score, opponent_score = (0, 0)
		player = self.position
		opponent = self.opponent.position

		# # Score center column
		# center_arr = [int(i) for i in list(state[:,3])]
		# center_count = center_arr.count(player)
		# player_score += center_count * 3
		# center_count = center_arr.count(opponent)
		# opponent_score += center_count * 3

		# Horizontal Score, 6 rows
		for r in range(6):
			row_arr = [int(i) for i in list(state[r,:])]
			for c in range(4):
				window = row_arr[c:c+4]
				player_score += self.window_score(window, player)
				opponent_score += self.window_score(window, opponent)

		# Vertical Score, 7 columns
		for c in range(7):
			col_arr = [int(i) for i in list(state[:,c])]
			for c in range(3):
				window = col_arr[c:c+4]
				player_score += self.window_score(window, player)
				opponent_score += self.window_score(window, opponent)

		# Positive Diagnol Score
		for r in range(3):
			for c in range(4):
				window = [state[r+i][c+i] for i in range(4)]
				player_score += self.window_score(window, player)
				opponent_score += self.window_score(window, opponent)

		# Negative Diagnol Score
		for r in range(3):
			for c in range(4):
				window = [state[r+3-i][c+i] for i in range(4)]
				player_score += self.window_score(window, player)
				opponent_score += self.window_score(window, opponent)

		print("Board: ", "\n", state, "\n")
		print("Player Score: ", player_score, "\n")
		print("Opp Score: ", opponent_score, "\n")
		return player_score - opponent_score
		
	def MAX(self, env, depth):
		if len(env.history[0]) + len(env.history[1]) == 42:
			return 0
		if env.gameOver(env.history[0][-1], self.opponent.position):
			return -100000
		if depth == 0:
			return self.eval(env.board)
		possible = env.topPosition >= 0
		columns = []
		for i, p in enumerate(possible):
			if p: columns.append(i)
		max_v = -math.inf
		for column in columns:
			child = self.simulateMove(deepcopy(env), column, self.position)
			max_v = max(max_v, self.MIN(child, depth - 1))
		return max_v

	def MIN(self, env, depth):
		if len(env.history[0]) + len(env.history[1]) == 42:
			return 0
		if env.gameOver(env.history[0][-1], self.position):
			return 100000
		if depth == 0:
			return self.eval(env.board)
		possible = env.topPosition >= 0
		columns = []
		for i, p in enumerate(possible):
			if p: columns.append(i)
		min_v = math.inf
		for column in columns:
			child = self.simulateMove(deepcopy(env), column, self.opponent.position)
			min_v = min(min_v, self.MAX(child, depth - 1))
		return min_v

	def minimax(self, env, move, max_depth):
		best_move = 0
		max_v = -math.inf
		possible = env.topPosition >= 0
		columns = []
		for i, p in enumerate(possible):
			if p: columns.append(i)
		for column in columns:
			child = self.simulateMove(deepcopy(env), column, self.position)
			v = self.MIN(child, max_depth - 1)
			if v > max_v:
				max_v = v
				best_move = column
		move[:] = [best_move]

	def play(self, env, move):
		self.minimax(deepcopy(env), move, 2)
		print("Finished!")

class alphaBetaAI(connect4Player):
	
	def simulateMove(self, env, move, player):
		env.board[env.topPosition[move]][move] = player
		env.topPosition[move] -= 1
		env.history[0].append(move)
		return env

	# Counting score in a given window for a player
	def window_score(self, window, player_piece):
		score = 0

		if window.count(player_piece) == 4:
			score += 1000
		if window.count(player_piece) == 3 and window.count(0) == 1:
			score += 100 
		elif window.count(player_piece) == 2 and window.count(0) == 2:
			score += 10
		elif window.count(player_piece) == 1 and window.count(0) == 3:
			score += 1

		return score	

	# Evaluation function
	def eval(self, state):
		player_score, opponent_score = (0, 0)
		player = self.position
		opponent = self.opponent.position

		# Horizontal Score, 6 rows
		for r in range(6):
			row_arr = [int(i) for i in list(state[r,:])]
			for c in range(4):
				window = row_arr[c:c+4]
				player_score += self.window_score(window, player)
				opponent_score += self.window_score(window, opponent)

		# Vertical Score, 7 columns
		for c in range(7):
			col_arr = [int(i) for i in list(state[:,c])]
			for c in range(3):
				window = col_arr[c:c+4]
				player_score += self.window_score(window, player)
				opponent_score += self.window_score(window, opponent)

		# Positive Diagnol Score
		for r in range(3):
			for c in range(4):
				window = [state[r+i][c+i] for i in range(4)]
				player_score += self.window_score(window, player)
				opponent_score += self.window_score(window, opponent)

		# Negative Diagnol Score
		for r in range(3):
			for c in range(4):
				window = [state[r+3-i][c+i] for i in range(4)]
				player_score += self.window_score(window, player)
				opponent_score += self.window_score(window, opponent)

		return player_score - opponent_score

	def MAX(self, env, depth, alpha, beta):
		if len(env.history[0]) + len(env.history[1]) == 42:
			return 0
		if env.gameOver(env.history[0][-1], self.opponent.position):
			return -100000
		if depth == 0:
			return self.eval(env.board)
		optimal_node_ordering = [3, 2, 4, 1, 5, 0, 6]
		possible = env.topPosition >= 0
		columns = []
		for i, p in enumerate(optimal_node_ordering):
			if possible[i]:
				columns.append(p)
		max_v = -math.inf
		for column in columns:
			child = self.simulateMove(deepcopy(env), column, self.position)
			max_v = max(max_v, self.MIN(child, depth - 1,alpha, beta))
			alpha = max(alpha, max_v)
			if max_v >= beta:
				break
		return max_v

	def MIN(self, env, depth, alpha, beta):
		if len(env.history[0]) + len(env.history[1]) == 42:
			return 0
		if env.gameOver(env.history[0][-1], self.position):
			return 100000
		if depth == 0:
			return self.eval(env.board)
		optimal_node_ordering = [3, 2, 4, 1, 5, 0, 6]
		possible = env.topPosition >= 0
		columns = []
		for i, p in enumerate(optimal_node_ordering):
			if possible[i]:
				columns.append(p)
		min_v = math.inf
		for column in columns:
			child = self.simulateMove(deepcopy(env), column, self.opponent.position)
			min_v = min(min_v, self.MAX(child, depth - 1, alpha, beta))
			beta = min(beta, min_v)
			if min_v <= alpha:
				break
		return min_v

	def minimax(self, env, move, max_depth):
		best_move = 0
		alpha = -math.inf
		beta = math.inf
		max_v = -math.inf
		optimal_node_ordering = [3, 2, 4, 1, 5, 0, 6]
		possible = env.topPosition >= 0
		columns = []
		for i, p in enumerate(optimal_node_ordering):
			if possible[i]:
				columns.append(p)	
		for column in columns:
			child = self.simulateMove(deepcopy(env), column, self.position)
			v = self.MIN(child, max_depth - 1, alpha, beta)
			if v > max_v:
				max_v = v
				best_move = column
		move[:] = [best_move]

	def play(self, env, move):
		self.minimax(deepcopy(env), move, 2)
		
SQUARESIZE = 100
BLUE = (0,0,255)
BLACK = (0,0,0)
RED = (255,0,0)
YELLOW = (255,255,0)

ROW_COUNT = 6
COLUMN_COUNT = 7

pygame.init()

SQUARESIZE = 100

width = COLUMN_COUNT * SQUARESIZE
height = (ROW_COUNT+1) * SQUARESIZE

size = (width, height)

RADIUS = int(SQUARESIZE/2 - 5)

screen = pygame.display.set_mode(size)



