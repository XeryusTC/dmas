import time
import traceback

from maze.maze import Maze
from gnui.gnui import GNUI
from agents.search import SearchAgent
from agents.db import DatabaseAgent

WIDTH  = 32
HEIGHT = 16
SEARCH = range(3)

if __name__ == "__main__":
    m = Maze(WIDTH, HEIGHT)
    display = GNUI(WIDTH, HEIGHT)

    display.update(m.getMaze(), [])

    search = [SearchAgent("search{}@127.0.0.1".format(i), "secret")
            for i in SEARCH]
    db = DatabaseAgent("db@127.0.0.1", "secret")
    db.width  = WIDTH
    db.height = HEIGHT

    try:
        db.start()
        while not db.is_setup:
            pass

        for s in search:
            s.setMaze(m)

        for i in range(1000):
            # Wait two seconds between starting each search bot
            if i % 20 == 0 and i/20 < len(search):
                search[i/20].start()

            display.update(db.map.getMap(),
                    [s.position for s in search if s.is_setup])
            time.sleep(.1)
    except KeyboardInterrupt:
        pass
    except Exception, ex:
        print traceback.format_exc()

    # stop all agents
    for s in search:
        s.stop()
    db.stop()
