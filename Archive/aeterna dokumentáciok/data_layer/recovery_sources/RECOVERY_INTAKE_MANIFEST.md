# AETERNA data documentation recovery intake manifest

## Intake identity

- **Intake date:** 2026-09-24
- **Baseline commit:** `d90eb7d9195ddd7f4aebf0e2805115a1cf4df57d`
- **Intake purpose:** W3B.1 recovery and current data documentation synthesis
- **Lifecycle:** historical evidence
- **Authority:** none over current data documentation
- **Preservation rule:** exact whole-file preservation; existing Archive content immutable; new intake append-only

The four files below are complete recovery inputs. They are preserved independently of Git history and are not current authority.

## Preserved files

| Source filename | Source identity | Source status | Source SHA-256 | Archive path | Archive SHA-256 | Replacement current artifact | Verdict |
|---|---|---|---|---|---|---|---|
| `AETERNA_EXCEL_STRUKTURA_ES_OSZLOPSZABVANY_1.2.md` | HEAD blob at baseline commit | old current predecessor | `642FEC43BA4F2DAE77BA1283FB321F6A4998A5E7C37A48F5FEE7AF560FB779B7` | `Archive/aeterna dokumentáciok/data_layer/recovery_sources/AETERNA_EXCEL_STRUKTURA_ES_OSZLOPSZABVANY_1.2.md` | `642FEC43BA4F2DAE77BA1283FB321F6A4998A5E7C37A48F5FEE7AF560FB779B7` | `data/specifications/CARD_DATA_MODEL.md` | `IDENTICAL` |
| `AETERNA_EXCEL_STRUKTURA_ES_OSZLOPSZABVANY_1.3.md` | local protected recovery candidate | recovery candidate | `705E7FB0B627E483C0EF46DA3B1BE2423FBA9F53466727E6CF949A88A9B96F16` | `Archive/aeterna dokumentáciok/data_layer/recovery_sources/AETERNA_EXCEL_STRUKTURA_ES_OSZLOPSZABVANY_1.3.md` | `705E7FB0B627E483C0EF46DA3B1BE2423FBA9F53466727E6CF949A88A9B96F16` | `data/specifications/CARD_DATA_MODEL.md` | `IDENTICAL` |
| `AETERNA_MUNKAFOLYAMAT_ES_ADATKEZELES_1.2.md` | HEAD blob at baseline commit | old current predecessor | `762190D717C02921A679991498A0917FD7768737D0F14182B36CC09819C3C6F2` | `Archive/aeterna dokumentáciok/data_layer/recovery_sources/AETERNA_MUNKAFOLYAMAT_ES_ADATKEZELES_1.2.md` | `762190D717C02921A679991498A0917FD7768737D0F14182B36CC09819C3C6F2` | `data/workflows/CARD_DATA_WORKFLOW.md` | `IDENTICAL` |
| `AETERNA_MUNKAFOLYAMAT_ES_ADATKEZELES_1.3.md` | local protected recovery candidate | recovery candidate | `25599404B81300B8462F074BBB8C261898A04C2B552AC1DB60A619628763E526` | `Archive/aeterna dokumentáciok/data_layer/recovery_sources/AETERNA_MUNKAFOLYAMAT_ES_ADATKEZELES_1.3.md` | `25599404B81300B8462F074BBB8C261898A04C2B552AC1DB60A619628763E526` | `data/workflows/CARD_DATA_WORKFLOW.md` | `IDENTICAL` |

## Preservation outcome

```text
retired durable source files = 4
durably archived originals = 4
new current replacement documents = 2
UNPAIRED_WHOLE_FILE_DELETION = 0
```

The archived files and this manifest must not be edited in place. A later correction requires a new append-only intake artifact with its own provenance.
