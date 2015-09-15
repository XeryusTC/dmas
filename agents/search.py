from __future__ import print_function

import random

import spade

class SearchAgent(spade.Agent.Agent):

    class RandomWalkBehav(spade.Behaviour.PeriodicBehaviour):
        def onStart(self):
            print("Starting random walk")

        def _onTick(self):
            self.myAgent
            self.myAgent.sense()
            print('visited: ', self.myAgent.visited)
            print('open:    ', self.myAgent.open)

            # Create possible directions to move in
            new = [ (self.myAgent.x,   self.myAgent.y-1),
                    (self.myAgent.x,   self.myAgent.y+1),
                    (self.myAgent.x-1, self.myAgent.y),
                    (self.myAgent.x+1, self.myAgent.x) ]
            new = random.choice([ n for n in new if n in self.myAgent.open ])
            self.myAgent.move(new[0], new[1])

    def _setup(self):
        print("Starting search agent...")
        self.visited = set()
        self.open = set()
        self.move(len(self.maze.maze) / 2, 1)
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
            pass
        self.x = x
        self.y = y

    def get_open_neighbours(self):
        n = []
        if (self.x-1, self.y) in self.open:
            n.append( (self.x-1, self.y) )
        if (self.x+1, self.y) in self.open:
            n.append( (self.x+1, self.y) )
        if (self.x, self.y-1) in self.open:
            n.append( (self.x, self.y-1) )
        if (self.x, self.y+1) in self.open:
            n.append( (self.x, self.y+1) )
        return n

    def setMaze(self, m):
        self.maze = m

    def sense(self):
        try:
            d = self.maze.getData(self.x, self.y)
        except AttributeError:
            return

        pos = [(0, -1), (1, -1), (1, 0), (1, 1), (0, 1), (-1, 1), (-1, 0), (-1, -1)]
        for i in range(len(d)):
            if d[i] == 2:
                x = self.x + pos[i][0]
                y = self.y + pos[i][1]
                if (x, y) not in self.visited:
                    self.open.add( (x, y) )
