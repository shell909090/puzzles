#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
@date: 2016-09-30
@author: Shell.Xu
@copyright: 2016, Shell.Xu <shell909090@gmail.com>
@license: BSD-3-clause
'''
import time
import random
import hashlib
import logging
import itertools


# Clubs, Diamonds, Hearts, Spades
COLORS = ['C', 'D', 'H', 'S']
# B for black and R for red
TYPES = {
    'C': 'B',
    'D': 'R',
    'H': 'R',
    'S': 'B'
}
cards = [c+str(n) for c, n in itertools.product(COLORS, range(1, 14))]


def top_of_pile(pile):
    if pile:
        return pile[-1]
    return 'N'


def move_card(p1, p2):
    if not p2:
        raise Exception('empty pile')
    p1.append(p2.pop(-1))


def map_color(card):
    color_map = {
        'C': '36',
        'D': '35',
        'H': '31',
        'S': '32'}
    code_map = ('A', '2', '3', '4', '5', '6', '7',
                '8', '9', '10', 'J', 'Q', 'K')
    if not card or card[0] not in color_map:
        return card
    code = color_map[card[0]]
    return '\x1B[%sm%s\x1B[39;49m' % (code, code_map[int(card[1:])-1])


def md5(s):
    h = hashlib.md5()
    h.update(s)
    return h.digest()


class Klondike(object):

    def __init__(self):
        self.moves = []
        self.knowns = [[] for i in range(7)]
        self.unknowns = [[] for i in range(7)]
        self.foundation = {c: None for c in COLORS}
        self.waste = []
        self.waste_show = []
        self.waste_prior = []
        self.initial()

    def initial(self):
        self.score = 0
        self.step = 0
        self.waste = cards[:]
        random.shuffle(self.waste)
        for i in range(7):
            for j in range(i):
                move_card(self.unknowns[i], self.waste)
            move_card(self.knowns[i], self.waste)
        logging.info('initial')

    def replay(self, moves, pause=0.05):
        for m in moves:
            if pause:
                time.sleep(pause)
            self.print_stat()
            if m == 't':
                self.tune_card()
            elif m[0] == 'f':
                self.pile_to_foundation(int(m[1:]))
            elif m[0] == 'd':
                self.waste_to_foundation()
            elif m[0] == 'w':
                self.waste_to_pile(int(m[1:]))
            elif m[0] == 'p':
                self.pile_to_pile(*(int(i) for i in m[1:].split(',')))
            elif m[0] == 'u':
                self.partial_pile_to_pile(*(int(i) for i in m[1:].split(',')))

    def line_to_row(self, lines):
        for p in range(100):
            row = []
            for i in range(7):
                row.append(lines[i][p] if len(lines[i]) > p else '')
            if row == ['', ] * 7:
                break
            yield row

    def print_stat(self):
        foundation = '\t'.join([
            map_color(self.foundation[c] or 'N') for c in COLORS])
        print('\x1B[2J\x1B[;H')
        print('N\t{}\t\t{}'.format(
            map_color(top_of_pile(self.waste_show)), foundation))
        print('')
        lines = []
        for i in range(7):
            l = ['N'] * len(self.unknowns[i]) + self.knowns[i]
            lines.append(list(map(map_color, l)))
        for row in self.line_to_row(lines):
            print('\t'.join(row))

    def print_prespective(self):
        print(','.join(self.waste))
        print(','.join(self.waste_show))
        print('\t'.join([self.foundation[c] or 'N' for c in COLORS]))
        print('')
        for row in self.line_to_row(self.unknowns):
            print('\t'.join(row))
        print('')
        for row in self.line_to_row(self.knowns):
            print('\t'.join(row))

    def hash(self):
        s = [','.join(self.waste), ]
        s.append(','.join(self.waste_show))
        s.append(','.join([self.foundation[c] or 'N' for c in COLORS]))
        for i in range(7):
            s.append(','.join(self.knowns[i]))
            s.append(','.join(self.unknowns[i]))
        return md5(';'.join(s).encode('utf-8'))

    def is_end(self):
        for c in COLORS:
            if not self.foundation[c]:
                return False
            card = self.foundation[c]
            if int(card[1:]) != 13:
                return False
        return True

    def tune_card(self):
        logging.info('tune card')
        self.moves.append('t')
        if not self.waste:
            self.waste = list(reversed(self.waste_show))
            self.waste_show = []
            logging.info('recycle waste')
            self.score -= 100
            if self.score <= 0:
                self.score = 0
            if self.waste == self.waste_prior:
                return False
            self.waste_prior = self.waste[:]
        else:
            move_card(self.waste_show, self.waste)
        self.step += 1
        return True

    def from_waste(self):
        return self.waste_show.pop(-1)

    def check_to_pile(self, card, n):
        if not self.knowns[n]:
            return int(card[1:]) == 13
        prior = self.knowns[n][-1]
        if TYPES[prior[0]] == TYPES[card[0]]:
            return False
        return int(card[1:]) == int(prior[1:]) - 1

    def tune_over(self, n):
        if not self.knowns[n] and self.unknowns[n]:
            move_card(self.knowns[n], self.unknowns[n])
            logging.info('tune over %d', n)
            self.score += 5
            return True

    def from_pile(self, n):
        card = self.knowns[n].pop(-1)
        self.tune_over(n)
        return card

    def to_pile(self, card, n):
        self.knowns[n].append(card)

    def check_to_foundation(self, card):
        C = card[0]
        if not self.foundation[C]:
            return int(card[1:]) == 1
        return int(card[1:]) == int(self.foundation[C][1:]) + 1

    def to_foundation(self, card):
        self.foundation[card[0]] = card

    def pile_to_foundation(self, n):
        if not self.knowns[n]\
           or not self.check_to_foundation(self.knowns[n][-1]):
            raise Exception('illegal')
        card = self.from_pile(n)
        self.to_foundation(card)
        logging.info('%s from pile %s to foundation', card, n)
        self.score += 10
        self.step += 1
        self.moves.append('f%d' % n)

    def waste_to_foundation(self):
        if not self.waste_show\
           or not self.check_to_foundation(self.waste_show[-1]):
            raise Exception('illegal')
        card = self.from_waste()
        self.to_foundation(card)
        logging.info('%s from waste to foundation', card)
        self.score += 10
        self.step += 1
        self.moves.append('d')

    def waste_to_pile(self, n):
        if not self.waste_show\
           or not self.check_to_pile(self.waste_show[-1], n):
            raise Exception('illegal')
        card = self.from_waste()
        self.to_pile(card, n)
        logging.info('%s from waste to pile %d', card, n)
        self.score += 5
        self.step += 1
        self.moves.append('w%d' % n)

    def check_pile_to_pile(self, t, f):
        return self.knowns[f] and self.check_to_pile(self.knowns[f][0], t)

    def pile_to_pile(self, t, f):
        if not self.knowns[f]\
           or not self.check_to_pile(self.knowns[f][0], t):
            raise Exception('illegal')
        self.knowns[t].extend(self.knowns[f])
        self.knowns[f] = []
        logging.info('pile %d merge into pile %d', f, t)
        self.tune_over(f)
        self.step += 1
        self.moves.append('p%d,%d' % (t, f))

    def partial_pile_to_pile(self, t, f, p):
        if not self.check_to_pile(self.knowns[f][p], t):
            raise Exception('illegal')
        movable = self.knowns[f][p:]
        self.knowns[t].extend(movable)
        self.knowns[f] = self.knowns[f][:p]
        logging.info('partial %s from pile %d to pile %d',
                     ','.join(movable), f, t)
        self.step += 1
        self.moves.append('u%d,%d,%d' % (t, f, p))
