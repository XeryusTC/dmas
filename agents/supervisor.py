from __future__ import print_function
import spade
import time

from util import backtrace

class SupervisorAgent(spade.Agent.Agent):
    is_setup = False

    class SearcherManager(spade.Behaviour.PeriodicBehaviour):
        moves = [(0, -1), (0, 1), (-1, 0), (1, 0)]

        @backtrace
        def _onTick(self):
            msg = self._receive(False)


    class RescueManager(spade.Behaviour.PeriodicBehaviour):
        @backtrace
        def _onTick(self):
            msg = self._receive(False)


    class RegisterServicesBehav(spade.Behaviour.OneShotBehaviour):
        def onSetup(self):
            print("Registering supervisor services")


    def _setup(self):
        print("Starting supervisor {}".format(self.name))
        self.visited = set()
        self.open    = set()
        self.targets = set()


        searchTemp = spade.Behaviour.ACLTemplate()
        searchTemp.setOntology("searcher")
        st = spade.Behaviour.MessageTemplate(searchTemp)
        sm = self.SearcherManager(.1)
        self.addBehaviour(sm, st)

        rescueTemp = spade.Behaviour.ACLTemplate()
        rescueTemp.setOntology("rescuer")
        rt = spade.Behaviour.MessageTemplate(rescueTemp)
        rm = self.RescueManager(.1)
        self.addBehaviour(rm, rt)

        self.is_setup = True

    def register_services(self):
        self.dad = spade.DF.DfAgentDescription()
        sd = spade.DF.ServiceDescription()
        sd.setType("supervisor")
        sd.setName("supervisor")
        self.dad.addService(sd)

        self.dad.setAID(self.getAID())
        res = self.registerService(self.dad)
        print("Supervisor registered:", str(res))
