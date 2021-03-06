from __future__ import print_function
import spade

from map.map import Map
from util import backtrace

class DatabaseAgent(spade.Agent.Agent):
    """Agent that keeps track of the map"""
    is_setup = False

    class StoreDataBehaviour(spade.Behaviour.PeriodicBehaviour):
        @backtrace
        def _onTick(self):
            msg = self._receive(False)

            if msg:
                perf = msg.getPerformative()

                if perf == "inform" and not msg.getContent().startswith("<rdf"):
                    content = eval(msg.getContent())
                    pos = content['pos']
                    data = content['data']
                    if isinstance(data, list):
                        self.myAgent.map.update(pos[0], pos[1], data)
                    else:
                        self.myAgent.map.updatePosition(pos[0], pos[1], data)

    class RequestInformationBehaviour(spade.Behaviour.PeriodicBehaviour):
        @backtrace
        def _onTick(self):

            msg = None
            msg = self._receive(False)
            if msg:
                data = None
                if msg.getContent() == "MAP":
                    data = self.myAgent.map.getMap()
                else:
                    content = eval(msg.getContent())
                    data = self.myAgent.map.getData(content['x'], content['y'])
                rep = msg.createReply()
                rep.setPerformative("inform")
                rep.setContent("map {}".format(data))
                self.myAgent.send(rep)


    class RegisterServicesBehav(spade.Behaviour.OneShotBehaviour):
        @backtrace
        def _process(self):
            self.myAgent.register_services()


    @backtrace
    def _setup(self):
        print("Starting DatabaseAgent {}...".format(self.name))
        self.map = Map(self.width, self.height)

        # Register services
        self.addBehaviour(self.RegisterServicesBehav(), None)

        template = spade.Behaviour.ACLTemplate()
        template.addReceiver(spade.AID.aid("db@127.0.0.1",
            ["xmpp://db@127.0.0.1"]))
        template.setPerformative("inform")
        t = spade.Behaviour.MessageTemplate(template)

        sd = self.StoreDataBehaviour(.1)
        self.addBehaviour(sd, t)

        replyTemp = spade.Behaviour.ACLTemplate()
        replyTemp.setPerformative("request")
        temp = spade.Behaviour.MessageTemplate(replyTemp)

        rb = self.RequestInformationBehaviour(.1)
        self.addBehaviour(rb, temp)

        self.is_setup = True

    def takeDown(self):
        print("Stopping database agent {}...".format(self.name))

    def register_services(self):
        self.dad = spade.DF.DfAgentDescription()
        self.sd = spade.DF.ServiceDescription()
        self.sd.setType("database")
        self.sd.setName("standalone")
        self.dad.addService(self.sd)
        self.dad.setAID(self.getAID())
        res = self.registerService(self.dad)
        print(self.name, "services registered:", res)


def main():
    import traceback
    import sys
    import time

    if len(sys.argv) < 3:
        print("Please give the width and height of the map (in that order)")
        sys.exit(1)

    db = DatabaseAgent("db@127.0.0.1", "secret")
    db.start()
    db.width = int(sys.argv[1])
    db.height = int(sys.argv[2])

    try:
        while 1: time.sleep(1)
    except KeyboardInterrupt:
        pass
    except:
        print(traceback.format_exc())

    db.stop()

if __name__ == '__main__':
    main()
