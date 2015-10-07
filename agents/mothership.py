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
                try:
                    convId = int(msg.getConversationId())
                    content = msg.getContent().split(' ', 1)
                    status = self.myAgent.queue[convId]
                except Exception as e:
                    print(e)
                    return
                if not status['map']:
                    if content[0] == "map":
                        status['map'] = content[1] #MAP
                        planMsg = spade.ACLMessage.ACLMessage(msg.REQUEST)

                        planMsg.setOntology("map")
                        planMsg.setConversationId(convId)
                        planMsg.addReceiver(spade.AID.aid("path@127.0.0.1",
                                                    ["xmpp://path@127.0.0.1"]))

                        planMsg.setContent({'map' : content[1], 'open' : list(self.myAgent.open), 'location' : status['start']})
                        self.myAgent.send(planMsg)
                    else:
                        reply = msg.createReply()
                        reply.setPerformative(msg.NOT_UNDERSTOOD)
                        self.myAgent.send(reply)
                else:
                    print("ROUTE RECEIVED")
                    if content[0] == "route":
                        try:
                            #Remove new target from open list
                            if len(eval(content[1])) > 0:
                                tempTarget = eval(content[1])[-1]
                        
                                if tempTarget in self.myAgent.open:
                                    self.myAgent.open.remove(tempTarget)

                        except Exception as e:
                            print(e)


                        reply = status['original'].createReply()
                        reply.setPerformative(msg.INFORM)
                        reply.setContent(msg.getContent())
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
                        #print("Send Reply: {}".format(new))
                    else: # Get a route to a point on the open list
                        print("Requesting path to point")
                        try:
                            dbMsg = spade.ACLMessage.ACLMessage(msg.REQUEST)
                            dbMsg.setOntology("map")
                            dbMsg.addReceiver(spade.AID.aid("db@127.0.0.1",
                                                    ["xmpp://db@127.0.0.1"]))
                            dbMsg.setConversationId(len(self.myAgent.queue))
                            self.myAgent.queue[len(self.myAgent.queue)] = {'original': msg,
                                                   'start': loc,
                                                   'map': None}
                            dbMsg.setContent("MAP")
                            self.myAgent.send(dbMsg)
                        except Exception, e:
                            print(e)

                msg = self._receive(False)


    class RegisterServicesBehav(spade.Behaviour.OneShotBehaviour):
        def onSetup(self):
            print("Registering mothership services")

        def _process(self):
            dad = spade.DF.DfAgentDescription()
            sd = spade.DF.ServiceDescription()
            sd.setType("mothership")
            sd.setName("mothership")
            dad.addService(sd)

            sd = spade.DF.ServiceDescription()
            sd.setType("pathfinder")
            sd.setName("mothership")
            dad.addService(sd)

            dad.setAID(self.myAgent.getAID())
            res = self.myAgent.registerService(dad)
            print("Mothership registered:", str(res))


    def _setup(self):
        print("Starting MotherShip {}".format(self.name))
        self.visited = set()
        self.open    = set()
        self.queue = {}

        self.addBehaviour(self.RegisterServicesBehav(), None)

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

        self.is_setup = True

    def takeDown(self):
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
