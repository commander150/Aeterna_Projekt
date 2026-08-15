# AETERNA – ProjectIgnis/Distribution ELEMZÉS

## VERZIÓ / DOKUMENTUMSTÁTUSZ

- **Dokumentumverzió:** 0.1
- **Dátum:** 2026-08-15
- **Státusz:** célzott content-distribution / localization / repository-composition source audit
- **Javasolt repository-útvonal:** `learning/analyses/projectignis__distribution.md`
- **Repository:** `ProjectIgnis/Distribution`
- **Vizsgált branch:** `master`
- **Vizsgált commit:** `54a6e2395c532648ff762540e9615319fac4f51b`
- **Fő technológia:** client resource repository / config / Git submodules
- **Licenc:** AGPL-3.0; egyes assetekhez/folderekhez külön licencek/credit szabályok tartozhatnak
- **Elsődleges AETERNA-érték:** runtime/distribution composition, content repository separation, path-based capability config, localization packaging, update/read policy
- **Vizsgálati korlát:** teljes EDOPro kliens loader, updater és assetlicenc-réteg nem került auditba
- **Nem AETERNA-szabályforrás.**

---

# 1. Projekt szerepe

A Distribution repository a klienshez szükséges resource/package réteg.

A README kifejezetten úgy írja le, mint:

> all assets for the game, except card images

Tartalmaz például:

- config;
- nyelvi stringeket;
- deckeket;
- fontokat;
- puzzleket;
- repository update configot;
- asseteket.

A szabálymag és a kártyatartalom több kapcsolódó repositoryból jön.

---

# 2. Composition by repository

A `.gitmodules`:

```text
script     -> ProjectIgnis/CardScripts
expansions -> ProjectIgnis/BabelCDB
puzzles    -> ProjectIgnis/Puzzles
```

A `configs.json` ezen túl update repositorykat is konfigurál.

## AETERNA tanulság

A release artifact összeállhat több külön authority/artifact rétegből:

```text
rules engine binary
canonical card data
ability/module content
localization
format policy
assets
examples/scenarios
```

Nem kell mindent egyetlen canonical table-be erőltetni.

---

# 3. Repository descriptor / capability config

A README szerinti repository config mezők:

- url;
- repo_path;
- has_core / core_path;
- data_path;
- script_path;
- pics_path;
- lflist_path;
- should_update;
- should_read;
- is_language;
- language;
- not_git_repo.

## Erős tanulság

A content source/deskriptor mondja meg, milyen capabilityt biztosít.

AETERNA későbbi package descriptor candidate:

```text
PackageKind
DataPath
AbilityModulePath
LocalizationPath
FormatPolicyPath
AssetPath
Dependencies
LoadPolicy
```

A konkrét formátum nem döntendő most.

---

# 4. Update és read policy külön

A config külön:

```text
should_update
should_read
```

Ez fontos különbség:

- egy source letölthető/frissíthető;
- de az aktuális runtime nem feltétlen aktiválja.

## AETERNA megfelelő

```text
installed
validated
published
enabled_for_format
loaded_for_match
```

külön state lehet.

Ne mossuk össze:

```text
package exists == mechanic active
```

---

# 5. Localization külön content layer

A Distribution külön language mappákban `strings.conf` állományokat tart.

A repository config külön language repository fogalmat is támogat.

## AETERNA tanulság

Localization legyen:

- card definition identityhoz kapcsolt;
- nem rules authority;
- verziózható;
- fallback policyval rendelkező;
- a runtime card definitiontől külön frissíthető, ha ezt a product design engedi.

---

# 6. Expansion loading

A README szerint az `expansions` könyvtárból a kliens képes olvasni:

- pics;
- scripts;
- CDB adatot;
- zip contentet;
- format listákat;
- akár compiled rules core verziókat.

## Pozitív tanulság

A content layer modularizálható.

## Negatív tanulság AETERNA számára

Nem akarjuk, hogy egy random expansion package tetszőleges compiled core-t vagy scriptet authoritative módon lecserélhessen explicit compatibility/security gate nélkül.

AETERNA:

```text
package capability allowlist
+ signature/fingerprint
+ compatibility validation
```

később szükséges lehet.

---

# 7. Format/list policy külön artifact

A forbidden/limited list külön repository/path capability.

Ez azt mutatja, hogy a játékhoz tartozó:

- card definition;
- rules implementation;
- deck/format legality

külön adatdomain.

## AETERNA candidate

```text
CardDefinitionRegistry
AbilityRegistry
FormatDefinition
DeckLegalityPolicy
```

ne ugyanazon schema jelentés legyen.

---

# 8. Asset provenance

A README explicit kéri a folderenkénti LICENSE/COPYING ellenőrzését.

## AETERNA tanulság

Release package provenance matrix:

```text
artifact
source
license
attribution
redistribution allowed?
```

különösen:
- card art;
- fonts;
- sounds;
- shader/textures;
- third-party libraries.

---

# 9. Amit érdemes átvenni elvi mintaként

1. composable distribution artifact;
2. package capability descriptor;
3. update vs activation külön;
4. localization külön layer;
5. format policy külön data domain;
6. dependency/submodule provenance;
7. release asset license matrix;
8. content modularity.

---

# 10. Amit nem szabad közvetlenül átvenni

1. arbitrary scripts/core replacement trust nélkül;
2. Git repo közvetlen runtime authorityként;
3. path convention mint rules contract;
4. AGPL repository kód/asset közvetlen átvétele;
5. EDOPro-specific config model.

---

# 11. Döntés

- **Distribution architecture:** P0
- **Localization/package composition:** P0
- **Activation/update separation:** P0
- **Asset provenance:** P1
- **Közvetlen átvétel:** nem
- **Clean-room architecture inspiráció:** igen.
