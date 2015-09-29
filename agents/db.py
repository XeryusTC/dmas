from __future__ import print_function
import spade

from map.map import Map

class DatabaseAgent(spade.Agent.Agent):
    """Agent that keeps track of the map"""
    class StoreDataBehaviour(spade.Behaviour.PeriodicBehaviour):
        def _onTick(self):
            msg = self._receive(False)

            if msg:
                content = eval(msg.getContent())
                pos = content['pos']
                data = content['data']
                self.myAgent.map.update(pos[0], pos[1], data)

    def _setup(self):
        print("Starting DatabaseAgent...")
        self.map = Map(self.width, self.height)

        template = spade.Behaviour.ACLTemplate()
        template.addReceiver(spade.AID.aid("db@127.0.0.1",
            ["xmpp://db@127.0.0.1"]))
        template.setPerformative("inform")
        t = spade.Behaviour.MessageTemplate(template)

        sd = self.StoreDataBehaviour(.1)
        self.addBehaviour(sd, t)
