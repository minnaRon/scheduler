# scheduler - aikatauluapulainen

1. välipalautus:
Tällä hetkellä sovellus on vielä täysin hahmotteluvaiheessa;
osa toiminnoista puuttuu, syötteiden tarkastaminen on puutteellista kuten myös
poikkeuksien käsitteleminen ja käyttöoikeuden tarkastaminen,
myös kyselyt ovat osittain löyhästi sinnepäin.
..joten tekemistä riittää vielä
Tiedostoista jossain määrin tarkastelua kestänee; schema.sql, app.py, db.py, users.py
loput aiheuttanevat tässä vaiheessa vain tutkijalleen harmaita hiuksia.

Sovelluksen kuvaus:

Sovelluksen avulla voidaan etsiä käyttäjien omiin aikatauluihin sopivat ajankohdat
tapahtumille, niin että sama ajankohta sopii riittävän monelle.
Sovellus on ajateltu erityisesti harrasteryhmien käyttöön esim. pelien (beach volley, padel, jne.)
ajankohdan sopimiseen.
Jokainen käyttäjä voi sovelluksessa merkitä itselleen sopivat ajankohdat kahdeksi viikoksi eteenpäin.
"Kalenterinäkymässä" näkyy seuraavien päivien osallistujatilanne viikon verran eteenpäin.

Tällä hetkellä
sovelluksen ominaisuuksia ovat:
    • käyttäjä voi rekisteröityä olemassa olevaan ryhmään
    • käyttäjä voi kirjautua sisään ja ulos
    • käyttäjä voi ilmoittaa kalenterissa itselleen sopivat tapahtuma-ajankohdat kaksi viikkoa 
      eteenpäin ja halutessaan myös kommentoida
    • käyttäjä näkee kalenterinäkymässä viikon osallistujatilanteen ja hahmotelmaa seuraavasta viikosta
    • admin voi luoda uusia tapahtumia

Sovellus on testattavissa [Herokussa](https://hobby-event-scheduler.herokuapp.com/).

