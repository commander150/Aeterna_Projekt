---
artifact_id: AET-DOC-DOCUMENT-EDITOR-SPECIFICATION
kind: document
type: specification
version: "0.1"
lifecycle: active
integration: current
authority: technical-contract
generated: false
depends_on:
  - AET-DOC-DOCUMENT-GOVERNANCE
  - AET-DOC-DOCUMENT-UPDATE-WORKFLOW
  - AET-DOC-PROJECT-PLAN
supersedes: []
---

# AETERNA Document Editor – MVP Specification

## 1. Cél és authority-határ

Az AETERNA Document Editor az AETERNA Document System funkcionális authoring
felülete a meglévő governed document workflow fölött. Célja, hogy a managed
Markdown dokumentumok megnyitását, szerkesztését, előnézetét, ellenőrzését és az
explicit emberi alkalmazás előkészítését egy összefüggő munkafolyamatban tegye
elérhetővé.

Az Editor nem új governance-rendszer, nem második dokumentum-authority, és nem
helyettesíti a repository natív metadatáját vagy a governed workflow-t. A
validációt, a tervezést és az alkalmazást a meglévő production workflow végzi.
Az ember marad a tartalom, az identity, az authority, az alkalmazás és a Git
handoff döntési authorityje.

## 2. Működési alapelvek

Az MVP kötelező alapelvei:

```text
HUMAN-DIRECTED
LOCAL-FIRST
GOVERNED
REVIEW-FIRST
```

- **HUMAN-DIRECTED:** minden canonical változás emberi szándékból indul, és
  explicit emberi döntéssel alkalmazható.
- **LOCAL-FIRST:** az alapvető dokumentummunka és a governed workflow helyben,
  külső szolgáltatástól függetlenül használható.
- **GOVERNED:** az Editor a current dokumentum-governance és az elfogadott
  operation contractok szerint működik.
- **REVIEW-FIRST:** a candidate, a validáció, a plan és a diff az apply előtt
  megtekinthető; hibás vagy driftelt input nem válhat csendben canonical
  állapottá.

## 3. MVP dokumentumformátum és hatókör

Az első MVP szerkeszthető dokumentumformátuma a natív YAML front matterrel
rendelkező managed Markdown. Az Editor megőrzi a stabil artifact identityt, a
canonical pathot, a fájl byte-konvencióját és a governance által védett
metadata-határokat.

Az MVP két dokumentumműveletet szolgál ki:

1. meglévő managed Markdown artifact governed UPDATE művelete;
2. új managed Markdown artifact explicit, ember által kezdeményezett governed
   CREATE művelete.

## 4. Meglévő dokumentum UPDATE folyamata

```text
open
→ edit
→ candidate
→ validation
→ plan-update
→ diff/review
→ explicit human apply
```

Az Editor lehetővé teszi egy managed dokumentum kiválasztását és megnyitását,
majd a szerkesztett teljes tartalmat candidate-ként kezeli. A candidate-et a
governed workflow validálja és determinisztikus UPDATE planhez köti. Az ember az
apply előtt áttekinti a tervet és a diffet. A canonical repository-állapotot
csak explicit emberi apply módosíthatja.

## 5. Új dokumentum CREATE folyamata

```text
explicit New Document
→ human-approved identity/path/authority
→ candidate
→ validation
→ plan-create
→ diff/review
→ explicit human apply
```

A New Document műveletet az ember indítja. Az artifact ID, a canonical path, az
authority, a dependencyk és az initial version végleges értéke explicit emberi
elfogadást igényel. Az Editor ezekkel az inputokkal candidate-et készíthet, majd
a production governed workflow-val validálja és CREATE planhez köti. Az apply
pontosan a jóváhagyott dokumentumot hozhatja létre; collision, invalid input
vagy baseline drift esetén a művelet blokkolt.

## 6. Kötelező MVP-felületek

### 6.1 Dokumentumlista és megnyitás

Az Editor megjeleníti a governed workflow által feloldható managed Markdown
dokumentumokat, és lehetővé teszi egy dokumentum kiválasztását és megnyitását.
A managed dokumentumlistában legalább az artifact ID, a title, a canonical path
és a version látható.
A lista nem válik a natív metadata vagy a repository fölötti authorityvé.

### 6.2 Markdown szerkesztés és előnézet

Az Editor biztosít Markdown-szerkesztést és a candidate olvasható előnézetét. A
preview tájékoztató nézet; a canonical tartalom továbbra is a repositoryban
alkalmazott fájl byte-tartalma.

### 6.3 Metadata-megjelenítés és segítség

Az Editor megjeleníti és validálja a natív metadatát, ismerteti az engedélyezett
értékeket, javaslatokat adhat, és segítheti a candidate előkészítését. CREATE
esetén az alábbi végleges értékeket nem találhatja ki vagy canonicalizálhatja
csendben:

- artifact ID;
- canonical path;
- authority;
- dependencies;
- initial version.

Ezek mindegyike explicit emberi elfogadást igényel.

### 6.4 Validáció

Az Editor láthatóvá teszi a governed workflow validációs eredményét, beleértve a
blokkoló diagnosztikákat. Sikertelen validáció mellett apply nem ajánlható fel
sikeres műveletként, és az input nem válhat canonical állapottá.

### 6.5 Plan, diff és review

Az Editor az apply előtt megjeleníti az operation típusát, a cél artifactot, a
várható changed pathokat, a dependency impactot és a releváns diffet. A plan és
a candidate közötti drift új validációt és új tervet igényel.

### 6.6 Explicit save/apply

A szerkesztés menthető candidate állapotba anélkül, hogy canonical repository
állapotot változtatna. A governed apply külön, explicit emberi művelet. Az Editor
nem kezelheti a candidate mentését implicit applyként.

### 6.7 New Document

Az Editor külön New Document akciót biztosít, amely az ember által jóváhagyott
identity-, path-, authority-, dependency- és initial-version inputokból indul.
Az akció a CREATE candidate és plan review-jáig vezet; a canonical létrehozás
külön explicit apply.

## 7. Governed workflow integráció

Az Editor a repository current production workflow-ját használja. UPDATE esetén
a feloldás és impact vizsgálat után `plan-update`, CREATE esetén `plan-create`
készíti a review-zandó tervet. Mindkét műveletet ugyanaz az explicit `apply`
entry point alkalmazza a plan schema szerinti dispatch-csel. A review evidence
ellenőrzésére a `verify-review` szolgál.

Az Editor nem kerülheti meg a fresh scan, baseline, target, metadata,
dependency, generated-output, scope vagy transaction ellenőrzéseket. Nem írhat
közvetlenül tracked canonical dokumentumot a governed apply megkerülésével.

A `project/generated/artifacts_registry.json` és a
`project/generated/DOCUMENT_INDEX.md` derived/generated output. Az Editor nem
szerkesztheti ezeket kézzel canonical inputként; frissítésük kizárólag a
governed workflow determinisztikus generálási folyamatán keresztül történhet.

## 8. Opcionális AI-segítség határa

Az AI opcionális; az Editor AI nélkül is teljes értékűen használható. Engedélyezett
AI-segítség lehet:

- szöveg draftolása és átírása;
- összefoglalás;
- metadata- és dependency-javaslat;
- consistency megfigyelés;
- candidate előkészítés.

```text
AUTONOMOUS_DOCUMENT_GENERATION = OUT_OF_SCOPE
```

Az AI nem döntheti el autonóm módon, hogy új canonical dokumentum szükséges; nem
hozhat létre canonical dokumentumot emberi kezdeményezés nélkül; nem választhat
végleges artifact ID-t vagy pathot; nem választhat vagy változtathat végleges
authorityt; nem írhatja át automatikusan a human-maintained dependenteket; és
nem stage-elhet, commitolhat vagy pusholhat. Az AI-output explicit emberi
elfogadásig candidate vagy proposal.

## 9. Git handoff határa

Az MVP nem futtat automatikusan `git add`, `git commit` vagy `git push`
műveletet. A governed apply és a Git publication külön határ. Apply után az
ember áttekinti a repository változásait, és külön dönt a stagingről, commitról
és pushról.

## 10. Build-vs-adopt stratégia

```text
DOCUMENT_EDITOR_IMPLEMENTATION_STRATEGY = BUILD_VS_ADOPT_NOT_YET_DECIDED
```

A Document Editor funkcionális cél, nem előre eldöntött custom program. Az
implementáció előtt értékelni kell, hogy az MVP teljesíthető-e:

- meglévő alkalmazással;
- meglévő alkalmazás és plugin vagy konfiguráció kombinációjával;
- meglévő editor és AETERNA-specifikus tooling kombinációjával;
- hybrid megoldással;
- teljesen custom alkalmazással.

A teljesen custom alkalmazás nem alapértelmezett követelmény. Az értékelés
szempontjai az MVP-követelmények lefedése, a local-first működés, a governed
workflow integrációja, a karbantarthatóság és a szükséges custom fejlesztési
ráfordítás. Ez a specifikáció nem választ konkrét terméket, implementációs
nyelvet, frameworköt vagy GUI toolkitet.

## 11. Explicit MVP non-goals

Az első MVP-n kívül marad:

- generic batch editing;
- generic move vagy rename;
- általános retire/archive UI;
- XLSX editing;
- source-bundle editing;
- package-manifest editing;
- repository-wide automatic reference rewriting;
- automatic dependent-document rewriting;
- automatic Git staging, commit vagy push;
- autonomous AI document generation;
- DOCX import.

Ezek deferred képességek, nem véglegesen elutasított irányok.

## 12. Magas értékű post-MVP lehetőségek

Az alábbi lehetőségek nem blokkolják az MVP elfogadását:

- dokumentumkeresés és navigáció;
- dependency- és impact-vizualizáció;
- Git history és diff megjelenítés;
- dokumentumsablonok;
- AI-assisted authoring;
- AI-assisted consistency review;
- DOCX → governed Markdown import.

Ezek csak külön, indokolt későbbi scope-döntéssel válhatnak követelménnyé.

## 13. MVP acceptance criteria

### 13.1 Meglévő dokumentum UPDATE

Az UPDATE út akkor fogadható el, ha:

- managed Markdown dokumentum kiválasztható és megnyitható;
- a szerkesztett tartalom candidate-té válik;
- a candidate validálható;
- a governed UPDATE plan review-zható;
- a diff és a review az apply előtt látható;
- explicit emberi apply be tudja fejezni a műveletet;
- invalid input nem válhat csendben canonical állapottá.

### 13.2 Explicit CREATE

A CREATE út akkor fogadható el, ha:

- az ember explicit New Document műveletet indít;
- az ember által jóváhagyott identity, path és authority megadható;
- a dokumentumtartalom candidate-té válik;
- a candidate validálható;
- a governed CREATE plan review-zható;
- a diff és a review az apply előtt megtörténik;
- explicit emberi apply pontosan a jóváhagyott dokumentumot hozza létre;
- invalid vagy driftelt input blokkolt.

### 13.3 Biztonság

Az MVP biztonsági elfogadásához:

- nincs automatikus Git staging, commit vagy push;
- nincs autonóm canonical dokumentumgenerálás;
- a meglévő governance marad az authority;
- hibás governed művelet nem hagyhat hamisan elfogadott canonical állapotot.

## 14. Implementációs technológia

Ez a dokumentum azt határozza meg, mit kell az MVP-nek elérnie, nem azt, hogyan
kell megvalósítani. Implementációs nyelv, framework, UI toolkit vagy konkrét
külső termék nincs kiválasztva. A technológiai döntés a build-vs-adopt értékelést
követi.
