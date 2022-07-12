import json
from requests import get, post
from quart import Quart, render_template, request

app = Quart(__name__)


@app.route("/")
async def home():
    return await render_template("home.html.jinja")


@app.route("/setup", methods=["GET", "POST"])
async def setup():
    if request.method == "GET":
        url = request.args.get('url')
        osd2f_status_request = get(url + "survey")
        return await render_template("setup.html.jinja",
                                     osd2f=json.loads(osd2f_status_request.text),
                                     url=url,
                                     done=False)
    else:
        data = await request.form
        osd2f_setup = post(data['url'] + "survey",
                           json={
                               "project_title": data['project_title'],
                               "admin_email": data['admin_email'],
                               "js_callback_after_upload": data['js_callback_after_upload'],
                               "upload": json.loads(data['upload_config']),
                               "content": {
                                   "blocks": [],
                                   "upload_box": {
                                       "explanation": [],
                                       "header": "hier steht die überschrift"
                                   },
                                   "donate_button": data['donate_button'],
                                   "empty_selection": "nix drin",
                                   "file_indicator_text": "",
                                   "inspect_button": "",
                                   "preview_component": {
                                       "entries_in_file_text": "",
                                       "explanation": [],
                                       "next_file_button": "",
                                       "previous_file_button": "vorherige datei",
                                       "remove_rows_button": "löschen",
                                       "search_box_placeholder": "",
                                       "search_prompt": "",
                                       "title": ""
                                   },
                                   "consent_popup": {
                                       "accept_button": data['accept_button'],
                                       "decline_button": data['decline_button'],
                                       "end_text": "",
                                       "lead": "",
                                       "points": [],
                                       "title": ""
                                   },
                                   "processing_text": "",
                                   "thanks_text": ""
                               }
                           })
        with open('osd2f_config.json', 'w') as file:
            file.write(osd2f_setup.text)
        return await render_template("setup.html.jinja",
                                     osd2f=json.loads(osd2f_setup.text),
                                     done=True)


@app.route("/survey")
async def survey():
    with open('osd2f_config.json', mode='r') as file:
        osd2f_config_raw = file.read()
    osd2f_config = json.loads(osd2f_config_raw)
    return await render_template("survey.html.jinja",
                                 osd2f=osd2f_config)


app.run(host='127.0.0.1',
        port=5001,
        debug=True)
