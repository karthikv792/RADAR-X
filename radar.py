from flask import Flask, render_template, request, jsonify, Response
import json
import requests
import urllib
from planner import Planner
from speak import Speak
from dbHandler import dbHandler
import speech_recognition as sr
import io
from google.cloud import speech
from google.cloud.speech import enums
from google.cloud.speech import types
app = Flask(__name__)
planner = Planner()
speech1 = Speak()
dbCaller = dbHandler()
recognizer = sr.Recognizer()
#dbCaller.initializeDatabase()

@app.route("/")
def index(exp=0, s=speech1.getSpeechText('INTRO'),gs='Extinguish Big Fire at BYENG'):
    planner.definePlanningProblem(gs)
    a = planner.getActionNames()
    g = ['Extinguish Big Fire At Byeng']#, 'Extinguish Small Fire At Byeng']
    if not a:
        # o = planner.getExcuses()
        # s = speech1.getSpeechText('INVALID_STATE')
        # lm = []
        pass
    else:
        o = planner.getOrderedObservations()
        lm = planner.getLandmarks()
    resc = planner.getImpResources()
    return render_template('index.html', plan=o, actions=a,goals=g, canAskForExplanations=exp, script=s,landmarks=lm,resources=resc)
def getPresentPlan(request):
    """
    Example 'plan' : [
    {"name":"address_media firechief","x":0,"y":0,"width":12,"height":1},
    {"name":"address_media firechief","x":0,"y":3,"width":12,"height":1}
    ]
    """
    seq = {}
    plan = json.loads(dict(request.form)['plan'])
    for act in plan:
        # We assume that only one action occurs at a time
        # TODO: Update code if we want to allow options for
        # two simultaneous actions (choices)
        seq[ act["y"] ] = act["name"]
    print ("\n======\n{0}\n======\n".format(seq))
    return seq

@app.route("/updateModels", methods=['GET','POST'])
def updateModels():
    planner.reconcileModels( dict(request.form) )
    return index(s=speech1.getSpeechText('MODEL_UPDATED'))

@app.route("/updateGoals", methods=['GET','POST'])
def updateGoals():
    d = dict(request.form)
    print("=================")
    print(d['option'])
    print("=================")
    return index(s=speech1.getSpeechText('GOAL_SELECTED'),gs=d['option'])

@app.route("/generateAlternative", methods=['GET','POST'])
def getOptimalPlan():
    planner.getSuggestedPlan({})
    return index(s=speech1.getSpeechText('OPTIMAL_PLAN'))


@app.route("/foil",methods=['GET','POST'])
def foil():
    plan = getPresentPlan(request)
    acts = [x.strip('() \n') for x in plan.values()]
    a = planner.getActionNames()
    return render_template('foil.html',prePlan=acts,actions=a)

@app.route("/foilrec",methods=['GET','POST'])
def foilrec():
    with open('service-account-file.json') as file:
        GOOGLE_CREDENTIALS = file.read()
    url = request.files['audio_data']
    print("GOT DATA")

    # url=url[5:]
    # print(url)
    # rawWav = requests.get(url,verify=False)

    wavFile = sr.AudioFile(url)
    with wavFile as source:
        #recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.record(source)
    text = recognizer.recognize_google_cloud(audio, credentials_json=GOOGLE_CREDENTIALS)
    print(text)
    return request.url



@app.route("/validate", methods=['GET', 'POST'])
def validate():
    planner.savePlan()
    planner.getValidatedPlan(getPresentPlan(request))
    return index(s=speech1.getSpeechText('VALIDATE_PLAN'))

@app.route("/getPlanExplanation", methods=['GET', 'POST'])
def getExplanationForPlan():
    exp = planner.getExplanations()
    return jsonify(exp)

@app.route("/updateResources", methods=['GET','POST'])
def updateResources():
    d = dict(request.form)
    dbCaller.updateResourcesInTable( d['resourceName'], d['tableName'], d['rowId'], d['presentState'])
    return index(s=speech1.getSpeechText('RESOURCE_UPDATED'))

@app.route("/foil",methods=['GET','POST'])
def foil():
    planner.loadPlan()
    acts = planner.getOrderedObservations()
    a = planner.getActionNames()
    return render_template('foil.html',plan=acts,actions=a)

@app.route("/suggest", methods=['GET', 'POST'])
def suggest():
    planner.savePlan()
    planner.getSuggestedPlan(getPresentPlan(request))
    return index(1, speech1.getSpeechText('SUGGEST_PLAN'))

@app.route("/fix", methods=['GET', 'POST'])
def fix():
    planner.savePlan()
    planner.getSuggestedPlan(getPresentPlan(request), True)
    return index(s=speech1.getSpeechText('CORRECT_PLAN'))

@app.route("/undo", methods=['GET', 'POST'])
def undo():
    planner.loadPlan()
    return index(s="")

@app.route("/readFireStationResources", methods=['GET', 'POST'])
def readFireStationResource():
    data = dbCaller.getFireStationsData()
    data = dbCaller.getUIReadyData( data, 'fire_stations_actual' )
    return jsonify( {"data" : data} )

@app.route("/readHospitalResources", methods=['GET', 'POST'])
def readHospitalResource():
    data = dbCaller.getHospitalData()
    data = dbCaller.getUIReadyData( data, 'hospitals' )
    return jsonify( {"data" : data} )

@app.route("/readPoliceStationResources", methods=['GET', 'POST'])
def readPoliceStationResource():
    data = dbCaller.getPoliceStationData()
    data = dbCaller.getUIReadyData( data, 'police_stations' )
    return jsonify( {"data" : data} )


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5080, ssl_context=('cert.pem','key.pem'))
