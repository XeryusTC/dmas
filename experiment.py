from subprocess import Popen
from time import sleep
from time import time
import mothership
import supervisor

def runExperiment(widht, height, searchers, rescuers):
    print("=================================")
    print("===    Starting Mothership    ===")
    print("=================================")
    spadeProc = Popen("runspade.py")
    sleep(5)
    motherstart = time()
    mothership.main(width, height, range(searchers), range(rescuers))
    motherend = time()
    spadeProc.terminate()
    sleep(5)

    print("=================================")
    print("===    Starting Supervisor    ===")
    print("=================================")
    spadeProc = Popen("runspade.py")
    sleep(5)
    superstart = time()
    supervisor.main(width, height, range(searchers), range(rescuers))
    superend = time()
    spadeProc.terminate()

    return (motherend - motherstart, superend - superstart)

width = 8
height = 8
searchers = 3
rescuers = 3

try:
    with open('experiment.csv', 'w') as f:
        f.write('supervisor, time, width, height, searchers, rescuers\n')
        for i in range(10):
            (mothertime, supertime) = runExperiment(width, height, searchers, rescuers)
            f.write(', '.join(["mothership", str(mothertime), str(width), 
                str(height), str(searchers), str(rescuers)]))
            f.write('\n')
            f.write(', '.join(["supervisor", str(supertime), str(width), 
                str(height), str(searchers), str(rescuers)]))
            f.write('\n')

except KeyboardInterrupt:
    print("Stopping...")
    spadeProc.kill()
