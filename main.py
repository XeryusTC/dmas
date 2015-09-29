import time
import traceback

from maze.maze import Maze
from gnui.gnui import GNUI
from agents.search import SearchAgent
from agents.db import DatabaseAgent

WIDTH  = 32
HEIGHT = 16

if __name__ == "__main__":
    m = Maze(WIDTH, HEIGHT)
    display = GNUI(WIDTH, HEIGHT)

    display.update(m.getMaze(), [])

    a = SearchAgent("search@127.0.0.1", "secret")
    db = DatabaseAgent("db@127.0.0.1", "secret")
    db.width  = WIDTH
    db.height = HEIGHT

    try:
        db.start()
        a.setMaze(m)
        a.start()

        for i in range(1000):
            time.sleep(.1)
            display.update(db.map.getMap(), [a.position])
    except KeyboardInterrupt:
        pass
    except Exception, ex:
        print traceback.format_exc()
    finally:
        a.stop()
        db.stop()
