# scheduler - aikatauluapulainen

Loppupalautus:
Sovelluksen toiminnallisuuksien tulisi toimia täysin.

Sovelluksen kuvaus:

Sovelluksen avulla voidaan etsiä käyttäjien omiin aikatauluihin sopivat ajankohdat tapahtumille, niin että
sama ajankohta sopii riittävän monelle. Sovellus on ajateltu erityisesti harrasteryhmien käyttöön
esim. pelien (beach volley, padel, jne.) ajankohdan sopimiseen.
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
      käyttäjä näkee kalenterinäkymässä viikon osallistujatilanteen
      käyttäjä näkee erillisessä ilmoittautumisnäkymässä päivän osallistujat, tapahtumat ja osallistumisajat
      käyttäjä näkee suunnittelunäkymässä hahmotelmaa seuraavasta viikosta
      käyttäjä näkee suunnittelunäkymässä kaveriensa alustavien suunnitelmien tapahtumat ja osallistumisajat
      käyttäjä voi vaihtaa kalenterissa näkyvän nimensä
      käyttäjä voi antaa adminille yhteystietonsa
      käyttäjä voi vaihtaa salasanansa
      käyttäjä voi valita viikottaisia tapahtumakohtaisia vakioaikoja, joihin ilmoittautuminen on automaattista
      käyttäjä voi valita kalenterinäkymässään näkyvät tapahtumat
      käyttäjä voi tehdä kaveripyyntöjä
      käyttäjä voi hyväksyä kaveripyyntöjä
      käyttäjä voi poistaa kavereitaan ja omia kaveripyyntöjään

    • admin voi vaihtaa ryhmän nimen
      admin voi vaihtaa ryhmän kuvauksen
      admin voi vaihtaa ryhmän liittymissalasanan
      admin voi luoda uusia tapahtumia
      admin voi muuttaa tapahtuman nimen, kuvauksen, minimi- ja maksimiosallistujamäärän ja tasomäärityksen
      admin voi poistaa tapahtuman käytöstä (ei poistu kokonaan)
      admin voi kirjoittaa kalenterinäkymässä erikseen näkyvän admin -viestin
      admin voi muuttaa käyttäjän tasomääritystä tapahtumakohtaisesti tapahtumaan sopivaksi
      admin voi vaihtaa käyttäjän roolia jäsenestä adminiksi ja administa jäseneksi
      admin voi resetoida käyttäjän salasanan vastaamaan käyttäjän tunnusta
      admin voi poistaa käyttäjän tapahtumasta ja myös lisätä takaisin tapahtumaan
      admin voi estää käyttäjän kaikista tapahtumista ja myös palauttaa oikeudet takaisin kaikkiin tapahtumiin
      admin näkee käyttäjistä listan, jossa on käyttäjän rooli, tunnus, kalenterinimi, yhteystiedot ja liittymisaika

Sovellus on testattavissa [Herokussa](https://hobby-event-scheduler.herokuapp.com/).
Kaikki ominaisuudet ovat testattavissa, tarvittaessa admin -käyttäjätunnukset löytyvät labtoolin viestistä
viikolta kaksi.

Kaikkia suunniteltuja ominaisuuksia en ole ehtinyt vielä toteuttaa. Tulevat ominaisuudet on jo osittain koodissa otettu
huomioon ja siksi mainitsen niistä tässä:
Projekti jatkuu loppukesästä, jolloin mm. muutan sovelluksen moniryhmäiseksi,
minimi ja maksimiosallistujamäärät on tarkoitus hyödyntää jonotuksessa, osallistujatilanteen seurannassa ja tilanteen
värikoodauksessa css:n puolella, myös jäsenten hallinta odottelee vielä lisäkehitystä jäsenlistan osalta.
