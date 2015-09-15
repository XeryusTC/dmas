from maze.maze import Maze
from gnui.gnui import GNUI
from map.map import Map

originalMap = Maze(32,16)
display = GNUI(32,16)
globalMap = Map(32,16)


for i in xrange(1,12):
	data = originalMap.getData(i,1)
	globalMap.update(i,1,data)

for i in xrange(6,26):
	data = originalMap.getData(i,7)
	globalMap.update(i,7,data)


display.update(originalMap.getMaze(),1)




