from PySimpleTest import *

section("Test eval function")

section("eval single value", level = 2)
should_be_equal(eval("1"), 1)
should_be_equal(eval("1.2"), 1.2)
should_be_equal(eval("-3.6"), -3.6)
should_be_equal(eval("True"), True)

section("eval math expression", level = 2)
should_be_equal(eval("3 + 5*2"), 13)
should_be_equal(eval("(6-2)*5"), 20)