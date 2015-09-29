from __future__ import print_function

import random
from map.map import Map
import spade

from maze import maze

class SearchAgent(spade.Agent.Agent):

    class RandomWalkBehav(spade.Behaviour.PeriodicBehaviour):
        def onStart(self):
            print("Starting random walk")

        def _onTick(self):
            # Create possible directions to move in
            moves = [(0, -1), (0, 1), (-1, 0), (1, 0)]
            new = [(self.myAgent.x+x, self.myAgent.y+y) for (x, y) in moves
                   if (self.myAgent.x+x,self.myAgent.y+y) in self.myAgent.open]
            if len(new):
                new = random.choice(new)
            else: # Jump to random location if stuck
                new = random.choice(list(self.myAgent.open))
            self.myAgent.move(new[0], new[1])

            # Update the map
            self.myAgent.sense()
            print('visited: ', self.myAgent.visited)
            print('open:    ', self.myAgent.open)

    def _setup(self):
        print("Starting search agent...")
        self.visited = set()
        self.open = set()
        #self.move(1, self.maze.h * 2)
        self.move(1, 1)

        rw = self.RandomWalkBehav(1)
        self.addBehaviour(rw, None)
        self.sense()

    def takeDown(self):
        print("Stopping search agent...")

    def move(self, x, y):
        self.visited.add( (x, y) )
        try:
            self.open.remove( (x, y) )
        except KeyError:
            print("Position ", (x, y), " not in open list")
        self.x = x
        self.y = y

    def setMaze(self, m, d):
        self.maze = m
        self.map = d

    def sense(self):
        try:
            d = self.maze.getData(self.x, self.y)
        except AttributeError:
            print("Unable to sense data")

        self.map.update(self.x, self.y, d)

        pos = [(0, -1), (1, -1), (1, 0), (1, 1), (0, 1), (-1, 1), (-1, 0), (-1, -1)]
        for i in range(len(d)):
            if d[i] == maze.PATH_VISITED:
                x = self.x + pos[i][0]
                y = self.y + pos[i][1]
                if (x, y) not in self.visited:
                    self.open.add( (x, y) )

    @property
    def position(self):
        return (self.x, self.y)
