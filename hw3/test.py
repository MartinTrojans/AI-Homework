__author__ = 'Martin'

from decimal import Decimal

string = ""
ele = 2.675

string += str("%.2f" % ele) + "\n"

string += str(round(ele, 2)) + "\n"

string += str(Decimal(str(ele)).quantize(Decimal('0.'))) + "\n"


print(string)


