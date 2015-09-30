from __future__ import print_function

from agents.search import SearchAgent
import random
import spade

class Mothership(spade.Agent.Agent):
    """The supervisor class for all other agents"""
    is_setup = False
    class RouteManager(spade.Behaviour.PeriodicBehaviour):
        def _onTick(self):
            msg = self._receive(False)
            while msg:
                print("Got Reply!")
                convId = int(msg.getConversationId())
                content = msg.getContent().split(' ', 1)
                try:
                    status = self.myAgent.queue[convId]
                except Exception as e:
                    print(e)
                    return 
                print(status)
                if not status['map']:
                    if content[0] == "map":
                        map = eval(content[1])
                        status['map'] = map
                        planMsg = spade.ACLMessage.ACLMessage(msg.REQUEST)
                        print("Got map!")
                        # gotta call the planner here
                    else:
                        reply = msg.createReply()
                        reply.setPerformative(msg.NOT_UNDERSTOOD)
                        self.myAgent.send(reply)
                else:
                    if content[0] == "route":
                        route = eval(content[1])
                        reply = status['original'].createReply()
                        reply.setPerformative(msg.INFORM)
                        reply.setContent("route {}".format(route))
                        self.myAgent.send(reply)
                        del self.myAgent.queue[convId]
                    else:
                        reply = msg.createReply()
                        reply.setPerformative(msg.NOT_UNDERSTOOD)
                        self.myAgent.send(reply)
                msg = self._receive(False)

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
                    print("got request")
                    loc = eval(msg.getContent())
                    new = [(loc[0] + x, loc[1] + y) for (x, y) in self.moves
                            if (loc[0] + x, loc[1] + y) in list(self.myAgent.open)]
                    if len(new): # Move to position next to you
                        new = random.choice(new)
                        reply = msg.createReply()
                        reply.setPerformative(reply.INFORM)
                        reply.setContent("route {}".format([new]))
                        self.myAgent.send(reply)
                        print("Send Reply: {}".format(new))
                    else: # Get a route to a point on the open list
                        dbMsg = spade.ACLMessage.ACLMessage(msg.REQUEST)
                        dbMsg.setOntology("map")
                        dbMsg.addReceiver(spade.AID.aid("db@127.0.0.1",
                                                    ["xmpp://db@127.0.0.1"]))
                        dbMsg.setConversationId(len(self.myAgent.queue))
                        self.myAgent.queue.append({'original': msg,
                                                   'start': loc,
                                                   'map': None})
                        dbMsg.setContent("MAP")
                        self.myAgent.send(dbMsg)
                msg = self._receive(False)

    def _setup(self):
        print("Starting MotherShip {}".format(self.name))
        self.visited = set()
        self.open    = set()
        self.queue = {}

        searchTemp = spade.Behaviour.ACLTemplate()
        searchTemp.setOntology("searcher")
        st = spade.Behaviour.MessageTemplate(searchTemp)
        sm = self.SearcherManager(.1)
        self.addBehaviour(sm, st)

        routeTemp = spade.Behaviour.ACLTemplate()
        routeTemp.setOntology("map")
        rt = spade.Behaviour.MessageTemplate(routeTemp)
        rm = self.RouteManager(.1)
        self.addBehaviour(rm, rt)

        self.searchers = []
        for i in range(1):
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
