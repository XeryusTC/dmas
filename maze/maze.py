from random import shuffle, randrange, randint

PATH = 0
WALL = 1
PATH_VISITED = 2
TARGET = 3

class Maze(object):

    def __init__(self, w = 16, h = 8, targets = 10):
        self.w = w
        self.h = h
        self.maze = self.make_maze(w, h)
        self._addTargets(10)
        self._addOpenings(50)

    def _addTargets(self, targets):
        for i in xrange(0, targets):
            
            searching = True
            while searching:
                y = randint(0,self.h * 2)
                x = randint(0,self.w * 2)

                if self.maze[y][x] == PATH:
                    self.maze[y][x] = TARGET
                    searching = False

    def _addOpenings(self, openings):
        for i in xrange(0, openings):
            
            searching = True
            while searching:
                y = randint(1,(self.h * 2) - 1)
                x = randint(1,(self.w * 2) - 1)

                if self.maze[y][x] == WALL:
                    self.maze[y][x] = PATH
                    searching = False
            
            




    def getData(self, x, y):
        data = []
        #TOP
        data.append(self.maze[y - 1][x])
        #TOPRIGHT
        data.append(self.maze[y - 1][x + 1])
        #RIGHT
        data.append(self.maze[y][x + 1])
        #BOTTOMRIGHT
        data.append(self.maze[y + 1][x + 1])
        #BOTTOM
        data.append(self.maze[y + 1][x])
        #BOTTOMLEFT
        data.append(self.maze[y + 1][x - 1])
        #LEFT
        data.append(self.maze[y][x - 1])
        #TOPLEFT
        data.append(self.maze[y - 1][x - 1])

        data = [PATH_VISITED if x == PATH  else x for x in data]

        return data

    def getMaze(self):
        return self.maze

    def make_maze(self, w, h):
        vis = [[0] * w + [1] for _ in range(h)] + [[1] * (w + 1)]
        ver = [["10"] * w + ['1'] for _ in range(h)] + [[]]
        hor = [["11"] * w + ['1'] for _ in range(h + 1)]

        def walk(x, y):
            vis[y][x] = 1

            d = [(x - 1, y), (x, y + 1), (x + 1, y), (x, y - 1)]
            shuffle(d)
            for (xx, yy) in d:
                if vis[yy][xx]: continue
                if xx == x: hor[max(y, yy)][x] = "10"
                if yy == y: ver[y][max(x, xx)] = "00"
                walk(xx, yy)

        walk(randrange(w), randrange(h))
        map = []
        for (a, b) in zip(hor, ver):
            map.append([int(x) for x  in list(''.join(a))])
            map.append([int(x) for x  in list(''.join(b))])

        del map[-1]

        #map[1][3] = 1
        #map[2][1] = 1

        return map
