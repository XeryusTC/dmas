import random
import spade

class RandomWalkBehav(spade.Behaviour.PeriodicBehaviour):
    def onStart(self):
        print("Starting random walk")

    def _onTick(self):
        # Create possible directions to move in
        new = [ (self.myAgent.x,   self.myAgent.y-1),
                (self.myAgent.x,   self.myAgent.y+1),
                (self.myAgent.x-1, self.myAgent.y),
                (self.myAgent.x+1, self.myAgent.y) ]
        new = [ n for n in new if n in self.myAgent.open ]
        if len(new):
            new = random.choice(new)
        else:
            new = random.choice(list(self.myAgent.open))
        self.myAgent.move(new[0], new[1])

        # Update the map
        self.myAgent.sense()
        print('visited: ', self.myAgent.visited)
        print('open:    ', self.myAgent.open)