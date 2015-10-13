import numpy as np

class Map(object):

    def __init__(self, w, h):
        self.width = (w * 2 + 1)
        self.height = (h * 2 + 1)

        self.map = []
        for i in xrange(0, self.height):
            self.map.append(([0] * self.width))

    def update(self, x, y, data):
        #TOP
        self.map[y - 1][x] = data[0]
        #TOPRIGHT
        self.map[y - 1][x + 1] = data[1]
        #RIGHT
        self.map[y][x + 1] = data[2]
        #BOTTOMRIGHT
        self.map[y + 1][x + 1] = data[3]
        #BOTTOM
        self.map[y + 1][x] = data[4]
        #BOTTOMLEFT
        self.map[y + 1][x - 1] = data[5]
        #LEFT
        self.map[y][x - 1] = data[6]
        #TOPLEFT
        self.map[y - 1][x - 1] = data[7]

    def updatePosition(self, x, y, value=2):
        self.map[y][x] = value

    def getData(self, x, y):
        return [self.map[y + dy][x + dx]
                for (dy, dx) in [(-1, 0), (-1, 1), (0, 1), (1,1),(1,0),(1, -1),
                                    (0,-1), (-1, -1)]]

    def getMap(self):
        return self.map
