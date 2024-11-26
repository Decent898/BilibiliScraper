import random

MAX = 1000
for i in range(MAX):
    bv = "BV"
    for j in range(10):
        n = random.randint(0,61)
        if 0 <= n <= 9:
            c = chr(n + ord('0'))
        elif 10 <= n <= 35:
            c = chr(n - 10 + ord('a'))
        else:
            c = chr(n - 36 + ord('A'))
        bv += c
    print(bv)
    with open('results/bv_list.txt', 'a', encoding='utf-8') as file:
        file.write(bv + "\n")