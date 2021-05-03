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
                        users.add_event(event, session["user_id"], 2)
                    return redirect("/calendar")
            return render_template("error.html", message="Rekisteröinti ei onnistunut, tarkista ryhmän liittymissalasana")
        return render_template("error.html", message="Rekisteröinti ei onnistunut")

#tämä käytössä, kun ryhmä perustetaan
@app.route("/register_new_group", methods=["GET","POST"])
def register_new_group():
    if request.form["group_reg"] == "new_group":
        username = request.form["username"].strip()
        if len(username) < 2 or len(username) > 35:
            return render_template("error.html", message="Tunnuksen tulee sisältää 2-35 merkkiä")
        password1 = request.form["password1"].strip()
        password2 = request.form["password2"].strip()
        if password1 != password2:
            return render_template("error.html", message="Salasanoissa oli eroa")
        if password1 == "":
            return render_template("error.html", message="Salasana oli tyhjä")

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
    return render_template("error.html", message="Rekisteröinti ei onnistunut")

@app.route("/logout")
def logout():
    users.logout()
    return redirect("/")
