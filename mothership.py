import multiprocessing as mp
import time
import traceback
import Queue

import numpy as np

from agents.db import DatabaseAgent
from agents.pathfinder import PathFinder
from agents.search import SearchAgent
from agents.mothership import Mothership
from agents.rescuer import RescueAgent
from gnui.gnui import GNUI
from maze.maze import Maze
import util

WIDTH     = 8
HEIGHT    = 8
SEARCHERS = range(3)
RESCUERS  = range(3)

def main():
    manager = mp.Manager()
    searchm = manager.list()
    rescuem = manager.list()
    mazem   = manager.list()
    comq    = mp.Queue()

    m = Maze(WIDTH, HEIGHT)
    print(type(mazem), type(m.maze))
    mazem[:] = m.maze
    m.maze = mazem
    print(type(mazem), type(m.maze))
    display = GNUI(WIDTH, HEIGHT, "Map")
    display2 = GNUI(WIDTH, HEIGHT, "Maze")

    display.update(m.getMaze(), [])

    db = DatabaseAgent("db@127.0.0.1", "secret")
    db.width = WIDTH
    db.height = HEIGHT
    time.sleep(1)
    db.start()
    time.sleep(1)

    searchers = mp.Process(target=searchmanager, args=(SEARCHERS, searchm, comq, m))
    rescuers = mp.Process(target=rescuemanager, args=(RESCUERS, rescuem, comq, m))
    pf = mp.Process(target=pathmanager, args=(comq,))
    mothership = mp.Process(target=mothermanager, args=(comq,))

    pf.start()
    mothership.start()
    searchers.start()
    rescuers.start()

    try:
        for i in range(100000):
            display.update(db.map.getMap(), list(searchm), list(rescuem))
            display2.update(m.getMaze(),list(searchm), list(rescuem))
            time.sleep(.1)

            print isReady(db.map.getMap(), rescuem)
    except KeyboardInterrupt:
        pass
    except Exception, ex:
        print traceback.format_exc()
    finally:
        # Send a stop signal to all the processes
        comq.put("STOP")
        comq.put("STOP")
        comq.put("STOP")
        comq.put("STOP")

    db.stop()

    searchers.join()
    rescuers.join()
    mothership.join()
    pf.join()
    print "Done."


def isReady(m, rescuers):
    
    for row in m:
        if (0 in row) or (3 in row):
            return False

    for rescuer in rescuers:
        if not (1,1) == rescuer:
            return False

    return True
 
def searchmanager(searchers, pos, comq, m):
    print "Starting searchers"
    search = [SearchAgent("search{}@127.0.0.1".format(i), "secret")
            for i in searchers]
    for s in search:
        s.setMaze(m)

    running = True
    i = 0
    try:
        while running:
            # Wait two seconds between starting each search bot
            if i % 20 == 0 and i/20 < len(search):
                search[i/20].start()
            try:
                if comq.get_nowait() == "STOP":
                    running = False
            except Queue.Empty:
                pass

            pos[:] = [s.position for s in search if s.is_setup]

            time.sleep(.1)
            i = i + 1
    except KeyboardInterrupt:
        pass

    for s in search:
        s.stop()
    print "Searchers stopped"

def rescuemanager(rescuers, pos, comq, m):
    print "Starting rescuers"
    rescue = [RescueAgent("rescue{}@127.0.0.1".format(i), "secret")
            for i in rescuers]
    for r in rescue:
        r.setMaze(m)
        r.start()
    time.sleep(.1)

    running = True
    try:
        while running:
            try:
                if comq.get_nowait() == "STOP":
                    running = False
            except Queue.Empty:
                pass

            pos[:] = [r.position for r in rescue if r.is_setup]

            time.sleep(.1)
    except KeyboardInterrupt:
        pass

    for r in rescue:
        r.stop()
    print "Rescuers stopped"

def pathmanager(comq):
    print "Starting pathfinder"
    pf = PathFinder("path@127.0.0.1", "secret")
    pf.start()
    running = True
    try:
        while running:
            try:
                if comq.get_nowait() == "STOP":
                    running = False
            except Queue.Empty:
                pass
            time.sleep(.1)
    except KeyboardInterrupt:
        pass

    pf.stop()
    print "Pathfinder stopped"

def mothermanager(comq):
    print "Starting mothership"
    ms = Mothership("mother@127.0.0.1", "secret")
    ms.start()

    running=True
    try:
        while running:
            try:
                if comq.get_nowait() == "STOP":
                    running = False
            except Queue.Empty:
                pass
            time.sleep(.1)
    except KeyboardInterrupt:
        pass

    ms.stop()
    print "Supervisor stopped"

if __name__ == '__main__':
    main()
