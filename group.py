from db import db
from werkzeug.security import check_password_hash, generate_password_hash
import os 

def get_info():
    sql = """SELECT name, description, admin_info FROM group_info"""
    return db.session.execute(sql).fetchone()

def check_password(password_group):
    sql = """SELECT password 
                FROM group_info"""
    group_password = db.session.execute(sql).fetchone()[0]
    return check_password_hash(group_password, password_group)

def add(name, description, password):
    hash_value = generate_password_hash(password)
    try:
        sql = """INSERT INTO group_info (name, description, password, founded)
                    VALUES (:name, :description, :password, NOW()) RETURNING id"""
        result = db.session.execute(sql, {"name":name, "description":description,"password":hash_value})
        group_id = result.fetchone()[0]
        db.session.commit()
        return group_id
    except:
        return -1

def set_founder(user_id):
    try:
        sql = """UPDATE group_info
                    SET founder_id=:user_id"""
        db.session.execute(sql, {"user_id":user_id})
        db.session.commit()
        return True
    except:
        return False

def change_group_name(name:str):
    try:
        sql = """UPDATE group_info
                    SET name=:name"""
        db.session.execute(sql, {"name":name})
        db.session.commit()
        return True
    except:
        return False

def change_group_description(description:str):
    try:
        sql = """UPDATE group_info
                    SET description=:description"""
        db.session.execute(sql, {"description":description})
        db.session.commit()
        return True
    except:
        return False

def change_group_password(new_password:str, old_password:str):
    hash_value = generate_password_hash(new_password)
    try:
        sql = """SELECT password FROM group_info"""
        password = db.session.execute(sql).fetchone()[0]
        if check_password_hash(password, old_password):
            sql = """UPDATE group_info
                        SET password=:new_password"""
            db.session.execute(sql, {"new_password":hash_value})
        db.session.commit()
        return True
    except:
        return False

def add_admin_message(admin_info):
    try:
        sql = """UPDATE group_info SET admin_info=:admin_info"""
        db.session.execute(sql, {"admin_info":admin_info})
        db.session.commit()
        return True
    except:
        return False

def get_all_users_info_for_userlist():
    sql = """SELECT id, username, name, contact_info, role, founded
                FROM users
                ORDER BY role, name"""
    return db.session.execute(sql).fetchall()

def get_all_users_in_events_info():
    sql = """SELECT *
                FROM users_in_events"""
    return db.session.execute(sql).fetchall()

def get_all_users_in_events_info_list() -> list:
    sql = """SELECT DISTINCT u.role, u.username, u.name, u.contact_info, u.founded, e.name, e.event_level, ue.user_level, ue.role
                    FROM users u LEFT JOIN users_in_events ue ON u.id=ue.user_id
                    LEFT JOIN events e ON e.id = ue.event_id
                    ORDER BY u.role, u.name"""
    return db.session.execute(sql).fetchall()

def get_all_users_in_events_info_dict() -> dict:
    info = {}
    sql = """SELECT id
                FROM users
                ORDER BY role, name"""
    user_id_list = db.session.execute(sql).fetchall()
    print("---user_id lista", user_id_list)
    for u_id in user_id_list:
        user = u_id[0]
        print("---user_id", user)
        sql = """SELECT e.name, e.event_level, ue.user_level, ue.role
                    FROM events e LEFT JOIN users_in_events ue ON e.id = ue.event_id
                    WHERE ue.user_id=:user_id
                    ORDER BY e.name"""
        info[user] = db.session.execute(sql, {"user_id":user}).fetchall()
        print("---info[user]",info[user])
        print("---info", info)
    return info

def get_admin_info() -> list:
    sql = """SELECT admin_info
                FROM group_info"""
    return db.session.execute(sql).fetchone()

def change_participation_rights(users_changing, event_id, role):
    try:
        for user_id in users_changing:
            sql = """UPDATE users_in_events SET role=:role
                        WHERE user_id=:user_id
                        AND event_id=:event_id"""
            db.session.execute(sql, {"user_id":user_id, "event_id":event_id, "role":role})
        db.session.commit()
        return True
    except:
        return False

def change_all_participation_rights(users_changing, role):
    try:
        for user_id in users_changing:
            sql = """UPDATE users_in_events SET role=:role
                        WHERE user_id=:user_id"""
            db.session.execute(sql, {"user_id":user_id, "role":role})
        db.session.commit()
        return True
    except:
        return False

#jos perustaa uuden ryhmän ja rekisteröityminen ei onnistu kokonaisuudessaan
#silloin ryhmä poistetaan tietokannasta tällä
def delete():
    sql = """DELETE 
             FROM group_info"""
    db.session.execute(sql)
    db.session.commit()
    return
