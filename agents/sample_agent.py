import spade
import time

class MyAgent(spade.Agent.Agent):
	class MyBehav(spade.Behaviour.Behaviour):
		def onStart(self):
			print "Starting behaviour . . ."
			self.counter = 0

		def _process(self):
			print "Counter:", self.counter
			self.counter = self.counter + 1
			#self.talk()
			#self.sleep()
			name = self.getAgent()
			time.sleep(1)

		def talk(self):
			receiver = spade.AID.aid(name="motherShip@127.0.0.1", 
                                     addresses=["xmpp://motherShip@127.0.0.1.com"])
			
			# Second, build the message
			self.msg = spade.ACLMessage.ACLMessage()  # Instantiate the message
			self.msg.setPerformative("inform")        # Set the "inform" FIPA performative
			self.msg.setOntology("myOntology")        # Set the ontology of the message content
			self.msg.setLanguage("OWL-S")	          # Set the language of the message content
			self.msg.addReceiver(receiver)            # Add the message receiver
			self.msg.setContent("Hello World")        # Set the message content
			
			# Third, send the message with the "send" method of the agent
			self.myAgent.send(self.msg)

		def listen(self):
			self.msg = None
			
			# Blocking receive for 10 seconds
			self.msg = self._receive(True, 10)
			
			# Check wether the message arrived
			if self.msg:
				print "I got a message!"
			else:
				print "I waited but got no message"

		def getAgent(self):
			return self.myAgent.getName()

	def _setup(self):
		print "MyAgent starting . . ."
		b = self.MyBehav()
		self.addBehaviour(b, None)

if __name__ == "__main__":
	a = MyAgent("agent@127.0.0.1", "secret")
	a.start()
