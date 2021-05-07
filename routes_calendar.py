from app import app
from flask import redirect, render_template, request, session
import users, group, entries, datetime, messages, events, subfunctions

@app.route("/calendar", methods=["GET","POST"])
def calendar():
    users.require_role(2)
    user_id = session["user_id"]

    if request.method == "GET":
        week, all_event_entries = entries.get_week(user_id, 1)
        all_own_entries = subfunctions.change_list_to_dict(5, all_event_entries)
        message_list =  messages.get_newest(25, user_id)
        group_info = group.get_info()
        today = datetime.date.today()
        days = {0:"SU", 1:"MA", 2:"TI", 3:"KE", 4:"TO", 5:"PE", 6:"LA"}
        days_i = subfunctions.change_days_dow_to_i_dict(days, today)
        return render_template("calendar.html", messages=message_list, days_i=days_i, all_own_entries=all_own_entries, group_info=group_info, days=days, week=week, all_event_entries=all_event_entries, today=today)
    
    if request.method == "POST":
        users.check_csrf()
        entry = request.form["calendar_pick"].split(",")
        entry_date = datetime.datetime.strptime(request.form["date"], "%Y-%m-%d").date()
        start_time = entry[0][2:-1]
        finish_time = entry[5][2:-2]
        times_of_own_entries_for_week = subfunctions.change_list_to_dict(0, entries.get_times_of_own_entries_for_week(user_id, 1))
        time_check_errors = subfunctions.check_times_dow(times_of_own_entries_for_week, int(datetime.datetime.strftime(entry_date,"%w")), start_time, finish_time)
        if time_check_errors != "ok":
            return render_template("error.html", message=time_check_errors)
        if entries.add_entry(entry_date, user_id, entry[4], start_time, finish_time) > 0:
            return redirect("/calendar")
        return render_template("error.html", message="Osallistumisesi lisäys ei onnistunut")

@app.route("/calendar_message", methods=["POST"])
def calendar_message():
    users.check_csrf()
    users.require_role(2)
    if len(request.form["comment"].strip()) > 0:
        if messages.add(session["user_id"], request.form["comment"]):
            return redirect("/calendar")
        else:
            return render_template("error.html", message="Viestin lähetys ei onnistunut, yritä uudelleen")
    else:
        return render_template("error.html", message="Viesti oli tyhjä, joten sitä ei voinut lähettää")

@app.route("/entry/<day>", methods=["GET","POST"])
def entry(day):
    users.require_role(2)
    day = int(float(day))
    user_id = session["user_id"]
    today = datetime.datetime.today()
    date = today + datetime.timedelta(days=day)

    if request.method == "GET":
        participants = entries.get_participants(session["user_id"], date)
        event_list = events.get_events(user_id)
        days = {0:"SU", 1:"MA", 2:"TI", 3:"KE", 4:"TO", 5:"PE", 6:"LA"}
        days_i = subfunctions.change_days_dow_to_i_dict(days, today)
        return render_template("entry.html", participants=participants, events=event_list, days_i=days_i, date=date, day=day)
    
    if request.method == "POST":
        users.check_csrf()
        times_of_own_entries_for_week = subfunctions.change_list_to_dict(0, entries.get_times_of_own_entries_for_week(user_id, 1))
        if request.form["time1"] and request.form["time2"]:
            start_time = request.form["time1"]
            finish_time = request.form["time2"]
            time_check_errors = subfunctions.check_times_dow(times_of_own_entries_for_week, int(datetime.datetime.strftime(date,"%w")), start_time, finish_time)
            if time_check_errors != "ok":
                return render_template("error.html", message=time_check_errors)
        else:
            return render_template("error.html", message="Osallistumisesi lisäys ei onnistunut, aikojen valinnassa oli puutteita. Tarkista ajat ja tallenna uudelleen")
        if request.form["extra_participants"]:
            extras = request.form["extra_participants"]
        else:
            extras = 0
        entry_id = entries.add_entry_with_extras(date, user_id, request.form["event_id"], start_time, finish_time, extras)
        if entry_id == -1:
            return render_template("error.html", message="Osallistumisesi lisäys ei onnistunut, tarkista tiedot ja tallenna uudelleen")
        if request.form["comment"]:
            content = request.form["comment"].strip()
            if len(content) > 0:
                content = " [" + request.form["event_id"] + "] " + content
                if not messages.add_entry_comment(user_id, entry_id, request.form["event_id"], content):
                    return render_template("error.html", message="Viestisi lähetys ei onnistunut, tarkista tiedot ja lähetä uudelleen")
        return redirect("/calendar")

@app.route("/calendar/entry_cancel", methods=["POST"])
def cancel_entry():
    users.check_csrf()
    users.require_role(2)
    entry_id = request.form["entry_id"]
    if entries.delete_own_entry(entry_id, session["user_id"]):
        return redirect("/calendar")
    return render_template("error.html", message="Ilmoittautumisesi peruminen ei onnistunut")
