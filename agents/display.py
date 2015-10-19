from __future__ import print_function
import spade
import time

from gnui.gnui import GNUI
from util import backtrace

class DisplayAgent(spade.Agent.Agent):
    """Agent that displays the map"""

    class UpdateDisplayBehav(spade.Behaviour.PeriodicBehaviour):
        def onStart(self):
            print("Starting to display the map")

            # request the first instance of the map from the db
            self.myAgent.requestmap()

        @backtrace
        def _onTick(self):
            if self.myAgent.map and self.myAgent.display:
                self.myAgent.display.update(self.myAgent.map, [s.position
                    for s in self.myAgent.agents if s.is_setup])


    class ReceiveMapBehav(spade.Behaviour.EventBehaviour):
        @backtrace
        def _process(self):
            msg = self._receive(False)
            content = msg.getContent().split(" ", 1)
            if content[0] == 'map':
                self.myAgent.map = eval(content[1])

            time.sleep(1)

            self.myAgent.requestmap()


    def _setup(self):
        print("Starting DisplayAgent {}...".format(self.name))
        self.map = False
        self.display = False
        self.agents = []

        replyTemp = spade.Behaviour.ACLTemplate()
        replyTemp.setPerformative("inform")
        replyTemp.setSender(spade.AID.aid("db@127.0.0.1",
            ["xmpp://db@127.0.0.1"]))
        t = spade.Behaviour.MessageTemplate(replyTemp)

        rm = self.ReceiveMapBehav()
        self.addBehaviour(rm, t)

        um = self.UpdateDisplayBehav(.1)
        self.addBehaviour(um, None)

    def requestmap(self):
        msg = spade.ACLMessage.ACLMessage("request")
        msg.setOntology("map")
        msg.addReceiver(spade.AID.aid("db@127.0.0.1",
                ["xmpp://db@127.0.0.1"]))
        msg.setContent("MAP")
        self.send(msg)


if __name__ == "__main__":
    import traceback

    display = GNUI(32, 16)
    da = DisplayAgent("display@127.0.0.1", "secret")
    da.start()
    # need to wait a bit before the display is ready
    time.sleep(.1)
    da.display = display

    try:
        while 1:
            time.sleep(1)
    except KeyboardInterrupt:
        pass
    except:
        traceback.format_exc()

    da.stop()
