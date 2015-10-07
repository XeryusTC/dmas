from __future__ import print_function
import spade

from map.map import Map
from astar.astar import Astar

class PathFinder(spade.Agent.Agent):
    """Agent that finds best path"""
    is_setup = False


    class RequestInformationBehaviour(spade.Behaviour.PeriodicBehaviour):
        astar = Astar()

        def _onTick(self):

            msg = None
            msg = self._receive(False)
            if msg:
                data = None
                content = eval(msg.getContent())
                
                if len(content['open']) == 0:
                    content['open'] = [(1,1)]

                path = self.astar.getPath(content['map'], content['location'], content['open'][0])
                
                for goal in content['open']:

                    try:
                        tempPath = self.astar.getPath(content['map'], content['location'], goal)

                        if len(tempPath) > 0:
                            if len(tempPath) < len(path):
                                path = tempPath
                    except Exception as e:
                        print(e)

                    if len(path) == 0:
                        path = self.astar.getPath(content['map'], content['location'], (1,1))        

                try:

                    rep = msg.createReply()
                    rep.setPerformative("inform")
                    rep.setContent("route {}".format(path))
                    self.myAgent.send(rep)
                except Exception as e:
                    print(e)
                print(path)
                print("PATH DONE")


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


    def _setup(self):
        print("Starting PathFinderAgent {}...".format(self.name))

        self.addBehaviour(self.RegisterServicesBehav(), None)

        replyTemp = spade.Behaviour.ACLTemplate()
        replyTemp.setPerformative("request")
        replyTemp.setOntology("map")
        temp = spade.Behaviour.MessageTemplate(replyTemp)

        rb = self.RequestInformationBehaviour(.1)
        self.addBehaviour(rb, temp)

        self.is_setup = True

    def takeDown(self):
        print("Stopping PathFinder agent {}...".format(self.name))
