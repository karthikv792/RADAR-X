from flask import Flask, render_template, request, jsonify
import json
from planner import Planner
from speak import Speak
app = Flask(__name__)
planner = Planner()
speech = Speak()

@app.route("/")
def index(exp=0, s=speech.getSpeechText('INTRO'),gs='Extinguish Big Fire at BYENG'):
    planner.definePlanningProblem(gs)
    a = planner.getActionNames()
    g = ['Extinguish Big Fire At Byeng']#, 'Extinguish Small Fire At Byeng']
    if not a:
        # o = planner.getExcuses()
        # s = speech.getSpeechText('INVALID_STATE')
        # lm = []
        pass
    else:
        o = planner.getOrderedObservations()
        print(o)
        lm = planner.getLandmarks()
    resc = planner.getImpResources()
    return render_template('index.html', plan=o, actions=a,goals=g, canAskForExplanations=exp, script=s)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5080)
