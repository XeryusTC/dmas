import numpy as np
import cv2

from maze import maze

class GNUI(object):

	def __init__(self, w, h):
		self.size = 10

		self.width = (w * 2 + 1) * self.size
		self.height = (h * 2 + 1) * self.size

		cv2.namedWindow("GNUI")

	def update(self, map, agents):
		screen = np.zeros((self.height, self.width, 3), 'uint8')

		screen = self.drawMap(screen, map)

		screen = self.drawAgents(screen, agents)

		cv2.imshow("GNUI", screen)

		cv2.waitKey(20)

	def drawMap(self, screen, map):
		idx = 0

		for row in map:
			jdx = 0
			for item in row:
				#WALL
				if item == maze.WALL:
					cv2.rectangle(screen, (jdx * self.size,idx * self.size), ((jdx * self.size) + self.size - 1, (idx * self.size) + self.size - 1), (255,0,0), -1)
				#PATH
				elif item == maze.PATH_VISITED:
					cv2.rectangle(screen, (jdx * self.size,idx * self.size), ((jdx * self.size) + self.size - 1, (idx * self.size) + self.size - 1), (0,255,0), -1)
				jdx += 1

			idx += 1

		return screen

	def drawAgents(self, screen, agents):
		for agent in agents:
			y, x = agent
			cv2.rectangle(screen, (y * self.size,x * self.size), (y * self.size + self.size - 1, x * self.size + self.size - 1), (0,0,255), -1)

		return screen
