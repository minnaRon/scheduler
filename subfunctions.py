import os, datetime, users

def check_username(name):
    if len(name) < 2 or len(name) > 35:
        return "Tunnuksen tulee sisältää 2-35 merkkiä"  
    if users.check_exist(name) > 0:
        return "Tunnus on jo käytössä, valitse toinen tunnus"
    return "ok"

def check_name(name, user_id):
    if len(name) < 2 or len(name) > 35:
        return "Nimen tulee sisältää 2-35 merkkiä"  
    if users.check_exist(name) > 0:
        if name != users.get_username(user_id):
            return "Nimi on jo käytössä, valitse toinen nimi"
    return "ok"

def check_password(password1, password2):
    if password1 != password2:
        return "Salasanoissa oli eroa"
    if password1 == "":
        return "Salasana oli tyhjä"
    return "ok"
  
def check_times_dow(times_of_own_entries_for_week, dow, start_time, finish_time):
    if start_time == "" or finish_time == "":
        return "Aikojen valinta oli puutteellinen, aika puuttui, tarkista ajat"
    if start_time < finish_time:
        if times_of_own_entries_for_week[dow]:
            start_time = datetime.datetime.strptime(start_time, "%H:%M").time()
            finish_time = datetime.datetime.strptime(finish_time, "%H:%M").time()
            for earlier_entry in times_of_own_entries_for_week[dow]:
                start = earlier_entry[1]
                end = earlier_entry[2]
                if not (start_time >= end or finish_time <= start):
                    return "Aika menee päällekkäin päivän toisen ilmoittautumisesi kanssa, peru ilmoittautumisia tarvittaessa"
                times_of_own_entries_for_week[dow] = times_of_own_entries_for_week[dow] + [(0,start_time,finish_time)]
        return "ok"
    else:
        return "Osallistumisesi lisäys ei onnistunut, aloitusaika oli suurempi tai yhtäsuuri kuin lopetusaika tai toinen ajoista puuttui, tarkista valitsemasi ajat"

def change_list_to_dict(wanted_key, all_entries):
    all_own_entries = {0:[],1:[],2:[],3:[],4:[],5:[],6:[]}
    for entry in all_entries:
        all_own_entries[entry[wanted_key]].append(entry)
    return all_own_entries

def change_days_dow_to_i_dict(days, today):
    days_i = {}
    for i in range(7):
        dow_wanted = (today + datetime.timedelta(days=i)).strftime("%w")
        days_i[i] = days[int(dow_wanted)]
    return days_i

def add_weekday(friends_plans:list) -> list:
    days = {0:"SU", 1:"MA", 2:"TI", 3:"KE", 4:"TO", 5:"PE", 6:"LA"}
    friends_plans_w = []
    for entry in friends_plans:
        entry = list(entry)
        entry[4] = days[entry[4]]
        friends_plans_w.append(entry)
    return friends_plans_w
