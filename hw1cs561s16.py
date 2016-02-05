import copy

__author__ = 'Martin'

#main function
class Solution:
    def main(self):
        file = FileOperator()
        file.read()
        task = file.task
        player = file.player
        cutoff = file.cutoff
        board = file.board
        state = file.state
        filename = "trace_state.txt"

        if task == 1:
            g = Greedy()
            file.write(filename, g.cal(player, board, state))
        elif task == 2:
            mm = Minimax()
            file.write(filename, mm.cal(player, cutoff, board, state))
        elif task == 3:
            p = Pruning()
            file.write(filename, p.cal(player, cutoff, board, state))


#operate the file including input and output
class FileOperator:
    task = None
    player = None
    cutoff = None
    board = []
    state = []

    def read(self):
        filename = 'input.txt'
        file = open(filename, "r")

        self.task = int(file.readline().strip('\n'))
        self.player = file.readline().strip('\n')
        self.cutoff = int(file.readline().strip('\n'))

        for i in range(5):
            line = file.readline().strip('\n')
            boardline = line.split(" ")
            self.board.append(boardline)

        for i in range(5):
            for j in range(5):
                self.board[i][j] = int(self.board[i][j])

        for i in range(5):
            line = file.readline().strip('\n')
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


#greedy best-first search
class Greedy:
    def cal(self, player, board, state):
        eva = Evaluation()
        action = Action()
        raidGrids = []
        freeGrids = []
        res = []
        bestValue = -float("inf")

        action.getRaidGrids(player, state, raidGrids)
        action.getFreeGrids(player, state, freeGrids)

        for i in range(len(freeGrids)):
            temp = copy.deepcopy(state)
            if raidGrids.__contains__(freeGrids[i]):
                action.raid(player, temp, freeGrids[i][0], freeGrids[i][1])
                value = eva.evaluation(player, board, temp)
            else:
                temp[freeGrids[i][0]][freeGrids[i][1]] = player
                value = eva.evaluation(player, board, temp)
            if value > bestValue:
                maxRaid = value
                res = temp

        return res


#minimax
class Minimax:
    res = None
    depth = None
    player = None
    buffer = ""
    def cal(self, player, cutoff, board, state):
        file = FileOperator()
        filename = "traverse_log.txt"
        self.depth = cutoff
        self.player = player
        self.minimax(player, cutoff, board, state, True, [0, 0])
        file.recordMinimax(filename, self.buffer)
        return self.res

    def minimax(self, player, cutoff, board, state, maxPlayer, location):
        action = Action()
        raidGrids = []
        freeGrids = []

        if player == 'X':
            enemy = 'O'
        else:
            enemy = 'X'

        #if it's the utility node
        if cutoff == 0:
            eva = Evaluation()
            value  = eva.evaluation(self.player, board, state)
            self.bufferStore(location, self.depth, value)
            return value

        action.getRaidGrids(player, state, raidGrids)
        action.getFreeGrids(player, state, freeGrids)


        if cutoff > 0:

            if maxPlayer:#for max player
                bestValue = -float('inf')
                self.bufferStore(location, self.depth-cutoff, bestValue)
                for i in range(freeGrids.__len__()):
                    if raidGrids.__contains__(freeGrids[i]):
                        temp = copy.deepcopy(state)
                        action.raid(player, temp, freeGrids[i][0], freeGrids[i][1])
                        value = self.minimax(enemy, cutoff-1, board, temp, False, freeGrids[i])
                    else:
                        temp = copy.deepcopy(state)
                        temp[freeGrids[i][0]][freeGrids[i][1]] = player
                        value = self.minimax(enemy, cutoff-1, board, temp, False, freeGrids[i])
                    if value > bestValue:
                        bestValue = value
                        if cutoff == self.depth:
                            self.res = temp
                    self.bufferStore(location, self.depth-cutoff, bestValue)
                return bestValue

            else:#for min player
                bestValue = float('inf')
                self.bufferStore(location, self.depth-cutoff, bestValue)
                for i in range(freeGrids.__len__()):
                    if raidGrids.__contains__(freeGrids[i]):
                        temp = copy.deepcopy(state)
                        action.raid(player, temp, freeGrids[i][0], freeGrids[i][1])
                        value = self.minimax(enemy, cutoff-1, board, temp, False, freeGrids[i])
                    else:
                        temp = copy.deepcopy(state)
                        temp[freeGrids[i][0]][freeGrids[i][1]] = player
                        value = self.minimax(enemy, cutoff-1, board, temp, False, freeGrids[i])
                    if value < bestValue:
                        bestValue = value
                        if cutoff == self.depth:
                            self.res = temp
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
    def cal(self, player, cutoff, board, state):
        file = FileOperator()
        filename = "traverse_log.txt"
        self.depth = cutoff
        self.player = player
        self.pruning(player, cutoff, board, state, True, [0, 0], -float("inf"), float("inf"))
        file.recordPruning(filename, self.buffer)
        return self.res

    def pruning(self, player, cutoff, board, state, maxPlayer, location, a, b):
        action = Action()
        raidGrids = []
        freeGrids = []

        if player == 'O':
            enemy = 'X'
        else:
            enemy = 'O'

        #if it's the utility node
        if cutoff == 0:
            eva = Evaluation()
            value  = eva.evaluation(self.player, board, state)
            self.bufferStore(location, self.depth, value, a, b)
            return value

        action.getRaidGrids(player, state, raidGrids)
        action.getFreeGrids(player, state, freeGrids)

        if cutoff > 0:

            if maxPlayer:#for max player
                bestValue = -float('inf')
                self.bufferStore(location, self.depth-cutoff, bestValue, a, b)
                for i in range(freeGrids.__len__()):
                    if raidGrids.__contains__(freeGrids[i]):
                        temp = copy.deepcopy(state)
                        action.raid(player, temp, freeGrids[i][0], freeGrids[i][1])
                        value = self.pruning(enemy, cutoff-1, board, temp, False, freeGrids[i], a, b)
                    else:
                        temp = copy.deepcopy(state)
                        temp[freeGrids[i][0]][freeGrids[i][1]] = player
                        value = self.pruning(enemy, cutoff-1, board, temp, False, freeGrids[i], a, b)

                    if value > bestValue:
                        bestValue = value
                        if cutoff == self.depth:
                            self.res = temp

                    if bestValue >= b:
                        self.bufferStore(location, self.depth-cutoff, bestValue, a, b)
                        break

                    a = max(a, bestValue)
                    self.bufferStore(location, self.depth-cutoff, bestValue, a, b)

                return bestValue

            else:#for min player
                bestValue = float('inf')
                self.bufferStore(location, self.depth-cutoff, bestValue, a, b)
                for i in range(freeGrids.__len__()):
                    if raidGrids.__contains__(freeGrids[i]):
                        temp = copy.deepcopy(state)
                        action.raid(player, temp, freeGrids[i][0], freeGrids[i][1])
                        value = self.pruning(enemy, cutoff-1, board, temp, False, freeGrids[i], a, b)
                    else:
                        temp = copy.deepcopy(state)
                        temp[freeGrids[i][0]][freeGrids[i][1]] = player
                        value = self.pruning(enemy, cutoff-1, board, temp, False, freeGrids[i], a, b)

                    if value < bestValue:
                        bestValue = value
                        if cutoff == self.depth:
                            self.res = temp

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

class Action:
    def getRaidGrids(self, player, state, raidGrids):
        l = 5
        #keep the order, from top left to bottom right mentioned in the rules
        for i in range(l):
            for j in range(l):
                if state[i][j] == player:
                    self.check(state, i, j, raidGrids)

    def getSneakGrids(self, player, state, raidGrids, sneakGrids):
        l = 5
        #keep the order, from top left to bottom right mentioned in the rules
        for i in range(l):
            for j in range(l):
                if state[i][j] == '*' and not raidGrids.__contains__([i, j]):
                    sneakGrids.append([i, j])

    def getFreeGrids(self, player, state, freeGrids):
        l = 5
        #keep the order, from top left to bottom right mentioned in the rules
        for i in range(l):
            for j in range(l):
                if state[i][j] == '*':
                    freeGrids.append([i, j])

    def check(self, state, m, n, res):
        for i in range(-1, 2):
            for j in range(-1, 2):
                if m+i >=0 and n+j >=0 and m+i<5 and n+j<5 and (i+j==1 or i+j==-1):
                    if state[m+i][n+j] == '*' and not res.__contains__([m+i, n+j]):
                        res.append([m+i, n+j])

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
        else:
            return


s = Solution()
s.main()