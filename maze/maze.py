from random import shuffle, randrange

class Maze(object):

    def __init__(self, w = 16, h = 8):
        self.maze = self.make_maze(w, h)

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

        print map
        
        return map