from app import app
from flask import redirect, render_template, request, session
import users, group, entries, datetime, events

@app.route("/plan", methods=["GET","POST"])
def plan():
    users.require_role(2)
    username = session["user_name"]
    user_id = session["user_id"]
    group_info = group.get_info()
    event_list = events.get_events(user_id)
    friends_plans = entries.friends_planning(user_id)
    friends_plans = add_weekday(friends_plans)
    week, all_event_entries = entries.get_week(user_id, 2)
    all_own_entries = entries.get_all_own_entries_dict(all_event_entries)
    today = datetime.date.today().strftime("%d.%m.")
    today1 = datetime.date.today()
    days = {0:"SU", 1:"MA", 2:"TI", 3:"KE", 4:"TO", 5:"PE", 6:"LA"}
    days_i = entries.change_days_dow_to_i_dict(days, today1)

    if request.method == "GET":
        return render_template("plan.html", friends_plans=friends_plans, all_own_entries=all_own_entries, days_i=days_i, group_info=group_info, events=event_list, days=days, week=week, all_event_entries=all_event_entries, today=today)

    if request.method == "POST":
        users.check_csrf()
        event_indices = request.form.getlist("event_index")
        start_times = request.form.getlist("time_start")
        finish_times = request.form.getlist("time_finish")
        days = request.form.getlist("day")
        if len(event_indices) == len(start_times) and len(start_times) == len(finish_times):
            for i in range(len(event_indices)-1):
                if start_times[i] < finish_times[i]:
                    print("-- start, finish",start_times[i], finish_times[i])
                    if all_own_entries[int(days[i])]:
                        for earlier_entry in all_own_entries[int(days[i])]:
                            start = earlier_entry[2]
                            end = earlier_entry[3]
                            start_time = datetime.datetime.strptime(start_times[i], "%H:%M").time()
                            finish_time = datetime.datetime.strptime(finish_times[i], "%H:%M").time()
                            if not (start_time >= end or finish_time <= start):
                                return render_template("error.html", message="Aika menee päällekkäin päivän toisen ilmoittautumisesi kanssa, peru ilmoittautumisia tarvittaessa")
                    entries.add_entry(datetime.datetime.today() + datetime.timedelta(days=7+int(float(days[i]))), user_id, event_list[int(event_indices[i])][0], start_times[i], finish_times[i])
                elif start_times[i] == "" and finish_times[i] =="":
                    continue
                else:
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
    #-- ['05:00', 'tapahtuma12', 4.0, 3, 12, '10:00']
    entry = request.form["plan_pick"].split(",")
    #--- 2021-04-22
    entry_date = datetime.datetime.strptime(request.form["date"], "%Y-%m-%d").date()
    print("---entry, ..date", entry, entry_date)
    today = datetime.date.today()
    day_i = entry_date - today
    entry_start = datetime.datetime.strptime(entry[0][2:-1], "%H:%M").time()
    entry_finish = datetime.datetime.strptime(entry[5][2:-2], "%H:%M").time()
    week, all_event_entries = entries.get_week(session["user_id"], 2)
    all_own_entries = entries.get_all_own_entries_dict(all_event_entries)
    if all_own_entries[day_i.days -7]:
        for earlier_entry in all_own_entries[day_i.days -7]:
            start = earlier_entry[2]
            end = earlier_entry[3]
            if not (entry_start >= end or entry_finish <= start):
                return render_template("error.html", message="Aika menee päällekkäin päivän toisen ilmoittautumisesi kanssa, peru ilmoittautumisia tarvittaessa")
    if entries.add_entry(entry_date, session["user_id"], entry[4], entry_start, entry_finish):
        return redirect("/plan")
    return render_template("error.html", message="Osallistumisesi lisäys ei onnistunut")

def add_weekday(friends_plans:list) -> list:
    days = {0:"SU", 1:"MA", 2:"TI", 3:"KE", 4:"TO", 5:"PE", 6:"LA"}
    friends_plans_w = []
    for entry in friends_plans:
        print("---entry", entry)
        entry = list(entry)
        entry[4] = days[entry[4]]
        friends_plans_w.append(entry)
    return friends_plans_w