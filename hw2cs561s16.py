import sys

__author__ = 'Martin'

class Solution:

    def __init__(self, filename):
        self.filename = filename

    def main(self,):
        f = FIO()
        s = FOLBC()
        kb = KB()
        f.read(self.filename, kb)
        s.BCOr(kb, kb.goal)
        f.write("output.txt", s.buffer)


class FIO:

    def read(self, fileName, kb):
        file = open(fileName, "r")

        kb.storeGoal(self.parserPre(file.readline().strip()))
        num = int(file.readline().strip())

        while num > 0:
            sen = file.readline()
            strs = sen.split("=>")
            if len(strs) == 1:
                kb.storePredicate(self.parserPre(strs[0]))
            else:
                kb.storeImplication(self.parserImp(strs[0], strs[1]))
            num -= 1

    def write(self, fileName, buffer):
        file = open(fileName, "w")
        file.write(buffer)

    def parserPre(self, pre):
        pre = pre.strip()
        value = True
        if pre[0] == '~':
            negation = True
            pre = pre[1:]
        else:
            negation = False
        strs = pre.split("(")
        name = strs[0].strip()
        vars = strs[1][:len(strs[1])-1].strip(", ")
        for var in vars:
            if var[0].islower():
                value = False
                break
        return Predicate(name, vars, negation, value)

    def parserImp(self, left, right):
        leftStrs = left.strip().split(" && ")
        preList = []
        for pre in leftStrs:
            preList.append(self.parserPre(pre))
        return Implication(preList, self.parserPre(right))


class Predicate:
    def __init__(self, name, vars, negation = False, value = False):
        self.name = name
        self.vars = vars
        self.negation = negation
        self.value = value

    def match(self, other):
        return self.name == other.name

    def __eq__(self, other):
        return self.name == other.name and self.vars == other.vars and self.negation == other.negation

    def toString(self):
        return ["~" + self.name + "(" + self.vars.join(", ") + ")", self.name + "(" + self.vars.join(", ") + ")"][self.negation is True]

class Implication:
    def __init__(self, lhs, rhs):
        self.lhs = lhs
        self.rhs = rhs


class FOLBC:

    def __init__(self):
        self.buffer = ""

    def BCask(self, kb, query):
        return self.BCOr(kb, query, {})

    def BCOr(self, kb, goal, theta):
        self.buffer += "Ask: " + goal.toString() + "\n"
        res = {}
        if kb.mathGoal(goal):
            self.buffer += "True: " + goal.toString() + "\n"
            return theta
        for rules in self.fetch(kb, goal):
            for imp in rules:
                newTheta = self.unify(imp.rhs, goal)
                for subs in self.BCAnd(kb, imp.lhs, theta + newTheta):
                    res += subs
        return res

    def BCAnd(self, kb, goals, theta):
        if len(theta) == 0:
            return
        if len(goals) == 0:
            return theta
        res = {}
        first = goals[0]
        rest = goals[1:]
        for theta1 in self.BCOr(kb, self.subst(theta, first), theta):
            for theta2 in self.BCAnd(kb, rest, theta1):
                res += theta2
        return res

    def fetch(self, kb, goal):
        res = []
        for imp in kb.implications:
            if imp.rhs.match(goal):
                res.append(imp)
        return res

    def unify(self, rhs, goal):
        newTheta = {}
        for idx, var in rhs.vars:
            if var[0].islower():
                newTheta[var] = goal.vars[idx]
        return newTheta

    def subst(self, theta, alpha):
        for var in alpha.vars:
            if var[0].islower() and theta.has_key(var):
                var = theta.get(var) #it will change the value of the alpha?
        return alpha


class KB:

    def __init__(self):
        self.goal = None
        self.implications = []
        self.predicates = []
        self.substitutions = {}

    def storeGoal(self, goal):
        self.goal = goal

    def storeImplication(self, implication):
        self.implications.append(implication)

    def storePredicate(self, predicate):
        self.predicates.append(predicate)

    def storeSubstitution(self, substitution):
        self.substitutions += substitution

    def mathGoal(self, goal):
        for pre in predicates:
            if pre == goal:
                return True
        return False

#s = Solution(sys.argv[2])
s = Solution("sample1.out.txt")
s.main()