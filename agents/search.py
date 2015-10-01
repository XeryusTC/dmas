from __future__ import print_function

import random
import spade
import time

from maze import maze

class SearchAgent(spade.Agent.Agent):
    CORRIDOR_WALK_CODE = 1
    PATH_WALK_CODE     = 2
    PICK_CORRIDOR_CODE = 3
    WAIT_FOR_PATH_CODE = 4

    TRANS_DEFAULT       = 0
    TRANS_CORRIDOR_WALK = 10
    TRANS_PATH_WALK     = 20
    TRANS_PICK_CORRIDOR = 30
    TRANS_WAIT_FOR_PATH = 40

    TIMEOUT = 1 # wait between proccessing oneshots

    is_setup = False

    class WalkCorridorBehav(spade.Behaviour.OneShotBehaviour):
        # CORRIDOR_WALK_CODE
        moves = [(0, -1), (0, 1), (-1, 0), (1, 0)]

        def onStart(self):
            print(self.myAgent.name + " starting corridor walk")

        def _process(self):
            new = []
            for x, y in self.moves:
                nextpos = (self.myAgent.x+x, self.myAgent.y+y)
                if nextpos in self.myAgent.open \
                        and nextpos != self.myAgent.previous:
                    new.append(nextpos)
            if len(new) == 1:
                (x, y) = new[0]
                self.myAgent.move(x, y)
            else:
                self._exitcode = self.myAgent.TRANS_PICK_CORRIDOR
                return self._exitcode
            # update the map
            self.myAgent.sense()
            self._exitcode = self.myAgent.TRANS_DEFAULT
            time.sleep(self.myAgent.TIMEOUT)


    class PickPathBehav(spade.Behaviour.OneShotBehaviour):
        # PICK_CORRIDOR_CODE
        def onStart(self):
            print(self.myAgent.name + " starting pick path")

        def _process(self):
            msg = spade.ACLMessage.ACLMessage()
            msg.setPerformative(msg.REQUEST)
            msg.setOntology("searcher")
            msg.addReceiver(self.myAgent.ship.getAID())
            msg.setContent( (self.myAgent.x, self.myAgent.y) )
            self.myAgent.send(msg)
            self._exitcode = self.myAgent.TRANS_WAIT_FOR_PATH


    class WaitForPathBehav(spade.Behaviour.OneShotBehaviour):
        # WAIT_FOR_PATH_CODE
        def onStart(self):
            print(self.myAgent.name + " starting wait path")

        def _process(self):
            msg = self._receive(True, 2)
            if msg:
                content = msg.getContent().split(' ', 1)
                if content[0] == "route":
                    route = eval(content[1])
                    self.myAgent.route = route
                    self._exitcode = self.myAgent.TRANS_PATH_WALK
                else:
                    reply = msg.createReply()
                    reply.setPerformative(reply.NOT_UNDERSTOOD)
                    self.myAgent.send(reply)
            else:
                self._exitcode = self.myAgent.TRANS_DEFAULT


    class PathWalkBehav(spade.Behaviour.OneShotBehaviour):
        # PATH_WALK_CODE
        def onStart(self):
            print(self.myAgent.name + " starting walk path")

        def _process(self):
            if self.myAgent.route == []:
                self._exitcode = self.myAgent.TRANS_CORRIDOR_WALK
            else:
                x, y = self.myAgent.route[0]
                self.myAgent.move(x, y)
                self.myAgent.sense()
                self.myAgent.route = self.myAgent.route[1:]
                self._exitcode = self.myAgent.TRANS_DEFAULT
            print(self._exitcode)
            time.sleep(self.myAgent.TIMEOUT)


    def _setup(self):
        print("Starting search agent {}...".format(self.name))
        self.visited = set()
        self.open = set()
        self.route = []
        #self.move(1, self.maze.h * 2)
        self.move(1, 1)

        #rw = self.RandomWalkBehav(1)
        temp = spade.Behaviour.ACLTemplate()
        temp.setOntology("searcher")
        rt = spade.Behaviour.MessageTemplate(temp)
        #self.addBehaviour(rw, rt)
        b = spade.Behaviour.FSMBehaviour()
        b.registerFirstState(self.PickPathBehav(), self.PICK_CORRIDOR_CODE)
        b.registerState(self.WalkCorridorBehav(), self.CORRIDOR_WALK_CODE)
        b.registerState(self.WaitForPathBehav(), self.WAIT_FOR_PATH_CODE)
        b.registerState(self.PathWalkBehav(), self.PATH_WALK_CODE)

        b.rT = b.registerTransition
        b.rT(self.PICK_CORRIDOR_CODE, self.WAIT_FOR_PATH_CODE, self.TRANS_WAIT_FOR_PATH)
        b.rT(self.CORRIDOR_WALK_CODE, self.CORRIDOR_WALK_CODE, self.TRANS_DEFAULT)
        b.rT(self.CORRIDOR_WALK_CODE, self.PICK_CORRIDOR_CODE, self.TRANS_PICK_CORRIDOR)
        b.rT(self.WAIT_FOR_PATH_CODE, self.WAIT_FOR_PATH_CODE, self.TRANS_DEFAULT)
        b.rT(self.WAIT_FOR_PATH_CODE, self.PATH_WALK_CODE,     self.TRANS_PATH_WALK)
        b.rT(self.PATH_WALK_CODE,     self.PATH_WALK_CODE,     self.TRANS_DEFAULT)
        b.rT(self.PATH_WALK_CODE,     self.CORRIDOR_WALK_CODE, self.TRANS_CORRIDOR_WALK)

        self.addBehaviour(b, rt)

        self.sense()
        self.is_setup = True

    def takeDown(self):
        print("Stopping search agent {}...".format(self.name))

    def move(self, x, y):
        try:
            self.previous = (self.x, self.y)
        except AttributeError:
            pass # This was the first step, so we can ignore the exception

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
