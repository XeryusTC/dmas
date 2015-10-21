from __future__ import print_function

import random
import spade
import time

from maze import maze
from util import backtrace

class SearchAgent(spade.Agent.Agent):
    CORRIDOR_WALK_CODE = 1
    PATH_WALK_CODE     = 2
    PICK_CORRIDOR_CODE = 3
    WAIT_FOR_PATH_CODE = 4
    DISCOVER_CODE      = 5

    TRANS_DEFAULT       = 0
    TRANS_CORRIDOR_WALK = 10
    TRANS_PATH_WALK     = 20
    TRANS_PICK_CORRIDOR = 30
    TRANS_WAIT_FOR_PATH = 40
    TRANS_DISCOVER      = 50

    TIMEOUT = .5 # wait between proccessing oneshots

    is_setup = False

    class WalkCorridorBehav(spade.Behaviour.OneShotBehaviour):
        # CORRIDOR_WALK_CODE
        moves = [(0, -1), (0, 1), (-1, 0), (1, 0)]
        @backtrace
        def _process(self):
            new = []
            self._exitcode = self.myAgent.TRANS_DEFAULT
            paths = [(x, y) for (x, y, z) in self.myAgent.paths]
            for x, y in self.moves:
                nextpos = (self.myAgent.x+x, self.myAgent.y+y)
                if nextpos in paths \
                        and nextpos != self.myAgent.previous:
                    new.append(nextpos)
            if len(new) == 1:
                (x, y) = new[0]
                self.myAgent.move(x, y)
            else:
                self._exitcode = self.myAgent.TRANS_PICK_CORRIDOR
            # update the map
            self.myAgent.sense()
            time.sleep(self.myAgent.TIMEOUT)


    class PickPathBehav(spade.Behaviour.OneShotBehaviour):
        # PICK_CORRIDOR_CODE
        @backtrace
        def _process(self):
            msg = spade.ACLMessage.ACLMessage()
            msg.setPerformative(msg.REQUEST)
            msg.setOntology("searcher")
            if self.myAgent.ship:
                msg.addReceiver(self.myAgent.ship)
            else:
                msg.addReceiver(self.myAgent.sv)
            msg.setConversationId(self.myAgent.pathcnt)
            msg.setContent( (self.myAgent.x, self.myAgent.y) )
            self.myAgent.send(msg)
            self._exitcode = self.myAgent.TRANS_WAIT_FOR_PATH


    class WaitForPathBehav(spade.Behaviour.OneShotBehaviour):
        # WAIT_FOR_PATH_CODE
        def onStart(self):
            if self.myAgent.waitPathTimer == None:
                self.myAgent.waitPathTimer = 4

        @backtrace
        def _process(self):
            msg = self._receive(False)
            if msg:
                content = msg.getContent().split(' ', 1)
                if content[0] == "route":
                    route = eval(content[1])
                    if int(msg.getConversationId()) == self.myAgent.pathcnt:
                        #print(self.myAgent.name, "received route:", route)
                        self.myAgent.route = route
                        self.myAgent.pathcnt += 1
                        self._exitcode = self.myAgent.TRANS_PATH_WALK
                        # in the case that the route is longer, mark the end as
                        # visited so other searchers dont plan the same path
                        if len(route) > 1 and self.myAgent.sv:
                            svmsg = spade.ACLMessage.ACLMessage()
                            svmsg.setPerformative("inform")
                            svmsg.setOntology("searcher")
                            svmsg.addReceiver(self.myAgent.sv)
                            svmsg.setContent("visited {}".format(route[-1]))
                            self.myAgent.send(svmsg)
                    else:
                        pass
                        #print(self.myAgent.name, "discarding route:", route,
                                #msg.getConversationId(), self.myAgent.pathcnt)
                elif content[0] == "destination":
                    planner = random.choice(self.myAgent.pf)
                    dest = eval(content[1])
                    #print(self.myAgent.name, "planning path to", dest)

                    msg = spade.ACLMessage.ACLMessage()
                    msg.setPerformative(msg.REQUEST)
                    msg.setOntology("map")
                    msg.addReceiver(planner)
                    msg.setConversationId(self.myAgent.pathcnt)
                    msg.setContent({'open': dest, 'location': self.myAgent.position,
                        'ontology': 'searcher'})
                    self.myAgent.send(msg)
                    self._exitcode = self.myAgent.TRANS_DEFAULT
                else:
                    reply = msg.createReply()
                    reply.setPerformative(reply.NOT_UNDERSTOOD)
                    self.myAgent.send(reply)
            else:
                if self.myAgent.waitPathTimer < 0:
                    #print(self.myAgent.name, "POSSIBLY STUCK, UNSTUCKING")
                    self.myAgent.waitPathTimer = None
                    self._exitcode = self.myAgent.TRANS_PICK_CORRIDOR
                else:
                    self.myAgent.waitPathTimer -= 0.1
                    time.sleep(0.1)
                    self._exitcode = self.myAgent.TRANS_DEFAULT


    class PathWalkBehav(spade.Behaviour.OneShotBehaviour):
        # PATH_WALK_CODE
        @backtrace
        def _process(self):
            if self.myAgent.route == []:
                self._exitcode = self.myAgent.TRANS_CORRIDOR_WALK
            else:
                x, y = self.myAgent.route[0]
                self.myAgent.move(x, y)
                self.myAgent.sense()
                self.myAgent.route = self.myAgent.route[1:]
                if self.myAgent.route == []:
                    self._exitcode = self.myAgent.TRANS_CORRIDOR_WALK
                else:
                    self._exitcode = self.myAgent.TRANS_DEFAULT
            time.sleep(self.myAgent.TIMEOUT)


    class DiscoverServicesBehav(spade.Behaviour.OneShotBehaviour):
        # DISCOVER_CODE
        @backtrace
        def _process(self):
            self._exitcode = self.myAgent.TRANS_DEFAULT
            # Discover mothership (if present)
            sd = spade.DF.ServiceDescription()
            sd.setType("mothership")
            dad = spade.DF.DfAgentDescription()
            dad.addService(sd)

            result = self.myAgent.searchService(dad)
            if len(result):
                #print(self.myAgent.name, "switching to mothership")
                self.myAgent.ship = result[0].getAID()
                self.myAgent.sense()
                self._exitcode = self.myAgent.TRANS_PICK_CORRIDOR
                return

            # Discover supervisor and other agents
            sd = spade.DF.ServiceDescription()
            sd.setType("supervisor")
            dad = spade.DF.DfAgentDescription()
            dad.addService(sd)

            result = self.myAgent.searchService(dad)
            if len(result):
                #print(self.myAgent.name, "switching to supervisor")
                self.myAgent.sv = result[0].getAID()
                self.myAgent.sense()

                # Discover pathfinders
                sd = spade.DF.ServiceDescription()
                sd.setType("pathfinder")
                dad = spade.DF.DfAgentDescription()
                dad.addService(sd)
                result = self.myAgent.searchService(dad)
                if len(result):
                    self.myAgent.pf = [pf.getAID() for pf in result]
                    self.myAgent.sense()
                    self._exitcode = self.myAgent.TRANS_PICK_CORRIDOR


    def _setup(self):
        print("Starting search agent {}...".format(self.name))
        self.route = []
        self.x = 1
        self.y = 1
        self.ship = False
        self.previous = None

        self.sv = False
        self.pf = []
        self.pathcnt = 0

        self.waitPathTimer = None

        temp = spade.Behaviour.ACLTemplate()
        temp.setOntology("searcher")
        rt = spade.Behaviour.MessageTemplate(temp)

        b = spade.Behaviour.FSMBehaviour()
        b.registerFirstState(self.DiscoverServicesBehav(), self.DISCOVER_CODE)
        b.registerState(self.PickPathBehav(),     self.PICK_CORRIDOR_CODE)
        b.registerState(self.WalkCorridorBehav(), self.CORRIDOR_WALK_CODE)
        b.registerState(self.WaitForPathBehav(),  self.WAIT_FOR_PATH_CODE)
        b.registerState(self.PathWalkBehav(),     self.PATH_WALK_CODE)

        b.rT = b.registerTransition
        b.rT(self.DISCOVER_CODE,      self.DISCOVER_CODE,      self.TRANS_DEFAULT)
        b.rT(self.DISCOVER_CODE,      self.PICK_CORRIDOR_CODE, self.TRANS_PICK_CORRIDOR)
        b.rT(self.PICK_CORRIDOR_CODE, self.WAIT_FOR_PATH_CODE, self.TRANS_WAIT_FOR_PATH)
        b.rT(self.CORRIDOR_WALK_CODE, self.CORRIDOR_WALK_CODE, self.TRANS_DEFAULT)
        b.rT(self.CORRIDOR_WALK_CODE, self.PICK_CORRIDOR_CODE, self.TRANS_PICK_CORRIDOR)
        b.rT(self.WAIT_FOR_PATH_CODE, self.WAIT_FOR_PATH_CODE, self.TRANS_DEFAULT)
        b.rT(self.WAIT_FOR_PATH_CODE, self.PICK_CORRIDOR_CODE, self.TRANS_PICK_CORRIDOR)
        b.rT(self.WAIT_FOR_PATH_CODE, self.PATH_WALK_CODE,     self.TRANS_PATH_WALK)
        b.rT(self.PATH_WALK_CODE,     self.PATH_WALK_CODE,     self.TRANS_DEFAULT)
        b.rT(self.PATH_WALK_CODE,     self.CORRIDOR_WALK_CODE, self.TRANS_CORRIDOR_WALK)

        self.addBehaviour(b, rt)

        self.is_setup = True

    def takeDown(self):
        print("Stopping search agent {}...".format(self.name))

    def move(self, x, y):
        self.previous = (self.x, self.y)

        self.x = x
        self.y = y
        msg = spade.ACLMessage.ACLMessage()
        msg.setPerformative("inform")
        msg.setOntology("searcher")
        if self.ship:
            msg.addReceiver(self.ship)
        else:
            msg.addReceiver(self.sv)
        msg.setContent("visited {}".format( (x, y) ))
        self.send(msg)

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
        self.paths = []
        for i in range(len(d)):
            if d[i] in maze.ACCESSIBLE:
                x = self.x + pos[i][0]
                y = self.y + pos[i][1]
                self.paths.append( (x, y, d[i]) )
        openlist = self.paths

        if len(openlist):
            msg = spade.ACLMessage.ACLMessage()
            msg.setPerformative("inform")
            msg.setOntology("searcher")
            if self.ship:
                msg.addReceiver(self.ship)
            else:
                msg.addReceiver(self.sv)
            msg.setContent("opened {}".format(openlist))
            self.send(msg)

    @property
    def position(self):
        return (self.x, self.y)
