#!/usr/bin/python3
# -*- coding: utf-8 -*-
'''
@date: 2020-05-30
@author: Shell.Xu
@copyright: 2020, Shell.Xu <shell909090@gmail.com>
@license: BSD-3-clause
'''
import sys
import collections


class Ball(object):
    
    def __init__(self, height, stacks):
        self.height = height
        self.stacks = stacks

    def clone(self):
        return Ball(self.height, [s[:] for s in self.stacks])

    def digest(self):
        return '|'.join([''.join(s) for s in self.stacks])

    def show(self):
        print('----')
        for s in self.stacks:
            print(''.join(s))
        print('----')

    # each move should move all balls in same color on the top of the source stack
    # otherwise it will be meaningless
    def check_move(self, x, y):
        if len(self.stacks[x]) == 0:
            return
        if len(self.stacks[y]) > 0 and self.stacks[x][-1] != self.stacks[y][-1]:
            return
        n = 0
        for i in range(len(self.stacks[x]) - 1, -1, -1):
            if self.stacks[x][i] == self.stacks[x][-1]:
                n += 1
            else:
                break
        if len(self.stacks[y]) + n <= self.height:
            return True

    @staticmethod
    def pure(s):
        for c in s:
            if c != s[0]:
                return False
        return True

    @staticmethod
    def move_stack(s, d):
        c = s[-1]
        while s and s[-1] == c:
            d.append(s.pop(-1))

    def move(self, x, y):
        if not self.check_move(x, y):
            raise Exception("can't move")
        Ball.move_stack(self.stacks[x], self.stacks[y])

    @staticmethod
    def score_stack(s):
        # 1 for each same color connected
        if len(s) < 2:
            return 0
        return sum([1 if s[i] == s[i+1] else 0 for i in range(len(s)-1)])

    def score(self):
        return sum([Ball.score_stack(s) for s in self.stacks])

    def margin(self, x, y):
        s, d = self.stacks[x][:], self.stacks[y][:]
        orig = Ball.score_stack(s) + Ball.score_stack(d)
        Ball.move_stack(s, d)
        new = Ball.score_stack(s) + Ball.score_stack(d)
        return new - orig

    def find_moves(self):
        for x in range(len(self.stacks)):
            if len(self.stacks[x]) == 0:
                continue
            for y in range(len(self.stacks)):
                # from x, to y
                if y == x:
                    continue
                if self.check_move(x, y):
                    yield x, y, self.margin(x, y)


class Resolver(object):
    # DFS

    def __init__(self, n, max_depth):
        self.n = n
        self.max_depth = max_depth
        self.path, self.steps = [], []

    def show_steps(self):
        for i in range(int(len(self.steps)/4)+1):
            if not self.steps[i*4:i*4+4]:
                continue
            print(', \t'.join(['%s %d to %d' % s for s in self.steps[i*4:i*4+4]]))

    def search(self, quiz):
        if len(self.path) >= self.max_depth:
            return
        if quiz.score() >= 3*self.n:
            self.max_depth = len(self.path)
            print(self.max_depth)
            self.show_steps()
            return
        self.path.append(quiz.digest())
        moves = sorted(quiz.find_moves(), key=lambda k: -k[2])
        for x, y, _ in moves:
            if Ball.pure(quiz.stacks[x]) and not quiz.stacks[y]:
                # don't move from a pure color stack to an empty stack
                continue
            # print(f'{x} to {y}')
            c = quiz.clone()
            b = c.stacks[x][-1]
            c.move(x, y)
            if c.digest() in self.path:
                continue
            self.steps.append((b, x+1, y+1))
            self.search(c)
            self.steps.pop(-1)
        self.path.pop(-1)


# R - Red, G - Green, B - Blue, Y - Yellow
# C - Cyan, S - Silver, O - Olive, V - Violet, P - Pink
def main():
    with open(sys.argv[1]) as fi:
        ballquiz = fi.read().upper()
    c = collections.Counter(ballquiz)
    for k, v in c.items():
        if k == '\n' or v == 4:
            continue
        print(f'{k} not qeual')
    quiz = [list(l) for l in ballquiz.splitlines() if l]
    b = Ball(4, quiz+[[], []])
    b.show()
    r = Resolver(len(quiz), 100)
    r.search(b)


if __name__ == '__main__':
    main()
