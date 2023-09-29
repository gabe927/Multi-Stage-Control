import requests
from flask import Flask, request
import sacn
import json
import time
import threading

node_url = "http://192.168.1.56/enter"

data = "univ_principal_01=2&univ_principal_type_01=1&end_of=true"

app = Flask(__name__)

###############
# Node Config #
###############

def build_node_config_packet(portConfig: dict):
    data = ""
    for k, v in portConfig.items():
        data = data + f"univ_principal_0{k}={v}&univ_principal_type_0{k}=1&"
    data += "end_of=true"
    return data

def send_config_to_node(data: str):
    response = requests.post(node_url, data=data)
    print(f"Config sent to node. Status code: {response.status_code}")

@app.route("/port-univ", methods=["GET", "POST"])
def port_config():
    returnMsg = "OK"
    ports = {}

    for i in request.args.items():
        param = i[0]
        param = param.lower()
        param = param.replace("port", "")
        if not param.isnumeric():
            returnMsg = "One or more parameters could not be processed."
            continue
        param = int(param)

        val = i[1]
        if not val.isnumeric():
            returnMsg = "One or more parameters could not be processed."
            continue

        ports.update({param:val})
    
    send_config_to_node(build_node_config_packet(ports))
    return returnMsg

##############
# sACN Scene #
##############

scene = {}
live_data = {}

receiver = sacn.sACNreceiver()
sender = sacn.sACNsender()
receiver.start()
sender.start()
registeredRecvUniverses = []
registeredSendUniverses = []
universe_map = {}

def receiveCallback(packet):
    univ = packet.universe
    dmxData = packet.dmxData
    live_data.update({univ:dmxData})

def sendData():
    try:
        while True:
            for u, d in scene.items():
                sender[u].dmx_data = d
            time.sleep(1)
    except:
        pass

def registerRecvUniverses(universes: list):
    global registeredRecvUniverses
    for i in universes:
        if i not in registeredRecvUniverses:
            receiver.register_listener("universe", receiveCallback, universe=i)
            receiver.join_multicast(i)
            registeredRecvUniverses.append(i)

def registerSendUniverses(universes: list):
    global registeredSendUniverses
    for i in universes:
        if i not in registeredSendUniverses:
            sender.activate_output(i)
            sender[i].multicast = True
            registeredSendUniverses.append(i)

@app.route("/register-universes", methods=["GET", "POST"])
def registerUniversesREST():
    global universe_map
    returnMsg = "OK"
    recv_universes = []
    send_universes = []
    for i in request.args.items():
        param = i[0]
        param = param.lower()
        val = i[1]
        if param in ["ru", "recv_univ", "receive_universe", "receive_universes"]:
            for j in val.split(","):
                recv_universes.append(int(j))
        if param in ["su", "send_univ", "send_universe", "send_universes"]:
            for j in val.split(","):
                send_universes.append(int(j))
    if len(recv_universes) != len(send_universes):
        return "Cannot register. Need to have same number of send and recive universes!"
    universe_map = {}
    for i in range(len(recv_universes)):
        universe_map.update({recv_universes[i]:send_universes[i]})
    registerRecvUniverses(recv_universes)
    registerSendUniverses(send_universes)

    return f"Universe Map: {json.dumps(universe_map)}"

@app.route("/record-scene", methods=["GET", "POST"])
def recordScene():
    global scene
    scene = {}
    for u, d in live_data.items():
            scene.update({universe_map[int(u)]:d})
    return f"Recorded Scene Data:\n{json.dumps(scene, indent=4)}"

sender_thread = threading.Thread(target=sendData)
sender_thread.start()

app.run()