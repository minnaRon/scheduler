# scheduler - aikatauluapulainen

Loppupalautus:
Kaikkien sovelluksen toiminnallisuuksien tulisi toimia ja ovat täysin kokeiltavissa.
(kts.viesti ohjaajalle readmen lopussa)

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
      ryhmän perustaja on admin, jonka roolia ei voi muuttaa

Sovellus on testattavissa [Herokussa](https://hobby-event-scheduler.herokuapp.com/).
Kaikki ominaisuudet ovat testattavissa, tarvittaessa admin -käyttäjätunnukset löytyvät labtoolin viestistä
viikolta kaksi.

Ohjaajalle:
Koska sovelluksesta tuli jokseenkin massiivinen tarkisteltava, niin kerron vähän itseni tiedostamista vikakohdista.
Sovelluksesta:
Sovelluksen perustoiminnot toiminevat jokseenkin hyvin. Keskeneräisiä toimintoja, jotka toimivat nyt kömpelösti:
Viikon kaksi suunnittelu (plan) virheen sattuessa ei tallenna uusista ajoista mitään. Viikon kaksi suunnittelu on tarkoitus
muuttaa niin, että kaikille päiville voi lisätä uusia ilmoittautumisia ja tallentaa kaikki kerralla ja vain virheelliset
ajat jäävät tallentamatta, joista sitten virheviestissä lista. Tätä en ehtinyt vielä laittamaan kuntoon.
Vakioaikojen peruminen poistaa nyt vakioajat myös kalenterista ja suunnittelusta, mikä on joko hyvä tai huono, selvinnee
kesän aikana. Valittu vakioaika jää näkyville, vaikka kalenterinäkymästä poistaa kyseisen tapahtuman näkymisen ja
vakioaikailmoittautuminen ei näin ollen näy myöskään muille, mikä on joko hyvä tai huono, selvinnee myös kesän aikana.
Tämän ominaisuuden toiminnallisuuden mietin vielä uusiksi kesän loppupuolella, nyt ei toimi vielä riittävän hyvin.
Uuden tapahtuman luomisessa voi luoda monta samannimistä tapahtumaa, jotta tapahtumat voidaan erotella eri tasoille.
Tämä ajatus on vielä kesken ja nykyinen toteutus ei ole riittävän toimiva, jotta voisi käyttää käytännössä. Tätä mietin vielä.
Jäsenlistanäkymä on keskeneräinen, tähän tulee vielä mahdollisuus järjestää lista eri parametreilla, myös asettelu muuttuu.
Yleensäkin css:n puolella layout on vähäistä ja siellä on alussa oleva ajatelma älypuhelinta ajatellen hieman ylimääräisenä.
Virheiden viestimistä lomakkeen sisällä erillisen näkymän sijaan en ehtinyt vielä toteuttaa. Virheiden tarkistus yleensäkin
toteutettaneen alustavasti osin JavaScriptillä, kunhan ehdin sitä hieman opiskella.
Koodista:
Koodi on hyvin yksinkertaista näin pelkillä pythonin perusteilla koodailtuna. Epäilen, että session -olion hyväksikäyttö
kasvanee, kunhan pääsen pythonin olioista perille. Apufunktioille on oma tiedosto subfunctions.py, näin pääsin suht hyvin
toisteisuudesta eroon. Kalenterin "moottorin" yhteyteen jätin siihen kuuluvat apufunktiot helpottamaan toiminnon tarkastelua.
Subfunctionsiin lisäsin kuitenkin yhden kyseisistä funktioista, koska käytin sitä muualla koodissa. Koodista saattaa löytyä
alkuajoilta jääneenä pari ylimääräistä funktiota, joita en itse paikallistanut.. tai sitten ei löydy. Tämä ei ihan varma..
toinen, mistä löytynee jonkinverran ylimääräisyyttä on kyselyjen tulostaulut. Sovelluksen "hahmottelu" kokonaisuudessaan koodiin
valmistui vasta tällä viikolla, kun sain friendsin lisäiltyä, jonka jälkeen aloin fiksailla pikkuongelmia ja siivoilla koodia.
Hahmotellessa käytin välillä hyväksi jo olevia kyselyitä ja lisäsin sinne tarvittavia sarakkeita.. mikä ei ollut kovinkaan viisasta..
Kyselyistä ehdin laittaa kuntoon sovelluksen nopeuteen eniten vaikuttavan ajantarkistuksen. Muutenkin kyselyistä ja koodista löytynee
sovelluksen nopeuteen vaikuttavia kohtia, joita voi vielä huomattavasti parannella, tätä en ehtinyt mietiskellä. Saa kertoa.
Koodissa on käytetty jokseenkin runsaasti muuttujia, jotta parametrit kertovat sisältönsä selkeästi. Tämä on joko hyvä tai huono.
Muuttujien ja funktioiden nimeäminen oli alkuaikana hieman ylimalkaista ja epäselkeää, tämä parantui loppua kohden, kun
funktioita alkoi olla jokseenkin paljon.. Viikonpäivä dow ja päivän indeksi tästä päivästä eteenpäin day_i toivat tässä oman
lisähaasteensa, ennenkuin ymmärsin nimetä ne selkeästi. Commitit ovat myös alkuaikana sisällöltään epämääräisiä, kunnes ymmärsin
ottaa käyttöön -p:n, jonka jälkeen commitit selkeytyivät. Loppuajan commitit lienevät selkeimpiä, kun keskityin kehittämään yhtä
ominaisuutta kerrallaan.
Csrf ja roolit mielestäni ovat aika hyvin koodissa mukana. Lisäilin "kommenttiviivoja" html tiedostoihin helpottamaan tarkastelua.
Yllättäen.. kaikkia suunniteltuja ominaisuuksia en ole ehtinyt vielä toteuttaa. Tulevat ominaisuudet ovat jo osittain koodissa
otettu huomioon: mm. sovellus muuttuu moniryhmäiseksi, minimi ja maksimiosallistujamäärät on tarkoitus hyödyntää jonotuksessa,
osallistujatilanteen seurannassa ja tilanteen värikoodauksessa css:n puolella, myös jäsenten hallinta odottelee vielä lisäkehitystä
jäsenlistan osalta.
Tarkoitukseni on testailla tätä protona kesän ajan ja jatkaa projektia loppukesästä, joten kaikki koodiin ja kehittämiseen liittyvät
kommentit ovat erittäin tervetulleita. Tämä projekti tullee olemaan varsinaisesti valmis vasta puolentoista vuoden päästä.
