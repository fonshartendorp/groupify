import random

input = 'a 20\nb 20\nc 30\nd 30\ne 15\n'

for i in range(115):
    options = ['a', 'b', 'c', 'd', 'e']
    mate = 0
    choice1 = options[random.randint(0,4)]
    choice2 = options[random.randint(0,4)]
    choice3 = options[random.randint(0,4)]

    line = str(i + 1) + ' 0 ' + choice1 + ' ' + choice2 + ' ' + choice3 + '\n'
    input += line

print(input)
