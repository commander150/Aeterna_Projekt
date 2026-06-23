# stats/

Ez a mappa jelenleg vegyes szerepu tartalmat tartalmaz. A projektiranyito dokumentumok alapjan
nem szabad egyben kezelni runtime, audit, report es historical retegeket, ezert ez a fajl egy
kis kockazatu, atmozgatas nelkuli elso kategoriarendezes.

## Letrehozott celstruktura

Az aktualis cleanup-elokeszitesi korben a kovetkezo ures celmappak lettek letrehozva:

- `runtime/`
- `scripts/`
- `reports/`
- `reports/compliance/`
- `reports/batches/`
- `reports/domain_specific/`
- `reports/cleanup/`

Fontos:
- ebben a korben nem tortent tomeges fajlmozgas
- az elso tenylegesen athelyezett report-csoport a canonical runtime batch summaryk kore
- a tovabbi fajlok egyelore tovabbra is tobbsegeben a `stats/` gyokerszinten maradtak

## Aktiv runtime-kozeli elem

- `analyzer.py`

Megjegyzes:
- ez az egyertelmuen aktiv, hivatalos futasi ut kozeli `stats/` elem
- core runtime-hoz kapcsolodik, ezert nem szabad osszekeverni a report- vagy archive-retteggel

## Audit script-ek

- `cards_xlsx_audit.py`
- `full_card_analysis.py`
- `standard_cleanup_audit.py`
- `standard_engine_audit.py`

Megjegyzes:
- fejlesztoi tooling jellegu fajlok
- nem meccsfuttatasi runtime-elemek

## Compliance reportok

- `keyword_compliance_audit.md`
- `trigger_compliance_audit.md`
- `effect_tag_compliance_audit.md`
- `target_compliance_audit.md`
- `standard_engine_compliance_audit.md`
- `standard_only_engine_compliance_audit.md`
- `canonical_alias_map.md`
- `warning_triage_report.md`
- `top_20_standardization_gaps.md`
- `standard_cleanup_summary.md`
- `standard_integration_summary.md`

## Batch summaryk

- athelyezve ide: `stats/reports/batches/`
- a `canonical_runtime_batch_1_summary.md` - `canonical_runtime_batch_7_summary.md`
  fajlok most mar ebben az almappaban vannak

## Domain-specific reportok

- `clan_audit_ignis_hamvaskezu_by_card_type.md`
- `clan_audit_ignis_hamvaskez_by_card_type.md`
- `effect_support_audit_ignis_hamvaskezu_simple.csv`
- `keyword_support_audit_ignis_hamvaskezu.csv`
- `keyword_support_audit_ignis_hamvaskezű.csv`
- `keyword_support_validation_ignis_hamvaskezu.md`
- `trap_validation_ignis_hamvaskezu.md`
- `cards_per_card_analysis.md`
- `cards_metadata_enrichment.csv`

## Historical / archive-gyanus elemek

Jelen allapotban ide sorolhatok azok a reportok, amelyek:
- mar nem runtime-kozeli segedfajlok
- torteneti fejlesztesi allapotot rogzitnek
- de meg nincs kimondott archive helyuk

Elsodleges jeloltek:
- a mar korabban athelyezett canonical runtime batch summaryk
- egyes kesobbi cleanup- vagy torteneti reportok, ha mar lesz vegleges archive-struktura

Megjegyzes:
- a batch summaryk mar kulon almappaba kerultek
- ebben a korben ezen kivul nem tortent mas report-csoport atmozgatasa vagy torlese

## Bizonytalan elemek

- `clan_audit_ignis_hamvaskez_by_card_type.md`
- `keyword_support_audit_ignis_hamvaskezű.csv`

Megjegyzes:
- ezeknel latszik nevkonvencios vagy duplikacios bizonytalansag
- kovetkezo cleanup-korben kulon ellenorizendo, hogy megorzendo alternativ nev-e vagy torteneti maradvany

## Javasolt kovetkezo kis cleanup-lepes

Legkisebb kovetkezo biztonsagos lepes:
- egyetlen tovabbi, biztosan nem runtime report-csoport kulon mozgatasa

Jo jeloltek lehetnek kesobb:
- compliance reportok
- cleanup / standardizacios reportok

Fontos:
- tovabbra is csak egy-egy jol korulhatarolt report-csoportot erdemes mozgatni
- runtime-kozeli es script jellegu fajlokhoz tovabbra sem erunk ebben a cleanup savban
