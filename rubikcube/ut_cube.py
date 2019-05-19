#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
@date: 2019-05-19
@author: Shell.Xu
@copyright: 2019, Shell.Xu <shell909090@gmail.com>
@license: BSD-3-clause
'''
from __future__ import absolute_import, division,\
    print_function, unicode_literals
import unittest

import numpy as np

import cube


class TestPack(unittest.TestCase):

    def test_pack(self):
        c = cube.Cube()
        c.shuffle()
        c1 = cube.Cube()
        c1.unpack(c.pack())
        self.assertTrue(np.all(c1.cube == c.cube))


class TestDump(unittest.TestCase):

    def test_dump(self):
        c = cube.Cube()
        c.shuffle()
        c1 = cube.Cube()
        c1.load(c.dump())
        self.assertTrue(np.all(c1.cube == c.cube))


class TestOp(unittest.TestCase):

    DATA = {
        'U': 'B/04nYcyyIqAOi6Jyg3/',
        'Ui': 'D/WyVQPfCI2j1NWrww3/',
        'U2': 'C/l1hop91jnSXWqExo3/',
        'D': 'BAEMf8n3Ailkcd/T30v/',
        'Di': 'BAEBTZtOd486/XFqTsf/',
        'D2': 'BAEG5rK1YHF010P0/wn/',
        'F': 'DXdOd7Aa/i9apL6gDfINvw',
        'Fi': 'Br2nucih1O9S4ZOzBGeZPw',
        'F2': 'ENQh1sgdcinfMImDmwnSPw',
        'R': 'DlF8aZj5z7xbIE6qaEsOH80',
        'Ri': 'KvRsBPKZTT0sDi2LI9fcsZs',
        'R2': 'R5dcXv4EjBIUjTCz/c2b+oI',
        'B': 'BMmq+Mbi5nztQN2jygGary3U',
        'Bi': 'CZNV7YzKFzh7uUMCgVwCw6V+',
        'B2': 'C/grZ++9sJgz1GsLl75Ct10o',
        'L': 'BgpepI+z4NPvE/25OUvLYI/v',
        'Li': 'AgN08rcZcy3YOX9oC2RdAA73',
        'L2': 'ChFIcTlO9ank/p4wG4XZNtBr',}

    def test_move(self):
        for m, p in self.DATA.items():
            c = cube.Cube()
            c.do(m)
            self.assertEqual(c.pack(), p)
