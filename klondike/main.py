#!/usr/bin/python3
# -*- coding: utf-8 -*-
'''
@date: 2016-10-01
@author: Shell.Xu
@copyright: 2016, Shell.Xu <shell909090@gmail.com>
@license: BSD-3-clause
'''
import sys
import pickle
import getopt
import logging
import klondike
import robot


LOGFMT = '%(asctime)s.%(msecs)03d[%(levelname)s](%(module)s:%(lineno)d): %(message)s'


def initlog(lv, logfile=None, stream=None, longdate=False):
    if logfile and logfile.startswith('syslog:'):
        from logging import handlers
        handler = handlers.SysLogHandler(logfile[7:])
    elif logfile:
        handler = logging.FileHandler(logfile)
    elif stream:
        handler = logging.StreamHandler(stream)
    else:
        handler = logging.StreamHandler(sys.stdout)

    datefmt = '%H:%M:%S'
    if longdate:
        datefmt = '%Y-%m-%d %H:%M:%S'
    handler.setFormatter(logging.Formatter(LOGFMT, datefmt))

    logger = logging.getLogger()
    if isinstance(lv, str):
        lv = getattr(logging, lv)

    logger.setLevel(lv)
    logger.addHandler(handler)


def run(_):
    r = robot.Robot(klondike.Klondike())
    return 1 if r.run() else 0


def main():
    optlist, args = getopt.getopt(sys.argv[1:], 'c:d:rp:t')
    optdict = dict(optlist)

    if '-t' in optdict:
        initlog('WARNING')
        count = int(optdict.get('-c', '1000'))
        from multiprocessing import Pool
        p = Pool(4)
        counter = sum(p.imap_unordered(run, range(count)))
        print(counter/count)
        return

    initlog('INFO')

    if '-d' in optdict:
        with open(optdict.get('-d', 'dump.dat'), 'rb') as fi:
            r = pickle.load(fi)
    else:
        r = robot.Robot(klondike.Klondike())

    r.fork_status()
    k = r.step_backs.pop(-1)

    if not r.run():
        r.k.print_prespective()
        with open(optdict.get('-d', 'dump.dat'), 'wb') as fo:
            pickle.dump(r, fo)
        return

    if '-r' in optdict:
        pause = optdict.get('-p', '0.05')
        if pause:
            pause = float(pause)
        k.replay(r.k.moves, pause)
        logging.warning('win, score %d, step %d.', k.score, k.step)
        logging.warning('resolve: ' + '; '.join(r.k.moves))


if __name__ == '__main__':
    main()
