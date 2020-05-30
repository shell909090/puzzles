#!/usr/bin/python3
# -*- coding: utf-8 -*-
'''
@date: 2019-05-09
@author: Shell.Xu
@copyright: 2019, Shell.Xu <shell909090@gmail.com>
@license: BSD-3-clause
'''
from __future__ import absolute_import, division,\
    print_function, unicode_literals
import random
import binascii

import numpy as np

# refer: https://ruwix.com/the-rubiks-cube/japanese-western-color-schemes/

MOVES = [
    'U', 'Ui', 'U2', 'D', 'Di', 'D2',
    'F', 'Fi', 'F2', 'R', 'Ri', 'R2',
    'B', 'Bi', 'B2', 'L', 'Li', 'L2',]

# White - U, Green - F, Red - R, Blue - B, Orange - L, Yellow - D
COLORS = 'WGRBOY'
RCOLORS = {c: i for i, c in enumerate(COLORS)}

TERM_COLORS = {
    'W': '97',
    'G': '92',
    'R': '91',
    'B': '94',
    'O': '96',
    'Y': '93',
}


def rotate(m):
    # 300 ns per loop
    return m[::-1, ::-1]


def rotate_cw(m):
    return m[::-1].T


# 1.33 µs per loop
# t = m[0].copy()
# m[0] = m[2]
# m[2] = t
# return m.T
# 877 ns per loop
# R = np.array([
#     [0,0,1],
#     [0,1,0],
#     [1,0,0],
# ])
# return np.dot(m, R).T
def rotate_ccw(m):
    # 330 ns per loop
    return m.T[::-1]


def tokenize(s):
    o = ''
    for c in s:
        if c in ' ,':
            continue
        if c.isupper() and o:
            yield o
            o = ''
        o += c
    if o:
        yield o


class Cube(object):
    circle = (4, 1, 2, 3)
    DEBUG = False

    def __init__(self):
        self.cube = np.array([np.full((3, 3), i) for i in range(1, 7)])

    @staticmethod
    def color_map(c):
        c = COLORS[c-1]
        cc = TERM_COLORS[c]
        return '\x1B[%sm%s\x1B[39;49m' % (cc, c)

    def __str__(self):
        s = []
        for i in range(3):  # self.cube[0]
            s.append(' ' * 6 + ' '.join([self.color_map(j) for j in self.cube[0, i]]))
        for i in range(3):  # self.cube[4,1,2,3]
            l = []
            for f in self.circle:
                l.extend((self.color_map(j) for j in self.cube[f, i]))
            s.append(' '.join(l))
        for i in range(3):  # self.cube[5]
            s.append(' ' * 6 + ' '.join([self.color_map(j) for j in self.cube[5, i]]))
        return '\n'.join(s)

    opmap = {
        '': rotate_cw,
        'i': rotate_ccw,
        "'": rotate_ccw,
        '2': rotate,
    }

    def _R(self, f, o, v0, v1, v2, v3):
        self.cube[f] = self.opmap[o](self.cube[f])
        if o == '':
            v3[:], v2[:], v1[:], v0[:] = v2, v1, v0, v3.copy()
        elif o == 'i':
            v0[:], v1[:], v2[:], v3[:] = v1, v2, v3, v0.copy()
        elif o == '2':
            v0[:], v1[:], v2[:], v3[:] = v2, v3, v0.copy(), v1.copy()

    def op(self, o):
        if o[0] == 'U':
            self._R(0, o[1:], self.cube[1, 0, ::-1], self.cube[4, 0, ::-1],
                    self.cube[3, 0, ::-1], self.cube[2, 0, ::-1])
        elif o[0] == 'D':
            self._R(5, o[1:], self.cube[1, -1], self.cube[2, -1],
                    self.cube[3, -1], self.cube[4, -1])
        elif o[0] == 'F':
            self._R(1, o[1:], self.cube[5, 0, ::-1], self.cube[4, ::-1, -1],
                    self.cube[0, -1], self.cube[2, :, 0])
        elif o[0] == 'R':
            self._R(2, o[1:], self.cube[5, ::-1, -1], self.cube[1, ::-1, -1],
                    self.cube[0, ::-1, -1], self.cube[3, :, 0])
        elif o[0] == 'B':
            self._R(3, o[1:], self.cube[5, -1, :], self.cube[2, ::-1, -1],
                    self.cube[0, 0, ::-1], self.cube[4, :, 0])
        elif o[0] == 'L':
            self._R(4, o[1:], self.cube[5, :, 0], self.cube[3, ::-1, -1],
                    self.cube[0, :, 0], self.cube[1, :, 0])
        else:
            raise Exception('unknown op: ' + o)

    def do(self, ops, debug=False):
        if not isinstance(ops, list):
            ops = tokenize(ops)
        for o in ops:
            self.op(o)
            if debug:
                print(o)
                print(self)

    # c.do('UFRBLD'*4), no print, 100 µs per loop

    def shuffle(self, l=40, moves=None, debug=False):
        if moves is None:
            moves = MOVES
        m = ' '.join([random.choice(moves) for _ in range(l)])
        if debug or self.DEBUG:
            print(m)
        self.do(m)

    def dump(self):
        o = []
        for f in range(6):
            o.append(''.join([COLORS[o-1] for o in self.cube[f].flat]))
        return '\n'.join(o)

    def load(self, s):
        for f, l in enumerate(s.splitlines()):
            self.cube[f] = np.array([RCOLORS[c]+1 for c in l]).reshape(3, 3)

    def pack(self):
        i = ''.join((str(i-1) for i in self.cube.flat))
        s = hex(int(i, 6))[2:]
        s = '0'+s if len(s) % 2 else s
        s = binascii.b2a_base64(binascii.unhexlify(s), newline=False)
        return s.decode('utf-8').strip('=')

    def unpack(self, s):
        s += '=' * (4-len(s)%4)
        x = int(binascii.hexlify(binascii.a2b_base64(s.encode('utf-8'))), 16)
        l = []
        while len(l) < 54:
            i, x = x % 6, x // 6
            l.append(i)
        self.cube = np.array([i+1 for i in l[::-1]]).reshape(6, 3, 3)


def main():
    c = Cube()
    print(c)

    c.do('U')
    print(c)

    # m = np.array(range(1, 10)).reshape(3, 3)
    # m = np.array([1,2,3])
    # m = np.array([[1],[2],[3]])
    # print(m)
    # print(rotate_cw(m))
    # print(rotate_ccw(m))
    # print(rotate(m))


if __name__ == '__main__':
    main()
