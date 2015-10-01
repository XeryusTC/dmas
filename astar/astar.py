import numpy as np
from heapq import *

class Astar(object):

	def __init__(self):
		print "Created Astar"
		pass


	def heuristic(self, a, b):
		return (b[0] - a[0]) ** 2 + (b[1] - a[1]) ** 2


	def convertPath(self, path):
		return [(step[1], step[0]) for step in path][::-1]

	def getPath(self, array, start, goal):

		start = (start[1], start[0])
		goal = (goal[1], goal[0])
		array = np.array(eval(array))

		array[array == 0] = 1
		array[array == 3] = 0
		array[array == 2] = 0

		neighbors = [(0,1),(0,-1),(1,0),(-1,0)]


		close_set = set()
		came_from = {}
		gscore = {start:0}
		fscore = {start:self.heuristic(start, goal)}
		oheap = []

		heappush(oheap, (fscore[start], start))
		
		while oheap:

			current = heappop(oheap)[1]

			if current == goal:
				data = []
				while current in came_from:
					data.append(current)
					current = came_from[current]
				
				return self.convertPath(data)

			close_set.add(current)
			for i, j in neighbors:
				neighbor = current[0] + i, current[1] + j 
				tentative_g_score = gscore[current] + self.heuristic(current, neighbor)

				if 0 <= neighbor[0] < array.shape[0]:
					if 0 <= neighbor[1] < array.shape[1]:
						if array[neighbor[0]][neighbor[1]] == 1:
							continue
					else:
						# array bound y walls
						continue
				else:
					# array bound x walls
					continue

				if neighbor in close_set and tentative_g_score >= gscore.get(neighbor, 0):
					continue

				if  tentative_g_score < gscore.get(neighbor, 0) or neighbor not in [i[1]for i in oheap]:
					came_from[neighbor] = current
					gscore[neighbor] = tentative_g_score
					fscore[neighbor] = tentative_g_score + self.heuristic(neighbor, goal)
					heappush(oheap, (fscore[neighbor], neighbor))
		
		return False