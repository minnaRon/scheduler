from app import app
from flask import redirect, render_template, request, session
import users, group, random, entries, datetime, messages, events

# kirjautuminen
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

# rekisteröi uusi jäsen (ja ryhmän rekisteröinti)
@app.route("/register", methods=["GET","POST"])
def register():
    
    if request.method == "GET":
        group_info = group.get_info()
        event_list = events.get_all_0_level_events()
        if not group_info:
            return render_template("new_group.html")
        return render_template("register.html", group_info=group_info, events=event_list)

    if request.method == "POST":
        username = request.form["username"]
        if len(username) < 1 or len(username) > 35:
            return render_template("error.html", message="Tunnuksen tulee sisältää 1-35 merkkiä")
        password1 = request.form["password1"]
        password2 = request.form["password2"]
        if password1 != password2:
            return render_template("error.html", message="Salasanoissa oli eroa")
        if password1 == "":
            return render_template("error.html", message="Salasana oli tyhjä")
        
        if request.form["group_reg"] == "old_group":
            password_group = request.form["password_group"]
            
            if group.check_password(password_group):
                if users.register(username, password1, 2):
                    events_checked = request.form.getlist("event_checked")
                    for event in events_checked:
                        users.add_event(event[0], session["user_id"], 2)
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
            if users.register(username, password1, 1):
                group.set_founder(session["user_id"])
                return redirect("/calendar")
            else:
                group.delete()
                users.delete(username)
        #...tähän asti uuden ryhmän perustaminen
        return render_template("error.html", message="Rekisteröinti ei onnistunut")

#         
@app.route("/calendar", methods=["GET","POST"])
def calendar():
    username = session["user_name"]
    user_id = session["user_id"]
    today = datetime.date.today()
    week, all_event_entries = entries.get_week(user_id, 1)
## v KESKENERÄINEN haku v
    message_list =  messages.get_newest(25, user_id)
    group_info = group.get_info()
    days = {0:"SU", 1:"MA", 2:"TI", 3:"KE", 4:"TO", 5:"PE", 6:"LA"}
        
    if request.method =="GET":
        return render_template("calendar.html", messages=message_list, group_info=group_info, days=days, week=week, all_event_entries=all_event_entries, today=today)
    
    if request.method == "POST":
        messages.add(user_id, request.form["comment"])
        return redirect("/calendar")

@app.route("/entry/<day>", methods=["GET","POST"])
def entry(day):
    print("-- entry")
    day = int(float(day))
    user_id = session["user_id"]
    date = datetime.datetime.today() + datetime.timedelta(days=day)
    print("--edelleen..")
    if request.method == "GET":
        event_list = events.get_events(user_id)
        return render_template("entry.html", events=event_list, date=date, day=day)
    
    if request.method == "POST":
        content = request.form["comment"]
        start_time = request.form["time1"]
        finish_time = request.form["time2"]
        if start_time < finish_time:
            entry_id = entries.add_entry(date, user_id, request.form["event_id"], start_time, finish_time)
        else:
            return render_template("error.html", message="Tapahtuman lisäys ei onnistunut, tarkista valitsemasi ajat")
        if len(content) > 0:
            messages.add_entry_comment(user_id, entry_id, request.form["event_id"], content)
        return redirect("/calendar")

@app.route("/plan", methods=["GET","POST"])
def plan():
    username = session["user_name"]
    user_id = session["user_id"]
    group_info = group.get_info
    event_list = events.get_events(user_id)
    friends_plans = entries.friends_planning(user_id)
    week, all_event_entries = entries.get_week(user_id, 2)
    today = datetime.date.today().strftime("%d.%m.")
    days = {0:"SU", 1:"MA", 2:"TI", 3:"KE", 4:"TO", 5:"PE", 6:"LA"}
        
    if request.method == "GET":
        return render_template("plan.html", friends_plans=friends_plans,group_info=group_info, events=event_list, days=days, week=week, all_event_entries=all_event_entries, today=today)
#KESKENERÄINEN
    if request.method == "POST":
        event_indices = request.form.getlist("event_index")
        start_times = request.form.getlist("time_start")
        finish_times = request.form.getlist("time_finish")
        days = request.form.getlist("day")
        
        print("--len",len(event_indices))
        print("---listat",event_indices, start_times, finish_times)
        if len(event_indices) == len(start_times) and len(start_times) == len(finish_times):
            for i in range(len(event_indices)-1):
                if start_times[i] < finish_times[i]:
                    entries.add_entry(datetime.datetime.today() + datetime.timedelta(days=7+int(float(days[i]))), user_id, event_list[int(event_indices[i])][0], start_times[i], finish_times[i])
                elif start_times[i] == "" and finish_times[i] =="":
                    continue
                else:
                    return render_template("error.html", message="Kaikkien tapahtumien lisäys ei onnistunut, tarkista valitsemasi ajat")
#errorin paluu takaisin kts.
        else:
            return render_template("error.html", message="Tapahtumien lisäys ei onnistunut, tarkista valitsemasi ajat")
        return redirect("/plan")

@app.route("/settings", methods=["GET","POST"])
def settings():
    if request.method == "GET":
        return render_template("settings.html", events=events.get_all_0_level_events())
#KESKENERÄINEN vain tapahtuman nimi, kuvaus viedään tietokantaan testailua varten
    if request.method == "POST":
        event_id = events.add_event(request.form["event_name"], request.form["description"])
        print("event_id", event_id)
        users.add_event(event_id, session["user_id"], 1)
        userlist = users.get_all_users_id_name()
        for user in userlist:
            users.add_event(event_id, user[0], 4)
#roolina 4, niin ei näy suoraan omissa tapahtumissa, asetuksista sitten uusia tapahtumia näkyviin näkymiin...

        return redirect("/settings")

@app.route("/logout")
def logout():
    users.logout()
    return redirect("/")
