from __future__ import print_function

from agents.search import SearchAgent
import random
import spade

class Mothership(spade.Agent.Agent):
    """The supervisor class for all other agents"""
    is_setup = False
    class SearcherManager(spade.Behaviour.PeriodicBehaviour):
        moves = [(0, -1), (0, 1), (-1, 0), (1,0)]

        def _onTick(self):
            msg = self._receive(False)

            while msg:
                perf = msg.getPerformative()
                if perf == "inform":
                    sc = msg.getContent().split(" ", 1)
                    if sc[0] == "visited":
                        loc = eval(sc[1])
                        self.myAgent.addVisited(loc)
                    elif sc[0] == "opened":
                        new = eval(sc[1])
                        for loc in new:
                            self.myAgent.addOpen(loc)
                elif perf == "request":
                    loc = eval(msg.getContent())
                    new = [(loc[0] + x, loc[1] + y) for (x, y) in self.moves
                            if (loc[0] + x, loc[1] + y) in list(self.myAgent.open)]
                    if len(new):
                        new = random.choice(new)
                    else:
                        new = random.choice(list(self.myAgent.open))
                    reply = spade.ACLMessage.ACLMessage()
                    reply.setPerformative("inform")
                    reply.setOntology("searcher")
                    reply.addReceiver(msg.getSender())
                    reply.setContent(new)
                    self.myAgent.send(reply)
                msg = self._receive(False)

    def _setup(self):
        print("Starting MotherShip {}".format(self.name))
        self.visited = set()
        self.open    = set()

        searchTemp = spade.Behaviour.ACLTemplate()
        searchTemp.setOntology("searcher")
        st = spade.Behaviour.MessageTemplate(searchTemp)
        sm = self.SearcherManager(.1)
        self.addBehaviour(sm, st)

        self.searchers = []
        for i in range(3):
            self.searchers.append(SearchAgent("search{}@127.0.0.1".format(i),
                                                "secret"))
            self.searchers[-1].setShip(self)
        self.is_setup = True

    def takeDown(self):
        print("Stopping Searchers")
        for search in self.searchers:
            search.stop()
        print("Stopping MotherShip {}...".format(self.name))

    def addOpen(self, location):
        """Add a new open location to the list of open locations"""
        if location not in self.visited:
            self.open.add(location)

    def addVisited(self, location):
        """Add a location to the visited list and remove it from the open list"""
        self.visited.add(location)
        try:
            self.open.remove(location)
        except KeyError:
            pass
