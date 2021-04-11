from db import db
from werkzeug.security import check_password_hash, generate_password_hash
import os 

def get_info():
    sql = """SELECT name, description FROM group_info"""
    return db.session.execute(sql).fetchone()

def check_password(password_group):
    sql = """SELECT password 
                FROM group_info"""
    group_password = db.session.execute(sql).fetchone()[0]
    return check_password_hash(group_password, password_group)

def add(name, description, password):
    hash_value = generate_password_hash(password)
    sql = """INSERT INTO group_info (name, description, password, founded) 
                VALUES (:name, :description, :password, NOW()) RETURNING id"""
    result = db.session.execute(sql, {"name":name, "description":description,"password":hash_value})
    group_id = result.fetchone()[0]
    db.session.commit()
    return group_id

def set_founder(user_id):
    sql = """UPDATE group_info 
                SET founder_id=:user_id"""
    db.session.execute(sql, {"user_id":user_id})
    db.session.commit()
    return

#keskeneräinen
def get_admin_info() -> list:
    sql = """SELECT admin_info
                FROM group_info"""
    return db.session.execute(sql).fetchone()

#jos perustaa uuden ryhmän ja rekisteröityminen ei onnistu kokonaisuudessaan
#silloin ryhmä poistetaan tietokannasta tällä
def delete():
    sql = """DELETE 
             FROM group_info"""
    db.session.execute(sql)
    db.session.commit()
    return
