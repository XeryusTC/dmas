import time
import traceback

from maze.maze import Maze
from gnui.gnui import GNUI
from agents.search import SearchAgent
from agents.db import DatabaseAgent
from agents.mothership import Mothership
from agents.pathfinder import PathFinder
from agents.display import DisplayAgent
from agents.rescuer import RescueAgent

WIDTH  = 32
HEIGHT = 16
SEARCHERS = range(3)
RESCUERS  = range(3)

if __name__ == "__main__":
    m = Maze(WIDTH, HEIGHT)
    display = GNUI(WIDTH, HEIGHT)

    display.update(m.getMaze(), [])

    da = DisplayAgent("display@127.0.0.1", "secret")
    da.start()

    try:
        print "Starting searchers"
        search = [SearchAgent("search{}@127.0.0.1".format(i), "secret")
                for i in SEARCHERS]
        for s in search:
            s.setMaze(m)
        print "Starting rescuers"
        rescue = [RescueAgent("rescue{}@127.0.0.1".format(i), "secret")
                for i in RESCUERS]
        for r in rescue:
            r.start()

        da.display = display
        da.agents = search + rescue

        for i in range(100000):
            # Wait two seconds between starting each search bot
            if i % 20 == 0 and i/20 < len(search):
                search[i/20].start()

#            display.update(db.map.getMap(),
#                    [s.position for s in search if s.is_setup])
            time.sleep(.1)
    except KeyboardInterrupt:
        pass
    except Exception, ex:
        print traceback.format_exc()

    # stop all agents
    for s in search:
        s.stop()
    for r in rescue:
        r.stop()
    da.stop()
