import copy
import sys

__author__ = 'Martin'


class Solution:
    def __init__(self, filename):
        self.filename = filename

    def main(self):
        f = FIO()
        fol = FOLBC()
        kb = KB()
        f.read(self.filename, kb)
        fol.BCask(kb, kb.goals)
        f.write("output.txt", fol.buffer)


class FIO:
    def read(self, fileName, kb):
        file = open(fileName, "r")

        goals = file.readline().strip().split(" && ")
        for goal in goals:
            kb.storeGoal(self.parserPre(goal))
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
        if pre[0] == '~':
            negation = True
            pre = pre[1:]
        else:
            negation = False
        strs = pre.split("(")
        name = strs[0].strip()
        vars = strs[1][:len(strs[1]) - 1].split(", ")

        return Predicate(name, vars, negation)

    def parserImp(self, left, right):
        leftStrs = left.strip().split(" && ")
        preList = []
        for pre in leftStrs:
            preList.append(self.parserPre(pre))
        return Implication(preList, self.parserPre(right))


class Predicate:
    def __init__(self, name, vars, negation=False):
        self.name = name
        self.vars = vars
        self.negation = negation

    def match(self, other):
        if self.name == other.name and len(self.vars) == len(other.vars):
            for i in range(len(self.vars)):
                if self.vars[i][0].isupper() and other.vars[i][0].isupper() and self.vars[i] != other.vars[i]:
                    return False
            return True
        else:
            return False

    def __eq__(self, other):
        return self.name == other.name and self.vars == other.vars and self.negation == other.negation

    def toString(self):
        negPart = "~" if self.negation else ""
        namePart = self.name
        varSegements = []
        for var in self.vars:
            varSegements.append("_") if var[0].islower() else varSegements.append(var)
        varPart = ", ".join(varSegements)
        return negPart + namePart + "(" + varPart + ")"


class Implication:
    def __init__(self, lhs, rhs):
        self.lhs = lhs
        self.rhs = rhs


class FOLBC:
    def __init__(self):
        self.buffer = ""

    def BCask(self, kb, query):
        for q in query:
            try:
                next(self.BCOr(kb, q, {}, []))
            except StopIteration:
                self.buffer += "False"
                return
        self.buffer += "True"

    def BCOr(self, kb, goal, theta, stack):
        hasImp = False
        hasYield = False

        for imp in FOLBC.fetch(kb, goal, stack):
            hasImp = True
            hasYield = False
            self.buffer += "Ask: " + goal.toString() + "\n"
            imp = copy.deepcopy(imp)
            FOLBC.standardize(imp, goal, theta)
            newTheta = self.unify(imp.rhs.vars, goal.vars, copy.deepcopy(theta))
            for ans in self.BCAnd(kb, imp.lhs, dict(theta, **newTheta), stack):
                tempgoal = FOLBC.subst(ans, goal)
                self.buffer += "True: " + tempgoal.toString() + "\n"
                hasYield = True
                yield ans
            if len(imp.lhs) != 0:
                stack.pop()

        if not hasImp:
            self.buffer += "Ask: " + goal.toString() + "\n"
            self.buffer += "False: " + goal.toString() + "\n"
        if hasImp and not hasYield:
            self.buffer += "False: " + goal.toString() + "\n"

    def BCAnd(self, kb, goals, theta, stack):
        if len(goals) == 0:
            yield theta
        else:
            first = goals[0]
            rest = goals[1:]

            for theta1 in self.BCOr(kb, FOLBC.subst(theta, first), theta, copy.deepcopy(stack)):
                for theta2 in self.BCAnd(kb, rest, theta1, copy.deepcopy(stack)):
                    yield theta2

    @staticmethod
    def fetch(kb, goal, stack):
        i = 0
        for imp in kb.implications:
            if imp.rhs.match(goal) and i not in stack:
                stack.append(i)
                yield imp
            i += 1
        for pre in kb.predicates:
            if pre.match(goal):
                yield Implication([], pre)

    @staticmethod
    def standardize(imp, goal, theta):
        map = {}
        set = []
        tempgoal = copy.deepcopy(goal)
        for idx, var in enumerate(tempgoal.vars):
            if var[0].islower():
                if imp.rhs.vars[idx][0].islower():
                    map[imp.rhs.vars[idx]] = tempgoal.vars[idx]
                    imp.rhs.vars[idx] = tempgoal.vars[idx]
                set.append(tempgoal.vars[idx])
            elif var in theta.values():
                tempgoal.vars[idx] = list(theta.keys())[list(theta.values()).index(var)]
                if imp.rhs.vars[idx][0].islower():
                    map[imp.rhs.vars[idx]] = tempgoal.vars[idx]
                    imp.rhs.vars[idx] = tempgoal.vars[idx]
                set.append(tempgoal.vars[idx])
        for idx, var in enumerate(tempgoal.vars):
            if var[0].isupper() and imp.rhs.vars[idx][0].islower():
                var = imp.rhs.vars[idx]
                while imp.rhs.vars[idx] in set:
                    imp.rhs.vars[idx] = chr(ord(imp.rhs.vars[idx]) - ord('a') + 1 % 26 + ord('a'))
                map[var] = imp.rhs.vars[idx]
        for i in range(len(imp.lhs)):
            for j in range(len(imp.lhs[i].vars)):
                if imp.lhs[i].vars[j] in map.keys():
                    imp.lhs[i].vars[j] = map.get(imp.lhs[i].vars[j])
                else:
                    var = imp.lhs[i].vars[j]
                    while imp.lhs[i].vars[j] in set:
                        imp.lhs[i].vars[j] = chr((ord(imp.lhs[i].vars[j]) - ord('a') + 1) % 26 + ord('a'))
                    map[var] = imp.lhs[i].vars[j]
                    set.append(map[var])

    def unify(self, rhs, goal, theta):
        if rhs == goal:
            return theta
        if len(rhs) > 1:
            return self.unify(rhs[1:], goal[1:], self.unify([rhs[0]], [goal[0]], theta))
        if rhs[0][0].islower():
            return self.unifyVar(rhs[0], goal[0], theta)
        if goal[0][0].islower():
            return self.unifyVar(goal[0], rhs[0], theta)
        return {}

    def unifyVar(self, var, x, theta):
        if theta is None or len(theta) == 0:
            theta[var] = x
            return theta
        if var in theta.keys():
            return self.unify([theta.get(var)], [x], theta)
        if x in theta.keys():
            return self.unify([var], [theta.get(x)], theta)
        theta[var] = x
        return theta

    @staticmethod
    def subst(theta, alpha):
        if theta is None or len(theta) == 0:
            return alpha
        nalpha = copy.deepcopy(alpha)
        for idx, var in enumerate(alpha.vars):
            if var[0].islower() and var in theta.keys():
                nalpha.vars[idx] = theta.get(var)
        return nalpha


class KB:
    def __init__(self):
        self.goals = []
        self.implications = []
        self.predicates = []
        self.substitutions = {}

    def storeGoal(self, goal):
        self.goals.append(goal)

    def storeImplication(self, implication):
        self.implications.append(implication)

    def storePredicate(self, predicate):
        self.predicates.append(predicate)

    def storeSubstitution(self, substitution):
        self.substitutions += substitution


s = Solution(sys.argv[2])
s.main()