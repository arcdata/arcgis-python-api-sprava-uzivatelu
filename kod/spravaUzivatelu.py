from arcgis.gis import GIS

## Definice pripojeni k portalu
portalURL = 'https://mujportal.maps.arcgis.com'
adminName = 'uzivatelskeJmenoAdministratora'
adminPwd  = 'heslo'

portal = GIS(portalURL, adminName, adminPwd)

## Ziskani uzivatelu z portalu
uzivatele = portal.users.search()
## Vyber uzivatelu
zpracujUzivatele = [u for u in uzivatele if u.username.startswith('geo_')]
print("Bude zpracovano uzivatelu: {}".format(len(zpracujUzivatele)))

## Funkce pro praci s uzivateli
def smazObsah(uziv):
        obsah = portal.content.search('owner:' + uziv.username)
        for polozka in obsah:
                try:
                        polozka.delete()
                        print('Smazana polozka: {}'.format(polozka.name))
                except Exception as e:
                        print (u'Doslo k chybe pri odstranovani polozky ', e, '\nale pokracuji...')

def zmenHeslo(uziv, staryZakladHesla, novyZakladHesla):
        cisloNaKonciHesla = uziv.username[-2:]
        stareHeslo = staryZakladHesla + cisloNaKonciHesla
        noveHeslo  = novyZakladHesla + cisloNaKonciHesla
        print ("\nZmena hesla z {} na {}".format(stareHeslo,noveHeslo))
        try:
                uziv.reset(stareHeslo,noveHeslo)
                print("heslo zmeneno OK")
        except Exception as e:
                print (">>> POZOR: HESLO NEZMENENO z duvodu chyby: {}".format(e))
                print ("Pravdepodobne nesouhlasi zadane stareHeslo se skutecnym aktualnim heslem.")

def zmenLocale(uziv, noveNastaveni):
        """noveNastaveni muze byt bud 'cs' nebo 'en'"""
        if noveNastaveni in ['cs','en']:
                cultureDict = {'cs':['cs', 'CZ'], 'en':['en', 'US']}
                print ("Zmena jazyka uzivatele na: ", noveNastaveni)
                uziv.update(culture=cultureDict[noveNastaveni][0], region=cultureDict[noveNastaveni][1])
        else:
                print("CHYBA v zadani jazykove verze!")

## Nastaveni prepinacu
smazatObsah  = False
zmenitHeslo  = False
zmenitLocale = False

## Nastaveni hesla uzivatelu
stareHeslo = 'StudentGeo_'
noveHeslo  = 'h180501_geo_'

## Nastaveni jazyka
jazyk = 'cs'

## Vlastni zpracovani
for uzivatel in zpracujUzivatele:
        print("\n-----------")
        print(uzivatel.username)

        if smazatObsah:
                smazObsah(uzivatel)

        if zmenitHeslo:
                zmenHeslo(uzivatel, stareHeslo, noveHeslo)

        if zmenitLocale:
                zmenLocale(uzivatel, jazyk)

print("\nHotovo.")
