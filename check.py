__author__ = 'Martin'

class Check:
    def check(self, filename1, filename2):
        file1 = open(filename1, "r")
        file2 = open(filename2, "r")
        line1 = file1.readline()
        line2 = file2.readline()
        while line1 and line2:
            if line1 != line2:
                return False
            line1 = file1.readline()
            line2 = file2.readline()
        return True

c = Check()
print(c.check("trace_state.txt", "contrast1.txt"))
print(c.check("traverse_log.txt", "contrast2.txt"))