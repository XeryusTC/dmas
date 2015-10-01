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

                try:
                    path = self.astar.getPath(content['map'], content['location'], content['open'][0])
                    for goal in content['open']:
                        tempPath = self.astar.getPath(content['map'], content['location'], goal)

                        if len(tempPath) < len(path):
                            path = tempPath
                except Exception as e:
                    print(e)

                try:
                    
                    rep = msg.createReply()
                    rep.setPerformative("inform")
                    rep.setContent("route {}".format(path))
                    self.myAgent.send(rep)
                except Exception as e:
                    print(e)
                print(path)
                print("PATH DONE")
                

        

    def _setup(self):
        print("Starting PathFinderAgent {}...".format(self.name))
        

        replyTemp = spade.Behaviour.ACLTemplate()
        replyTemp.setPerformative("request")
        replyTemp.setOntology("map")
        temp = spade.Behaviour.MessageTemplate(replyTemp)

        rb = self.RequestInformationBehaviour(.1)
        self.addBehaviour(rb, temp)
        
        self.is_setup = True

    def takeDown(self):
        print("Stopping PathFinder agent {}...".format(self.name))
