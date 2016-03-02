import random

__author__ = 'Martin'

content = ""
task = random.randint(1, 3)
playerRandom = random.random()
if playerRandom <= 0.5:
    player = 'X'
else:
    player = 'O'
cutoff = random.randint(1, 20)
board = [[0 for i in range(5)] for j in range(5)]
for i in range(5):
    for j in range(5):
        board[i][j] = random.randint(1,1000)
state = [['' for i in range(5)] for j in range(5)]
for i in range(5):
    for j in range(5):
        stateRandom = random.randint(1, 3)
        if stateRandom == 1:
            state[i][j] = '*'
        elif stateRandom == 2:
            state[i][j] = 'O'
        else:
            state[i][j] = 'X'

content += str(task) + '\n'
content += player + '\n'
content += str(cutoff) + '\n'
for i in range(5):
    line = ""
    for j in range(5):
        if j != 4:
            line += str(board[i][j]) + ' '
        else:
            line += str(board[i][j])
    line += '\n'
    content += line
for i in range(5):
    line = ""
    for j in range(5):
        line += state[i][j]
    if i != 4:
        line += '\n'
    content += line

filename = 'input.txt'

file = open(filename, "w")

file.writelines(content)