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
                        self.myAgent.path = eval(content[1])
                        print(self.myAgent.name, "Going to rescue", self.myAgent.path)
                        self.myAgent.ret = [self.myAgent.position]
                        self.myAgent.toggleOccupied()
                        self.myAgent.isrescueing = True
                    elif content[0] == 'target':
                        self.myAgent.toggleOccupied()
                        target = eval(content[1])
                        planner = random.choice(self.myAgent.pf)
                        print(self.myAgent.name, "should rescue", target)
                        msg = spade.ACLMessage.ACLMessage()
                        msg.setPerformative(msg.REQUEST)
                        msg.setOntology("map")
                        msg.addReceiver(planner)
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
                        self.myAgent.path = eval(content[1])
                        print(self.myAgent.name, "Going to rescue", self.myAgent.path)
                        self.myAgent.ret = [self.myAgent.position]
                        self.myAgent.isrescueing = True
                    else:
                        print(self.myAgent.name, msg.getContent())
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
                    print(self.myAgent.ret)
                    # we are at the target, turn arround, notify mothership
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
                        self.myAgent.pf = [pf.getAID() for pf in result]

            # Stop this behaviour if we found something
            if self.myAgent.ship or (self.myAgent.sv and self.myAgent.pf):
                print(self.myAgent.name, "removing discovery behaviour")
                self.myAgent.removeBehaviour(self)


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

        self.occupied = False
        self.sd = spade.DF.ServiceDescription()
        self.sd.setType("rescue")
        self.sd.setName("available")
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
