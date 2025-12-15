import flask
import datetime
import calendar
import json
import os
import pytz
from operator import itemgetter

app = flask.Flask(__name__)
JSON_FILE = 'events.json'

# Pacific Time zone
pacific_tz = pytz.timezone('America/Los_Angeles')

def load_events():
    if os.path.exists(JSON_FILE):
        with open(JSON_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_events(events):
    with open(JSON_FILE, 'w') as f:
        json.dump(events, f, indent=4)

# Helper: sorted list of all events with index for deletion
def get_sorted_events():
    events = load_events()
    event_list = []
    for date_str, event_items in events.items():
        year, month, day = map(int, date_str.split('-'))
        event_date = datetime.date(year, month, day)
        for idx, item in enumerate(event_items):
            event_list.append({
                'date_str': date_str,
                'date': event_date,
                'desc': item['desc'],
                'time': item.get('time', ''),
                'color': item['color'],
                'index': idx
            })
    event_list.sort(key=itemgetter('date'))
    return event_list

@app.route('/')
def home():
    return flask.render_template('base.html',
                                 active_tab='home',
                                 content_template='home.html')

@app.route('/calendar')
def calendar_redirect():
    now = datetime.datetime.now(pacific_tz).date()
    return flask.redirect(flask.url_for('calendar_view', year=now.year, month=now.month))

@app.route('/calendar/<int:year>/<int:month>')
def calendar_view(year, month):
    events = load_events()
    cal_matrix = calendar.monthcalendar(year, month)
    today = datetime.datetime.now(pacific_tz).date()

    # Navigation
    prev_month = month - 1
    prev_year = year
    if prev_month == 0:
        prev_month = 12
        prev_year -= 1

    next_month = month + 1
    next_year = year
    if next_month == 13:
        next_month = 1
        next_year += 1

    return flask.render_template('base.html',
                                 active_tab='calendar',
                                 content_template='calendar.html',
                                 year=year,
                                 month=month,
                                 month_name=calendar.month_name[month],
                                 cal_matrix=cal_matrix,
                                 today=today,
                                 events=events,
                                 prev_year=prev_year,
                                 prev_month=prev_month,
                                 next_year=next_year,
                                 next_month=next_month)

@app.route('/events')
def events_list():
    sorted_events = get_sorted_events()
    return flask.render_template('base.html',
                                 active_tab='events',
                                 content_template='events.html',
                                 events=sorted_events)

@app.route('/add_event', methods=['POST'])
def add_event():
    date = flask.request.form['date']
    desc = flask.request.form['description'].strip()
    time = flask.request.form.get('time', '').strip()
    color = flask.request.form['color']

    if desc:
        events = load_events()
        if date not in events:
            events[date] = []
        events[date].append({"desc": desc, "time": time, "color": color})
        save_events(events)

    year, month, _ = map(int, date.split('-'))
    return flask.redirect(flask.url_for('calendar_view', year=year, month=month))

@app.route('/delete_event', methods=['POST'])
def delete_event():
    date = flask.request.form['date']
    index = int(flask.request.form['index'])

    events = load_events()
    if date in events and 0 <= index < len(events[date]):
        events[date].pop(index)
        if not events[date]:
            del events[date]
        save_events(events)

    year, month, _ = map(int, date.split('-'))
    return flask.redirect(flask.url_for('calendar_view', year=year, month=month))

@app.route('/delete_event_from_list', methods=['POST'])
def delete_event_from_list():
    date = flask.request.form['date']
    index = int(flask.request.form['index'])

    events_dict = load_events()
    if date in events_dict and 0 <= index < len(events_dict[date]):
        events_dict[date].pop(index)
        if not events_dict[date]:
            del events_dict[date]
        save_events(events_dict)

    return flask.redirect(flask.url_for('events_list'))

if __name__ == '__main__':
    app.run(debug=True)