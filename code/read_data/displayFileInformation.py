import os

with open('../ath.txt') as f:
    min10, klst, vg = 0, 0, 0
    line = f.readline()

    while line:
        if '10min' in line:
            min10 += 1
        elif 'klst' in line:
            klst += 1
        elif 'vg' in line:
            vg += 1

        line = f.readline()

    print('Num files 10 min: ', min10)
    print('Num file klst: ', klst)
    print('Num files vg: ', vg)