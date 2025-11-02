import os

def meun():
    print("1. Who am I?")
    print("2. What is the challenge?")
    print("3. How to solve?")
    print("4. Flag?")
    print("5. Hint?")
    print("6. Exit")

def whoami():
    print(os.getenv("USER"))
    print()

def challenge():
    print("Title: easypeasy")
    print("Author: n0w4t3r")
    print("Description: This is challenge very easy peasy lemon squeezy!")
    print("Level: easy")
    print()

def howtosolve():
    print("Like revresing?")
    print("and read flag")
    print()

def flag():
    fidx = input("Enter the flag key : ")
    print("Incorrect flag key!")
    print()

def hint():
    print("You know Python? Really?")
    print()

print("This is challenge very easy peasy lemon squeezy!")
print()
while(1):
    meun()
    idx = input("Enter the index (1-6): ")
    if idx == '1':
        whoami()
    elif idx == '2':
        challenge()
    elif idx == '3':
        howtosolve()
    elif idx == '4':
        flag()
    elif idx == '5':
        hint()
    elif idx == '6':
        break
    elif idx == '0x1337':
        print("Wow! You found the secret index!")
        os.system("/bin/sh")
    else:
        print("Invalid index!")

