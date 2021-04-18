from db import db
from flask import render_template
import os 

#    event_info = {1:request.form["new_event_name"], 2:request.form["new_event_description"], 3:request.form["new_event_min_participants"], 4:request.form["new_event_max_participants"], 5:request.form["new_event_level"]}
def add_new_event(event_info:dict):
    try:
        sql = """INSERT INTO events (name, description, min_participants, max_participants, event_level)
                    VALUES (:name, :description, :min, :max, :level) RETURNING id"""
        event_id = db.session.execute(sql, {"name":event_info[1], "description":event_info[2], "min":event_info[3], "max":event_info[4], "level":event_info[5]}).fetchone()[0]
        db.session.commit()  
        return event_id
    except:
        return -1

#keskeneräinen, poista kun yläp. toimii..
def add_event(event_name:str, description:str):
    try:
        sql = """INSERT INTO events (name, description, min_participants, max_participants, event_level)
                    VALUES (:name, :description, 0, 100, 0) RETURNING id"""
        event_id = db.session.execute(sql, {"name":event_name, "description":description}).fetchone()[0]
        db.session.commit()  
        return event_id
    except:
        return render_template("error.html", message="Tapahtuman lisäys ei onnistunut")

def get_all_0_level_events():
    try:
        sql = """SELECT id, name, description, min_participants, max_participants
                    FROM events
                    WHERE event_level = 0
                    ORDER BY name"""
        return db.session.execute(sql).fetchall()
    except:
        return []

def get_all_events():
    try:
        sql = """SELECT *
                    FROM events
                    ORDER BY name"""
        return db.session.execute(sql).fetchall()
    except:
        return []

def get_all_events_for_user(user_id):
#poistettu rajoitus AND ue.role < 4 ...hakee nyt kaikki johon taso oikeuttaa
    try:
        sql = """SELECT DISTINCT e.id, e.name, e.description, e.min_participants, e.max_participants, e.event_level, ue.role
                    FROM users u 
                    LEFT JOIN users_in_events ue ON u.id=ue.user_id
                    LEFT JOIN events e ON e.id=ue.event_id
                    WHERE u.id=:user_id 
                    AND ue.user_id=:user_id
                    AND e.event_level <= ue.user_level
                    ORDER BY e.name, e.event_level"""
        return db.session.execute(sql, {"user_id":user_id}).fetchall()  
    except:
        return []

def get_events(user_id):
    try:
        sql = """SELECT e.id, e.name, e.description, e.min_participants, e.max_participants, e.event_level
                    FROM users u 
                    LEFT JOIN users_in_events ue ON u.id=ue.user_id
                    LEFT JOIN events e ON e.id=ue.event_id
                    WHERE u.id=:user_id
                    AND e.event_level <= ue.user_level
                    AND ue.role < 4
                    ORDER BY e.id"""
        return db.session.execute(sql, {"user_id":user_id}).fetchall()  
    except:
        return []

def delete_event(event_id):
    try:
        sql = """DELETE FROM events
                    WHERE id=:event_id"""
        db.session.execute(sql,{"event_id":event_id})
        db.session.commit()
        print("---tämä on true")
        return True
    except:
        return False

def change_name(event_id, name):
    try:
        sql = """UPDATE events SET name=:name
                    WHERE id=:event_id"""
        db.session.execute(sql,{"event_id":event_id, "name":name})
        db.session.commit()
        return True
    except:
        return False

def change_description(event_id, description):
    try:
        sql = """UPDATE events SET description=:description
                    WHERE id=:event_id"""
        db.session.execute(sql,{"event_id":event_id, "description":description})
        db.session.commit()
        return True
    except:
        return False

def change_min_participants(event_id, min_participants):
    try:
        sql = """UPDATE events SET min_participants=:min_participants
                    WHERE id=:event_id"""
        db.session.execute(sql,{"event_id":event_id, "min_participants":min_participants})
        db.session.commit()
        return True
    except:
        return False

def change_max_participants(event_id, max_participants):
    try:
        sql = """UPDATE events SET max_participants=:max_participants
                    WHERE id=:event_id"""
        db.session.execute(sql,{"event_id":event_id, "max_participants":max_participants})
        db.session.commit()
        return True
    except:
        return False

def change_level(event_id, level):
    try:
        sql = """UPDATE events SET event_level=:event_level
                    WHERE id=:event_id"""
        db.session.execute(sql,{"event_id":event_id, "event_level":level})
        db.session.commit()
        return True
    except:
        return False

def delete(group_id):
    sql = """DELETE 
            FROM groups 
            WHERE id=:group_id"""
    db.session.execute(sql, {"group_id":group_id})
    db.session.commit()
    return

