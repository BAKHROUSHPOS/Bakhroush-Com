import random


def larger(nums):
    print(random.randint(0,len(nums)))


nums = []
num = input("Enter how many elements you want:")

print('Enter numbers: ')
for i in range(int(num)):
    n = input("num :")
    nums.append(int(n))
x,position = larger(nums)

print('Max number ', x)
print('Position ' , position)
