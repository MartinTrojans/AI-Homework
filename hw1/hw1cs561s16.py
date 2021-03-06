import sys

#main function
class Solution:
    inFilename = ""
    def __init__(self, inFilename):
        self.inFilename = inFilename
    def main(self):
        file = FileOperator()
        file.read(self.inFilename)
        task = file.task
        player = file.player
        cutoff = file.cutoff
        board = file.board
        state = file.state
        player1 = file.player1
        player1al = file.player1al
        player1cut = file.player1cut
        player2 = file.player2
        player2al = file.player2al
        player2cut = file.player2cut
        filename = "next_state.txt"

        if task == 1:
            g = Greedy()
            file.write(filename, g.cal(player, cutoff, board, state, False))
        elif task == 2:
            mm = Minimax()
            file.write(filename, mm.cal(player, cutoff, board, state, True))
        elif task == 3:
            p = Pruning()
            file.write(filename, p.cal(player, cutoff, board, state, True))
        elif task == 4:
            b = BattleSimulation()
            b.battle(player1, player1al, player1cut, player2, player2al, player2cut, board, state)


#operate the file including input and output
class FileOperator:
    task = None
    player = None
    cutoff = None
    player1 = None
    player1al = None
    player1cut = None
    player2 = None
    player2al = None
    player2cut = None
    board = []
    state = []

    def read(self, inFilename):
        file = open(inFilename, "r")

        self.task = int(file.readline().strip())
        if self.task != 4:
            self.player = file.readline().strip()
            self.cutoff = int(file.readline().strip())
        else:
            self.player1 = file.readline().strip()
            self.player1al = int(file.readline().strip())
            self.player1cut = int(file.readline().strip())
            self.player2 = file.readline().strip()
            self.player2al = int(file.readline().strip())
            self.player2cut = int(file.readline().strip())

        for i in range(5):
            line = file.readline().strip()
            boardline = line.split(" ")
            self.board.append(boardline)

        for i in range(5):
            for j in range(5):
                self.board[i][j] = int(self.board[i][j])

        for i in range(5):
            line = file.readline().strip()
            stateline = []
            for j in range(5):
                stateline.append(line[j])
            self.state.append(stateline)

        file.close()

    def write(self, filename, res):
        file = open(filename, "w")
        for i in range(5):
            line = ""
            for j in range(5):
                line += res[i][j]
            if i != 4:
                file.write(line + '\n')
            else:
                file.write(line)
        file.close()

    def recordMinimax(self, filename, buffer):
        file = open(filename, "w")
        buffer = "Node,Depth,Value\n" + buffer[:len(buffer)-1] #delete last \n
        file.writelines(buffer)
        file.close()

    def recordPruning(self, filename, buffer):
        file = open(filename, "w")
        buffer = "Node,Depth,Value,Alpha,Beta\n" + buffer[:len(buffer)-1] #delete last \n
        file.writelines(buffer)
        file.close()

    def recordBattle(self, filename, buffer):
        file = open(filename, "w")
        file.writelines(buffer[:len(buffer)-1])
        file.close()

#greedy best-first search
class Greedy:
    def cal(self, player, cutoff, board, state, traverse):
        eva = Evaluation()
        action = Action()
        freeGrids = []
        res = []
        bestValue = -float("inf")

        action.getFreeGrids(player, state, freeGrids)

        for i in range(len(freeGrids)):
            temp = action.copyMatrix(state)
            if action.canRaid(player, state, freeGrids[i][0], freeGrids[i][1]):
                action.raid(player, temp, freeGrids[i][0], freeGrids[i][1])
                value = eva.evaluation(player, board, temp)
            else:
                temp[freeGrids[i][0]][freeGrids[i][1]] = player
                value = eva.evaluation(player, board, temp)
            if value > bestValue:
                bestValue = value
                res = action.copyMatrix(temp)

        return res


#minimax
class Minimax:
    res = None
    depth = None
    player = None
    buffer = ""
    def cal(self, player, cutoff, board, state, traverse):
        file = FileOperator()
        filename = "traverse_log.txt"
        self.depth = cutoff
        self.player = player
        self.minimax(player, cutoff, board, state, True, [0, 0])
        if traverse:
            file.recordMinimax(filename, self.buffer)
        return self.res

    def minimax(self, player, cutoff, board, state, maxPlayer, location):
        action = Action()
        freeGrids = []

        if player == 'X':
            enemy = 'O'
        else:
            enemy = 'X'


        #if it's the utility node
        if cutoff == 0:
            eva = Evaluation()
            value  = eva.evaluation(self.player, board, state)
            self.bufferStore(location, self.depth-cutoff, value)
            return value

        action.getFreeGrids(player, state, freeGrids)

        if len(freeGrids) == 0:
            eva = Evaluation()
            value  = eva.evaluation(self.player, board, state)
            self.bufferStore(location, self.depth-cutoff, value)
            return value



        if cutoff > 0:

            if maxPlayer:#for max player
                bestValue = -float('inf')
                self.bufferStore(location, self.depth-cutoff, bestValue)
                for i in range(len(freeGrids)):
                    temp = action.copyMatrix(state)
                    if action.canRaid(player, state, freeGrids[i][0], freeGrids[i][1]):
                        action.raid(player, temp, freeGrids[i][0], freeGrids[i][1])
                        value = self.minimax(enemy, cutoff-1, board, temp, not maxPlayer, freeGrids[i])
                    else:
                        temp[freeGrids[i][0]][freeGrids[i][1]] = player
                        value = self.minimax(enemy, cutoff-1, board, temp, not maxPlayer, freeGrids[i])
                    if value > bestValue:
                        bestValue = value
                        if cutoff == self.depth:
                            self.res = action.copyMatrix(temp)
                    self.bufferStore(location, self.depth-cutoff, bestValue)
                return bestValue

            else:#for min player
                bestValue = float('inf')
                self.bufferStore(location, self.depth-cutoff, bestValue)
                for i in range(len(freeGrids)):
                    temp = action.copyMatrix(state)
                    if action.canRaid(player, state, freeGrids[i][0], freeGrids[i][1]):
                        action.raid(player, temp, freeGrids[i][0], freeGrids[i][1])
                        value = self.minimax(enemy, cutoff-1, board, temp, not maxPlayer, freeGrids[i])
                    else:
                        temp[freeGrids[i][0]][freeGrids[i][1]] = player
                        value = self.minimax(enemy, cutoff-1, board, temp, not maxPlayer, freeGrids[i])
                    if value < bestValue:
                        bestValue = value
                        if cutoff == self.depth:
                            self.res = action.copyMatrix(temp)
                    self.bufferStore(location, self.depth-cutoff, bestValue)
                return bestValue

    def bufferStore(self, location, cutoff, value):
        line = ""
        if cutoff == 0:
            line += "root"
        else:
            line += chr((location[1] - 0) + ord("A"))
            line += chr(location[0] + 1 + ord("0"))
        if value == float("inf"):
            valueStr = "Infinity"
        elif value == -float("inf"):
            valueStr = "-Infinity"
        else:
            valueStr = str(value)
        line += ',' + str(cutoff) + ',' + valueStr + '\n'
        self.buffer += line

#alphabeta pruning
class Pruning:
    res = None
    depth = None
    player = None
    buffer = ""
    def cal(self, player, cutoff, board, state, traverse):
        file = FileOperator()
        filename = "traverse_log.txt"
        self.depth = cutoff
        self.player = player
        self.pruning(player, cutoff, board, state, True, [0, 0], -float("inf"), float("inf"))
        if traverse:
            file.recordPruning(filename, self.buffer)
        return self.res

    def pruning(self, player, cutoff, board, state, maxPlayer, location, a, b):
        action = Action()
        freeGrids = []

        if player == 'O':
            enemy = 'X'
        else:
            enemy = 'O'

        #if it's the utility node
        if cutoff == 0:
            eva = Evaluation()
            value  = eva.evaluation(self.player, board, state)
            self.bufferStore(location, self.depth-cutoff, value, a, b)
            return value

        action.getFreeGrids(player, state, freeGrids)

        if len(freeGrids) == 0:
            eva = Evaluation()
            value  = eva.evaluation(self.player, board, state)
            self.bufferStore(location, self.depth-cutoff, value, a, b)
            return value


        if cutoff > 0:

            if maxPlayer:#for max player
                bestValue = -float('inf')
                self.bufferStore(location, self.depth-cutoff, bestValue, a, b)
                for i in range(len(freeGrids)):
                    temp = action.copyMatrix(state)
                    if action.canRaid(player, state, freeGrids[i][0], freeGrids[i][1]):
                        action.raid(player, temp, freeGrids[i][0], freeGrids[i][1])
                        value = self.pruning(enemy, cutoff-1, board, temp, not maxPlayer, freeGrids[i], a, b)
                    else:
                        temp[freeGrids[i][0]][freeGrids[i][1]] = player
                        value = self.pruning(enemy, cutoff-1, board, temp, not maxPlayer, freeGrids[i], a, b)

                    if value > bestValue:
                        bestValue = value
                        if cutoff == self.depth:
                            self.res = action.copyMatrix(temp)

                    if bestValue >= b:
                        self.bufferStore(location, self.depth-cutoff, bestValue, a, b)
                        break

                    a = max(a, bestValue)
                    self.bufferStore(location, self.depth-cutoff, bestValue, a, b)

                return bestValue

            else:#for min player
                bestValue = float('inf')
                self.bufferStore(location, self.depth-cutoff, bestValue, a, b)
                for i in range(len(freeGrids)):
                    temp = action.copyMatrix(state)
                    if action.canRaid(player, state, freeGrids[i][0], freeGrids[i][1]):
                        action.raid(player, temp, freeGrids[i][0], freeGrids[i][1])
                        value = self.pruning(enemy, cutoff-1, board, temp, not maxPlayer, freeGrids[i], a, b)
                    else:
                        temp[freeGrids[i][0]][freeGrids[i][1]] = player
                        value = self.pruning(enemy, cutoff-1, board, temp, not maxPlayer, freeGrids[i], a, b)

                    if value < bestValue:
                        bestValue = value
                        if cutoff == self.depth:
                            self.res = action.copyMatrix(temp)

                    if bestValue <= a:
                        self.bufferStore(location, self.depth-cutoff, bestValue, a, b)
                        break

                    b = min(b, bestValue)
                    self.bufferStore(location, self.depth-cutoff, bestValue, a, b)

                return bestValue

    def bufferStore(self, location, cutoff, value, a, b):
        line = ""
        if cutoff == 0:
            line += "root"
        else:
            line += chr((location[1] - 0) + ord("A"))
            line += chr(location[0] + 1 + ord("0"))
        if value == float("inf"):
            valueStr = "Infinity"
        elif value == -float("inf"):
            valueStr = "-Infinity"
        else:
            valueStr = str(value)
        if a == float("inf"):
            alphaStr = "Infinity"
        elif a == -float("inf"):
            alphaStr = "-Infinity"
        else:
            alphaStr = str(a)
        if b == float("inf"):
            betaStr = "Infinity"
        elif b == -float("inf"):
            betaStr = "-Infinity"
        else:
            betaStr = str(b)

        line += ',' + str(cutoff) + ',' + valueStr + "," + alphaStr + "," + betaStr +'\n'

        self.buffer += line


#simulate the battle
class BattleSimulation:
    buffer = ""
    def battle(self, firstPlayer, p1al, p1cut, secondPlayer, p2al, p2cut, board, state):
        filename = "trace_state.txt"
        action = Action()
        file = FileOperator()
        curState = state
        if p1al == 1:
            p1 = Greedy()
        elif p1al == 2:
            p1 = Minimax()
        else:
            p1 = Pruning()
        if p2al == 1:
            p2 = Greedy()
        elif p2al == 2:
            p2 = Minimax()
        else:
            p2 = Pruning()

        while(not action.checkEnd(curState)):
            curState = p1.cal(firstPlayer, p1cut, board, curState, False)
            self.bufferStore(curState)
            if action.checkEnd(curState):
                break
            curState = p2.cal(secondPlayer, p2cut, board, curState, False)
            self.bufferStore(curState)

        file.recordBattle(filename, self.buffer)

    def bufferStore(self, matrix):
        l = 5
        for i in range(l):
            line = ""
            for j in range(l):
                line += matrix[i][j]
            line += '\n'
            self.buffer += line

#some useful actions
class Action:

    def getRaidGrids(self, player, state, raidGrids):
        l = 5
        for i in range(l):
            for j in range(l):
                if state[i][j] == "*":
                    if i == 0:
                        if state[i+1][j] == player:
                            raidGrids.append([i,j])
                            break
                    elif i == l-1:
                        if state[i-1][j] == player:
                            raidGrids.append([i,j])
                            break
                    elif state[i+1][j] == player or state[i-1][j] == player:
                        raidGrids.append([i,j])
                        break
                    if j == 0:
                        if state[i][j+1] == player:
                            raidGrids.append([i,j])
                            break
                    elif j == l-1:
                        if state[i][j-1] == player:
                            raidGrids.append([i,j])
                            break
                    elif state[i][j+1] == player or state[i][j-1] == player:
                        raidGrids.append([i,j])
                        break

    def getFreeGrids(self, player, state, freeGrids):
        l = 5
        #keep the order, from top left to bottom right mentioned in the rules
        for i in range(l):
            for j in range(l):
                if state[i][j] == '*':
                    freeGrids.append([i, j])

    def canRaid(self, player, state, i, j):
        if i > 0 and state[i-1][j] == player: return True
        if i < 4 and state[i+1][j] == player: return True
        if j > 0 and state[i][j-1] == player: return True
        if j < 4 and state[i][j+1] == player: return True

    def raid(self, player, state, m, n):
        state[m][n] = player
        if player == 'X':
            enemy = 'O'
        else:
            enemy = 'X'
        for i in range(-1, 2):
            for j in range(-1, 2):
                if m+i >=0 and n+j >=0 and m+i<5 and n+j<5 and (i+j==1 or i+j==-1):
                    if state[m+i][n+j] == enemy:
                        state[m+i][n+j] = player

    def checkEnd(self, state):
        for i in range(5):
            for j in range(5):
                if state[i][j] == '*':
                    return False
        return True

    def copyMatrix(self, matrix):
        return [r[:] for r in matrix]

#evaluation for the current state
class Evaluation:
    def evaluation(self, player, board, state):
        len = 5
        xcount = 0
        ocount = 0

        for i in range(len):
            for j in range(len):
                if state[i][j] == 'X':
                    xcount += board[i][j]
                elif state[i][j] == 'O':
                    ocount += board[i][j]

        if player == 'X':
            return xcount - ocount
        elif player == 'O':
            return ocount - xcount

if __name__ == '__main__':
    s = Solution(sys.argv[2])
    s.main()
