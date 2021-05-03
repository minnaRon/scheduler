from db import db
import os

def add_friend_request(user_id, friend_calendarname):
    try:
        sql = """SELECT id
                    FROM users
                    WHERE name=:name"""
        friend_id = db.session.execute(sql, {"name":friend_calendarname}).fetchone()[0]
        sql = """SELECT COUNT(id) FROM friends
                    WHERE (user_id1=:user_id AND user_id2=:friend_id)
                    OR (user_id2=:user_id AND user_id1=:friend_id)"""
        already = db.session.execute(sql, {"user_id":user_id, "friend_id":friend_id}).fetchone()[0]
        if already == 0:
            sql = """INSERT INTO friends (user_id1, user_id2, active)
                        VALUES (:user_id, :friend_id, 0)"""
            db.session.execute(sql, {"user_id":user_id, "friend_id":friend_id})
        db.session.commit()
        return True
    except:
        return False

def accept_friends(user_id, friend_asks):
    try:
        for friend in friend_asks:
            sql = """UPDATE friends SET active=1
                        WHERE user_id1=:friend
                        AND user_id2=:user_id"""
            db.session.execute(sql, {"user_id":user_id, "friend":friend})
        db.session.commit()
        return True
    except:
        return False

def remove_friends(user_id, friends):
    try:
        for friend in friends:
            sql = """DELETE FROM friends
                        WHERE (user_id1=:user_id AND user_id2=:friend)
                        OR (user_id2=:user_id AND user_id1=:friend)"""
            db.session.execute(sql, {"user_id":user_id, "friend":friend})
        db.session.commit()
        return True
    except:
        return False

def cancel_friend_request(user_id, ask_cancel):
    try:
        for asked_id in ask_cancel:
            sql = """DELETE FROM friends
                        WHERE user_id1 = :user_id
                        AND user_id2 = :asked_id
                        AND active = 0"""
            db.session.execute(sql, {"user_id":user_id, "asked_id":asked_id})
        db.session.commit()
        return True
    except:
        return False

def get_friends_open_requests(user_id):
    sql = """SELECT u.id, u.name, fr.active, fr.user_id1
                FROM (SELECT * FROM friends f
                        WHERE (f.user_id2=:user_id AND f.active=0)) fr JOIN users u ON user_id1=u.id
                WHERE u.id <> :user_id
                ORDER BY u.name"""
    return db.session.execute(sql, {"user_id":user_id}).fetchall()

def get_friends(user_id):
    sql = """SELECT u.id, u.name, fr.active, fr.user_id1
                FROM (SELECT * FROM friends f
                        WHERE ((f.user_id1=:user_id AND f.active=1)
                        OR (f.user_id2=:user_id AND f.active=1))) fr JOIN users u ON user_id2=u.id OR user_id1=u.id
                WHERE u.id <> :user_id
                ORDER BY u.name"""
    return db.session.execute(sql, {"user_id":user_id}).fetchall()

def get_own_requests(user_id):
    sql = """SELECT u.id, u.name, fr.active, fr.user_id2
                FROM (SELECT * FROM friends f
                        WHERE (f.user_id1=:user_id AND f.active=0)) fr JOIN users u ON user_id2=u.id
                WHERE u.id <> :user_id
                ORDER BY u.name"""
    return db.session.execute(sql, {"user_id":user_id}).fetchall()
