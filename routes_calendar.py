from app import app
from flask import redirect, render_template, request, session
import users, group, entries, datetime, messages, events

@app.route("/calendar", methods=["GET","POST"])
def calendar():
    users.require_role(2)
    username = session["user_name"]
    user_id = session["user_id"]
    today = datetime.date.today()
    week, all_event_entries = entries.get_week(user_id, 1)
    all_own_entries = entries.get_all_own_entries_dict(all_event_entries)
    message_list =  messages.get_newest(25, user_id)
    group_info = group.get_info()
    days = {0:"SU", 1:"MA", 2:"TI", 3:"KE", 4:"TO", 5:"PE", 6:"LA"}
    days_i = entries.change_days_dow_to_i_dict(days, today)

    if request.method == "GET":
        return render_template("calendar.html", messages=message_list, days_i=days_i, all_own_entries=all_own_entries, group_info=group_info, days=days, week=week, all_event_entries=all_event_entries, today=today)
    
    if request.method == "POST":
        users.check_csrf()
        entry = request.form["calendar_pick"].split(",")
        entry_date = datetime.datetime.strptime(request.form["date"], "%Y-%m-%d").date()
        day_i = entry_date - today
        entry_start = datetime.datetime.strptime(entry[0][2:-1], "%H:%M").time()
        entry_finish = datetime.datetime.strptime(entry[5][2:-2], "%H:%M").time()
        if all_own_entries[day_i.days]:
            for earlier_entry in all_own_entries[day_i.days]:
                start = earlier_entry[2]
                end = earlier_entry[3]
                if not (entry_start >= end or entry_finish <= start):
                    return render_template("error.html", message="Aika menee päällekkäin päivän toisen ilmoittautumisesi kanssa, peru ilmoittautumisia tarvittaessa")
        if entries.add_entry(entry_date, session["user_id"], entry[4], entry_start, entry_finish):
            return redirect("/calendar")
        return render_template("error.html", message="Osallistumisesi lisäys ei onnistunut")

@app.route("/calendar_message", methods=["POST"])
def calendar_message():
    users.check_csrf()
    users.require_role(2)
    if len(request.form["comment"].strip()) > 0:
        if messages.add(session["user_id"], request.form["comment"]):
            return redirect("/calendar")
    return render_template("error.html", message="Viestin lisäys ei onnistunut, tarkista viesti")

@app.route("/entry/<day>", methods=["GET","POST"])
def entry(day):
    users.require_role(2)
    day = int(float(day))
    user_id = session["user_id"]
    week, all_event_entries = entries.get_week(user_id, 1)
    all_own_entries = entries.get_all_own_entries_dict(all_event_entries)
    today = datetime.datetime.today()
    date = today + datetime.timedelta(days=day)

    if request.method == "GET":
        participants = entries.get_participants(session["user_id"], date)
        event_list = events.get_events(user_id)
        days = {0:"SU", 1:"MA", 2:"TI", 3:"KE", 4:"TO", 5:"PE", 6:"LA"}
        days_i = entries.change_days_dow_to_i_dict(days, today)
        return render_template("entry.html", participants=participants, events=event_list, days_i=days_i, date=date, day=day)
    
    if request.method == "POST":
        users.check_csrf()
        if request.form["time1"] and request.form["time2"]:
            start_time = datetime.datetime.strptime(request.form["time1"], "%H:%M").time()
            finish_time = datetime.datetime.strptime(request.form["time2"], "%H:%M").time()
        else:
            return render_template("error.html", message="Osallistumisesi lisäys ei onnistunut, tarkista valitsemasi ajat")
        if request.form["extra_participants"]:
            extras = request.form["extra_participants"]
        else:
            extras = 0
        if start_time < finish_time:
            if all_own_entries[day]:
                for earlier_entry in all_own_entries[day]:
                    start = earlier_entry[2]
                    end = earlier_entry[3]
                    if not (start_time >= end or finish_time <= start):
                        return render_template("error.html", message="Aika menee päällekkäin päivän toisen ilmoittautumisesi kanssa, peru ilmoittautumisia tarvittaessa")
            entry_id = entries.add_entry_with_extras(date, user_id, request.form["event_id"], start_time, finish_time, extras)
            if entry_id == -1:
                return render_template("error.html", message="Osallistumisesi lisäys ei onnistunut, tarkista valitsemasi ajat")
        else:
            return render_template("error.html", message="Osallistumisesi lisäys ei onnistunut, tarkista valitsemasi ajat")
        if request.form["comment"]:
            content = request.form["comment"].strip()
            if len(content) > 0:
                content = " [" + request.form["event_id"] + "] " + content
                if not messages.add_entry_comment(user_id, entry_id, request.form["event_id"], content):
                    return render_template("error.html", message="Viestisi lähetys ei onnistunut, tarkista viestin sisältö")
        return redirect("/calendar")

@app.route("/calendar/entry_cancel", methods=["POST"])
def cancel_entry():
    users.check_csrf()
    users.require_role(2)
    entry_id = request.form["entry_id"]
    if entries.delete_own_entry(entry_id, session["user_id"]):
        return redirect("/calendar")
    return render_template("error.html", message="Ilmoittautumisesi peruminen ei onnistunut")
