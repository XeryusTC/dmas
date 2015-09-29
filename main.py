import time
import traceback
from map.map import Map

from maze.maze import Maze
from gnui.gnui import GNUI
from agents.search import SearchAgent

if __name__ == "__main__":
    m = Maze(32,16)
    display = GNUI(32,16)
    globalMap = Map(32, 16)

    display.update(m.getMaze(), [])

    a = SearchAgent("search@127.0.0.1", "secret")

    try:
        a.setMaze(m, globalMap)
        a.start()

        for i in range(1000):
            time.sleep(.1)
            display.update(globalMap.getMap(), [a.position])
    except KeyboardInterrupt:
        pass
    except Exception, ex:
        print traceback.format_exc()
    finally:
        a.stop()
