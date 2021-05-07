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
        times_of_own_entries_for_week = subfunctions.change_list_to_dict(0, entries.get_times_of_own_entries_for_week(user_id, 2))
        if len(event_indices) == len(start_times) and len(start_times) == len(finish_times):
            for i in range(len(event_indices)-1):
                if start_times[i] == "" and finish_times[i] == "":
                    continue
                date = today1 + datetime.timedelta(days=7+int(float(days_list[i])))
                time_check_errors = subfunctions.check_times_dow(times_of_own_entries_for_week, int(datetime.datetime.strftime(date,"%w")), start_times[i], finish_times[i])
                if time_check_errors != "ok":
                    return render_template("error.html", message=time_check_errors)
                else:
                    entry_id = entries.add_entry(date, user_id, event_list[int(event_indices[i])][0], start_times[i], finish_times[i])
                    if entry_id == -1:
                        return render_template("error.html", message="Kaikkien tapahtumien lisäys ei onnistunut, tarkista valitsemasi ajat")
        else:
            return render_template("error.html", message="Tapahtumien lisäys ei onnistunut, tarkista valitsemasi ajat")
        return redirect("/plan")

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
    entry = request.form["plan_pick"].split(",")
    entry_date = datetime.datetime.strptime(request.form["date"], "%Y-%m-%d").date()
    times_of_own_entries_for_week = subfunctions.change_list_to_dict(0, entries.get_times_of_own_entries_for_week(session["user_id"], 2))
    start_time = entry[0][2:-1]
    finish_time = entry[5][2:-2]
    time_errors = subfunctions.check_times_dow(times_of_own_entries_for_week, int(datetime.datetime.strftime(entry_date,"%w")), start_time, finish_time)
    if time_errors != "ok":
        return render_template("error.html", message=time_errors)
    if entries.add_entry(entry_date, session["user_id"], entry[4], start_time, finish_time) > 0:
        return redirect("/plan")
    return render_template("error.html", message="Osallistumisesi lisäys ei onnistunut")
