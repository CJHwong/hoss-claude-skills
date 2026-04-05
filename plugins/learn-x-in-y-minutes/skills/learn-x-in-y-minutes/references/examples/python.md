---
name: Python
contributors:
    - ["Louie Dinh", "http://pythonpracticeprojects.com"]
    - ["Steven Basart", "http://github.com/xksteven"]
filename: learnpython.py
---

Python was created by Guido van Rossum in the early 90s. It is now one of the
most popular languages in existence. I fell in love with Python for its
syntactic clarity. It's basically executable pseudocode.

```python
# Single line comments start with a number symbol.

""" Multiline strings can be written
    using three "s, and are often used
    as documentation.
"""

####################################################
## 1. Primitive Datatypes and Operators
####################################################

# You have numbers
3  # => 3

# Math is what you would expect
1 + 1   # => 2
8 - 1   # => 7
10 * 2  # => 20
35 / 5  # => 7.0

# Floor division rounds towards negative infinity
5 // 3       # => 1
-5 // 3      # => -2

# Exponentiation (x**y, x to the yth power)
2**3  # => 8

# Boolean values are primitives (Note: the capitalization)
True   # => True
False  # => False

# negate with not
not True   # => False
not False  # => True

# Equality is ==
1 == 1  # => True
2 == 1  # => False

# Strings are created with " or '
"This is a string."
'This is also a string.'

# Strings can be added too
"Hello " + "world!"  # => "Hello world!"

# A string can be treated like a list of characters
"Hello world!"[0]  # => 'H'

# You can find the length of a string
len("This is a string")  # => 16

# Since Python 3.6, you can use f-strings
name = "Reiko"
f"She said her name is {name}."  # => "She said her name is Reiko."


####################################################
## 2. Variables and Collections
####################################################

# Python has a print function
print("I'm Python. Nice to meet you!")  # => I'm Python. Nice to meet you!

# By default the print function also prints out a newline at the end.
# Use the optional argument end to change the end string.
print("Hello, World", end="!")  # => Hello, World!

# Simple way to get input data from console
input_string_var = input("Enter some data: ")  # Returns the data as a string

# There are no declarations, only assignments.
some_var = 5
some_var  # => 5

# None is an object
None  # => None

# Lists store sequences
li = []
# You can start with a prefilled list
other_li = [4, 5, 6]

# Add stuff to the end of a list with append
li.append(1)    # li is now [1]
li.append(2)    # li is now [1, 2]
li.append(4)    # li is now [1, 2, 4]
li.append(3)    # li is now [1, 2, 4, 3]

# Access a list like you would any array
li[0]   # => 1
# Look at the last element
li[-1]  # => 3

# Slice syntax — li[start:end:step]
li[1:3]   # => [2, 4]
li[::2]   # => [1, 4]
li[::-1]  # => [3, 4, 2, 1]


####################################################
## 3. Control Flow and Iterables
####################################################

# Let's just make a variable
some_var = 5

# Here is an if statement. Indentation is significant in Python!
if some_var > 10:
    print("some_var is totally bigger than 10.")
elif some_var < 10:    # This elif clause is optional.
    print("some_var is smaller than 10.")
else:                  # This is optional too.
    print("some_var is indeed 10.")

# For loops iterate over lists
for animal in ["dog", "cat", "mouse"]:
    print(f"{animal} is a mammal")

# range(number) returns an iterable of numbers from zero up to (but not including) the given number
for i in range(4):
    print(i)
# prints: 0 1 2 3

# While loops go until a condition is no longer met.
x = 0
while x < 4:
    print(x)
    x += 1  # Shorthand for x = x + 1
```

<!-- Source: https://github.com/adambard/learnxinyminutes-docs/blob/master/python.md (truncated for reference) -->
