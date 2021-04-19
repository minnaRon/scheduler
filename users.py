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

def get_username(user_id):
    sql = """SELECT username
                FROM users
                WHERE id=:user_id"""
    return db.session.execute(sql, {"user_id":user_id}).fetchone[0]

def check_password(user_id, password):
    sql = """SELECT password
                FROM users
                WHERE id=:user_id"""
    password_db = db.session.execute(sql, {"user_id":user_id}).fetchone()[0]
    return check_password_hash(password_db, password)

def change_password(user_id, password):
    hash_value = generate_password_hash(password)
    try:
        sql = """UPDATE users SET password=:password
                    WHERE id=:user_id"""
        db.session.execute(sql, {"user_id":user_id, "password":hash_value})
        db.session.commit()
    except:
        return False
    return True

def change_name(user_id, name):
    try:
        sql = """UPDATE users SET name=:name
                    WHERE id=:user_id"""
        db.session.execute(sql, {"user_id":user_id, "name":name})
        db.session.commit()
    except:
        return False
    return True

def change_contact_info(user_id, contact_info):
    try:
        sql = """UPDATE users SET contact_info=:contact_info
                WHERE id=:user_id"""
        db.session.execute(sql, {"user_id":user_id, "contact_info":contact_info})
        db.session.commit()
    except:
        return False
    return True

def add_event(event_id:int, user_id:int, role:int):
    sql = """INSERT INTO users_in_events (event_id, user_id, role)
                VALUES (:event_id, :user_id, :role)"""
    db.session.execute(sql, {"event_id":event_id, "user_id":user_id, "role":role})
    db.session.commit()

def update_calendarview(user_id, events:list):
    try:
        sql = """UPDATE users_in_events SET role=4
                    WHERE user_id=:user_id
                    AND role<>5"""
        db.session.execute(sql, {"user_id":user_id, "event_id":event_id})
        for event_id in events:
            sql = """UPDATE users_in_events SET role=2
                    WHERE user_id=:user_id
                    AND event_id=:event_id"""
            db.session.execute(sql, {"user_id":user_id, "event_id":event_id, "role":role})
        db.session.commit()
        return True
    except:
        return False

def get_friends_all_info(user_id):
    sql = """SELECT u.id, u.name, f.active, f.user_id1
                FROM friends f, users u
                WHERE ((f.user_id1=:user_id AND f.active=1)
                OR (f.user_id2=:user_id AND f.active=0))
                AND u.id <> :user_id
                ORDER BY u.name
                """
    return db.session.execute(sql, {"user_id":user_id}).fetchall()

def add_friend_request(user_id, friend_calendarname):
    print("--f cal",friend_calendarname)
    try:
        sql = """SELECT id
                    FROM users
                    WHERE name=:name"""
        friend_id = db.session.execute(sql, {"name":friend_calendarname}).fetchone()[0]
        print("--f id", friend_id)
        sql = """INSERT INTO friends (user_id1, user_id2)
                    VALUES (:user_id, :friend_id)"""
        db.session.execute(sql, {"user_id":user_id, "friend_id":friend_id})
        db.session.commit()
        return True
    except:
        return False


def get_user_info(user_id):
    sql = """SELECT username, name, contact_info
                FROM users
                WHERE id=:user_id"""
    return db.session.execute(sql, {"user_id":user_id}).fetchone()

def get_all_users_id_name():
    sql = """SELECT id, name FROM users"""
    return db.session.execute(sql)

#tarvitaanko tätä? missä tapahtumakohtainen user level määrittely jos ei tässä?
#pitäisikö ohjata lisäämään usereille sopivat levelit heti?
def add_event_for_everyone(event_id):
    try:
        sql = """SELECT id
                    FROM users"""
        users = db.session.execute(sql).fetchall()
        print("---id:t", users)
        for user in users:
            sql = """INSERT INTO users_in_events (event_id, user_id)
                        VALUES (:event_id, :user_id)"""
            db.session.execute(sql, {"event_id":event_id, "user_id":user[0]})
        db.session.commit()
        return True
    except:
        return False

def change_level(users_changing, event_id):
    try:
        sql = """SELECT event_level FROM events
                    WHERE id=:event_id"""
        level = db.session.execute(sql, {"event_id":event_id}).fetchone()[0]
        print("---level", level, users_changing, event_id)
        for user_id in users_changing:
            sql = """UPDATE users_in_events SET user_level=:event_level
                        WHERE user_id=:user_id
                        AND event_id=:event_id"""
            db.session.execute(sql, {"user_id":user_id, "event_id":event_id, "event_level":level})
        db.session.commit()
        return True
    except:
        return False

def change_role(users_changing):
    try:
        for user_id in users_changing:
            sql = """SELECT role FROM users
                        WHERE id=:user_id"""
            role = db.session.execute(sql, {"user_id":user_id}).fetchone()[0]
            if role == 1:
                role = 2
            elif role == 2:
                role = 1
            sql = """UPDATE users SET role=:role
                        WHERE id=:user_id"""
            db.session.execute(sql, {"user_id":user_id, "role":role})
        db.session.commit()
        return True
    except:
        return False

def reset_password(users_changing):
    try:
        for user_id in users_changing:
            sql = """SELECT username FROM users
                        WHERE id=:user_id"""
            username = db.session.execute(sql, {"user_id":user_id}).fetchone()[0]
            hash_value = generate_password_hash(username)
            sql = """UPDATE users SET password=:password
                        WHERE id=:user_id"""
            db.session.execute(sql, {"user_id":user_id, "password":hash_value})
        db.session.commit()
        return True
    except:
        return False

def delete_user(username):
    sql = """DELETE FROM users 
             WHERE username=:username"""
    db.session.execute(sql, {"username":username})
    db.session.commit()
