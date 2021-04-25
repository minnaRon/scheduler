# scheduler - aikatauluapulainen

2. välipalautus:
Tällä hetkellä sovelluksen toiminnallisuuksista jäsenenä kirjautuneen käyttäjän toiminnallisuudet ovat suurimmaksi osin valmiina ja kaikki nyt jäsenenä kirjautuneelle näkyvät toiminnot ovat testattavissa ja niiden tulisi toimia täysin (keskeneräiset toiminnallisuudet on poistettu näkymästä).
Admin -toiminnallisuudet ovat osittain valmiina ja testailtavaksi valmiit toiminnallisuudet on kirjoitettu asetukset -näkymässä vihreällä ja löytyvät myös alla luetteloituna. (Jotain puutteita määrityksissä siellä saattaa olla, ei pitäisi olla kuitenkaan mitään rikkovaa, joten uskaltaa testailla myös niitä.)
Käyttöoikeuksien tarkastaminen on edelleen köykäistä ja seuraavaksi lisäilen csrf -tarkistukset, tällä hetkellä tarkistuksia on vain joissain adminin toiminnoissa. Poikkeuksista suurin osa käsitellään jo, voi mahdollisesti olla joitain yksittäisiä vielä ilman poikkeuskäsittelyä. Koodi vaatii vielä hieman selkeyttä ja routes -tiedosto useampaan tiedostoon jakamista.

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
      käyttäjä voi kirjautua sisään ja ulos
      käyttäjä voi ilmoittaa kalenterissa itselleen sopivat tapahtuma-ajankohdat kaksi viikkoa eteenpäin
      käyttäjä voi perua ilmoittautumisiaan
      käyttäjä voi ilmoittaa lisäosallistujia ilmoittautuessaan erillisessä ilmoittautumisnäkymässä
      käyttäjä voi kommentoida ilmoittautuessaan erillisessä ilmoittautumisnäkymässä
      käyttäjä voi viestitellä muiden käyttäjien kanssa vapaasti kalenterinäkymässä
      käyttäjä näkee kalenterinäkymässä viikon osallistujatilanteen ja suunnittelunäkymässä hahmotelmaa seuraavasta viikosta
      käyttäjä voi vaihtaa kalenterissa näkyvän nimensä
      käyttäjä voi antaa adminille yhteystietonsa
      käyttäjä voi vaihtaa salasanansa

    • admin voi valita kalenterinäkymässään näkyvät tapahtumat (tämä tulee myös jäsenen ominaisuudeksi)
      admin voi vaihtaa ryhmän nimen
      admin voi vaihtaa ryhmän kuvauksen
      admin voi vaihtaa ryhmän liittymissalasanan
      admin voi luoda uusia tapahtumia
      admin voi muuttaa tapahtuman nimen, kuvauksen, minimi- ja maksimiosallistujamäärän ja tasomäärityksen
      admin voi poistaa tapahtuman käytöstä (ei poistu kokonaan)
      admin voi kirjoittaa kalenterinäkymässä erikseen näkyvän admin -viestin
      admin voi muuttaa jäsenen tasomääritystä tapahtumakohtaisesti tapahtumaan sopivaksi
      admin voi vaihtaa käyttäjän roolia jäsenestä adminiksi ja administa jäseneksi
      admin voi resetoida käyttäjän salasanan vastaamaan käyttäjän tunnusta

Sovellus on testattavissa [Herokussa](https://hobby-event-scheduler.herokuapp.com/).
