# AETERNA LOOKUPS bővítési terv – structured értéklisták

## Kiindulás

A Hibakategória mező szétbontása jelenleg elvetett irány. A következő feladat a LOOKUPS bővítése, főként a 22 oszlopos runtime/export mezők validációjához. A program által használt végleges kártyalista később a 7. EXPORT_RUNTIME lapból készül, ezért a LOOKUPS-nak nemcsak a CARDS_MASTER adminisztratív mezőit, hanem a structured mezőket is támogatnia kell.

## Javasolt új LOOKUPS-oszlopok

- `Zóna_Felismerve értékek`
- `Kulcsszavak_Felismerve értékek`
- `Trigger_Felismerve értékek`
- `Célpont_Felismerve értékek`
- `Hatáscímkék értékek`
- `Időtartam_Felismerve értékek`
- `Értelmezési_Státusz értékek`

A `Feltétel_Felismerve` teljes értékkészletét nem javasolt normál LOOKUPS-listába emelni, mert jelenleg több száz egyedi feltételmintát tartalmaz. Később külön condition-pattern szótárként érdemes kezelni.

## Összefoglaló számok

| LOOKUPS oszlop | Mező | Oszlopszabvány érték | CARDS_MASTER érték | IMPORT_ORIGINAL érték | CARDS_MASTER nem szabványos | IMPORT_ORIGINAL nem szabványos | Összes javasolt/figyelt érték |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Zóna_Felismerve értékek | Zóna_Felismerve | 11 | 14 | 14 | 3 | 3 | 17 |
| Kulcsszavak_Felismerve értékek | Kulcsszavak_Felismerve | 12 | 14 | 13 | 2 | 1 | 15 |
| Trigger_Felismerve értékek | Trigger_Felismerve | 45 | 110 | 46 | 70 | 7 | 119 |
| Célpont_Felismerve értékek | Célpont_Felismerve | 37 | 84 | 34 | 52 | 0 | 89 |
| Hatáscímkék értékek | Hatáscímkék | 59 | 115 | 64 | 60 | 9 | 124 |
| Időtartam_Felismerve értékek | Időtartam_Felismerve | 11 | 33 | 11 | 24 | 0 | 35 |
| Értelmezési_Státusz értékek | Értelmezési_Státusz | 4 | 24 | 4 | 20 | 0 | 24 |

## Fontos döntési pontok

1. `blank` és `none`: a 22 oszlopos szabvány több mezőben `blank` értéket ír, a munkafájl viszont gyakran `none`-t is használ. Dönteni kell, hogy mindkettő engedélyezett-e, vagy később egységesítés történik.
2. `graveyard` és `void`: a szabványban még `graveyard` szerepel, de a javított CARDS_MASTER már több helyen `void` értéket használ. Ez terminológiai döntést igényel az Üresség gépi nevére.
3. `trap` vs `jel` / `sign`: a korábbi legacy értékeket nem célszerű hivatalosként engedélyezni, de átmeneti aliasként érdemes követni.
4. `Trigger_Felismerve`, `Célpont_Felismerve` és `Hatáscímkék`: a CARDS_MASTER sok olyan értéket használ, amely nincs az oszlopszabványban. Ezeket nem szabad mind automatikusan hivatalossá tenni; külön kell választani a valódi új szabványjelölteket, aliasokat és javítandó értékeket.
5. `Értelmezési_Státusz`: a jelenlegi mező státuszértékeket és auditfolyamat-jelöléseket is tartalmaz. Vagy a LOOKUPS listát kell kibővíteni ezekkel, vagy hosszabb távon külön mezőt kell fenntartani az auditfolyamat státuszaira.

## Első gyakorlati átvezetési javaslat

Első körben a LOOKUPS lapra csak a hivatalos oszlopszabvány-értékeket és a ténylegesen gyakori munkafájl-üresértékeket (`blank`, `none`) érdemes felvenni. A nem szabványos, de használt értékek külön auditlistában maradjanak, amíg nem döntünk róluk.

A teljes értéklista és javasolt műveletek a TSV-fájlban találhatók.
