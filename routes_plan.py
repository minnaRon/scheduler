from app import app
from flask import redirect, render_template, request, session
import users, group, entries, datetime, events, subfunctions

@app.route("/plan", methods=["GET","POST"])
def plan():
    users.require_role(2)
    user_id = session["user_id"]
    event_list = events.get_events(user_id)
    today1 = datetime.date.today()

    if request.method == "GET":
        group_info = group.get_info()
        week, all_event_entries = entries.get_week(user_id, 2)
        all_own_entries = subfunctions.change_list_to_dict(5, all_event_entries)
        friends_plans = subfunctions.add_weekday(entries.friends_planning(user_id))
        today = datetime.date.today().strftime("%d.%m.")
        days = {0:"SU", 1:"MA", 2:"TI", 3:"KE", 4:"TO", 5:"PE", 6:"LA"}
        days_i = subfunctions.change_days_dow_to_i_dict(days, today1)
        return render_template("plan.html", friends_plans=friends_plans, all_own_entries=all_own_entries, days_i=days_i, group_info=group_info, events=event_list, days=days, week=week, all_event_entries=all_event_entries, today=today)

    if request.method == "POST":
        users.check_csrf()
        event_indices = request.form.getlist("event_index")
        start_times = request.form.getlist("time_start")
        finish_times = request.form.getlist("time_finish")
        days_list = request.form.getlist("day")
        if len(event_indices) == len(start_times) and len(start_times) == len(finish_times):
            day_i = int(float(days_list[0]))
            dow = int(datetime.datetime.strftime(today1 + datetime.timedelta(days=day_i + 7), "%w"))
            times_of_own_entries_for_day = entries.get_times_of_own_entries_for_day(user_id, dow, day_i + 7)
            new_entry_times_list = subfunctions.get_new_entry_times(start_times, finish_times)
            if not new_entry_times_list:
                return render_template("error.html", message="Tapahtumien lisäys ei onnistunut, tarkista valitsemasi ajat, aikojen valitsemisessa oli puutteita")
            if times_of_own_entries_for_day or len(new_entry_times_list) > 1:
                if subfunctions.check_times_many(times_of_own_entries_for_day, new_entry_times_list) != "ok":
                    return render_template("error.html", message=subfunctions.check_times_many(times_of_own_entries_for_day, new_entry_times_list))
            elif new_entry_times_list[0][0] >= new_entry_times_list[0][1]:
                    return render_template("error.html", message="Antamasi ajat olivat samat tai alkuaika oli suurempi kuin loppuaika, tarkista ajat ja tallenna uudelleen")
            for entry in new_entry_times_list:
                date = today1 + datetime.timedelta(days=7+int(float(days_list[entry[2]])))
                index = entry[2]
                if entries.add_entry(date, user_id, event_list[int(event_indices[index])][0], start_times[index], finish_times[index]) < 0:
                    return render_template("error.html", message="Tapahtumien lisäys ei onnistunut, tallenna uudelleen")
            return redirect("/plan")
        return render_template("error.html", message="Tapahtumien lisäys ei onnistunut, tarkista valitsemasi ajat ja tallenna uudelleen")

@app.route("/plan/entry_cancel", methods=["POST"])
def cancel_plan_entry():
    users.check_csrf()
    users.require_role(2)
    entry_id = request.form["entry_id"]
    if entries.delete_own_entry(entry_id, session["user_id"]):
        return redirect("/plan")
    return render_template("error.html", message="Ilmoittautumisesi peruminen ei onnistunut")

@app.route("/plan/pick", methods=["POST"])
def add_plan_pick():
    users.check_csrf()
    users.require_role(2)
    user_id = session["user_id"]
    entry = request.form["plan_pick"].split(",")
    entry_date = datetime.datetime.strptime(request.form["date"], "%Y-%m-%d").date()
    start_time = datetime.datetime.strptime(entry[0][2:-1], "%H:%M").time()
    finish_time = datetime.datetime.strptime(entry[5][2:-2], "%H:%M").time()
    dow = int(float(entry[2]))
    day_i = entry_date - datetime.date.today()
    times_of_own_entries_for_day = entries.get_times_of_own_entries_for_day(user_id, dow, day_i.days)
    if times_of_own_entries_for_day:
        if subfunctions.check_times_one(times_of_own_entries_for_day, (start_time, finish_time)) != "ok":
            return render_template("error.html", message=subfunctions.check_times_one(times_of_own_entries_for_day, (start_time, finish_time)))
    if entries.add_entry(entry_date, user_id, entry[4], start_time, finish_time) > 0:
        return redirect("/plan")
    return render_template("error.html", message="Osallistumisesi lisäys ei onnistunut")
