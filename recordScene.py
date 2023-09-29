import sacn
import time
import json
import sys

scene = {}

receiver = sacn.sACNreceiver()

receiverUniverses = []

def recordCallback(packet):
    univ = packet.universe
    dmxData = packet.dmxData
    scene.update({univ:dmxData})
    print(scene)
    receiverUniverses.remove(univ)
    receiver.leave_multicast(univ)
    if len(receiverUniverses) == 0:
        receiver.remove_listener(receiverUniverses)
        # receiver.stop()

def recordScene(universes: list):
    print(universes)
    global receiverUniverses
    receiverUniverses = universes
    for i in universes:
        receiver.register_listener("universe", recordCallback, universe=i)
        receiver.join_multicast(i)
    print("sACN Receiver Started")

if __name__ == "__main__":

    universes = []
    for i in sys.argv[1].split(","):
        universes.append(int(i))

    recordScene(universes)
    receiver.start()

    time.sleep(1)

    f = open("scene.txt", "w")
    f.write(json.dumps(scene, indent=4))
    f.close()
    receiver.stop()