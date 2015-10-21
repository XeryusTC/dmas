from __future__ import print_function
import spade

from map.map import Map
from astar.astar import Astar
from util import backtrace

class PathFinder(spade.Agent.Agent):
    """Agent that finds best path"""
    is_setup = False


    class RequestInformationBehaviour(spade.Behaviour.PeriodicBehaviour):
        astar = Astar()

        @backtrace
        def _onTick(self):
            msg = self._receive(False)
            while msg:
                data = None
                content = eval(msg.getContent())

                if 'map' not in content.keys():
                    path = self.superpath(content['location'], content['open'])
                else:
                    try:
                        path = self.motherpath(content['map'], content['location'],
                                content['open'])
                    except:
                        print(self.myAgent.name, "error with", content)
                        raise

                rep = msg.createReply()
                if self.myAgent.sv:
                    rep.setOntology(content['ontology'])
                else:
                    rep.setPerformative("inform")
                rep.setContent("route {}".format(path))
                self.myAgent.send(rep)
                #print(self.myAgent.name, "path done", path)
                msg = self._receive(False)

        def motherpath(self, map, location, open):
            if len(open) == 0:
                open = [(1, 1)]
            path = self.astar.getPath(map, location, open[0])
            for goal in open:
                tempPath = self.astar.getPath(map, location, goal)
                if len(tempPath) > 0:
                    if len(tempPath) < len(path):
                        path = tempPath

                if len(path) == 0:
                    path = self.astar.getPath(map, location, (1, 1))
            return path

        def superpath(self, location, open):
            return self.motherpath(self.myAgent.map, location, open)


    class DatabaseMapUpdates(spade.Behaviour.PeriodicBehaviour):
        @backtrace
        def _onTick(self):
            msg = self._receive(False)
            if msg:
                content = msg.getContent().split(' ', 1)
                if content[0] == "map":
                    self.myAgent.map = content[1]
            self.myAgent.sendMapUpdateRequest()


    class RegisterServicesBehav(spade.Behaviour.OneShotBehaviour):
        def _process(self):
            dad = spade.DF.DfAgentDescription()
            sd = spade.DF.ServiceDescription()
            sd.setType("pathfinder")
            sd.setName("standalone")
            dad.addService(sd)

            dad.setAID(self.myAgent.getAID())
            res = self.myAgent.registerService(dad)
            print(self.myAgent.name, "services registred:", res)


    class SupervisorDetection(spade.Behaviour.PeriodicBehaviour):
        def onStart(self):
            print(self.myAgent.name, "Looking for supervisor")
            self.counter = 0

        @backtrace
        def _process(self):
            sd = spade.DF.ServiceDescription()
            sd.setType("supervisor")
            dad = spade.DF.DfAgentDescription()
            dad.addService(sd)

            result = self.myAgent.searchService(dad)
            if len(result):
                self.myAgent.sv = True

            if self.counter > 50 or self.myAgent.sv:
                self.myAgent.removeBehaviour(self)
            if self.counter > 50:
                self.myAgent.removeBehaviour(self.myAgent.mapbehav)
            self.counter = self.counter + 1


    def _setup(self):
        print("Starting PathFinderAgent {}...".format(self.name))

        self.sv = False
        self.map = []

        self.addBehaviour(self.RegisterServicesBehav(), None)

        replyTemp = spade.Behaviour.ACLTemplate()
        replyTemp.setPerformative("request")
        replyTemp.setOntology("map")
        temp = spade.Behaviour.MessageTemplate(replyTemp)

        rb = self.RequestInformationBehaviour(.1)
        self.addBehaviour(rb, temp)

        sb = self.SupervisorDetection(.1)
        self.addBehaviour(sb, None)

        dbTemp = spade.Behaviour.ACLTemplate()
        dbTemp.setPerformative("inform")
        temp = spade.Behaviour.MessageTemplate(dbTemp)
        self.mapbehav = self.DatabaseMapUpdates(.1)
        self.addBehaviour(self.mapbehav, temp)
        self.sendMapUpdateRequest()

        self.is_setup = True

    def takeDown(self):
        print("Stopping PathFinder agent {}...".format(self.name))

    def sendMapUpdateRequest(self):
        msg = spade.ACLMessage.ACLMessage()
        msg.setPerformative(msg.REQUEST)
        msg.addReceiver(spade.AID.aid("db@127.0.0.1", ["xmpp://db@127.0.0.1"]))
        msg.setContent("MAP")
        self.send(msg)


def main():
    import time
    import traceback
    pf = PathFinder("path@127.0.0.1", "secret")
    pf.start()

    try:
        while 1: time.sleep(1)
    except KeyboardInterrupt:
        pass
    except:
        print(traceback.format_exc())

    pf.stop()

if __name__ == '__main__':
    main()
