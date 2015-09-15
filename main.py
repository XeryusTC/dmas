import time
import traceback

from maze.maze import Maze
from gnui.gnui import GNUI
from agents.search import SearchAgent

if __name__ == "__main__":
    m = Maze(32,16)
    display = GNUI(32,16)

    display.update(m.getMaze(),1)

    a = SearchAgent("search@127.0.0.1", "secret")

    try:
        a.setMaze(m)
        a.start()
        time.sleep(5)
    except Exception, ex:
        print traceback.format_exc()
    finally:
        a.stop()
