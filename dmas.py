from maze.maze import Maze
from gnui.gnui import GNUI

map = Maze(32,16)
display = GNUI(32,16)

display.update(map.getMaze(),1)

test = map.getMaze()
