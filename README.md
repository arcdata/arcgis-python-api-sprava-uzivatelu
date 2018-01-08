# Automatizovaná správa uživatelů v organizaci ArcGIS Online (Portal for ArcGIS)

Autoři: Vladimír Zenkl, Zdeněk Jankovský, ARCDATA PRAHA, s.r.o.

----
V následujícím textu budeme pro organizaci ArcGIS Online a Portal for ArcGIS používat též souhrnné označení „Portál“.

Pokud má Portál více (mnoho) pojmenovaných uživatelů, je často třeba je hromadně spravovat. Například v naší firmě máme organizaci ArcGIS Online určenou pro účely školení. Po každém kurzu je třeba ve všech studentských účtech smazat obsah a změnit hesla. Nebo třeba ve škole je třeba na konci školního roku, resp. když studenti opouštějí školu, jejich účty zrušit a na začátku nového školního roku přidat pojmenované uživatele pro nové studenty.

Hromadnou správu pojmenovaných uživatelů je velmi pracné a frustrující provádět ručně, ale naštěstí je možné ji automatizovat. Pro celou oblast automatizace správy Portálu lze použít [jedno ze dvou řešení](http://server.arcgis.com/en/portal/latest/administer/windows/scripting-and-automation-for-your-portal.htm). V tomto příspěvku se zaměříme pouze na správu uživatelů pomocí ArcGIS Python API. Cílem tohoto článku je uvést do problematiky na jednoduchém příkladu a poskytnout tak odrazový můstek pro realizaci vlastního řešení. Podrobnosti jsou uvedeny v [dokumentaci](http://server.arcgis.com/en/portal/latest/administer/windows/scripting-with-the-arcgis-python-api.htm).

### Co je k tomu potřeba

Pro vytvoření skriptu automatizujícího práci s Portálem je třeba pythonovský balíček (site package) `arcgis`. Nejprve se tedy přesvědčíme, zda tento balíček máme instalovaný a případně jej nainstalujeme. K tomu využijeme manažer pythonovských balíčků Conda, který je součástí ArcGIS Pro. Spustíme ArcGIS Pro a otevřeme libovolný projekt. Na kartě Projekt klikneme na volbu Python a podíváme se, zda seznam Installed Packages obsahuje balíček `arcgis`. Pokud ne, pomocí Add Packages jej vyhledáme a naistalujeme.

### Začínáme vytvářet skript

Pro práci s funkcemi balíčku `arcgis` je třeba používat takové prostředí Pythonu, které je obsluhováno prostřednictvím manažeru balíčků v rámci instalace ArcGIS Pro, tedy např. interaktivní okno Pythonu v ArcGIS Pro, Python IDLE nebo webové prostředí Jupyter notebooks, které je vhodné pro interaktivní práci. Pro další výklad nezáleží na tom které prostředí použijeme.
> **Poznámka:** pokud pro začátek chceme použít základní prostředí Python IDLE, musíme použít to, které se nachází v instalaci ArcGIS Pro, typicky `C:\Program Files\ArcGIS\Pro\bin\Python\envs\arcgispro-py3\Scripts\idle.exe`, nikoliv to, které je určeno pro aplikaci ArcMap!

### Ukázky funkcí

> V následujících ukázkách jde o způsob volání jednotlivých funkcí, takže pro jednoduchost nejsou ošetřovány možné chybové stavy.

#### Připojení k Portálu

Nejprve importujeme balíček `arcgis`, resp. tu jeho část, která slouží našemu účelu:
```python
from arcgis.gis import GIS
```
a vytvoříme připojení k Portálu:

```python
portalURL = 'URL organizace ArcGIS Online, resp Portalu'
adminName = 'uzivatelskeJmenoSpravce'
adminPwd  = 'hesloSpravce'

portal = GIS(portalURL,adminName,adminPwd)
```

#### Získání seznamu uživatelů, které je třeba zpracovat

Nyní získáme seznam pojmenovaných uživatelů (objektů typu `arcgis.gis.User`):
```python
uzivatele = portal.users.search()
```
Pokud v metodě search neuvedeme žádný parametr, bude získán seznam všech uživatelů, přesněji řečeno maximálně prvních 100 uživatelů ze seznamu setříděného vzestupně podle uživatelských jmen. Pro změnu tohoto nastavení můžeme použít parametry `query`, `max_users`, `sort_field`, `sort_order` a `outside_org`. Viz [Podrobný popis syntaxe pro funkce search](http://resources.arcgis.com/en/help/arcgis-rest-api/#/Search_reference/02r3000000mn000000/)

Například chceme, aby získaný seznam neobsahoval aktuálně přihlášeného administrátora a uživatele s uživatelským jménem 'student03':
```python
uzivatele = portal.users.search(query='!student03 & !{}'.format(adminName))
```

Častější případ je, že chceme zpracovat pouze uživatele, kteří splňují složitější kritéria, například je budeme chtít filtrovat podle znaků v uživatelském jméně, podle členství ve skupině nebo podle přiřazení určité role. V takových případech nestačí parametr `query` a bude vhodnější do metody `search()` nevkládat žádný parametr, tj. získat seznam všech členů:
```python
uzivatele = portal.users.search()
```

Několik příkladů na zpracování seznamu uživatelů:

1. Výběr uživatelů podle jména

   Pro snazší správu pojmenovaných uživatelů je vhodné, když jejich uživatelská jména sestavujeme podle schématu. Například první tři písmena představují zkratku studijního oboru, např. 'geo\_student01', 'bio\_student01' apod. Pro výběr uživatelů studijního oboru geo, tj. těch, jejichž uživatelské jméno začíná na znaky 'geo\_', pak provedeme jednoduše třeba takto:
   ```python
   zpracujUzivatele = [u for u in uzivatele if u.username.startswith('geo_')]
   ```
   Zde pak není problém doplnit seznam uživatelských jmen, které naopak nechceme zpracovávat. Tedy například chceme zpracovat uživatele u uživatelskými jmény začínajícími na 'geo\_', ale s výjimkou uživatelů 'geo\_student07' a 'geo\_student11':
   ```python
   nezpracuj = ['geo_student07', 'geo_student_11']
   zpracujUzivatele = [u for u in uzivatele if u.username.startswith('geo_') and u.username not in nezpracuj]
   ```

2. Výběr podle příslušnosti do skupin

   Například chceme vybrat uživatele, kteří jsou členy skupin pojmenovaných 'školení A' nebo 'projekt 1', ale pouze ty, kteří nejsou vlastníky těchto skupin.
   ```python
   hledejSkupiny = ['školení A','projekt 1']
   vybraneSkupiny = [sk for sk in portal.groups.search() if sk.title in hledejSkupiny]
   clenoveSkupin = []
   for skupina in vybraneSkupiny:
	  for clen in skupina.get_members()['users']: # viz poznamka
		 if not clen in clenoveSkupin:
			clenoveSkupin.append(clen)
	```
   > **Poznámka**: metoda .get_members() vrací [slovník, v němž klíčem je vztah člena ke skupině](http://esri.github.io/arcgis-python-api/apidoc/html/arcgis.gis.toc.html?highlight=get_members#arcgis.gis.Group.get_members)

   Takto získaný seznam clenove obsahuje uživatelská jména jako řetězce. Proto musíme ještě získat seznam objektů těchto uživatelů:
   ```python
   zpracujUzivatele = [u for u in uzivatele if u.username in clenoveSkupin]
   ```

3. Výběr podle uživatelských rolí

   Výběr uživatelů podle přiřazených uživatelských rolí je již poněkud složitější záležitostí a přesahuje rámec tohoto stručného návodu. Proto zde uvedeme jen nástin postupu na jednoduchém příkladu:
   Předpokládejme, že chceme získat seznam všech uživatelů, kteří mají přiřazenu uživatelskou roli pojmenovanou 'Student1'.
   Nejprve je třeba projít seznam všech rolí v Portálu, tj. objektů `arcgis.gis.Role`, a vybrat požadovanou:
   ```python
   for r in portal.users.roles.all():
	  if r.name == 'Student1':
		 vybranaRole = r
   ```
   Nyni můžeme projít seznam uživatelů a vybrat ty, kteří mají přiřazenou vybranou roli. Pozor, v seznamu uživatelů musíme porovnávat ID role, ne její jméno!
   ```python
   zpracujUzivatele = [u for u in uzivatele if u.role == vybranaRole.role_id]
   ```

   > **Tip:** pomocí dotazů na vlastnosti objektu Role lze získat mj. informaci o oprávněních dané role. Díky tomu můžeme například získat seznam uživatelů, jejichž role umožňuje editaci prvků a veřejné sdílení položek:
   ```python
   vybraneRoleID = []
   for r in portal.users.roles.all():
	  if 'portal:user:shareToPublic' in r.privileges or 'features:user:edit' in r.privileges:
		 vybraneRoleID.append(r.role_id)
   zpracujUzivatele = [u.username for u in uzivatele if u.role in vybraneRole]
   ```
   Podrobnosti najdete v [dokumentaci](https://developers.arcgis.com/python/guide/accessing-and-managing-users)


4. Výběr podle dostupných kreditů

   Chceme vybrat ty uživatele, kterým zůstává k dispozici méně než 1/10 přiřazených kreditů:
   ```python
   zpracujUzivatele = [u for u in uzivatele if u.availableCredits < u.assignedCredits / 10]
   ```

   Přiřazení kreditů uživatelům je popsáno v [dokumentaci](https://developers.arcgis.com/python/guide/administering-your-gis/#Allocating-credits-to-a-user)


#### Vlastní zpracování získaného seznamu uživatelů

V následující ukázce všem uživatelům ze získaného seznamu
- smažeme veškerý obsah
- změníme heslo
- změníme jazykovou verzi webových stránek jejich účtu.

1. Smazání obsahu

   ```python
   def smazObsah(uziv):
	  obsah = portal.content.search("owner:"+uziv.username)
	  for polozka in obsah:
		 try:
			polozka.delete()
			print("Smazana polozka: {}".format(polozka.name))
		 except Exception as e:
			print(u"Doslo k chybe pri odstranovani polozky ",e,"\nale pokracuji...")
   ```


2. Změna hesla

   V tomto případě bude záležet na tom, jakým způsobem máme vytvořená hesla. Zde předpokládáme, že uživatelské jméno každého uživatele končí dvoumístným číslem uživatele a hesla všech uživatelů mají stejný základ a na konci hesla je také číslo uživatele. Například:
   - uživatel 'geo_student01' má heslo 'st_Geo-01' a chceme je změnit na 'studentGeo-01'
   - uživatel 'geo_student02' má heslo 'st_Geo-02' a chceme je změnit na 'studentGeo-02'
   - atd.

   POZOR, funkce .reset() vyžaduje znalost aktuálního hesla! Zde předpokládáme, že si uživatel heslo sám nezměnil.

   ```python
   def zmenHeslo(uziv, staryZakladHesla, novyZakladHesla):
	  cisloNaKonciHesla = uziv.username[-2:]
	  stareHeslo = staryZakladHesla + cisloNaKonciHesla
	  noveHeslo  = novyZakladHesla + cisloNaKonciHesla
	  print ("\nZmena hesla z {} na {}".format(stareHeslo,noveHeslo))
	  if uziv.reset(stareHeslo,noveHeslo):
		 print("OK")
	  else:
		 print (">>>>> POZOR: HESLO NEZMENENO!")
   ```

3. Změna jazykové verze uživatelského rozhraní

   ```python
   def zmenLocale(uziv,noveNastaveni):
   """noveNastaveni muze byt bud 'cs' nebo 'en'"""
   if noveNastaveni in ['cs','en']:
	  cultureDict = {'cs':['cs', 'CZ'], 'en':['en', 'US']}
	  print ("Zmena jazyka uzivatele na: ", noveNastaveni)
	  student.update(culture=cultureDict[noveNastaveni][0], region=cultureDict[noveNastaveni][1])
   else:
	  print("CHYBA v zadani jazykove verze!")
   ```

4. Vlastní zpracování

   Na závěr provedeme vlastní zpracování jednotlivých uživatelů, například:

   ```python
   smazatObsah  = True
   zmenitHeslo  = True
   zmenitLocale = True

   stareHeslo = 'st_Geo-'
   noveHeslo  = 'studentGeo-'

   jazyk = 'cs'

   for uzivatel in zpracujUzivatele:
	  print("\n-----------")
	  print(uzivatel.username)

   if smazatObsah:
	  smazObsah(uzivatel)

   if zmenitHeslo:
	  zmenHeslo(uzivatel,stareHeslo,noveHeslo)

   if zmenitLocale:
	  zmenLocale(uzivatel,jazyk)

   print("\nHotovo.")
   ```

#### Odstranění uživatelů a přidání nových

Odstranění vybraných uživatelů je jednoduché:

```python
for u in zpracujUzivatele:
	u.delete()
```

Přidání nových uživatelů je dobře popsáno v [dokumentaci](https://developers.arcgis.com/python/guide/accessing-and-managing-users/#creating-new-user-accounts)

### Závěr

Další možné změny v nastavení Portálu a pojmenovaných uživatelů jsou uvedeny v [dokumentaci](https://developers.arcgis.com/python/guide/).

V případě, že byste měli zájem, abychom vám pomohli s řešením automatizované správy Vaší organizace ArcGIS Online nebo Portal for ArcGIS, [obraťte se na nás](mailto:sluzby@arcdata.cz) a rádi Vám v rámci konzultačních služeb poradíme či vytvoříme skripty na míru.


### Užitečné odkazy
- [Přehled nápovědy](https://developers.arcgis.com/python/guide/)
- [Příklady skriptů](https://developers.arcgis.com/python/sample-notebooks/)
- [Referenční příručka](http://esri.github.io/arcgis-python-api/apidoc/html/)
