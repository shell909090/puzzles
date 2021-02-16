#!/usr/bin/python3
# -*- coding: utf-8 -*-
'''
@date: 2021-02-17
@author: Shell.Xu
@copyright: 2021, Shell.Xu <shell909090@gmail.com>
@license: BSD-3-clause
@comment:
Interpreter of brainfuck.
https://en.wikipedia.org/wiki/Brainfuck
https://gist.github.com/roachhd/dce54bec8ba55fb17d3a
Test code: +++++++++[>+++++++++>++++++++<<-]>++++++.---.>--.
'''
import sys
import argparse


class Env(object):

    def __init__(self, size=30000, debug=False):
        self.size = size
        self.mem = [0,]*self.size
        self.pt = 0
        self.debug = debug

    @staticmethod
    def find_bracket(code, i):
        deep = 0
        while i < len(code):
            if code[i] == '[':
                deep += 1
            elif code[i] == ']':
                deep -= 1
            if deep == 0:
                return i
            i += 1

    def show_mem(self, size=16):
        return '[{}]'.format(
            ', '.join((f'*{o}' if i == self.pt else f'{o}'
                       for i, o in enumerate(self.mem[:size]))))

    def eval(self, code):
        i = 0
        self.stack = []
        while i < len(code):
            op = code[i]
            if self.debug:
                print(op, self.show_mem(), self.stack)
            if op == '>':
                self.pt += 1
                if self.pt >= self.size:
                    raise Exception('pointer big than size')
            elif op == '<':
                self.pt -= 1
                if self.pt < 0:
                    raise Exception('pointer less than zero')
            elif op == '+':
                self.mem[self.pt] += 1
            elif op == '-':
                self.mem[self.pt] -= 1
            elif op == '[':
                if self.mem[self.pt] == 0:
                    i = self.find_bracket(code, i)
                else:
                    self.stack.append(i)
            elif op == ']':
                i = self.stack.pop()-1
            elif op == ',':
                self.mem[self.pt] == ord(sys.stdin.read(1))
            elif op == '.':
                sys.stdout.write(chr(self.mem[self.pt]))
            i += 1


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--debug', '-d', action='store_true', default=False)
    parser.add_argument('--size', '-s', default=30000, type=int)
    parser.add_argument('--file', '-f', action='append')
    parser.add_argument('rest', nargs='*', type=str)
    args = parser.parse_args()

    env = Env(size=args.size, debug=args.debug)

    if args.file:
        for fn in args.file:
            if fn == '-':
                env.eval(sys.stdin.read())
            else:
                with open(fn) as fi:
                    env.eval(fi.read())

    for code in args.rest:
        env.eval(code)


if __name__ == '__main__':
    main()
