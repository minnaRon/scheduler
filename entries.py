from db import db
import datetime
        
def add_entry(date, user_id, event_id, time1, time2):
    try:
        sql = """INSERT INTO entries (user_id, event_id, date, start_time, finish_time)
                VALUES (:user_id, :event_id, :date, :time1, :time2)
                RETURNING id"""
        entry_id = db.session.execute(sql, {"user_id":user_id, "event_id":event_id, "date":date, "time1":time1, "time2":time2}).fetchone()[0]
        db.session.commit()
        return entry_id
    except:
        return -1

def add_entry_with_extras(date, user_id, event_id, time1, time2, extras):
    try:
        sql = """INSERT INTO entries (user_id, event_id, date, start_time, finish_time, extra_participants)
                VALUES (:user_id, :event_id, :date, :time1, :time2, :extras)
                RETURNING id"""
        entry_id = db.session.execute(sql, {"user_id":user_id, "event_id":event_id, "date":date, "time1":time1, "time2":time2, "extras":extras}).fetchone()[0]
        db.session.commit()
        return entry_id
    except:
        return -1

def add_weekly_entry(user_id, event_id, time_start, time_end, dow):
    try:
        sql = """INSERT INTO entries (user_id, event_id, start_time, finish_time, weekly)
                VALUES (:user_id, :event_id, :time_start, :time_end, :dow)"""
        db.session.execute(sql, {"user_id":user_id, "event_id":event_id, "time_start":time_start, "time_end":time_end, "dow":dow})
        db.session.commit()
        return True
    except:
        return False


def get_weekly_entries_for_user(user_id):
    sql = """SELECT en.weekly, e.id, e.name, en.start_time, en.finish_time, en.id
                FROM entries en LEFT JOIN events e ON en.event_id=e.id
                WHERE en.user_id=:user_id
                AND en.weekly IS NOT NULL
                ORDER BY en.weekly """
    return db.session.execute(sql, {"user_id":user_id})

#-------------------------------------------------------------------------------------------------
#mm. KALENTERIIN JA SUUNNITTELUNÄKYMÄÄN OSALLISTUJATILANNETIETOJEN HAKU suoritetaan alla näkyvillä funktioilla.
#haetaan tietokannasta yhdellä kyselyllä kaikkien osallistumiset viikoksi eteenpäin kaikille päiville niistä tapahtumista, joita käyttäjä seuraa
#sekä eritellään käyttäjän omat ilmoittautumiset omaksi listakseen.
#..tässä aika tarkkaa kuvausta mitä funktioissa tapahtuu, poistan osan näistä kommenteista ennen lopullista palautusta, kun onhan tämä loppujen lopuksi aika yksinkertainen.

#1/5
#funktio get_week: haetaan viikon ilmoittautumistiedot ja jaetaan sopiviin tietorakenteisiin kalenterinäkymää varten
#erotellaan käyttäjän omat ilmoittautumiset omaksi listakseen, palautetaan viikon tapahtumat -sanakirja ja käyttäjän omat tapahtumat -lista tuplena.
def get_week(user_id:int, week_wanted:int) -> dict:
    #tässä kyselyn muuttujaan tieto onko kalenterinäkymän vai suunnittelunäkymän tiedot haettavana; first_day 0, last_day 6 on viikko 1 eli kalenterinäkymä
    first_day = 0 if week_wanted == 1 else 6
    last_day = 6 if week_wanted == 1 else 13
    #sql -kyselyssä haetaan tapahtuman id ja nimi, ilmoittautuneen käyttäjän id, dow eli viikonpäivän nro (0=su, 1=ma,...,6=la)
    #päivä haetaan dow:n kautta, jotta viikottaiset vakioajat saadaan mukaan kalenterin osallistujatilanteeseen,
    #ilmoitettu aloitusaika, ilmoitettu lopetusaika, ilmoitetut lisäosallistujat, ilmoittautumisen tapahtuma id ja ilmoittautumisen id -numero
    #haetaan tauluista users_in_events, events ja entries käyttäjät, tapahtumat ja ilmoittautumiset
    #jossa aika on haluttu ajanjakso; joko ensimmäinen tai toinen viikko,
    #ue rooli alle neljä (4=käyttäjä ei seuraa tapahtumaa, 5=admin on estänyt käyttäjää seuraamasta tapahtumaa)
    #en.activella vakioajan voi laittaa (tulevaisuudessa) tauolle
    #tapahtuman tasovaatimus on pienempi tai sama kuin käyttäjälle määritelty taso
    #tulostaulun järjestys viikonpäivän ja ilmoittautumisen tapahtuma id:n mukaan
    sql = """SELECT DISTINCT ev.id, ev.name, en.user_id,
                        COALESCE(weekly, (SELECT DATE_PART('dow', en.date))) dow,
                        en.start_time, en.finish_time, en.extra_participants, en.event_id, en.id
                FROM users_in_events ue 
                LEFT JOIN events ev ON ue.event_id=ev.id 
                LEFT JOIN entries en ON ev.id=en.event_id
                WHERE ((en.date BETWEEN ((SELECT CURRENT_DATE) + INTEGER ':first_day') AND ((SELECT CURRENT_DATE) + INTEGER ':last_day'))
                        OR en.weekly IS NOT NULL)
                AND ue.role < 4
                AND en.active > 0
                AND (ev.event_level <= ue.user_level AND ue.user_id=:user_id)
                ORDER BY dow, en.event_id"""
    result = db.session.execute(sql, {"user_id":user_id, "first_day":first_day, "last_day":last_day}).fetchall()
    return add_structure(result, user_id, week_wanted)

#2/5
#jaetaan tieto listoille, jotka tallennetaan week -sanakirjaan tapahtumapäivän kohdalle
def add_structure(result, user_id, week_wanted):
    #alustus;
    #(kts.3/5) week -sanakirjan avaimena päivän indeksi alkaen tänään=0, huomenna=1, jne., lisätään sanakirjan arvoksi varsinainen päivämäärä päivän kohdalle
    #times_and_changes -listaan kirjataan yksittäisen päivän yksittäisen tapahtuman kaikki ilmoitetut alku ja loppuajat erikseen sekä niiden osallistujamäärän muutos (ym.tietoa ajankohtaan liittyen)
    #dow ja event_id -muuttujilla seurataan viikonpäivän ja tapahtuman vaihtumista kyselyn tulosta läpikäytäessä
    #entries_all_events -listaan kirjataan käyttäjän omat ilmoittautumiset, tämä on täysin erillinen lista joka saadaan tässä samalla
    week = prepare_dict_with_days(week_wanted)
    times_and_changes = []
    dow = 0 if not result else result[0][3] 
    event_id = 0 if not result else result[0][0]
    entries_all_events = []
    #käydään kyselyn tulos läpi
    for i in range(len(result)):
        #jos käyttäjän oma ilmoittautuminen, lisätään käyttäjän omien ilmoittautumisien listaan
        if user_id == result[i][2]:
            today = datetime.datetime.today()                    #pvm, event.name, alkuaika, loppuaika, dow, day_i, event_id, en.id
            entries_all_events.append(((today + datetime.timedelta(days=match_day_to_dict_week7i(result[i][3]))), result[i][1], result[i][4], result[i][5], result[i][3], match_day_to_dict_week7i(result[i][3]), result[i][0], result[i][8]))
        #jos läpikäytävä viikonpäivä tai tapahtuman id muuttuu (kyselyssä on järjestys näiden mukaan);
        #(kts.4/5) haetaan viikonpäivän perusteella oikea day eli kalenterin päivän indeksi tästä päivästä alkaen 0=tänään, 1=huomenna, jne.
        #otetaan talteen tältä päivältä sanakirjasta aiemmat päivän tapahtumat ja päivän varsinainen päivämäärä
        if dow != result[i][3] or event_id != result[i][0]:
            day = match_day_to_dict_week7i(dow)
            store_events = week[day][:-1] 
            store_day = week[day][-1]
            #jos molemmat muuttuvat; (kts.5/5) lasketaan tapahtuman osallistujat ilmoitettujen aikojen mukaan ja lisätään päivän kohdalle week -sanakirjaan
            #tyhjennetään lista seuraavaa tapahtumaa varten, vaihdetaan viikonpäivä ja tapahtuman id muuttujiin vaihtumisen seuraamista varten
            if dow != result[i][3] and event_id != result[i][0]:
                week[day] = [store_events[:]+calc_participants(sorted(times_and_changes))]+[store_day]
                times_and_changes = []
                dow = result[i][3]
                event_id = result[i][0]
            #jos vain viikonpäivä vaihtuu..
            elif dow != result[i][3]:
                week[day] = [store_events[:]+calc_participants(sorted(times_and_changes))]+[store_day]
                times_and_changes = []
                dow = result[i][3]
            #jos vain tapahtuman id vaihtuu..
            elif event_id != result[i][0]:
                week[day] = store_events[:]+calc_participants(sorted(times_and_changes))+[store_day]
                times_and_changes = []
                event_id = result[i][0]
        #jos mikään ei vaihdu..
        #times_and_changes -listaan lisätään lista, jossa alkuaika, tapahtuman nimi, dow, lisäosallistujat + itse, tapahtuman id
        #sorttauksen mahdollistamiseksi omalla rivillään loppuaika, tapahtuman nimi, dow, - (lisäosallistujat + itse), tapahtuman id
        times_and_changes.append([result[i][4].strftime("%H:%M"), result[i][1], result[i][3], result[i][6] + 1, result[i][0]])
        times_and_changes.append([result[i][5].strftime("%H:%M"), result[i][1], result[i][3], - (result[i][6] + 1), result[i][0]])
        #kyselyn viimeinen rivi vielä erikseen, kun viikonpäivä tai tapahtuma ei muutu, tapahtuman times_and_changes -lista käsitellään ja lisätään week -sanakirjaan
        if i == len(result) - 1:
            day = match_day_to_dict_week7i(dow)
            store_events = week[day][:-1]
            store_day = week[day][-1]
            week[day] = [store_events[:]+calc_participants(sorted(times_and_changes))]+[store_day]
    #print("---week",week)
    #print("---entries_all_events", entries_all_events)
    return week, sorted(entries_all_events) 

#3/5
#alustetaan week -sanakirjan avaimiksi 0-6, tänään=0, huomenna=1, jne.
def prepare_dict_with_days(week_wanted:int) -> dict:
    today = datetime.date.today()
    weekdays = {}
    for i in range(7):
        weekdays[i] = [today + datetime.timedelta(days=i)] if week_wanted == 1 else [today + datetime.timedelta(days=i+7)]
    return weekdays

#4/5
#haetaan viikonpäivää vastaava sanakirjan avain, esim. jos tänään (day=0) on keskiviikko (dow=3), viikonpäivän dow=3 tapahtumat kirjataan week -sanakirjan avaimelle day=0
def match_day_to_dict_week7i(dow) -> int:
    dow_now = datetime.date.today().weekday() + 1
    if dow < dow_now:
        day = 7 - (dow_now - dow)
    else:
        day = dow - dow_now
    return day

#5/5
#lasketaan yksittäisen tapahtuman osallistujien määrä alku- ja loppuaikojen perusteella sortatusta times_and_changes -listasta (jossa alkioina listat, jossa alku tai loppuaika, tapahtuman nimi, dow, muutos lisäosallistujat + itse, tapahtuman id)
def calc_participants(sorted_times_and_changes:list) -> list:
    participant_count = 0
    #lasketaan osallistujat participant_count -muuttujaa apuna käyttäen; jos rivin listalla alkuaika -tiedot, niin lisää osallistujia, jos loppuaika -tiedot niin vähentää osallistujia
    #vaihdetaan osallistujien määrän muutos -alkion paikalle todellinen osallistujien määrä kyseisestä ajankohdasta alkaen
    #lisätään viimeiseksi alkioksi seuraavan rivin aikatiedon sisältävä -alkio osoittamaan aika johon asti kyseinen osallistujamäärä pätee
    #poistetaan viimeinen osallistujarivi (joka kertoo, että osallistujia on nolla)
    for i in range(len(sorted_times_and_changes)-1):
        participant_count = participant_count + sorted_times_and_changes[i][3]
        sorted_times_and_changes[i][3] = participant_count
        sorted_times_and_changes[i].append(sorted_times_and_changes[i+1][0])
    sorted_times_and_changes.pop(-1)
    #käydään rivit läpi ja poimitaan sieltä rivit, joissa alkuaika on eri kuin loppuaika ja osallistujia on enemmän kuin nolla
    times_and_changes = []
    for row in sorted_times_and_changes:
        if row[0] != row[5] and row[3] != 0:
            times_and_changes.append(row)
    #print("---times and changes", times_and_changes)
    return times_and_changes
#--------------------------------------------------------------------------------

def get_all_own_entries_dict(all_entries:list) -> dict:
    #print("---all_entries", all_entries)
    #pvm, event.name, alkuaika, loppuaika, dow, day_i, event_id
    all_own_entries = {0:[],1:[],2:[],3:[],4:[],5:[],6:[]}
    for entry in all_entries:
        all_own_entries[entry[5]].append(entry)
    #print("---all own entries", all_own_entries)
    return all_own_entries

def delete_own_entry(entry_id):
    #print("---",entry_id)
    try:
        sql = """DELETE FROM entries WHERE id=:entry_id"""
        db.session.execute(sql, {"entry_id":entry_id})
        db.session.commit()
        return True
    except:
        return False

#TÄMÄ KYSELY KESKENERÄINEN
def friends_planning(user_id):
    first_day = 7
    last_day = 13
    sql = """SELECT DISTINCT u.name, e.name, en.start_time, en.finish_time,
                COALESCE(weekly, (SELECT DATE_PART('dow', en.date))) dow, en.event_id, en.date, en.weekly
                FROM users_in_events ue
                JOIN friends f ON ue.user_id=f.user_id1 OR ue.user_id=f.user_id2
                JOIN entries en ON en.user_id=f.user_id1 OR ue.user_id=f.user_id2
                JOIN users u ON u.id=en.user_id
                JOIN events e ON en.event_id=e.id
                WHERE ue.user_id=:user_id
                AND ue.role < 4
                AND u.id <> :user_id
                AND ((en.date BETWEEN ((SELECT CURRENT_DATE) + INTEGER ':first_day') AND ((SELECT CURRENT_DATE) + INTEGER ':last_day'))
                        OR en.weekly IS NOT NULL)
                AND (f.user_id1=:user_id OR f.user_id2=:user_id)
                AND (f.active=1 AND (f.user_id1=:user_id OR f.user_id2=:user_id))
                AND en.active > 0
                ORDER BY dow, en.event_id, u.name"""
    return db.session.execute(sql, {"user_id":user_id, "first_day":first_day, "last_day":last_day}).fetchall()

def find_entry(all_event_entries, entry_i):
    for entry in all_event_entries:
        if entry[7] == entry_i:
            return entry

def change_days_dow_to_i_dict(days, today):
    days_i = {}
    for i in range(7):
        dow_wanted = (today + datetime.timedelta(days=i)).strftime("%w")
        days_i[i] = days[int(dow_wanted)]
    #print("--days_i", days_i)
    return days_i

def get_participants(date) -> list:
    sql = """SELECT e.name, u.name, en.start_time, en.finish_time, extra_participants, m.content
                FROM entries en JOIN users u ON en.user_id=u.id
                JOIN events e ON en.event_id=e.id
                JOIN messages m ON en.id=m.entries_id
                WHERE (en.date=:date OR en.weekly=(SELECT DATE_PART('dow', :date)))
                AND en.active=1
                ORDER BY e.name, en.start_time"""
    return db.session.execute(sql, {"date":date}).fetchall()