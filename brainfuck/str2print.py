#!/usr/bin/python3
# -*- coding: utf-8 -*-
'''
@date: 2021-02-17
@author: Shell.Xu
@copyright: 2021, Shell.Xu <shell909090@gmail.com>
@license: BSD-3-clause
'''
import sys

def resolv_N(s, N=9):
    groups = {i//N for i in s}
    # print(groups)
    group_map = {g: i for i, g in enumerate(groups)}
    ctl = ''.join(['>'+'+'*g for g in groups])
    rt = '<'*len(groups)+'-'
    cmd = '+'*N+f'[{ctl}{rt}]>'
    state = [N*g for g in groups]
    pt = 0
    # print(group_map, state)
    for o in s:
        g = group_map[o//N]
        # print(g, pt, o, state[g])
        if g > pt:
            cmd += '>'*(g-pt)
        else:
            cmd += '<'*(pt-g)
        pt = g
        if o > state[g]:
            cmd += '+'*(o-state[g])
        else:
            cmd += '-'*(state[g]-o)
        state[g] = o
        cmd += '.'
    return cmd


def main():
    s = sys.argv[1]
    s = list(map(ord, s))
    # print(s)
    size = -1
    best = ''
    for i in range(5, 20):
        cmd = resolv_N(s, i)
        if size == -1 or len(cmd) < size:
            N = i
            best = cmd
            size = len(cmd)
    print(f'N={N}, groups={ {i//N for i in s} }, size={size}', file=sys.stderr)
    print(best)


if __name__ == '__main__':
    main()
