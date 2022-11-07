from . import survey
from app import log
from flask import request, render_template
from app.application import survey as msurvey
import sys, json, html


@survey.route('/survey/start/<string:period>/<string:targetgroup>/<string:schoolcode>', methods=['GET'])
def start(period, targetgroup, schoolcode):
    try:
        data = msurvey.prepare_survey(period, targetgroup, schoolcode)
        return render_template('/survey/survey_formio.html', data=data)
    except Exception as e:
        log.error(f'{sys._getframe().f_code.co_name}: {e}')
        return html.escape(str(e))

@survey.route('/survey/save', methods=['POST'])
def save():
    try:
        data = json.loads(request.data)
        data = msurvey.save_survey(data)
        return json.dumps({"status": True, "data": data})
    except Exception as e:
        log.error(f'{sys._getframe().f_code.co_name}: {e}')
        return json.dumps({"status": False, "data": html.escape(str(e))})


@survey.route('/survey/done', methods=['GET'])
def done():
    try:
        # data = json.loads(request.data)
        data = msurvey.survey_done(request.values)
        return render_template('/survey/survey_formio.html', data=data)
    except Exception as e:
        log.error(f'{sys._getframe().f_code.co_name}: {e}')
        return json.dumps({"status": False, "data": html.escape(str(e))})


