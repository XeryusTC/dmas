from __future__ import print_function
import spade
import random
import time

from maze import maze
from util import backtrace

class SupervisorAgent(spade.Agent.Agent):
    is_setup = False

    class SearcherManager(spade.Behaviour.PeriodicBehaviour):
        moves = [(0, -1), (0, 1), (-1, 0), (1, 0)]

        @backtrace
        def _onTick(self):
            msg = self._receive(False)
            while msg:
                perf = msg.getPerformative()
                if perf == "inform":
                    content = msg.getContent().split(" ", 1)
                    if content[0] == "opened":
                        new = eval(content[1])
                        for loc in new:
                            self.myAgent.addOpen(loc[:2])
                            if loc[2] == maze.TARGET and loc[:2] not in self.myAgent.saved:
                                self.myAgent.targets.add(loc[:2])
                    elif content[0] == "visited":
                        loc = eval(content[1])
                        self.myAgent.addVisited(loc)
                elif perf == "request":
                    # Try to see if there is an open route next to the searcher
                    loc = eval(msg.getContent())
                    new = [(loc[0] + x, loc[1] + y) for (x, y) in self.moves
                            if (loc[0] +x, loc[1] + y) in list(self.myAgent.open)]
                    if len(new):
                        new = random.choice(new)
                        reply = msg.createReply()
                        reply.setPerformative(reply.INFORM)
                        reply.setContent("route {}".format([new]))
                        self.myAgent.send(reply)
                    # otherwise pick a random position from the open list to
                    # send the agent to
                    else:
                        if len(self.myAgent.open) == 0:
                            # There are no more open spaces so send the agent to the start
                            loc = [(1, 1)]
                        else:
                            # Send the entire list of open location so the
                            # pathfinder can do the hard work
                            loc = list(self.myAgent.open)
                        reply = msg.createReply()
                        reply.setPerformative(reply.INFORM)
                        reply.setContent("destination {}".format(loc))
                        self.myAgent.send(reply)
                msg = self._receive(False)


    class RescueManager(spade.Behaviour.PeriodicBehaviour):
        @backtrace
        def _onTick(self):
            msg = self._receive(False)
            while msg:
                content = msg.getContent().split(' ', 1)
                if content[0] == 'nopath':
                    # No path means that we put the target back in the set
                    target = eval(content[1])
                    self.myAgent.saved.discard(target)
                    self.myAgent.targets.add(target)
                    print(self.myAgent.name, "rescuer could not find path to", target)
                else:
                    print(self.myAgent.name, "UNKNOWN MESSAGE", msg.getContent())
                msg = self._receive(False)

            if len(self.myAgent.targets):
                # Find a rescuer to send to the target
                sd = spade.DF.ServiceDescription()
                sd.setType("rescue")
                sd.setName("available")
                dad = spade.DF.DfAgentDescription()
                dad.addService(sd)
                result = self.myAgent.searchService(dad)
                if len(result):
                    rescuer = result[0].getAID()
                    target = self.myAgent.targets.pop()
                    self.myAgent.saved.add(target)
                    msg = spade.ACLMessage.ACLMessage()
                    msg.setOntology("rescuer")
                    msg.addReceiver(rescuer)
                    msg.setContent("target {}".format(target))
                    self.myAgent.send(msg)
                    print(self.myAgent.name, "send", rescuer.getName(), "to", target)

        def onEnd(self):
            # hacked in deregistering of services
            self.myAgent.deregisterService(self.myAgent.dad)


    class RegisterServicesBehav(spade.Behaviour.OneShotBehaviour):
        def onSetup(self):
            print("Registering supervisor services")

        def _process(self):
            self.myAgent.register_services()


    def _setup(self):
        print("Starting supervisor {}".format(self.name))
        self.visited = set()
        self.open    = set()
        self.targets = set()
        self.saved   = set()

        self.addBehaviour(self.RegisterServicesBehav(), None)


        searchTemp = spade.Behaviour.ACLTemplate()
        searchTemp.setOntology("searcher")
        st = spade.Behaviour.MessageTemplate(searchTemp)
        sm = self.SearcherManager(.1)
        self.addBehaviour(sm, st)

        rescueTemp = spade.Behaviour.ACLTemplate()
        rescueTemp.setOntology("rescuer")
        rt = spade.Behaviour.MessageTemplate(rescueTemp)
        rm = self.RescueManager(.1)
        self.addBehaviour(rm, rt)

        self.is_setup = True

    def register_services(self):
        self.dad = spade.DF.DfAgentDescription()
        sd = spade.DF.ServiceDescription()
        sd.setType("supervisor")
        sd.setName("supervisor")
        self.dad.addService(sd)

        self.dad.setAID(self.getAID())
        res = self.registerService(self.dad)
        print("Supervisor registered:", str(res))

    def addOpen(self, location):
        if location not in self.visited:
            self.open.add(location)

    def addVisited(self, location):
        self.visited.add(location)
        try:
            self.open.remove(location)
        except KeyError:
            pass
