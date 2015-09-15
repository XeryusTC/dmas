import numpy as np
import cv2

class GNUI(object):

	def __init__(self, w, h):
		self.size = 10

		self.width = (w * 2 + 1) * self.size
		self.height = (h * 2 + 1) * self.size

		cv2.namedWindow("GNUI")

	def update(self, map, agents):
		screen = np.zeros((self.height, self.width, 3), 'uint8')
		
		screen = self.drawMap(screen, map)

		cv2.imshow("GNUI", screen)

		cv2.waitKey(30000)

	def drawMap(self, screen, map):
		idx = 0

		for row in map:
			jdx = 0
			for item in row:
				if item:
					cv2.rectangle(screen, (jdx * self.size,idx * self.size), (jdx * self.size + self.size, idx * self.size + self.size), (255,0,0), -1)
				else:
					pass
				jdx += 1

			idx += 1

		return screen

	def drawAgent(x,y):
		pass