#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
@date: 2016-10-01
@author: Shell.Xu
@copyright: 2016, Shell.Xu <shell909090@gmail.com>
@license: BSD-3-clause
'''
from __future__ import absolute_import, division,\
    print_function, unicode_literals
import copy
import time
import logging
import klondike


# According to https://en.wikipedia.org/wiki/Klondike_(solitaire), "Thus in
# order to receive a maximum score, no cards should be moved directly from the
# Waste to Foundation."
# But after a quick test, I found the possiblity of resolve is 0.1% when it
# cloesed. That's almost not working. So I keep it open.
WASTE_TO_FOUNDATION = True


class Robot(object):

    def __init__(self, k):
        self.k = k
        self.step_backs = []
        self.cached = []

    def fork_status(self):
        # n = next statue
        n = copy.deepcopy(self.k)
        self.step_backs.append(n)
        return n

    def deal_piles(self):
        for i in range(7):
            if not self.k.knowns[i]:
                continue
            if self.k.check_to_foundation(self.k.knowns[i][-1]):
                self.k.pile_to_foundation(i)
                return True

    def find_merge(self):
        # f = from and t = to
        for f in range(7):
            for t in range(7):
                if f == t:
                    continue
                # merge from an empty pile to an empty pile is stupid.
                if self.k.check_pile_to_pile(t, f)\
                   and not (self.k.knowns[f][0][1:] == '13'
                            and not self.k.unknowns[f]):
                    n = self.fork_status()
                    n.pile_to_pile(t, f)
                    yield n

    def merge_piles(self):
        if not list(self.find_merge()):
            return False
        self.k = self.step_backs.pop(-1)
        return True

    def find_card(self, card):
        for f in range(7):
            if card not in self.k.knowns[f]:
                continue
            # short for position
            p = self.k.knowns[f].index(card)
            return f, p+1
        return -1, -1

    def find_target(self, f, p):
        for t in range(7):
            if f == t:
                continue
            if self.k.check_to_pile(self.k.knowns[f][p], t):
                yield t

    def find_uncover(self):
        for c in klondike.COLORS:
            if not self.k.foundation[c]:
                continue
            card = self.k.foundation[c][-1]
            card = card[0] + str(int(card[1:])+1)

            f, p = self.find_card(card)
            if f == -1:
                continue

            for t in self.find_target(f, p):
                logging.info(
                    'find uncoverable card %s in pile %d,\
 rest should merge to pile %d',
                    card, f, t)
                n = self.fork_status()
                n.partial_pile_to_pile(t, f, p)
                yield n

    def uncover_piles(self):
        if not list(self.find_uncover()):
            return False
        self.k = self.step_backs.pop(-1)
        return True

    def find_waste(self):
        t = self.k.waste_show[-1]
        for i in range(7):
            if self.k.check_to_pile(t, i):
                n = self.fork_status()
                n.waste_to_pile(i)
                yield n

    def deal_waste(self):
        if not self.k.waste_show:
            return
        t = self.k.waste_show[-1]
        if WASTE_TO_FOUNDATION and self.k.check_to_foundation(t):
            self.k.waste_to_foundation()
            return True
        if not list(self.find_waste()):
            return False
        self.k = self.step_backs.pop(-1)
        return True

    def run(self, print_status=False, pause=0.05):
        while not self.k.is_end():
            h = self.k.hash()
            if h in self.cached:
                logging.info('hit in cached.')
                if self.step_backs:
                    self.k = self.step_backs.pop(-1)
                    logging.info('step back.')
                else:
                    logging.warning('lost.')
                    return False
            self.cached.append(h)

            if print_status:
                if pause:
                    time.sleep(pause)
                self.k.print_stat()
            if self.deal_piles():
                continue
            if self.merge_piles():
                continue
            if self.uncover_piles():
                continue
            if self.deal_waste():
                continue
            if not self.k.tune_card():
                logging.info('no more step.')

                if self.step_backs:
                    self.k = self.step_backs.pop(-1)
                    logging.info('step back.')
                else:
                    logging.warning('lost.')
                    return False

        logging.warning('win, score %d, step %d.',
                        self.k.score, self.k.step)
        return True
