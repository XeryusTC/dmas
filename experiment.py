from subprocess import Popen
from time import sleep
from time import time
import mothership
import supervisor

WIDTH = 10
HEIGHT = 10

print("=================================")
print("===    Starting Mothership    ===")
print("=================================")
spadeProc = Popen("runspade.py")
sleep(2)
motherstart = time()
mothership.main(WIDTH, HEIGHT, range(3), range(3))
motherend = time()
spadeProc.terminate()
print("=================================")
print("===    Starting Supervisor    ===")
print("=================================")
spadeProc = Popen("runspade.py")
sleep(2)
supertime = time()
supervisor.main(WIDTH, HEIGHT, range(3), range(3))
superend = time()
spadeProc.terminate()

print("Mothertime", motherend - motherstart)
print("Supertime", superend - superstart)
