from flask import redirect, render_template, request, url_for, jsonify
import json
from . import guest
from app import log

# @guest.route('/guest/<string:code>/<string:name>/<string:time>', methods=['POST', 'GET'])
@guest.route('/guest', methods=['POST', 'GET'])
def show():
    print(request.args)
    config = {
        'check_server_endpoint': 'guest.server_ajax_endpoint',
        'intro_video': "https://www.youtube.com/embed/YrLk4vdY28Q",
        'code': 'abcde',
        'first_name': 'manuel',
        'last_name': 'borowski',
        'email': 'emmanuel.borowski@gmail.com'
    }
    return render_template('guest/guest.html', config=config)



@guest.route('/guest/action/<string:jds>', methods=['GET', 'POST'])
def server_ajax_endpoint(jds):
    try:
        jd = json.loads(jds)
        if jd['action'] == 'get_timeout_1':
            return jsonify({"status": True})
    except Exception as e:
        log.error(f'execute action: {jd}')
        return jsonify({"status": False})

    return jsonify({"status": True})



