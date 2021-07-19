import bs4


def solution(n):
    sum = 0
    n = str(n)
    for i in n:
        sum += int(i)
    return sum
solution(123)

a = [[2, 5, 3], [4, 4, 1], [1, 7, 3]]
a[0]

def solution(array, commands):
    for i in commands:


solution([1, 5, 2, 6, 3, 7, 4], [[2, 5, 3], [4, 4, 1], [1, 7, 3]])

a = [1,4,2]
a.sort()
a
def solution(array, commands):
    sub_list = []
    main_list = []
    for i in commands:
        sub_list = array[i[0]-1 : i[1]]
        sub_list.sort()
        main_list.append(sub_list[i[2]-1])
    return main_list
solution([1, 5, 2, 6, 3, 7, 4], [[2, 5, 3], [4, 4, 1], [1, 7, 3]])
