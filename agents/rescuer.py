from __future__ import print_function
import random
import spade

from maze import maze
from util import backtrace

class RescueAgent(spade.Agent.Agent):
    """Rescuer Agent"""

    class RegisterServicesBehav(spade.Behaviour.OneShotBehaviour):
        def _process(self):
            res = self.myAgent.registerService(self.myAgent.dad)
            print(self.myAgent.name, "services registered:", res)


    class RescueBehav(spade.Behaviour.PeriodicBehaviour):
        @backtrace
        def _onTick(self):
            if not self.myAgent.occupied:
                msg = self._receive(False)
                if msg:
                    content = msg.getContent().split(' ', 1)
                    if content[0] == 'rescue':
                        print(self.myAgent.name, "Going to rescue", self.myAgent.path)
                        self.myAgent.ret = [self.myAgent.position]
                        self.myAgent.target = eval(content[1])
                        self.myAgent.toggleOccupied()
                        self.myAgent.isrescueing = False
                        reply = msg.createReply()
                        reply.setPerformative(msg.REQUEST)
                        cont = {'start': self.myAgent.position,
                                'end': self.myAgent.target}
                        reply.setContent("route {}".format(cont))
                        self.myAgent.send(reply)
                    elif content[0] == 'target':
                        self.myAgent.toggleOccupied()
                        target = eval(content[1])
                        self.myAgent.target = target
                        print(self.myAgent.name, "should rescue", target)
                        msg = spade.ACLMessage.ACLMessage()
                        msg.setPerformative(msg.REQUEST)
                        msg.setOntology("map")
                        msg.addReceiver(self.myAgent.pf)
                        msg.setContent({'open': [target], 'ontology': 'rescuer',
                            'location': self.myAgent.position})
                        self.myAgent.send(msg)
            # We are waiting for a path
            if self.myAgent.occupied and not self.myAgent.isrescueing:
                msg = self._receive(False)
                # Receive path messages in supervisor mode
                if msg:
                    content = msg.getContent().split(' ', 1)
                    if content[0] == 'route':
                        path = eval(content[1])
                        if len(path):
                            self.myAgent.path = eval(content[1])
                            print(self.myAgent.name, "Going to rescue", self.myAgent.path)
                            self.myAgent.ret = [self.myAgent.position]
                            self.myAgent.isrescueing = True
                        else:
                            print(self.myAgent.name, "no path to target",
                                    self.myAgent.target)
                            # No path to target, notify supervisor
                            reply = spade.ACLMessage.ACLMessage()
                            reply.setOntology("rescuer")
                            reply.addReceiver(self.myAgent.sv)
                            reply.setContent('nopath {}'.format(self.myAgent.target))
                            self.myAgent.send(reply)
                            self.myAgent.toggleOccupied()
                            self.myAgent.isrescueing = False
                            self.myAgent.carrying = False
                    elif content[0] == 'target':
                        print(self.myAgent.name,
                            "got duplicate target, respond with nopath to reset")
                        reply = spade.ACLMessage.ACLMessage()
                        reply.setOntology("rescuer")
                        reply.addReceiver(self.myAgent.sv)
                        reply.setContent('nopath {}'.format(eval(content[1])))
                        self.myAgent.send(reply)
                    else:
                        print(self.myAgent.name, "GOT UNKOWN MESSAGE", msg.getContent())
            elif self.myAgent.isrescueing: # go rescue
                if len(self.myAgent.path) > 0:
                    dst = self.myAgent.path[0]
                    self.myAgent.path = self.myAgent.path[1:]
                    self.myAgent.move(dst[0], dst[1])
                    if dst == (1, 1):
                        # we returned a target to the entry
                        self.myAgent.ret = []
                        self.myAgent.toggleOccupied()
                        self.myAgent.carrying = False
                        self.myAgent.isrescueing = False
                    else:
                        self.myAgent.ret = [dst] + self.myAgent.ret
                else:
                    print(self.myAgent.name, "arrived at target")
                    print(self.myAgent.name, self.myAgent.ret)
                    # we are at the target, turn arround, notify mothership

                    self.myAgent.maze.rescue(self.myAgent.position)

                    self.myAgent.path = self.myAgent.ret
                    self.myAgent.carrying = True
                    msg = spade.ACLMessage.ACLMessage()
                    msg.setPerformative("inform")
                    msg.setOntology("rescuer")
                    if self.myAgent.sv:
                        msg.addReceiver(self.myAgent.sv)
                    else:
                        msg.addReceiver(self.myAgent.ship)
                    msg.setContent("carrying {}".format(self.myAgent.position))
                    self.myAgent.send(msg)
                    # when under supervisor, update the database
                    if self.myAgent.sv:
                        dbmsg = spade.ACLMessage.ACLMessage()
                        dbmsg.setPerformative("inform")
                        dbmsg.addReceiver(spade.AID.aid("db@127.0.0.1",
                            ["xmpp://db@127.0.0.1"]))
                        dbmsg.setContent({'pos': self.myAgent.position,
                            'data': maze.PATH_VISITED})
                        self.myAgent.send(dbmsg)


    class DiscoverServicesBehav(spade.Behaviour.PeriodicBehaviour):
        def onStart(self):
            print(self.myAgent.name, "Starting service discovery")

        @backtrace
        def _onTick(self):
            # Discover mothership
            sd = spade.DF.ServiceDescription()
            sd.setType("mothership")
            dad = spade.DF.DfAgentDescription()
            dad.addService(sd)

            result = self.myAgent.searchService(dad)
            if len(result):
                print(self.myAgent.name, "switching to mothership")
                self.myAgent.ship = result[0].getAID()
            else:
                # Discover supervisor and other agents
                sd = spade.DF.ServiceDescription()
                sd.setType("supervisor")
                dad = spade.DF.DfAgentDescription()
                dad.addService(sd)
                result = self.myAgent.searchService(dad)
                if len(result):
                    print(self.myAgent.name, "switching to supervisor")
                    self.myAgent.sv = result[0].getAID()

                    # Discover pathfinders
                    sd = spade.DF.ServiceDescription()
                    sd.setType("pathfinder")
                    dad = spade.DF.DfAgentDescription()
                    dad.addService(sd)
                    result = self.myAgent.searchService(dad)
                    if len(result):
                        self.myAgent.pf = result[0].getAID()

            # Stop this behaviour if we found something
            if self.myAgent.ship or (self.myAgent.sv and self.myAgent.pf):
                print(self.myAgent.name, "removing discovery behaviour")
                self.myAgent.removeBehaviour(self)
                self.myAgent.toggleOccupied()


    def _setup(self):
        print("Starting Rescuer agent {}...".format(self.name))
        self.is_setup = False

        self.ship = False
        self.sv   = False
        self.pf   = False
        self.path = []
        self.ret = []
        self.carrying = False
        self.x = 1
        self.y = 1
        self.isrescueing = False

        self.occupied = True
        self.sd = spade.DF.ServiceDescription()
        self.sd.setType("rescue")
        self.sd.setName("occupied")
        self.dad = spade.DF.DfAgentDescription()
        self.dad.addService(self.sd)
        self.dad.setAID(self.getAID())

        self.addBehaviour(self.RegisterServicesBehav(), None)

        temp = spade.Behaviour.ACLTemplate()
        temp.setOntology("rescuer")
        rt = spade.Behaviour.MessageTemplate(temp)

        rb = self.RescueBehav(1)
        self.addBehaviour(rb, rt)

        self.addBehaviour(self.DiscoverServicesBehav(.1), None)

        self.is_setup = True

    def takeDown(self):
        print("Stopping Rescuer agent {}...".format(self.name))

    def toggleOccupied(self):
        self.deregisterService(self.dad)
        self.occupied = not self.occupied
        if self.occupied:
            self.sd.setName("occupied")
        else:
            self.sd.setName("available")
        self.dad.updateService(self.sd)

        res = self.registerService(self.dad)
        print(self.name, "toggled to:", self.occupied, res)

    def move(self, x, y):
        self.x = x
        self.y = y

    def setMaze(self, m):
        self.maze = m

    @property
    def position(self):
        return (self.x, self.y)


if __name__ == '__main__':
    import time
    import traceback

    ra = RescueAgent("rescue@127.0.0.1", "secret")
    ra.start()

    try:
        while 1: time.sleep(1)
    except KeyboardInterrupt:
        pass
    except:
        print(traceback.format_exc())

    ra.stop()
