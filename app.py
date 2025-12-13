import flask
import datetime
import calendar
import json
import os

app = flask.Flask(__name__)
JSON_FILE = 'events.json'

def load_events():
    if os.path.exists(JSON_FILE):
        with open(JSON_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_events(events):
    with open(JSON_FILE, 'w') as f:
        json.dump(events, f, indent=4)

@app.route('/')
def index():
    now = datetime.date.today()
    return flask.redirect(flask.url_for('calendar_view', year=now.year, month=now.month))

@app.route('/calendar/<int:year>/<int:month>')
def calendar_view(year, month):
    events = load_events()
    cal_matrix = calendar.monthcalendar(year, month)
    today = datetime.date.today()

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

    return flask.render_template('index.html',
                                 year=year,
                                 month=month,
                                 month_name=calendar.month_name[month],
                                 cal_matrix=cal_matrix,
                                 today=today,
                                 events=events,
                                 prev_year=prev_year,
                                 prev_month=prev_month,
                                 next_year=next_year,
                                 next_month=next_month,
                                 calendar=calendar)

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

if __name__ == '__main__':
    app.run(debug=True)