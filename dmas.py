from maze.maze import Maze
from gnui.gnui import GNUI
from map.map import Map
from astar.astar import Astar

import numpy as np

import time

originalMap = Maze(32,16)
display = GNUI(32,16)
pathPlanner = Astar()

print originalMap.getData(1,1)

print np.array(originalMap.getMaze())



display.update(originalMap.getMaze(), [(1,1)])


time.sleep(2)


