from collections import Set
import copy
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
        s.BCask(kb, kb.goals)
        f.write("output.txt", s.buffer)


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
        value = True
        if pre[0] == '~':
            negation = True
            pre = pre[1:]
        else:
            negation = False
        strs = pre.split("(")
        name = strs[0].strip()
        vars = strs[1][:len(strs[1])-1].split(", ")
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
        ans = self.BCAnd(kb, query, {})
        self.buffer += str(ans[0])

    def BCOr(self, kb, goal, theta):
        hasImp = False
        if kb.matchGoal(goal):
            self.buffer += "Ask: " + goal.toString() + "\n"
            self.buffer += "True: " + goal.toString() + "\n"
            return [True, theta]

        for imp in self.fetch(kb, goal):
            imp = copy.deepcopy(imp)
            self.buffer += "Ask: " + goal.toString() + "\n"
            self.standardize(imp, goal, theta)
            newTheta = self.unify(imp.rhs.vars, goal.vars, copy.deepcopy(theta))
            ans = self.BCAnd(kb, imp.lhs, dict(theta, **newTheta))
            hasImp = ans[0]
            subs = ans[1]
            goal = self.subst(subs, goal)
            tempsub = self.subst(subs, imp.rhs)
            if goal != tempsub:
                hasImp = False
            if hasImp:
                self.buffer += "True: " + goal.toString() + "\n"
                return [True, subs]

        if not hasImp:
            self.buffer += "False: " + goal.toString() + "\n"
            return [False, theta]

    def BCAnd(self, kb, goals, theta):
        if len(goals) == 0:
            return [True, theta]
        first = goals[0]
        rest = goals[1:]
        ans1 = self.BCOr(kb, self.subst(theta, first), theta)
        if ans1[0]:
            ans2 = self.BCAnd(kb, rest, ans1[1])
            return [ans2[0], ans2[1]]
        else:
            return [False, theta]

    def fetch(self, kb, goal):
        res = []
        for imp in kb.implications:
            if imp.rhs.match(goal):
                res.append(imp)
        for pre in kb.predicates:
            if pre.match(goal):
                res.append(Implication([], pre))
        return res
    '''
    def standardize(self, imp, goal, theta):
        if theta is None:
            return
        map = {}
        for idx, var in enumerate(goal.vars):
            if var[0].islower() and imp.rhs.vars[idx][0].islower():
                map[imp.rhs.vars[idx]] = var
                imp.rhs.vars[idx] = var
            if var in theta.values():
                map[imp.rhs.vars[idx]] = list(theta.keys())[list(theta.values()).index(var)]
                if imp.rhs.vars[idx][0].islower():
                    imp.rhs.vars[idx] = list(theta.keys())[list(theta.values()).index(var)]
        for i in range(len(imp.lhs)):
            for j in range(len(imp.lhs[i].vars)):
                if imp.lhs[i].vars[j] in map.keys() and imp.lhs[i].vars[j][0].islower():
                    imp.lhs[i].vars[j] = map.get(imp.lhs[i].vars[j])
    '''

    def standardize(self, imp, goal, theta):
        if theta is None:
            return
        map = {}
        set = []
        for idx in range(len(goal.vars)):
            if goal.vars[idx][0].islower() and set.__contains__(goal.vars[idx]):
                goal.vars[idx] = imp.rhs.vars[idx]
            elif goal.vars[idx][0].islower() and imp.rhs.vars[idx][0].islower():
                map[imp.rhs.vars[idx]] = goal.vars[idx]
                imp.rhs.vars[idx] = goal.vars[idx]
                set.append(goal.vars[idx])
            elif goal.vars[idx] in theta.values():
                map[imp.rhs.vars[idx]] = list(theta.keys())[list(theta.values()).index(goal.vars[idx])]
                if imp.rhs.vars[idx][0].islower():
                    imp.rhs.vars[idx] = list(theta.keys())[list(theta.values()).index(goal.vars[idx])]
            if goal.vars[idx][0].islower():
                set.append(goal.vars[idx])
            elif imp.rhs.vars[idx][0].islower():
                set.append(imp.rhs.vars[idx])
        for i in range(len(imp.lhs)):
            for j in range(len(imp.lhs[i].vars)):
                if imp.lhs[i].vars[j] in map.keys() and imp.lhs[i].vars[j][0].islower():
                    imp.lhs[i].vars[j] = map.get(imp.lhs[i].vars[j])

    '''
    def unify(self, rhs, goal):
        newTheta = {}
        for idx in range(len(goal.vars)):
            if goal.vars[idx][0].islower() and rhs.vars[idx][0].isupper():
                newTheta[goal.vars[idx]] = rhs.vars[idx]
                goal.vars[idx] = rhs.vars[idx]
            elif goal.vars[idx][0].isupper() and rhs.vars[idx][0].islower():
                newTheta[rhs.vars[idx]] = goal.vars[idx]
                rhs.vars[idx] = goal.vars[idx]
        return newTheta
    '''
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


    def subst(self, theta, alpha):
        if theta is None or len(theta) == 0:
            return alpha
        nalpha = copy.deepcopy(alpha)
        for idx, var in enumerate(alpha.vars):
            if var[0].islower() and var in theta.keys(): #theta.has_key(var)
                nalpha.vars[idx] = theta.get(var)
        nalpha.value = True
        for var in nalpha.vars:
            if var[0].islower():
                nalpha.value = False
                break
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

    def matchGoal(self, goal):
        for pre in self.predicates:
            if pre == goal:
                return True
        return False

#s = Solution(sys.argv[2])
s = Solution("sample04.txt")
s.main()