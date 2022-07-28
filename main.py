import json
from requests import get, post, ConnectionError
from requests.models import MissingSchema
from quart import Quart, render_template, request

app = Quart(__name__)


@app.route("/")
async def home():
    return await render_template("home.html.jinja",
                                 error=False,
                                 error_title="",
                                 error_message="")


@app.route("/setup", methods=["GET", "POST"])
async def setup():
    if request.method == "GET":
        url = request.args.get('url')
        try:
            osd2f_status_request = get(url + "survey")
        except MissingSchema:
            return await render_template("home.html.jinja",
                                         error=True,
                                         error_title="URL missing",
                                         error_message="Enter a base URL first.")
        except ConnectionError:
            return await render_template("home.html.jinja",
                                         error=True,
                                         error_title="OSD2F not found",
                                         error_message="Make sure the URL is correct, that it is only the base URL (e.g., https://data-donation.my-domain.de/), and that OSD2F runs in 'Survey' mode.")

        return await render_template("setup.html.jinja",
                                     osd2f=json.loads(osd2f_status_request.text),
                                     osd2f_prettified=json.dumps(json.loads(osd2f_status_request.text), ensure_ascii=False, indent=4),
                                     url=url,
                                     successfully_done=False,
                                     defaults={})
    else:
        data = await request.form
        try:
            data_upload = json.loads(data['upload_config'])
        except json.JSONDecodeError as error:
            return await render_template("setup.html.jinja",
                                         osd2f={"success": False,
                                                "error": f"Invalid JSON: {str(error)}"},
                                         osd2f_prettified=json.dumps({"success": False,
                                                                      "error": f"Invalid JSON: {str(error)}"}, ensure_ascii=False, indent=4),
                                         url=data['url'],
                                         successfully_done=False,
                                         defaults=data)

        osd2f_setup = post(data['url'] + "survey",
                           json={
                               "token": data['token'],
                               "project_title": data['project_title'],
                               "admin_email": data['admin_email'],
                               "js_callback_after_upload": data['js_callback_after_upload'],
                               "upload": data_upload,
                               "content": {
                                   "blocks": [],
                                   "upload_box": {
                                       "explanation": data['upload_box_explanation'].split('\n'),
                                       "header": data['upload_box_header']
                                   },
                                   "donate_button": data['donate_button'],
                                   "empty_selection": data['empty_selection'],
                                   "file_indicator_text": data['file_indicator_text'],
                                   "inspect_button": data['inspect_button'],
                                   "preview_component": {
                                       "entries_in_file_text": data['preview_component_entries_in_file_text'],
                                       "explanation": data['preview_component_explanation'].split('\n'),
                                       "next_file_button": data['preview_component_next_file_button'],
                                       "previous_file_button": data['preview_component_previous_file_button'],
                                       "remove_rows_button": data['preview_component_remove_rows_button'],
                                       "search_box_placeholder": data['preview_component_search_box_placeholder'],
                                       "search_prompt": data['preview_component_search_prompt'],
                                       "title": data['preview_component_title'],
                                       "file_text": data['preview_file_text'],
                                       "entries_per_page_text": data['preview_entries_per_page_text'],
                                       "today_text": data['preview_today_text'],
                                       "close_text": data['preview_close_text'],
                                       "startdate_text": data['preview_startdate_text'],
                                       "enddate_text": data['preview_enddate_text'],
                                       "no_matches_text": data['preview_no_matches_text'],
                                       "show_all_text": data['preview_show_all_text']
                                   },
                                   "consent_popup": {
                                       "accept_button": data['consent_popup_accept_button'],
                                       "decline_button": data['consent_popup_decline_button'],
                                       "end_text": data['consent_popup_end_text'],
                                       "lead": data['consent_popup_lead'],
                                       "points": data['consent_popup_points'].split('\n'),
                                       "title": data['consent_popup_title']
                                   },
                                   "processing_text": data['processing_text'],
                                   "thanks_text": data['thanks_text']
                               }
                           })
        osd2f_setup_json = json.loads(osd2f_setup.text)
        if osd2f_setup_json['success']:
            with open('osd2f_config.json', 'w') as file:
                file.write(osd2f_setup.text)
            for i in range(len(osd2f_setup_json['head_inclusion'])):
                head_file = osd2f_setup_json['head_inclusion'][i]
                head_file_response = get(head_file)
                head_file_name = head_file.split('/').pop()
                open(head_file_name, 'wb').write(head_file_response.content)
                osd2f_setup_json['head_inclusion'][i] = head_file_name
        return await render_template("setup.html.jinja",
                                     osd2f=osd2f_setup_json,
                                     osd2f_prettified=json.dumps(osd2f_setup_json, ensure_ascii=False, indent=4),
                                     url=data['url'],
                                     successfully_done=osd2f_setup_json['success'],
                                     defaults=data)


@app.route("/survey")
async def survey():
    with open('osd2f_config.json', mode='r') as file:
        osd2f_config_raw = file.read()
    osd2f_config = json.loads(osd2f_config_raw)
    osd2f_config['js_embed'] = osd2f_config['js_embed'].replace(osd2f_config['js_embed_placeholder_surveyid'],
                                                                '42')
    osd2f_config['js_embed'] = osd2f_config['js_embed'].replace(osd2f_config['js_embed_placeholder_libarchivejs'],
                                                                '/static/libarchive.js/worker-bundle.js')
    return await render_template("survey.html.jinja",
                                 osd2f=osd2f_config)


app.run(host='127.0.0.1',
        port=5001,
        debug=True)
