#!/usr/bin/python3
# -*- coding: utf-8 -*-
'''
@date: 2019-05-06
@author: Shell.Xu
@copyright: 2019, Shell.Xu <shell909090@gmail.com>
@license: BSD-3-clause
'''
import time
import pprint
import random
import argparse
import itertools
import collections

import numpy as np


def seta(a, s, t):
    a[a==s] = t


def mark_xy(m, x, y):
    seta(m[x, :], 0, -1)
    seta(m[:, y], 0, -1)
    i, j = x-x%3, y-y%3
    seta(m[i:i+3, j:j+3], 0, -1)


def check(m, f):
    for i in range(0, 9):
        if f(m[i, :]):
            return i, -1
        if f(m[:, i]):
            return -1, i
    for i in range(0, 3):
        for j in range(0, 3):
            a = m[i*3:i*3+3, j*3:j*3+3]
            if f(a.flatten()):
                return i, j


class Sudoku(object):

    def __init__(self, quiz):
        self.quiz = np.array(quiz)
        self.cur = self.quiz.copy()
        self.flagmaps = np.array([self.cur,]*9)
        self.moves = []
        for n in range(1, 10):
            m = self.flagmaps[n-1, :, :]
            for x, y in np.array(np.where(m == n)).transpose():
                mark_xy(m, x, y)

    def fill(self, x, y, n, c):
        if self.cur[x, y] > 0:
            raise Exception('number existed in this place: %d, %d' % (x, y))
        self.cur[x, y] = n
        self.moves.append((x, y, n, c))
        self.flagmaps[:, x, y] = n
        mark_xy(self.flagmaps[n-1, :, :], x, y)

    def is_balanced(self):
        ele = list(range(1, 10))
        return check(self.cur, 
                     lambda a: sorted(a) != ele) == None

    def is_full(self):
        return not collections.Counter(self.cur.flatten()).get(0)

    def find_pos(self, n):
        m = self.flagmaps[n-1, :, :]
        r = check(m, lambda a: collections.Counter(a).get(0) == 1)
        if r is None:
            return
        x, y = r
        if x == -1:
            x = np.where(m[:, y]==0)[0][0]
        elif y == -1:
            y = np.where(m[x, :]==0)[0][0]
        else:
            i, j = np.where(m[3*x:3*x+3, 3*y:3*y+3]==0)
            x, y = 3*x+i[0], 3*y+j[0]
        return x, y

    def fill_n(self, n):
        r = self.find_pos(n)
        while r:
            x, y = r
            self.fill(x, y, n, 'n')
            r = self.find_pos(n)

    def fill_one(self):
        ele = [-1, -1, -1, -1, -1, -1, -1, -1, 0]
        for x in range(0, 9):
            for y in range(0, 9):
                if self.cur[x, y] != 0:
                    continue
                a = self.flagmaps[:, x, y]
                if sorted(a) == ele:
                    n = np.where(a==0)[0][0]
                    self.fill(x, y, n+1, 'one')

    def resolve(self):
        l = -1
        while len(self.moves) != l:
            l = len(self.moves)
            for n in range(1, 10):
                self.fill_n(n)
            self.fill_one()

    def generate_fill(self, n):
        m = self.flagmaps[n-1, :, :]
        zeros = np.array(np.where(m == 0)).transpose()
        if not len(zeros):
            return
        x, y = random.choice(zeros)
        self.fill(x, y, n, 'gen')
        return x, y, n

    def is_resolvable(self):
        self.resolve()
        return self.is_balanced()

    def mask_one_path(self):
        m = self.cur.copy()
        coords = list(itertools.product(range(0, 9), range(0, 9)))
        while True:
            random.shuffle(coords)
            for x, y in coords:
                m1 = m.copy()
                m1[x, y] = 0
                if Sudoku(m1).is_resolvable():
                    coords.remove((x, y))
                    m = m1
                    break
            else:
                return len(coords), m

    def mask_quiz(self, n):
        c, m = min((self.mask_one_path() for _ in range(n)),
                   key=lambda x: x[0])
        print('best one has %d numbers' % c)
        return Sudoku(m)

    @classmethod
    def generate(cls):
        m = np.zeros((9, 9), dtype=int)
        row = list(range(1, 10))
        random.shuffle(row)
        m[4, :] = row
        for i in range(10):
            s = cls(m)
            c = collections.Counter(s.cur.flatten())
            while c.get(0):
                n = random.choice([k for k, v in c.items() if k != 0 and v < 9])
                if not s.generate_fill(n):
                    break
                s.resolve()
                c = collections.Counter(s.cur.flatten())
            else:
                print('generate matrix %d times' % i)
                return s


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--maskcycle', '-m',
                        type=int, default=10)
    parser.add_argument('--resolve', '-r',
                        action='store_true', default=False)
    args = parser.parse_args()

    s = Sudoku.generate()
    print(s.cur)
    q = s.mask_quiz(args.maskcycle)
    if not q:
        print('no quiz match')
    else:
        print(q.cur)

    if args.resolve:
        q.resolve()
        pprint.pprint(q.moves)


if __name__ == '__main__':
    main()
