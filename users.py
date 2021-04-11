from db import db
from flask import abort, request, session, render_template
from werkzeug.security import check_password_hash, generate_password_hash
import os

def login(username, password):
    sql = """SELECT id, password, name, role 
            FROM users
            WHERE username=:username"""
    result = db.session.execute(sql, {"username":username})
    user = result.fetchone()
    if not user:
        return False
    else:
        if check_password_hash(user[1], password):
            session["user_id"] = user[0]
            session["user_name"] = user[2]
            session["user_role"] = user[3]
            session["csrf_token"] = os.urandom(16).hex()
            return True
        else:
            return False

def logout(): 
    del session["user_id"]
    del session["user_name"]
    del session["user_role"]
    del session["csrf_token"]
    return

def register(username, password, role):
    hash_value = generate_password_hash(password)
    try:
        sql = """INSERT INTO users (username, name, password, founded, role) 
                    VALUES (:username, :username, :password, NOW(), :role)"""
        db.session.execute(sql, {"username":username, "password":hash_value, "role":role})
        db.session.commit()
    except:
        return render_template("error.html", message="Rekisteröinti ei onnistunut")
    return login(username, password)

def add_event(event_id:int, user_id:int, role:int):
    sql = """INSERT INTO users_in_events (event_id, user_id, role)
                VALUES (:event_id, :user_id, :role)"""
    db.session.execute(sql, {"event_id":event_id, "user_id":user_id, "role":role})
    db.session.commit()

def get_all_users_id_name():
    sql = """SELECT id, name FROM users"""
    return db.session.execute(sql)

def delete(username):
    sql = """DELETE FROM users 
             WHERE username=:username"""
    db.session.execute(sql, {"username":username})
    db.session.commit()





