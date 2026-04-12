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
- ebben a korben nem tortent tomeges fajlmozgatas
- a jelenlegi fajlok tovabbra is a `stats/` gyokerszinten maradtak
- a fenti almappak a kovetkezo, kis lepeses cleanup-korok celhelyei

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

- `canonical_runtime_batch_1_summary.md`
- `canonical_runtime_batch_2_summary.md`
- `canonical_runtime_batch_3_summary.md`
- `canonical_runtime_batch_4_summary.md`
- `canonical_runtime_batch_5_summary.md`
- `canonical_runtime_batch_6_summary.md`
- `canonical_runtime_batch_7_summary.md`

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
- `canonical_runtime_batch_1_summary.md`
- `canonical_runtime_batch_2_summary.md`
- `canonical_runtime_batch_3_summary.md`
- `canonical_runtime_batch_4_summary.md`
- `canonical_runtime_batch_5_summary.md`

Megjegyzes:
- ez most csak jeloles
- ebben a korben nincs atmozgatva vagy torolve semmi

## Bizonytalan elemek

- `clan_audit_ignis_hamvaskez_by_card_type.md`
- `keyword_support_audit_ignis_hamvaskezű.csv`

Megjegyzes:
- ezeknel latszik nevkonvencios vagy duplikacios bizonytalansag
- kovetkezo cleanup-korben kulon ellenorizendo, hogy megorzendo alternativ nev-e vagy torteneti maradvany

## Javasolt kovetkezo kis cleanup-lepes

Legkisebb biztonsagos kovetkezo lepes:
- csak mappan beluli kategoriak dokumentalasa es egy rovid naming/placement szabaly rogzitese

Ez utan jo kovetkezo kor lehet:
- `stats/reports/`
- `stats/scripts/`
- `stats/runtime/`

elokeszitese csak ures almappakkal es egy mozgatasi tervvel, tenyleges fajlmozgatasi hullam nelkul.
