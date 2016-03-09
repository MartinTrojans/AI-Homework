__author__ = 'Martin'

class test:
    def generator(self):
        i = 0;
        while i < 10:
            i += 1
            if i % 2 == 3:
                yield i**2

    def exe(self):
        for i in range(10):
            try:
                print(next(self.generator()))
            except StopIteration:
                print("False")
                break

t = test()
t.exe()