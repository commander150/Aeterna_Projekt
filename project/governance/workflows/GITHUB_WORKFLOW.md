---
artifact_id: AET-DOC-GITHUB-WORKFLOW
kind: document
type: workflow
version: "1.0"
lifecycle: active
integration: current
authority: operational-workflow
generated: false
depends_on:
  - AET-DOC-DOCUMENT-GOVERNANCE
  - AET-DOC-PROJECT-PLAN
  - AET-DOC-ENGINE-CHECKPOINT
supersedes: []
---

# AETERNA GitHub workflow

## 1. Cél és authority

Ez a dokumentum az AETERNA repository változtatásainak operatív GitHub-munkarendjét szabályozza. A dokumentum-governance, az aktuális projektterv és az engine checkpoint határozza meg, hogy mi az authority és mi a current projektállapot; ez a workflow azt rögzíti, hogyan jut el egy meghatározott változtatás a lokális implementációtól a távoli ellenőrzésig.

## 2. Canonical folyamat

```text
scope / planning
→ Codex local implementation + validation
→ review bundle
→ ChatGPT/human review
→ human approval
→ GitHub Desktop commit/push
→ remote verification
```

Egy munkakörnek világos célja, engedélyezett fájlköre, ellenőrzési kapuja és review-bizonyítéka legyen. Az implementáció nem terjesztheti ki saját hatáskörét egy következő mérföldkőre.

## 3. Scope és baseline

A munka megkezdése előtt rögzíteni kell legalább:

- az aktuális branchet és `HEAD`-et;
- a teljes worktree állapotot;
- a módosítható és védett fájlokat;
- a feladat által elvárt teszteket és kimeneteket;
- a tartalmi vagy bináris források hashét, ha az integritás része a feladatnak.

A dirty worktree önmagában nem tiltja a munkát. A már jelen lévő változásokat azonban külön kell azonosítani, és csak akkor szabad megérinteni, ha a feladat kifejezetten erre jogosít. Recovery candidate, kézi helyreállítás vagy más párhuzamos munka védett állapotnak számít; hash- vagy státuszeltérés esetén a feladatot meg kell állítani és a különbséget jelenteni kell.

## 4. Codex lokális implementáció

Codex alapértelmezett feladata a jóváhagyott scope lokális implementációja, ellenőrzése és review-ra előkészítése. Alapértelmezés szerint nem hajt végre `git add`, `git commit` vagy `git push` műveletet.

Az implementáció közben:

- csak a feladathoz szükséges fájlok változhatnak;
- a protected recovery állapotot változatlanul kell hagyni;
- archív vagy fagyasztott forrásra vonatkozó integritási szabályt hash-sel kell igazolni;
- generált nézetet a canonical forrásból, a repository toolingjával kell előállítani;
- váratlan eltérést nem szabad automatikus cleanup-pal elfedni.

## 5. Validáció és source-integrity gate

A review előtt le kell futtatni a scope szerinti legszűkebb teljes bizonyító tesztkört. Ennek része lehet unit test, fordítás, schema- vagy metadata-validáció, determinisztikus generálás, path-audit és whitespace-ellenőrzés.

A source-integrity gate PASS feltétele:

- a baseline `HEAD` a feladat alatt nem változott;
- a védett recovery fájlok és fagyasztott források hash-e változatlan;
- nincs scope-on kívüli új módosítás;
- content-identical move esetén a forrás- és célhash azonos;
- az `unpaired whole-file deletion` száma `0`;
- a teszt- és validációs eredmények teljesítik a feladat kapuját.

`Unpaired whole-file deletion` minden olyan megszüntetett durable source vagy artifact, amelynek nincs content-identical move-ja, replacement mellett megőrzött eredeti archív példánya vagy más explicit durable preservation dispositionje. A Git history nem minősül megfelelő párnak. Ezt a kaput commit approval előtt külön ellenőrizni kell; a scope-on kívüli, pre-existing protected recovery deletions külön védett baseline állapotként kezelendők.

Hiba esetén a review artifactnak meg kell őriznie a bizonyítékot; a hibát külön engedély nélkül nem szabad a scope kiterjesztésével javítani.

## 6. TEMP evidence és review bundle

Az átmeneti fixture, parancskimenet, hashlista és review bundle a Git által ignorált `TEMP/` alatt készül. Ezek review-bizonyítékok, nem current authority-k és nem kerülnek a commitba.

A review bundle legalább a következőket tegye ellenőrizhetővé:

- baseline és végső Git állapot;
- changed path lista és diff-összegzés;
- a releváns módosított tartalom;
- tesztparancsok, exit code-ok és teljes eredmények;
- integritási és determinisztikussági bizonyíték;
- ismert eltérés, bizonytalanság vagy scope violation.

## 7. Review és emberi jóváhagyás

A lokális eredményt a bundle és a diff alapján ChatGPT- vagy emberi review követi. A commit/push handoff csak akkor indulhat, ha:

1. a review eredménye elfogadható;
2. a forrásintegritás és a kötelező tesztkapu PASS;
3. a commitba kerülő útvonalak köre egyértelmű;
4. az ember jóváhagyta a változtatást.

## 8. Commit cohesion és commitüzenet

Egy commit egy fő célt szolgáljon. A közvetlenül kapcsolódó implementáció, teszt és dokumentáció együtt tartható, ha ugyanazt a változtatási egységet bizonyítja. Független runtime, dokumentációs rendezés, report, cleanup vagy tooling munka külön commitba kerüljön.

A commitüzenet röviden nevezze meg a területet és a tényleges változást:

```text
<terület>: <konkrét eredmény>
```

Példák: `docs: establish testing ownership` vagy `tests: add combat regression coverage`. Kerülendő a homályos `update`, `misc` és „mindent egyszerre” üzenet.

Nagyobb, kockázatos vagy több napos munkához külön branch használható. A branch neve jelezze a célt, például `docs/reference-ownership` vagy `runtime/trigger-fix`.

## 9. GitHub Desktop handoff

Az elfogadott változtatást az ember GitHub Desktopban veszi át:

1. ellenőrzi a repositoryt és a branchet;
2. összeveti a changed file listát a jóváhagyott scope-pal;
3. kizárja a protected recovery, `TEMP/`, build- és cache-tartalmat;
4. áttekinti a diffet és a commit kohézióját;
5. megadja a konkrét commitüzenetet;
6. commitol, majd pushol.

PowerShell vagy Git CLI nem a normál commit/push munkafolyamat ebben a projektben.

## 10. Remote verification

Push után ellenőrizni kell:

- a távoli branch és commit azonosítóját;
- hogy a várt fájlok megjelentek, a tiltottak pedig nem;
- a remote CI vagy más automatikus check eredményét, ha van;
- hogy a lokális és távoli végállapot között nincs megmagyarázatlan eltérés.

A feladat akkor zárható le, amikor a jóváhagyott commit a remote repositoryban ellenőrizhető, vagy a handoff dokumentáltan megállt egy jelentett blokkolónál.
