__author__ = 'Martin'

import sys
import copy

class Main:

    def __init__(self, fileName):
        self.fileName = fileName

    def main(self):

        f = FIO()
        kb = KB()
        f.read(self.fileName, kb)
        enum = Enum()
        dm = DM()

        for p in kb.P:
            kb.addBufferP(enum.enumAsk(p, kb))


        for eu in kb.EU:
            kb.addBufferEU(dm.EU(eu, kb))

        for meu in kb.MEU:
            kb.addBufferMEU(dm.MEU(meu, kb))

        f.write(kb)


class FIO:
    def read(self, fileName, kb):
        file = open(fileName, "r")

        newLine = file.readline().strip().split("(")
        while newLine[0] != "******":
            params = self.parseParams(newLine[1][:len(newLine[1])-1])
            if newLine[0] == "P":
                kb.P.append(params)
            elif newLine[0] == "EU":
                kb.EU.append(params)
            elif newLine[0] == "MEU":
                kb.MEU.append(params)
            newLine = file.readline().strip().split("(")

        newLine = file.readline().strip()
        while newLine != "******":
            names = newLine.split(" | ")
            newLine = file.readline().strip()
            n = Node(names[0])
            if len(names) > 1:
                n.parent = names[1].strip().split(" ")
                while newLine != "***" and newLine != "******":
                    strs = newLine.split(" ")
                    n.value.append(float(strs[0]))
                    n.bools.append("".join(strs[1:]))
                    newLine = file.readline().strip()
                    if newLine == '':
                        break
            else:
                if newLine == 'decision':
                    n.decision = True
                    n.value.append(1) #unknown
                else:
                    n.value.append(float(newLine))
                n.bools.append(None)
                newLine = file.readline().strip()
            kb.tree.append(n)
            if newLine == '':
                return
            if newLine == "******":
                break
            else:
                newLine = file.readline().strip()#if there exist nextline

        newLine = file.readline().strip()
        while newLine != '':
            names = newLine.split(" | ")
            newLine = file.readline().strip()
            n = Node(names[0])
            n.parent = names[1].strip().split(" ")
            while newLine != "***":
                strs = newLine.split(" ")
                n.value.append(float(strs[0]))
                n.bools.append("".join(strs[1:]))
                newLine = file.readline().strip()
                if newLine == '':
                    break
            kb.tree.append(n)

        file.close()


    def parseParams(self, paraStr):
        expression = Expression()
        params = paraStr.split(" | ")
        nameArrays = params[0].split(", ")
        for name in nameArrays:
            nameArray = name.split(" = ")
            expression.name.append(nameArray[0])
            if len(nameArray) > 1:
                if nameArray[1] == "+":
                    expression.value.append(True)
                elif nameArray[1] == "-":
                    expression.value.append(False)
            else:
                expression.value.append(None)
        if len(params) > 1:
            nameArrays = params[1].split(", ")
            for i in range(len(nameArrays)):
                eparams = nameArrays[i].split(" = ")
                expression.parent.append(eparams[0])
                if len(eparams) > 1:
                    if eparams[1] == "+":
                        expression.pvalues.append(True)
                    elif eparams[1] == "-":
                        expression.pvalues.append(False)
                else:
                    expression.pvalues.append(None)
        return expression


    def write(self, kb):
        file = open("output.txt", "w")
        file.write(kb.buffer[:len(kb.buffer)-1])    #delete the final \n



class Node:

    def __init__(self, name):
        self.name = name
        self.value = []
        self.bools = []
        self.parent = []
        self.child = []
        self.decision = False

class Expression:

    def __init__(self):
        self.name = []
        self.value = []
        self.parent = []
        self.pvalues = []


class KB:
    def __init__(self):
        self.tree = []
        self.P = []
        self.EU = []
        self.MEU = []
        self.buffer = ""

    def addBufferP(self, ele):
        self.buffer += str("%.2f" % ele)
        self.buffer += "\n"

    def addBufferEU(self, ele):
        self.buffer += str("%.f" % ele)
        self.buffer += "\n"

    def addBufferMEU(self, list):
        self.buffer += " ".join(list[0]) + " "
        self.buffer += str("%.f" % list[1])
        self.buffer += "\n"


# don't use the algorithm of the textbook
class Enum:
    def enumAsk(self, p, kb):
        q = []
        res = []
        res.append(p.value)
        self.enum(len(p.value), 0, [], res)
        for treeNode in kb.tree:
            if treeNode.decision:
                for i, decisionName in enumerate(p.parent):
                    if treeNode.name == decisionName:
                        if p.pvalues[i]:
                            treeNode.value[0] = 1
                        else:
                            treeNode.value[0] = 0
        for array in res:
            ex = {}
            for i in range(len(array)):
                ex[p.name[i]] = array[i]
            for i in range(len(p.parent)):
                ex[p.parent[i]] = p.pvalues[i]
            q.append(self.enumAll(kb.tree, ex))
        return self.normorlize(q)

    def enumAll(self, vars, ex):
        if len(vars) == 0:
            return 1.0
        vars = copy.deepcopy(vars)
        y = vars.pop(0)
        if y.name == "utility":
            return 1.0
        if ex.get(y.name) != None:
            return self.conP(y, ex) * self.enumAll(vars, copy.deepcopy(ex))
        else:
            ex[y.name] = True
            y1 = self.conP(y, ex) * self.enumAll(vars, copy.deepcopy(ex))
            ex[y.name] = False
            y2 = self.conP(y, ex) * self.enumAll(vars, copy.deepcopy(ex))
            return y1 + y2

    def conP(self, y, ex):
        bools = ""
        for p in y.parent:
            bools += "+" if ex.get(p) else "-"
        if bools == '':
            if ex.get(y.name) == True:
                return y.value[0]
            elif ex.get(y.name) == False:
                return 1 - y.value[0]
        else:
            if ex.get(y.name) == True:
                return y.value[y.bools.index(bools)]
            elif ex.get(y.name) == False:
                return 1 - y.value[y.bools.index(bools)]


    def enum(self, len, i, temp, res):
        if i == len:
            if not res.__contains__(temp):
                res.append(temp)
            return
        self.enum(len, i+1, copy.deepcopy(temp + [True]), res)  #does it need deepcopy
        self.enum(len, i+1, copy.deepcopy(temp + [False]), res)


    def normorlize(self, q):
        if len(q) == 1:
            return q
        sum = 0
        for num in q:
            sum += num
        if sum == 0:
            return 0
        return q[0]/sum


class DM:
    def EU(self, eu, kb):
        enum = Enum()
        value = 0
        for treeNode in kb.tree:
            if treeNode.decision:
                for i, decisionName in enumerate(eu.name):
                    if treeNode.name == decisionName:
                        if eu.value[i]:
                            treeNode.value[0] = 1
                        else:
                            treeNode.value[0] = 0
            if treeNode.name == "utility": #it's the final node or not exsit
                for i, boolStr in enumerate(treeNode.bools):
                    expression = Expression()
                    expression.name = treeNode.parent
                    expression.parent = eu.parent
                    expression.pvalues = eu.pvalues
                    for ch in boolStr:
                        if ch == '+':
                            expression.value.append(True)
                        elif ch == '-':
                            expression.value.append(False)
                    value += enum.enumAsk(expression, kb) * treeNode.value[i]
        return value

    def MEU(self, meu, kb):
        tempRes = []
        max = -float('Inf')
        self.enumBools(len(meu.name), 0, [], tempRes)
        for boolVal in tempRes:
            eu = Expression()
            eu.name = meu.name
            eu.value = boolVal
            eu.parent = meu.parent
            eu.pvalues = meu.pvalues
            newValue = self.EU(eu, kb)
            if newValue > max:
                max = newValue
                decision = boolVal
        resPart1 = []
        for des in decision:
            if des:
                resPart1.append('+')
            else:
                resPart1.append('-')
        res = []
        res.append(resPart1)
        res.append(max)
        return res

    def enumBools(self, len, i, temp, res):
        if i == len:
            res.append(temp)
            return
        self.enumBools(len, i+1, copy.deepcopy(temp + [True]), res)  #does it need deepcopy
        self.enumBools(len, i+1, copy.deepcopy(temp + [False]), res)


main = Main(sys.argv[2])
main.main()