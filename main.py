import time
import traceback

from maze.maze import Maze
from gnui.gnui import GNUI
from agents.search import SearchAgent
from agents.db import DatabaseAgent
from agents.mothership import Mothership

WIDTH  = 32
HEIGHT = 16
SEARCH = range(3)

if __name__ == "__main__":
    m = Maze(WIDTH, HEIGHT)
    display = GNUI(WIDTH, HEIGHT)

    display.update(m.getMaze(), [])

    mother = Mothership("mother@127.0.0.1", "secret")
    db = DatabaseAgent("db@127.0.0.1", "secret")
    db.width  = WIDTH
    db.height = HEIGHT

    try:
        mother.start()
        db.start()
        while (not db.is_setup) or (not mother.is_setup):
            pass

        print "Starting searchers"
        search = mother.searchers
        for s in search:
            s.setMaze(m)

        for i in range(1000):
            search = mother.searchers
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
    try:
        for s in mother.searchers:
            s.stop()
    except:
        pass
    db.stop()
    mother.stop()
