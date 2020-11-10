import RPi.GPIO as GPIO
import json
import os
import datetime
from flask import Flask, jsonify, request


app = Flask(__name__)
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)


#define actuators GPIOs
ch = [26, 19, 13, 6] #GPIO26, GPIO19, GPIO13 and GPIO06
cooler = 5 #GPIO5
pw = [21, 20, 16, 12, 7, 8, 25, 24, 23, 18]

#set the duty cicle for PWM
dutyCicle = 50

# Define led pins as output
GPIO.setup(ch[0], GPIO.OUT)
GPIO.setup(ch[1], GPIO.OUT)
GPIO.setup(ch[2], GPIO.OUT)
GPIO.setup(ch[3], GPIO.OUT)
GPIO.setup(cooler, GPIO.OUT)
for powerPlug in pw:
    GPIO.setup(powerPlug, GPIO.OUT)


#get the time value and format
now = datetime.datetime.now()
timeString = now.strftime("%H")


@app.route("/v1/lighting/api/settings/power", methods=['GET'])
def getPowerSettings():
    templateData = {}
    
    with open('./../LightingManager/powerPlugConfig.json') as json_file:
        templateData = json.load(json_file)
    
    return jsonify(templateData)


@app.route("/v1/lighting/api/status/light", methods=['GET'])
def lightStatus():
    channelStatus = []
    for x in range(0, len(ch)):
        channelStatus.append(GPIO.input(ch[x]))
    
    coolerStatus = GPIO.input(cooler)
    
    templateData = {
              'ch1': channelStatus[0],
              'ch2': channelStatus[1],
              'ch3': channelStatus[2],
              'ch4': channelStatus[3],
              'cooler': coolerStatus
        }
    
    return jsonify(templateData)


@app.route("/v1/lighting/api/status/power", methods=['GET'])
def powerStatus():
    powerStatus = []
    for x in range(0, len(pw)):
        powerStatus.append(GPIO.input(pw[x]))
    
    templateData = {
              'pw1': powerStatus[0],
              'pw2': powerStatus[1],
              'pw3': powerStatus[2],
              'pw4': powerStatus[3],
              'pw5': powerStatus[4],
              'pw6': powerStatus[5],
              'pw7': powerStatus[6],
              'pw8': powerStatus[7],
              'pw9': powerStatus[8],
              'pw10': powerStatus[9]
        }
    
    return jsonify(templateData)


@app.route("/v1/lighting/api/settings/light", methods=['GET'])
def getLightSettings():
    templateData = {}

    with open('./../LightingManager/lightConfig.json') as json_file:
        templateData = json.load(json_file)
    
    return jsonify(templateData)



@app.route('/v1/lighting/api/settings/light', methods=['POST'])
def setLightSettings():
    body = request.get_json()
    
    with open('./../LightingManager/lightConfig.json', 'w') as file:
            json.dump(body, file, indent=2)
            
    templateData = {"status": "Light configuration updated."}
    
    for conf in body['settings']:
        if timeString == conf['time']:
            signCH = []
            for x in range(0, len(ch)):
                actuator="ch%d" % (x)
                signCH.append(GPIO.PWM(ch[x],dutyCicle))
                signCH[x].start(conf[actuator])
                
    if ch[0] == GPIO.LOW and ch[1] == GPIO.LOW and ch[2] == GPIO.LOW and ch[3] == GPIO.LOW:
        GPIO.output(cooler, GPIO.LOW)
    else:
        GPIO.output(cooler, GPIO.HIGH)
        
    return jsonify(templateData)



@app.route('/v1/lighting/api/settings/power', methods=['POST'])
def setPowerSettings():
    body = request.get_json()
    
    with open('./../LightingManager/powerPlugConfig.json', 'w') as file:
            json.dump(body, file, indent=2)
    
    for conf in body['settings']:
        if timeString == conf['time']: 
            for x in range(0, len(pw)):
                actuator="pw%d" % (x)
                GPIO.output(pw[x], conf[actuator])
            
    templateData = {"status": "Power configuration updated."}
    return jsonify(templateData)

if __name__ == '__main__':
    app.run(debug=True, port=80, host='0.0.0.0')
