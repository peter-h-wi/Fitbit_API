from flask import Flask, jsonify
from datetime import date, timedelta, datetime
import requests

app = Flask(__name__)
myheader = {'Authorization': 'Bearer not_valid_token_for_security'}


@app.route("/heartrate/last", methods=["GET"])
def get_heart_rate():
    # Return the most recent heartrate.
    dayinput = date.today()
    myurl = "https://api.fitbit.com/1/user/-/activities/heart/date/{}/1d.json".format(
        dayinput)
    resp = requests.get(myurl, headers=myheader).json()
    activity_dataset = resp["activities-heart-intraday"]["dataset"]

    while (len(activity_dataset) == 0):
        # if there is no data on that day, check the previous days.
        dayinput -= timedelta(days=1)
        myurl = "https://api.fitbit.com/1/user/-/activities/heart/date/{}/1d.json".format(
            dayinput)
        resp = requests.get(myurl, headers=myheader).json()
        activity_dataset = resp["activities-heart-intraday"]["dataset"]

    recent = activity_dataset[-1]
    # retrieve heartrate, timeoffset (min)
    heartrate = recent["value"]
    timeoffset = datetime.now() - datetime.combine(dayinput, datetime.strptime(
        recent["time"], "%H:%M:%S").time())
    ret = {"heart-rate": heartrate, "time offset": timeoffset.seconds//60}
    return jsonify(ret)


@app.route("/steps/last", methods=["GET"])
def get_steps():
    # Return the most recent step.
    dayinput = date.today()
    myurl = "https://api.fitbit.com/1/user/-/activities/steps/date/today/1d.json"
    resp = requests.get(myurl, headers=myheader).json()
    activity_step = resp["activities-steps"]
    timeoffset = resp["activities-steps-intraday"]["datasetInterval"]
    myurl = "https://api.fitbit.com/1/user/-/activities/distance/date/today/1d.json"
    resp = requests.get(myurl, headers=myheader).json()
    activity_distance = resp["activities-distance"]

    while (len(activity_step) == 0 or len(activity_distance) == 0):
        # if there is no data on that day, check the previous days.
        dayinput -= timedelta(days=1)
        myurl = "https://api.fitbit.com/1/user/-/activities/steps/date/{}/1d.json".format(
            dayinput)
        resp = requests.get(myurl, headers=myheader).json()
        activity_step = resp["activities-steps"]
        myurl = "https://api.fitbit.com/1/user/-/activities/distance/date/{}/1d.json".format(
            dayinput)
        resp = requests.get(myurl, headers=myheader).json()
        activity_distance = resp["activities-distance"]

    timeoffset = datetime.now() - datetime.combine(dayinput, datetime.min.time())
    ret = {"step-count": activity_step[-1]["value"],
           "distance": activity_distance[-1]["value"], "time offset": timeoffset.seconds//60}
    return jsonify(ret)


@app.route("/sleep/<date_input>", methods=["GET"])
def get_sleep(date_input):
    myurl = "https://api.fitbit.com/1.2/user/-/sleep/date/{}.json".format(
        date_input)
    resp = requests.get(myurl, headers=myheader).json()
    ret = {}

    if len(resp["sleep"]) > 0:
        sleep = resp["sleep"][0]["levels"]["summary"]
        for key in sleep:
            ret[key] = sleep[key]["minutes"]
    return ret


@app.route("/activity/<date_input>", methods=["GET"])
def get_activeness(date_input):
    # Return the activeness.
    myurl = "https://api.fitbit.com/1/user/-/activities/date/{}.json".format(
        date_input)

    resp = requests.get(myurl, headers=myheader).json()
    summary = resp["summary"]

    sedentary = summary["sedentaryMinutes"]
    lightly_active = summary["lightlyActiveMinutes"]
    fairly_active = summary["fairlyActiveMinutes"]
    very_active = summary["veryActiveMinutes"]

    ret = {"very-active": very_active, "fairly-active": fairly_active,
           "lightly-active": lightly_active, "sedentary": sedentary}
    return jsonify(ret)


if __name__ == '__main__':
    app.run(debug=True)
