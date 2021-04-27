from app import app
from flask import redirect, render_template, request, session
import users, group, random, entries, datetime, messages, events

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/login", methods=["POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        if users.login(username, password):
            return redirect("/calendar")
        else:
            return render_template("error.html", message="Tunnus tai salasana meni väärin")

@app.route("/register", methods=["GET","POST"])
def register():
    
    if request.method == "GET":
        group_info = group.get_info()
        #event_list = events.get_all_0_level_events()
        event_list = events.get_all_events_for_register()
        if not group_info:
            return render_template("new_group.html")
        return render_template("register.html", group_info=group_info, events=event_list)

    if request.method == "POST":
        username = request.form["username"].strip()
        if len(username) < 2 or len(username) > 35:
            return render_template("error.html", message="Tunnuksen tulee sisältää 2-35 merkkiä")
        password1 = request.form["password1"].strip()
        password2 = request.form["password2"].strip()
        if password1 != password2:
            return render_template("error.html", message="Salasanoissa oli eroa")
        if password1 == "":
            return render_template("error.html", message="Salasana oli tyhjä")
        
        if request.form["group_reg"] == "old_group":
            password_group = request.form["password_group"]
            if not password_group:
                return render_template("error.html", message="Liittymissalasana oli tyhjä, jos salasana ei ole tiedossasi, kysy ohjeet salasanan saamiseksi ryhmän jäseneltä.")
            if group.check_password(password_group):
                if users.register(username, password1, 2):
                    events_checked = request.form.getlist("event_checked")
                    for event in events_checked:
                        print("events reg", event)
                        users.add_event(event, session["user_id"], 2)
                    return redirect("/calendar")
        
        #tämä käytössä vain kerran, kun perustaja tallentaa ryhmän tiedot..
        if request.form["group_reg"] == "new_group":
            group_name = request.form["group_name"]
            group_description = request.form["group_description"]
            
            if len(group_name) < 5 or len(group_name) > 20:
                return render_template("error.html", message="Ryhmän nimen tulee sisältää 5-20 merkkiä")
            if len(group_description) > 400:
                return render_template("error.html", message="Ryhmän kuvauksen tulee sisältää enintään 400 merkkiä")
            group_password1 = request.form["password_newgroup1"]
            group_password2 = request.form["password_newgroup2"]
            if group_password1 != group_password2:
                return render_template("error.html", message="Liittymissalasanoissa oli eroa")
            if group_password1 == "":
                return render_template("error.html", message="Liittymissalasana oli tyhjä")
            
            group_id = group.add(group_name, group_description, group_password1)
            if users.register(username, password1, 0):
                group.set_founder(session["user_id"])
                return redirect("/calendar")
            else:
                group.delete()
                users.delete_user(username)
        #...tähän asti uuden ryhmän perustaminen
        return render_template("error.html", message="Rekisteröinti ei onnistunut")

@app.route("/logout")
def logout():
    users.logout()
    return redirect("/")

#####################################################################
###kalenteri omaksi route tiedostoksi??
#####################################################################

@app.route("/calendar", methods=["GET","POST"])
def calendar():
    username = session["user_name"]
    user_id = session["user_id"]
    today = datetime.date.today()
    week, all_event_entries = entries.get_week(user_id, 1)
    all_own_entries = entries.get_all_own_entries_dict(all_event_entries)
##kun ehtii.. niin tarkenna vielä mahdollisuus hakea/lisätä yhtä tapahtumaa koskevat viestit kaikkien viestien lisäksi v
    message_list =  messages.get_newest(25, user_id)
    group_info = group.get_info()
    days = {0:"SU", 1:"MA", 2:"TI", 3:"KE", 4:"TO", 5:"PE", 6:"LA"}
    days_i = entries.change_days_dow_to_i_dict(days, today)

    if request.method == "GET":
        return render_template("calendar.html", messages=message_list, days_i=days_i, all_own_entries=all_own_entries, group_info=group_info, days=days, week=week, all_event_entries=all_event_entries, today=today)
    
    if request.method == "POST":
        #-- ['05:00', 'tapahtuma12', 4.0, 3, 12, '10:00']
        entry = request.form["calendar_pick"].split(",")
        #--- 2021-04-22
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
    if len(request.form["comment"].strip()) > 0:
        if messages.add(session["user_id"], request.form["comment"]):
            return redirect("/calendar")
    return render_template("error.html", message="Viestin lisäys ei onnistunut, tarkista viesti")

@app.route("/entry/<day>", methods=["GET","POST"])
def entry(day):
    day = int(float(day))
    user_id = session["user_id"]
    week, all_event_entries = entries.get_week(user_id, 1)
    all_own_entries = entries.get_all_own_entries_dict(all_event_entries)
    today = datetime.datetime.today()
    date = today + datetime.timedelta(days=day)
    if request.method == "GET":
        participants = entries.get_participants(date)
        #print("---participants", participants)
        event_list = events.get_events(user_id)
        days = {0:"SU", 1:"MA", 2:"TI", 3:"KE", 4:"TO", 5:"PE", 6:"LA"}
        days_i = entries.change_days_dow_to_i_dict(days, today)
        return render_template("entry.html", participants=participants, events=event_list, days_i=days_i, date=date, day=day)
    
    if request.method == "POST":
        #muodonmuutos vertailua varten
        if request.form["time1"] and request.form["time2"]:
            start_time = datetime.datetime.strptime(request.form["time1"], "%H:%M").time()
            finish_time = datetime.datetime.strptime(request.form["time2"], "%H:%M").time()
        else:
            return render_template("error.html", message="Osallistumisesi lisäys ei onnistunut, tarkista valitsemasi ajat")
        #print("finish_time", finish_time)
        if request.form["extra_participants"]:
            extras = request.form["extra_participants"]
        else:
            extras = 0
        if start_time < finish_time:
            if all_own_entries[day]:
                #print("---all_own_entries", all_own_entries)
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

@app.route("/entry/delete_entry/<entry_id>")
def delete_entry(entry_id):
    #print("---entry id", entry_id)
    if entries.delete_own_entry(entry_id):
        return redirect("/calendar")
    return render_template("error.html", message="Ilmoittautumisesi peruminen ei onnistunut")

@app.route("/plan", methods=["GET","POST"])
def plan():
    username = session["user_name"]
    user_id = session["user_id"]
    group_info = group.get_info()
    event_list = events.get_events(user_id)
    friends_plans = entries.friends_planning(user_id)
    week, all_event_entries = entries.get_week(user_id, 2)
    all_own_entries = entries.get_all_own_entries_dict(all_event_entries)
    today = datetime.date.today().strftime("%d.%m.")
    today1 = datetime.date.today()
    days = {0:"SU", 1:"MA", 2:"TI", 3:"KE", 4:"TO", 5:"PE", 6:"LA"}
    days_i = entries.change_days_dow_to_i_dict(days, today1)
    if request.method == "GET":
        return render_template("plan.html", friends_plans=friends_plans, all_own_entries=all_own_entries, days_i=days_i, group_info=group_info, events=event_list, days=days, week=week, all_event_entries=all_event_entries, today=today)
    if request.method == "POST":
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

@app.route("/entry/delete_entry/plan/<entry_id>")
def delete_entry_planned(entry_id):
    if entries.delete_own_entry(entry_id):
        return redirect("/plan")
    return render_template("error.html", message="Ilmoittautumisesi peruminen ei onnistunut")

@app.route("/plan/pick", methods=["POST"])
def add_plan_pick():
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

#########################################################################
##########################################################################
##settings omaksi routes tiedostoksi?
####################################################
#############################################################

@app.route("/settings")
def settings():
    user_id = session["user_id"]
    events_with_own_level = events.get_all_events_for_user(user_id)
    #print("--own level", events_with_own_level)
    #    sql = """SELECT e.id, e.name, e.description, e.min_participants, e.max_participants, e.event_level, ue.role
    own_weekly_entries = entries.get_weekly_entries_for_user(user_id)
    #    sql = """SELECT en.weekly, e.id, e.name, en.start_time, en.finish_time, en.id
    friends = users.get_friends(user_id)
    #    sql = """SELECT u.id, u.name, f.active, f.user_id1
    friend_requests = users.get_friends_open_requests(user_id)
    weekdays = {0:"SU", 1:"MA", 2:"TI", 3:"KE", 4:"TO", 5:"PE", 6:"LA"}
    user_info = users.get_user_info(user_id)
    #    sql = """SELECT username, name, contact_info FROM users"""
    if session["user_role"] == 1:
        all_events = events.get_all_events()
    #    sql = """SELECT *
        return render_template("settings.html", all_events=all_events, user_info=user_info, days=weekdays, events_with_own_level=events_with_own_level, own_weekly_entries= own_weekly_entries, friends=friends, friend_requests=friend_requests)
    else:
        return render_template("settings.html", user_info=user_info,  days=weekdays, events_with_own_level=events_with_own_level, own_weekly_entries= own_weekly_entries, friends=friends, friend_requests=friend_requests)

@app.route("/settings/change_user_name", methods=["POST"])
def change_name():
    user_id = session["user_id"]  
    changed_name = request.form["name"]
    if changed_name:
        if len(changed_name) < 1 or len(changed_name) > 35:
            return render_template("error.html", message="Nimen tulee sisältää 1-35 merkkiä")
        if not users.change_name(user_id, changed_name):
            return render_template("error.html", message="Nimen vaihtaminen ei onnistunut, nimi on jo käytössä")
    return redirect("/settings")

@app.route("/settings/change_contact_info", methods=["POST"])
def change_contact_info():
    user_id = session["user_id"]
    changed_contact_info = request.form["contact_info"]
    if not users.change_contact_info(user_id, changed_contact_info):
        return render_template("error.html", message="Yhteystietojen päivittäminen ei onnistunut")
    return redirect("/settings")

@app.route("/settings/change_password", methods=["POST"])
def change_password():
    if session["csrf_token"] != request.form["csrf_token"]:
        abort(403)
    user_id = session["user_id"]
    changing_password = [request.form["old_password"], request.form["new_password1"], request.form["new_password2"]]
    if not users.check_password(user_id, changing_password[0]):
        return render_template("error.html", message="Vanha salasana meni väärin, tarkista salasana")
    if changing_password[1] != changing_password[2]:
        return render_template("error.html", message="Uusissa salasanoissa oli eroa")
    if changing_password[1] == "":
        return render_template("error.html", message="Uusi salasana oli tyhjä")
    if not users.change_password(user_id, changing_password[1]):
        return render_template("error.html", message="Uuden salasanan rekisteröinti ei onnistunut")
    return redirect("/settings")
    
@app.route("/settings/weekly_entries", methods=["POST"])
def weekly_entries():
    if entries.add_weekly_entry(session["user_id"], request.form["weekly_event"], request.form["weekly_time_start"], request.form["weekly_time_end"], request.form["weekly_dow"]):
        return redirect("/settings")
    return render_template("error.html", message="Uuden vakioajan lisääminen ei onnistunut")

######kysy tähän ohje kuinka checked ainoastaan muuttuneet voi muuttaa, kun active/not active
#nyt kysely muuttaa kaikki not active ja lisää muuttuneet activeksi ..en rustaile tätä valmiiksi näin
@app.route("/settings/change_calendarview", methods=["POST"])
def change_calendarview():
    events = request.form.getlist("event_pick")
    #print("--events calendar", events)
    if users.update_calendarview(session["user_id"], events):
        return redirect("/settings")
    return render_template("error.html", message="Kalenterissa näkyvien tapahtumien päivittäminen ei onnistunut")


##tämä keskeneräinen..kaverit ei poistu.. :D
@app.route("/settings/friends", methods=["POST"])
def friends():
    if request.form["friend"]:
        if users.add_friend_request(session["user_id"], request.form["friend"]):
            return redirect("/settings")
    if request.form.getlist("friends"):
        #print("---friends", request.form.getlist("friends"))
        if users.change_friends(session["user_id"], request.form.getlist("friends")):
            return redirect("/settings")
    return render_template("error.html", message="Kaveripyyntö ei onnistunut")
 
@app.route("/settings/change_group_name", methods=["POST"])
def change_group_name():
    if session["csrf_token"] != request.form["csrf_token"]:
        abort(403)
    if group.change_group_name(request.form["name_group"]):
        return redirect("/settings")
    return render_template("error.html", message="Nimenvaihto ei onnistunut")
 
@app.route("/settings/change_group_description", methods=["POST"])
def change_group_description():
    if session["csrf_token"] != request.form["csrf_token"]:
        abort(403)
    if group.change_group_description(request.form["group_description"]):
        return redirect("/settings")
    return render_template("error.html", message="Ryhmän kuvauksen vaihto ei onnistunut")
 
@app.route("/settings/change_group_password", methods=["POST"])
def change_group_password():
    if session["csrf_token"] != request.form["csrf_token"]:
        abort(403)
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
###pitäisikö tässä poistaa tapahtuma kokonaan, jos ei rekisteröi jäsenille vai näkyykö valittavissa silti???

@app.route("/settings/change_event_info", methods=["POST"])
def change_event_info():
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
    if group.add_admin_message(request.form["admin_info"]):
        return redirect("/settings")
    return render_template("error.html", message="viestin tallentaminen ei onnistunut")

@app.route("/settings/admin/userlist", methods=["GET", "POST"])
def userlist():
    if request.method == "GET":
        all_events = events.get_all_events()
        userlist = group.get_all_users_info_for_userlist()
        users_in_events_info = group.get_all_users_in_events_info_list()
        return render_template("userlist.html", users_in_events_info=users_in_events_info, all_events=all_events, userlist=userlist)
#sql = """SELECT u.id, u.name, u.contact_info, u.role, u.founded, ue.event_id, ue.role
    if request.method == "POST":
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
