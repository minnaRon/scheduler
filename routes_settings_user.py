from app import app
from flask import redirect, render_template, request, session
import users, entries, datetime, events, friends, subfunctions

@app.route("/settings")
def settings():
    users.require_role(2)
    user_id = session["user_id"]
    events_with_own_level = events.get_all_events_for_user(user_id)
    own_weekly_entries = entries.get_weekly_entries_for_user(user_id)
    friends_list = friends.get_friends(user_id)
    friend_requests = friends.get_friends_open_requests(user_id)
    friend_requests_own = friends.get_own_requests(user_id)
    weekdays = {0:"SU", 1:"MA", 2:"TI", 3:"KE", 4:"TO", 5:"PE", 6:"LA"}
    user_info = users.get_user_info(user_id)
    if session["user_role"] == 1 or session["user_role"] == 0:
        all_events = events.get_all_events()
        return render_template("settings.html", all_events=all_events, friend_requests_own=friend_requests_own, user_info=user_info, days=weekdays, events_with_own_level=events_with_own_level, own_weekly_entries= own_weekly_entries, friends=friends_list, friend_requests=friend_requests)
    return render_template("settings.html", friend_requests_own=friend_requests_own, user_info=user_info,  days=weekdays, events_with_own_level=events_with_own_level, own_weekly_entries= own_weekly_entries, friends=friends_list, friend_requests=friend_requests)

@app.route("/settings/change_user_name", methods=["POST"])
def change_name():
    users.check_csrf()
    users.require_role(2)
    user_id = session["user_id"]  
    changed_name = request.form["name"]
    if changed_name:
        if subfunctions.check_name(changed_name, user_id) != "ok":
            return render_template("error.html", message=subfunctions.check_name(changed_name, user_id))
        if not users.change_name(user_id, changed_name):
            return render_template("error.html", message="Nimen vaihtaminen ei onnistunut")
    return redirect("/settings")

@app.route("/settings/change_contact_info", methods=["POST"])
def change_contact_info():
    users.check_csrf()
    users.require_role(2)
    user_id = session["user_id"]
    changed_contact_info = request.form["contact_info"]
    if not users.change_contact_info(user_id, changed_contact_info):
        return render_template("error.html", message="Yhteystietojen p??ivitt??minen ei onnistunut")
    return redirect("/settings")

@app.route("/settings/change_password", methods=["POST"])
def change_password():
    users.check_csrf()
    users.require_role(2)
    user_id = session["user_id"]
    changing_password = [request.form["old_password"], request.form["new_password1"], request.form["new_password2"]]
    if not users.check_password(user_id, changing_password[0]):
        return render_template("error.html", message="Vanha salasana meni v????rin tai oli tyhj??, tarkista salasana")
    if subfunctions.check_password(changing_password[1], changing_password[2]) != "ok":
            return render_template("error.html", message=subfunctions.check_password(changing_password[1],changing_password[2]))
    if not users.change_password(user_id, changing_password[1]):
        return render_template("error.html", message="Uuden salasanan rekister??inti ei onnistunut")
    return redirect("/settings")
    
@app.route("/settings/weekly_entries", methods=["POST"])
def weekly_entries():
    users.check_csrf()
    users.require_role(2)
    user_id = session["user_id"]
    if request.form["weekly_time_start"] and request.form["weekly_time_end"] and request.form["weekly_time_start"] < request.form["weekly_time_end"]:
        start_time = datetime.datetime.strptime(request.form["weekly_time_start"], "%H:%M").time()
        finish_time = datetime.datetime.strptime(request.form["weekly_time_end"], "%H:%M").time()
        dow = int(request.form["weekly_dow"])
        day_i = subfunctions.match_day_to_dict_week7i(dow)
        times_of_own_entries_for_week1_day = entries.get_times_of_own_entries_for_day(user_id, dow, day_i)
        times_of_own_entries_for_week2_day = entries.get_times_of_own_entries_for_day(user_id, dow, day_i+7)
        if times_of_own_entries_for_week1_day:
            if subfunctions.check_times_one(times_of_own_entries_for_week1_day, (start_time, finish_time)) != "ok":
                return render_template("error.html", message=subfunctions.check_times_one(times_of_own_entries_for_week1_day, (start_time, finish_time)))
        if times_of_own_entries_for_week2_day:
            if subfunctions.check_times_one(times_of_own_entries_for_week2_day, (start_time, finish_time)) != "ok":
                return render_template("error.html", message=subfunctions.check_times_one(times_of_own_entries_for_week2_day, (start_time, finish_time)))
        if entries.add_weekly_entry(user_id, request.form["weekly_event"], start_time, finish_time, dow):
            return redirect("/settings")
        return render_template("error.html", message="Uuden vakioajan lis????minen ei onnistunut")
    return render_template("error.html", message="Osallistumisesi lis??ys ei onnistunut, aikojen valinta oli puutteellinen tai ajat olivat virheellisi??, tarkista valitsemasi ajat ja tallenna uudelleen")

@app.route("/settings/weekly_cancel", methods=["POST"])
def weekly_cancel():
    users.check_csrf()
    users.require_role(2)
    if entries.delete_own_entry(request.form["entry_id"], session["user_id"]):
        return redirect("/settings")
    return render_template("error.html", message="Vakioajan peruminen ei onnistunut")

@app.route("/settings/change_calendarview", methods=["POST"])
def change_calendarview():
    users.check_csrf()
    users.require_role(2)
    events = request.form.getlist("event_pick")
    if users.update_calendarview(session["user_id"], events):
        return redirect("/settings")
    return render_template("error.html", message="Kalenterissa n??kyvien tapahtumien p??ivitt??minen ei onnistunut")

@app.route("/settings/friends", methods=["POST"])
def friends_settings():
    users.check_csrf()
    users.require_role(2)
    if request.form["friend"]:
        friend_name = request.form["friend"].strip()
        if len(friend_name) == 0:
            return render_template("error.html", message="Nimikentt?? oli tyhj??, tarkista nimi ja tallenna pyynt?? uudelleen")
        friend_id = users.get_user_id(friend_name)
        if friend_id == -1:
            return render_template("error.html", message="Kaveria ei l??ytynyt antamallasi nimell??, tarkista nimi ja tallenna pyynt?? uudelleen")
        if not friends.add_friend_request(session["user_id"], friend_id):
            return render_template("error.html", message="Kaveripyynt?? on jo l??hetetty")
    if request.form.getlist("friend_asks"):
        if not friends.accept_friends(session["user_id"], request.form.getlist("friend_asks")):
            return render_template("error.html", message="Kaverip??ivitys ei onnistunut")
    if request.form.getlist("friends"):
        if not friends.remove_friends(session["user_id"], request.form.getlist("friends")):
            return render_template("error.html", message="Kaverip??ivitys ei onnistunut")
    if request.form.getlist("ask_cancel"):
        if not friends.cancel_friend_request(session["user_id"], request.form.getlist("ask_cancel")):
            return render_template("error.html", message="Kaverip??ivitys ei onnistunut")
    return redirect("/settings")
