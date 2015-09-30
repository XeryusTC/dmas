from __future__ import print_function

import random
import spade

from maze import maze

class SearchAgent(spade.Agent.Agent):
    is_setup = False

    class RandomWalkBehav(spade.Behaviour.PeriodicBehaviour):
        moves = [(0, -1), (0, 1), (-1, 0), (1, 0)]
        def onStart(self):
            print("Starting random walk")
            self.waiting = False

        def _onTick(self):
            if self.waiting:
                msg = self._receive(False)
                if msg:
                    content = msg.getContent().split(' ', 1)
                    if content[0] == "route":
                        route = eval(content[1])
                        self.myAgent.route = route
                        self.waiting = False
                    else:
                        reply = msg.createReply()
                        reply.setPerformative(reply.NOT_UNDERSTOOD)
                        self.myAgent.send(reply)
                        return
                else:
                    return
            r = self.myAgent.route
            if len(r):
                (x, y) = r[0]
                self.myAgent.move(x, y)
                self.myAgent.route = r[1:]
            else:
                new = [(self.myAgent.x+x, self.myAgent.y+y) 
                        for (x, y) in self.moves
                        if (self.myAgent.x+x,self.myAgent.y+y) 
                                in self.myAgent.open]
                if len(new) == 1:
                    (x, y) = new[0]
                    self.myAgent.move(x, y)
                else:
                    msg = spade.ACLMessage.ACLMessage()
                    msg.setPerformative(msg.REQUEST)
                    msg.setOntology("searcher")
                    msg.addReceiver(self.myAgent.ship.getAID())
                    msg.setContent( (self.myAgent.x, self.myAgent.y) )
                    self.myAgent.send(msg)
                    self.waiting = True
            # Update the map
            self.myAgent.sense()

    def _setup(self):
        print("Starting search agent {}...".format(self.name))
        self.visited = set()
        self.open = set()
        self.route = []
        #self.move(1, self.maze.h * 2)
        self.move(1, 1)

        rw = self.RandomWalkBehav(1)
        temp = spade.Behaviour.ACLTemplate()
        temp.setOntology("searcher")
        rt = spade.Behaviour.MessageTemplate(temp)
        self.addBehaviour(rw, rt)
        self.sense()
        self.is_setup = True

    def takeDown(self):
        print("Stopping search agent {}...".format(self.name))

    def move(self, x, y):
        self.visited.add( (x, y) )
        try:
            self.open.remove( (x, y) )
        except KeyError:
            print("Position ", (x, y), " not in open list")
        self.x = x
        self.y = y
        msg = spade.ACLMessage.ACLMessage()
        msg.setPerformative("inform")
        msg.setOntology("searcher")
        msg.addReceiver(self.ship.getAID())
        msg.setContent("visited {}".format( (x, y) ))
        self.send(msg)

    def setShip(self, s):
        self.ship = s

    def setMaze(self, m):
        self.maze = m

    def sense(self):
        try:
            d = self.maze.getData(self.x, self.y)
        except AttributeError:
            print("Unable to sense data")

        # send data to the database agent
        msg = spade.ACLMessage.ACLMessage()
        msg.setPerformative("inform")
        msg.addReceiver(spade.AID.aid("db@127.0.0.1",
            ["xmpp://db@127.0.0.1"]))
        msg.setContent({'pos': self.position, 'data': d})
        self.send(msg)

        pos = [(0, -1), (1, -1), (1, 0), (1, 1), (0, 1), (-1, 1), (-1, 0), (-1, -1)]
        openlist = []
        for i in range(len(d)):
            if d[i] == maze.PATH_VISITED or d[i] == maze.TARGET:
                x = self.x + pos[i][0]
                y = self.y + pos[i][1]
                if (x, y) not in self.visited:
                    self.open.add( (x, y) )
                    openlist.append( (x, y) )
        if len(openlist):
            msg = spade.ACLMessage.ACLMessage()
            msg.setPerformative("inform")
            msg.setOntology("searcher")
            msg.addReceiver(self.ship.getAID())
            msg.setContent("opened {}".format(openlist))
            self.send(msg)

    @property
    def position(self):
        return (self.x, self.y)
