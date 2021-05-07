from app import app
from flask import redirect, render_template, request, session
import users, group, events

@app.route("/settings/change_group_name", methods=["POST"])
def change_group_name():
    users.check_csrf()
    users.require_role(1)
    if group.change_group_name(request.form["name_group"]):
        return redirect("/settings")
    return render_template("error.html", message="Nimenvaihto ei onnistunut")
 
@app.route("/settings/change_group_description", methods=["POST"])
def change_group_description():
    users.check_csrf()
    users.require_role(1)
    if group.change_group_description(request.form["group_description"]):
        return redirect("/settings")
    return render_template("error.html", message="Ryhmän kuvauksen vaihto ei onnistunut")
 
@app.route("/settings/change_group_password", methods=["POST"])
def change_group_password():
    users.check_csrf()
    users.require_role(1)
    new_password = request.form["new_password1"]
    if  new_password != request.form["new_password2"]:
        return render_template("error.html", message="Uusissa salasanoissa oli eroa")
    if new_password == "":
        return render_template("error.html", message="Uusi salasana oli tyhjä")
    if group.change_group_password(new_password, request.form["old_password"]):
        return redirect("/settings")
    return render_template("error.html", message="Uuden salasanan rekisteröinti ei onnistunut")
    
@app.route("/settings/add_new_event", methods=["POST"])
def add_new_event():
    users.check_csrf()
    users.require_role(1)
    if events.old_events_with_level_100(5):
        return render_template("error.html", message="Uuden tapahtuman lisäys ei onnistu. Saat luotua uuden tapahtuman muuttamalla yhden käytöstä poistamasi tapahtuman kohdassa Tapahtuman muuttaminen tai poistaminen käytöstä.")
    event_info = {1:request.form["new_event_name"], 2:"", 3:0, 4:0, 5:0}
    if request.form["new_event_description"]:
        event_info[2] = request.form["new_event_description"]
    if request.form["new_event_min_participants"]:
        event_info[3] = int(request.form["new_event_min_participants"])
    if request.form["new_event_max_participants"]:
        event_info[4] = int(request.form["new_event_max_participants"])
    if request.form["new_event_level"]:
        event_info[5] = int(request.form["new_event_level"])
    if event_info[3] > event_info[4]:
        return render_template("error.html", message="Tapahtuman lisäys ei onnistunut, tarkista minimi- ja maksimiosallistujamäärät")
    event_id = events.add_new_event(event_info)
    if event_id == - 1:
        return render_template("error.html", message="Tapahtuman lisäys ei onnistunut")
    if users.add_event_for_everyone(event_id):
        return redirect("/settings")
    return render_template("error.html", message="Uuden tapahtuman rekisteröinti jäsenille ei onnistunut")

@app.route("/settings/change_event_info", methods=["POST"])
def change_event_info():
    users.check_csrf()
    users.require_role(1)
    action = request.form["event_action"]
    event_id = request.form["event_pick"]
    if action == "1":
        if events.change_level(event_id, 100):
            return redirect("/settings")
        else:
            return render_template("error.html", message="Tapahtuman poistaminen ei onnistunut")
    elif action == "2":
        if request.form["event_name"]:
            if events.change_name(event_id, request.form["event_name"]):
                return redirect("/settings")
    elif action == "3":
        if request.form["event_description"]:
            if events.change_description(event_id, request.form["event_description"]):
                return redirect("/settings")
    elif action == "4":
        if request.form["number_value1"]:
            if events.change_min_participants(event_id, request.form["number_value1"]):
                return redirect("/settings")
    elif action == "5":
        if request.form["number_value1"]:
            if events.change_max_participants(event_id, request.form["number_value1"]):
                return redirect("/settings")
    elif action == "6":
        if request.form["number_value2"]:
            if events.change_level(event_id, request.form["number_value2"]):
                return redirect("/settings")
    return render_template("error.html", message="Tapahtuman muuttaminen ei onnistunut")

@app.route("/settings/admin/message", methods=["POST"])
def admin_message():
    users.check_csrf()
    users.require_role(1)
    if group.add_admin_message(request.form["admin_info"]):
        return redirect("/settings")
    return render_template("error.html", message="viestin tallentaminen ei onnistunut")

@app.route("/settings/admin/userlist", methods=["GET", "POST"])
def userlist():
    users.require_role(1)
    if request.method == "GET":
        all_events = events.get_all_events()
        userlist = group.get_all_users_info_for_userlist()
        users_in_events_info = group.get_all_users_in_events_info_list()
        return render_template("userlist.html", users_in_events_info=users_in_events_info, all_events=all_events, userlist=userlist)

    if request.method == "POST":
        users.check_csrf()
        action = request.form["action"]
        users_changing = request.form.getlist("user_id")
        if action == "1":
            if users.change_level(users_changing, request.form["event_on"]):
                return redirect("/settings/admin/userlist")
        elif action == "2":
            if users.change_role(users_changing):
                return redirect("/settings/admin/userlist")
        elif action == "3":
            if users.reset_password(users_changing):
                return redirect("/settings/admin/userlist")
        elif action == "4":
            if group.change_participation_rights(users_changing, request.form["event_off"], 5):
                return redirect("/settings/admin/userlist")
        elif action == "5":
            if group.change_participation_rights(users_changing, request.form["event_off"], 2):
                return redirect("/settings/admin/userlist")
        elif action == "6":
            if group.change_all_participation_rights(users_changing, 5):
                return redirect("/settings/admin/userlist")
        elif action == "7":
            if group.change_all_participation_rights(users_changing, 2):
                return redirect("/settings/admin/userlist")
        return render_template("error.html", message="muutoksen tallentaminen ei onnistunut")
