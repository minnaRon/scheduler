from app import app
from flask import redirect, render_template, request, session
import users, group, entries, datetime, messages, events, subfunctions

@app.route("/calendar", methods=["GET","POST"])
def calendar():
    users.require_role(2)
    user_id = session["user_id"]
    today = datetime.date.today()

    if request.method == "GET":
        week, all_event_entries = entries.get_week(user_id, 1)
        all_own_entries = subfunctions.change_list_to_dict(5, all_event_entries)
        message_list =  messages.get_newest(25, user_id)
        group_info = group.get_info()
        days = {0:"SU", 1:"MA", 2:"TI", 3:"KE", 4:"TO", 5:"PE", 6:"LA"}
        days_i = subfunctions.change_days_dow_to_i_dict(days, today)
        return render_template("calendar.html", messages=message_list, days_i=days_i, all_own_entries=all_own_entries, group_info=group_info, days=days, week=week, all_event_entries=all_event_entries, today=today)
    
    if request.method == "POST":
        users.check_csrf()
        entry = request.form["calendar_pick"].split(",")
        entry_date = datetime.datetime.strptime(request.form["date"], "%Y-%m-%d").date()
        start_time = datetime.datetime.strptime(entry[0][2:-1], "%H:%M").time()
        finish_time = datetime.datetime.strptime(entry[5][2:-2], "%H:%M").time()
        dow = int(float(entry[2]))
        day_i = entry_date - today
        times_of_own_entries_for_day = entries.get_times_of_own_entries_for_day(user_id, dow, day_i.days)
        if times_of_own_entries_for_day:
            if subfunctions.check_times_one(times_of_own_entries_for_day, (start_time, finish_time)) != "ok":
                return render_template("error.html", message=subfunctions.check_times_one(times_of_own_entries_for_day, (start_time, finish_time)))
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
        return render_template("error.html", message="Viestin lähetys ei onnistunut, yritä uudelleen")

@app.route("/entry/<day>", methods=["GET","POST"])
def entry(day):
    users.require_role(2)
    day_i = int(float(day))
    user_id = session["user_id"]
    today = datetime.datetime.today()
    date = today + datetime.timedelta(days=day_i)

    if request.method == "GET":
        participants = entries.get_participants(session["user_id"], date)
        event_list = events.get_events(user_id)
        days = {0:"SU", 1:"MA", 2:"TI", 3:"KE", 4:"TO", 5:"PE", 6:"LA"}
        days_i = subfunctions.change_days_dow_to_i_dict(days, today)
        return render_template("entry.html", participants=participants, events=event_list, days_i=days_i, date=date, day=day_i)
    
    if request.method == "POST":
        users.check_csrf()
        if request.form["time1"] and request.form["time2"] and request.form["time1"] < request.form["time2"]:
            dow = int(datetime.datetime.strftime(date,"%w"))
            times_of_own_entries_for_day = entries.get_times_of_own_entries_for_day(user_id, dow, day_i)
            start_time = datetime.datetime.strptime(request.form["time1"], "%H:%M").time()
            finish_time = datetime.datetime.strptime(request.form["time2"], "%H:%M").time()
            if times_of_own_entries_for_day:
                if subfunctions.check_times_one(times_of_own_entries_for_day, (start_time, finish_time)) != "ok":
                    return render_template("error.html", message=subfunctions.check_times_one(times_of_own_entries_for_day, (start_time, finish_time)))
        else:
            return render_template("error.html", message="Osallistumisesi lisäys ei onnistunut, alku tai loppuaika oli virheellinen tai puuttui. Tarkista ajat ja tallenna uudelleen")
        extras = 0 if not request.form["extra_participants"] else request.form["extra_participants"]

        entry_id = entries.add_entry_with_extras(date, user_id, request.form["event_id"], start_time, finish_time, extras)
        if entry_id == -1:
            return render_template("error.html", message="Osallistumisesi lisäys ei onnistunut, tallenna uudelleen")

        if request.form["comment"]:
            content = request.form["comment"].strip()
            if len(content) > 0:
                if not messages.add_entry_comment(user_id, entry_id, request.form["event_id"], " [" + request.form["event_id"] + "] " + content):
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
