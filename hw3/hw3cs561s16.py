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

        for p in kb.P:
            kb.addBuffer(enum.enumAsk(p, kb))

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

        #newLine = file.readline().strip()
        #while newLine != "******":

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

    def addBuffer(self, list):
        for ele in list:
            self.buffer += str("%.2f" % ele) + " "
        self.buffer += "\n"


# don't use the algorithm of the textbook
class Enum:
    def enumAsk(self, p, kb):
        q = []
        res = []
        self.enum(p.value, 0, [], res)
        for array in res:
            ex = {}
            px = {}
            for i in range(len(array)):
                ex[p.name[i]] = array[i]
            for i in range(len(p.parent)):
                ex[p.parent[i]] = p.pvalues[i]
                px[p.parent[i]] = p.pvalues[i]
            q.append(self.enumAll(kb.tree, ex, px))
            print("end")
        return self.normorlize(q)

    def enumAll(self, vars, ex, px):
        if len(vars) == 0:
            return 1.0
        vars = copy.deepcopy(vars)
        y = vars.pop(0)
        if px.get(y.name) != None:
            return self.enumAll(vars, copy.deepcopy(ex), px)
        if ex.get(y.name) != None:
            yy = self.conP(y, ex) * self.enumAll(vars, copy.deepcopy(ex), px)
            print(ex)
            print(y.name + " " + str(self.conP(y, ex)) + " " + str(yy))
            return yy
        else:
            ex[y.name] = True
            y1 = self.conP(y, ex) * self.enumAll(vars, copy.deepcopy(ex), px)
            print(ex)
            print(y.name + " " + str(self.conP(y, ex)) + " " + str(y1))
            ex[y.name] = False
            y2 = self.conP(y, ex) * self.enumAll(vars, copy.deepcopy(ex), px)
            print(ex)
            print(y.name + " " + str(self.conP(y, ex)) + " " + str(y2))
            print(y.name + " " + str(self.conP(y, ex)) + " " + str(y1+y2))
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

    def enum(self, array, i, temp, res):
        if i == len(array):
            res.append(temp)
            return
        if array[i] == None:
            self.enum(array, i+1, copy.deepcopy(temp + [True]), res)  #does it need deepcopy
            self.enum(array, i+1, copy.deepcopy(temp + [False]), res)
        else:
            self.enum(array, i+1, temp + [array[i]], res)


    def normorlize(self, q):
        if len(q) == 1:
            return q
        sum = 0
        for num in q:
            sum += num
        for i in range(len(q)):
            q[i] /= sum
        return q





main = Main("sample04.txt")
main.main()