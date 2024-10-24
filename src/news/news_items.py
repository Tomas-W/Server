from datetime import datetime, timedelta
import random


def random_dates(count=20):
    start_date = datetime.now() - timedelta(weeks=3)
    end_date = datetime.now()
    return sorted(datetime.fromtimestamp(random.randint(int(start_date.timestamp()), int(end_date.timestamp()))).strftime("%d %b %H:%M") for _ in range(count))



def _get_news_dict() -> dict:
    data = {
        1: {
            "header": "Retourname",
            "title": "Retourname Streeckgenoten Grillworst naturel",
            "code": 999,
            "important": "Je moet onderstaand artikel onmiddellijk uit de verkoop nemen. Zorg dat de winkelvoorraad op 0 (nul) staat. De allergenen declaratie klopt niet.",
            "grid_cols": ["Nasa", "Artikelomschrijving", "Verpakking/inhoud"],
            "grid_rows": ["687307", "Streeckgenoten Grillworst naturel", "Ca 120 gram"],
            "info_cols": ["Rode zakken", "Kassablokkade", "Winkelvoorraad op 0", "Retoursturen", "Mogelijk nog geleverd", "Klantenretouren", "Boetes NVWA (NL) / FABB (BE)", "Callcenter"],
            "info_rows": ["Je haalt het artikel ongeacht de code uit het schap en de koelcel. Je verpakt het in de rode code 999-plastic zakken die je eerst in standaard 23 cm CBL-fust plaatst",
                          "De kassa blokkeert bij het scannen van bovengenoemd artikel. In de instructie Een code 999 artikel bij de kassa verwerken lees je hoe je de kassa kunt deblokkeren.",
                          "Vandaag, 16 mei 2024, wordt de eerste retourafspraak geactiveerd in de handterminal. Zet deze artikelen onmiddellijk in de retourafspraak en meld de retourafspraak compleet. Zo wordt de voorraad in Wink bijgewerkt",
                          "De 999 procedure is pas volledig uitgevoerd zodra de voorraad op 0 (nul) staat. Je controleert na het compleet melden van de retourafspraak of de voorraad daadwerkelijk op nul staat. Als dit niet het geval is tel je de voorraad handmatig naar nul.",
                          "Je zet de CBL-fusten op een aparte container en je doet er een rode code 999 containerhoes overheen. Je stuurt de artikelen met de eerstvolgende reguliere DC-wagen retour.",
                          "Je controleert de afleveringen de eerstvolgende 24 uur ook op bovengenoemd artikel. Als je het nog geleverd krijgt, stuur je ook deze artikelen retour en zet je de voorraad (opnieuw) op nul. Nog geleverde artikelen plaats je ook in rode zakken in 23cm fust onder een rode code 999 containerhoes. Je ontvangt in de komende 4 dagen nog 2 keer een retourafspraak voor het retoursturen van eventuele leveringen in de komende 24 uur.",
                          "Als klanten het artikel terugbrengen naar de winkel dan registreer je dat op OKG-vergoeden. Daarmee wordt het artikel automatisch administratief vernietigd. Vervolgens gooi je het artikel weg in de vuilnisbak.",
                          "We rapporteren aan de Nederlandse Voedsel- en Waren Autoriteit (NVWA) en het Belgisch Federaal Agentschap voor de veiligheid van de voedselketen (FAVV) wat onze actuele administratieve winkelvoorraad is. Op basis van dit rapport deelt de NVWA/FAVV boetes uit als de code 999 niet juist blijkt uitgevoerd in winkels. Het is dus (naast de veiligheid voor consumenten) heel belangrijk dat de winkelvoorraad op 0 staat. \nEen extern callcenter belt alle winkels om te wijzen op dit bericht. De medewerkers van het callcenter hebben geen inhoudelijke informatie. Je kunt met vragen niet bij hen terecht. Als je inhoudelijke vragen hebt, maak hiervoor dan een case aan in Questie"],
            "author": "Halil Suzulmus & Dionne Vonk",
        },
        2: {
            "header": "Retourname",
            "title": "Retourname 3 varianten filet americain",
            "code": 999,
            "important": "Je moet onderstaande artikelen onmiddellijk uit de verkoop nemen. Zorg dat de winkelvoorraad op 0 (nul) staat. Er is gevaar voor de volksgezondheid.",
            "grid_cols": ["Nasa", "Artikelomschrijving", "Verpakking/inhoud"],
            "grid_rows": ["83461", "Filet americain naturel", "150 gram",
                          "83469", "Filet americain mager", "150 gram",
                          "772036", "Filet americain peper", "150 gram"],
            "info_cols": ["Rode zakken", "Kassablokkade", "Winkelvoorraad op 0", "Retoursturen", "Mogelijk nog geleverd", "Klantenretouren", "Boetes NVWA (NL) / FABB (BE)", "Callcenter"],
            "info_rows": ["Je haalt de artikelen ongeacht de code uit het schap en de koelcel. Je verpakt het in de rode code 999-plastic zakken die je eerst in standaard 23 cm CBL-fust plaatst",
                          "De kassa blokkeert bij het scannen van bovengenoemde artikelen. In de instructie Een code 999 artikel bij de kassa verwerken lees je hoe je de kassa kunt deblokkeren",
                          "Vandaag, 31 mei 2024, wordt de eerste retourafspraak geactiveerd in de handterminal. Zet deze artikelen onmiddellijk in de retourafspraak en meld de retourafspraak compleet. Zo wordt de voorraad in Wink bijgewerkt.",
                          "De 999 procedure is pas volledig uitgevoerd zodra de voorraad op 0 (nul) staat. Je controleert na het compleet melden van de retourafspraak of de voorraad daadwerkelijk op nul staat. Als dit niet het geval is tel je de voorraad handmatig naar nul. ",
                          "Je zet de CBL-fusten op een aparte container en je doet er een rode code 999 containerhoes overheen. Bij verschillende code 999 retourafspraken tegelijkertijd zet je de artikelen per retourafspraak op een aparte container. Je stuurt de artikelen met de eerstvolgende reguliere DC-wagen retour.",
                          "Je controleert de afleveringen de eerstvolgende 24 uur ook op bovengenoemde artikelen. Als je het nog geleverd krijgt, stuur je ook deze artikelen retour en zet je de voorraad (opnieuw) op nul. Nog geleverde artikelen plaats je ook in rode zakken in 23cm fust onder een rode code 999 containerhoes. Je ontvangt in de komende 4 dagen nog 2 keer een retourafspraak voor het retoursturen van eventuele leveringen in de komende 24 uur.",
                          "Als klanten het artikel terugbrengen naar de winkel dan registreer je dat op OKG-vergoeden. Daarmee wordt het artikel automatisch administratief vernietigd. Vervolgens gooi je het artikel weg in de vuilnisbak. Klanten kunnen ook terugkomen met het artikel NLW Duitse biefstuk (nasanummer 60793). De winkels hebben hier geen voorraad meer van maar klanten kunnen dit artikel nog wel thuis hebben en retour brengen. \nEen extern callcenter belt alle winkels om te wijzen op dit bericht. De medewerkers van het callcenter hebben geen inhoudelijke informatie. Je kunt met vragen niet bij hen terecht. Als je inhoudelijke vragen hebt, maak hiervoor dan een case aan in Questie."],
            "author": "Halil Suzulmus & Fred Heijman",
        },
        3: {
            "header": "WORP",
            "title": "WORP week 35 Bakkerij update",
            "code": 111,
            "important": "We krijgen erg veel positieve geluiden over de nieuwe WORP van onze collega’s en klanten. Zo zien we veel verkopen van de bakkerpuntjes in de winkels waar deze goed gepresenteerd zijn! Ook Streeckgenoten laat een mooie vlucht in omzet zien.",
            "grid_cols": [],
            "grid_rows": [],
            "info_cols": ["Communicatiemiddelen", "Presentatie gebak", "Worstenbroodje", "Broodhulpje", "Beschikbaarheid op de Bakkerij", ""],
            "info_rows": ["Wat nog een aandachtspunt is, zijn alle communicatiemiddelen rondom de nieuwe WORP. Zorg ervoor dat je de flatcards met nieuw (TIB: 29075), productinformatiekaartjes ophangt bij alle producten. Desem Carré kaartjes zijn fout gedrukt en dienen te vervangen worden door productinformatiekaartjes waarbij alleen Carré. Je hebt deze ontvangen in de comco van week 35. Streeckgenoten middelen en de permanente multibuy kaartjes goed presenteert. Hiermee kunnen we duidelijk aan onze klanten communiceren dat we nieuwe producten hebben en mooie aanbiedingen! Inlegvel Streeckgenoten kan je middels TIB bestellen met het volgende nummer: 27263)",
                          "Petit Patisserie verpakkingen met vier gebakjes erin gaan in de bak. De verpakkingen met twee gebakjes presenteer je op de plank. Daardoor maken we optimaal gebruik van de beschikbare ruimte. Van de verpakking met twee gebakjes kan je twee verpakkingen achterelkaar kwijt op de plank. Een voorbeeld van Excellent gebak. De excellent taarten presenteer je in de bak. De excellent taartpunten presenteer je op de plank.",
                          "Ook krijgen we Questies binnen over het worstenbroodje. Het worstenbroodje is een ontdooi artikel, dit artikel moet niet gebakken worden. Net als onze andere ontdooiproducten (donuts etc.) is dit artikel wel gekoppeld aan een bakprogramma, omdat deze anders niet zichtbaar is in het Bakplan. Het worstenbroodje moet 180 minuten ontdooit worden en kan daarna direct gevuld worden in het schap. Deze ontdooi je buiten de koeling, zo is het resultaat uiteindelijk het lekkerst. Je mag het worstenbroodje ook ’s nachts laten ontdooien net zoals onze Liefde en Passie broden. Zorg er dan wel voor dat het worstenbroodje altijd in een afgesloten verpakking ontdooid wordt.",
                          "In week 37 ontvang je een broodhulpje met alle nieuwe artikelen. Wij vragen je om niet zelf te printen, maar de levering via de comco af te wachten.",
                          "Vanaf deze week worden onze oude vertrouwde Petit croissant weer geleverd! Daarnaast zijn er bij de lancering van de WORP helaas wat uitdagingen geweest en nog gaan met betrekking tot beschikbaarheid, waardoor nog niet alle nieuwe artikelen in de winkels liggen. We begrijpen dat dit een grote verstoring is en we hiermee klanten teleurstellen. Petit Patisserie banket is een heel nieuw concept met nieuwe verpakkingen en nieuwe artikelen waar we gezamenlijk met leverancier hard aan werken om deze z.s.m. beschikbaar te maken. Naar verwachting zal het grootste deel volgende week volledig beschikbaar zijn. Verder zullen de hardlopers volgende week weer beter beschikbaar zijn. We werken dagelijks keihard aan het oplossen van deze problemen om te zorgen dat de artikelen zo snel mogelijk weer beschikbaar zijn voor de winkels, maar bovenal voor de klant."],
            "author": "Team bakkerij",
        },
        4: {
            "header": "Multibuy",
            "title": "Permanente multibuy petit croissant en bakkersbroodjes",
            "code": 111,
            "important": "Deze week (week 38) is weer de multibuy gestart met een permanente actie op de Bakkersbroodjes en AH Petit Croissant.",
            "grid_cols": ["Nasa", "Artikel"],
            "grid_rows": ["833034", "Petit Croissant",
                          "20141", "Bakkersbroodje bastille",
                          "20143", "Bakkersbroodje matisse"],
            "info_cols": ["Multibuy"],
            "info_rows": ["Wij vragen je om voor de nieuwe multibuy het second placement meubel in te zetten en hierin de AH Petit Croissant, Bakkersbroodje Bastille en Bakkersbroodje Matisse te doen."],
            "author": "Team bakkerij",
        },
        5: {
            "header": "Bonuskorting",
            "title": "Mogelijk problemen met verrekenen bonuskorting 23-8 (3)",
            "code": 222,
            "important": "De problemen met het verrekenen van bonus(box)korting en koopzegels zijn opgelost.",
            "grid_cols": [],
            "grid_rows": [],
            "info_cols": ["Korting gemist"],
            "info_rows": ["Mogelijk komen er ook na vandaag nog klanten die bonuskorting gemist hebben terug. We vragen je daarom de bonusfolder van deze week (week 34) goed te bewaren. Zo kun je deze klanten ook volgende week zo goed mogelijk met behulp van de OKG-regeling helpen. Mocht je toch nog problemen ondervinden, dan kun je contact opnemen met de hard- en softwarelijn op 088 – 659 292. Dit is het laatste bericht over dit procesincident."],
            "author": "Team Procesincidenten",           
        },
        
        
    }
    return data


def get_news_items() -> list[dict]:
    data = _get_news_dict()
    return [data[key] for key in sorted(data.keys())]

