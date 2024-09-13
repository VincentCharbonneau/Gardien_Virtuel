import winsound

def makeBeep(frequency=750, duration=200, nBeep=3):
    for i in range(nBeep):
        winsound.Beep(frequency, duration)
