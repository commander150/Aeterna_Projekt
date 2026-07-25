# AETERNA – SIMEYDOTME POKÉMON CARDS CSS HOLOGRAFIKUS EFFEKTEK ELEMZÉSE

## VERZIÓ / DOKUMENTUMSTÁTUSZ

- **Dokumentumverzió:** 0.1
- **Dátum:** 2026-07-25
- **Státusz:** első teljes repository-, effect-layer-, interaction-, performance-, provenance-, licenc- és AETERNA-adaptációs audit
- **Fő elemzési fájl:** `learning/analyses/simeydotme__pokemon-cards-css-holographic-effects.md`
- **Kapcsolódó katalógus:** az aktuális verziózott „AETERNA – LEARNING PROJECT CATALOG” dokumentum
- **Elsődleges repository:** `simeydotme/pokemon-cards-css`
- **Elsődleges demo:** `https://poke-holo.simey.me/`
- **Kapcsolódó hivatalos repository:** `simeydotme/pokemon-cards-151`
- **Kapcsolódó demo:** `https://poke-151.simey.me/`
- **Kapcsolódó külön interakciós komponens:** `simeydotme/hover-tilt`
- **Vizsgált elsődleges branch:** `main`
- **Vizsgált elsődleges commit:** `acb1197633e749a1fba4412231db2f6581586d00`
- **Elsődleges commit dátuma:** 2025-12-15
- **Vizsgált 151 commit:** `98030f941cdc4919b648457200277e29b60d5f5a`
- **Vizsgált Hover Tilt commit:** `5db58f38cbbfa20054ca2c21a144d866d304b34a`
- **Technológiai alap:** Svelte / JavaScript / CSS 3D transforms / gradients / masks / blend modes / filters
- **Repositorylicenc – Pokémon CSS projektek:** GPL-3.0
- **Hover Tilt licenc:** MPL-2.0
- **Külső vizuális asset- és attributionréteg:** Pokémon kártyaképek, Pokémon hátlap, külső Galaxy Holo, Vecteezy-hátterek, CDN-ről betöltött fóliatextúrák
- **AETERNA összehasonlítási bázis:** production C# engine authority + Godot presentation layer + viewer projection + determinisztikus transition/event rendszer
- **Összehasonlítási szabály:** minden megállapítás kizárólag az AETERNA rendszeréhez viszonyított
- **Vizsgálati korlát:** nem történt helyi browserprofilozás, WebGL/GPU capture, mobilteszt, Godot shaderport vagy pixelpontos vizuális összehasonlítás
- **Elsődleges AETERNA-érték:** adatvezérelt holografikus fóliaprofilok, pointer-/giroszkópvezérelt irizálás, többrétegű spektrum–minta–glitter–glare rendszer, maszkolt kártyarégiók
- **Elsődleges AETERNA-kockázat:** a demonstráció rendkívül nehéz webes effektlánc; a repository nem modul, a CSS/JS/Svelte összekapcsolt; közvetlen átvétel GPL- és assetkockázatot okozna
- **AETERNA-döntés:** a vizuális tudás kiemelten hasznos, de csak saját Godot CanvasItem shader- és `FoilProfile` rendszerként, clean-room módon építhető be

# 1. Vizsgált forráscsalád

## 1.1 Elsődleges projekt

```text
simeydotme/pokemon-cards-css
```

Célja a Pokémon Sword & Shield korszak különböző fizikai holografikus
fóliakezeléseinek CSS-alapú vizuális szimulációja.

A projekt nem általános kártyakomponens és nem kész játékmodul. A szerző saját
dokumentációja külön figyelmeztet arra, hogy:

- showcase és demonstráció;
- a CSS és JavaScript együtt szükséges;
- nem szétválasztható egyszerűen;
- a Svelte-komponensek nem általános frameworkadapterek;
- jelentős munka kell bármilyen más alkalmazáshoz;
- a teljes effekt rendkívül költséges a böngésző számára.

## 1.2 Kapcsolódó 151 projekt

```text
simeydotme/pokemon-cards-151
```

A Scarlet & Violet 151 kártyakorszak vizuális fóliaprofiljait mutatja be.

A technikai alap hasonló, de a rétegmodell több önálló presentationelemet tartalmaz:

```text
card image
shine
glitter
glare
glare2
mask / foil textures
```

## 1.3 Kapcsolódó Hover Tilt

```text
simeydotme/hover-tilt
```

Ez már külön, telepíthető Svelte 5 és Web Component tilt/glare komponens.

A fő tanulsága az AETERNA számára nem a közvetlen integráció, hanem az, hogy a
következő két felelősség elválasztható:

```text
pointer / orientation → tilt + glare coordinates
holographic material profile → visual layer composition
```

# 2. Vezetői összefoglaló

A látvány nem egyetlen hologramfilterből áll.

A rendszer több fizikailag különböző jelenséget közelít:

1. a kártya térbeli megdöntése;
2. a fólia spektrális színváltása;
3. irányfüggő, ismétlődő diffrakciós sávok;
4. lokális, pointerkövető glare;
5. fóliaminta vagy szemcsetextúra;
6. eltérő parallaxissal mozgó csillámrétegek;
7. maszkolt kártyarégiók;
8. középponttól és dőlésszögtől függő intenzitás;
9. ritkaságonként eltérő material recipe;
10. aktív kártyára korlátozott nagy részletesség.

A webes rendszer logikája röviden:

```text
pointer vagy device orientation
→ normalizált kártyakoordináta
→ rugós simítás
→ CSS változók
→ 3D kártyadőlés
→ spektrumminta eltolása
→ glare középpont
→ maszk és blend layer kompozíció
```

A legfontosabb AETERNA-következtetés:

> Nem „Pokémon-holo shadert” kell készíteni, hanem egy adatvezérelt,
> AETERNA-saját holografikus anyagrendszert, amely több különböző
> `FoilProfile` receptet képes megjeleníteni.

# 3. Eredet és repositoryállapot

## 3.1 Elsődleges repository

| Mező | Érték |
|---|---|
| Repository | `simeydotme/pokemon-cards-css` |
| Default branch | `main` |
| Vizsgált commit | `acb1197633e749a1fba4412231db2f6581586d00` |
| Commitüzenet | `improve perf & animation a little` |
| Commit dátuma | 2025-12-15 |
| Repository | public, nem archivált |
| Fő technológia | Svelte, JavaScript, CSS |
| Root licenc | GPL-3.0 |
| GitHub Actions workflow proof | nem talált |
| Vizsgált commit status | Vercel deployment status: failure |
| Szerzői minősítés | demonstráció / showcase, nem modul |

## 3.2 151 repository

| Mező | Érték |
|---|---|
| Repository | `simeydotme/pokemon-cards-151` |
| Default branch | `main` |
| Vizsgált commit | `98030f941cdc4919b648457200277e29b60d5f5a` |
| Repository | public, nem archivált |
| Fő technológia | Svelte, JavaScript, CSS |
| Root licenc | GPL-3.0 |
| GitHub Actions workflow proof | nem talált |
| Fő scope | Scarlet & Violet 151 fóliaprofilok |

## 3.3 Hover Tilt

| Mező | Érték |
|---|---|
| Repository | `simeydotme/hover-tilt` |
| Vizsgált commit | `5db58f38cbbfa20054ca2c21a144d866d304b34a` |
| Scope | tilt + glare interakciós komponens |
| Felület | Svelte 5 és Web Component |
| Licenc | MPL-2.0 |
| AETERNA-szerep | az interakciós koordinátamodell különválaszthatóságának referenciája |

# 4. A holografikus rendszer fogalmi rétegei

A webes source alapján az effekt több, külön vezérelhető rétegre bontható.

## 4.1 Base card

A normál kártyakép.

Feladata:

- kártyagrafika;
- szöveg;
- keret;
- illusztráció;
- normál alpha.

A holografikus shader nem írhatja olvashatatlanná a szabályszöveget.

## 4.2 Spectrum layer

Szivárványszerű, ismétlődő vagy folyamatos spektrum.

Forrásoldali eszközök:

- repeating linear gradient;
- hat színű „sunpillar” paletta;
- background position pointerfüggő eltolása;
- hue, overlay vagy color-dodge keverés.

Godot-megfelelő:

```text
angle
frequency
phase
spectrum palette
intensity
saturation
brightness
```

## 4.3 Diffraction / stripe layer

Vékony, irányított sávok, amelyek a kártyadőlésre változnak.

Forrásoldali minták:

- scanline;
- ismétlődő világos/sötét csík;
- két ellentétes szögű sáv;
- rotáció alapján változó sávszög.

Godot-megfelelő:

```text
stripe_angle
stripe_frequency
stripe_width
stripe_contrast
cross_stripe_strength
```

## 4.4 Pattern layer

Fizikai fóliát utánzó mintázat:

- cosmos;
- grain;
- noise;
- illusion;
- Poké Ball / Master Ball pattern;
- iridescent texture atlas;
- birthday holo;
- egyedi ritkasági textúra.

AETERNA-ban kizárólag saját készítésű:

```text
foil_pattern_texture
noise_texture
grain_texture
pattern_scale
pattern_seed
```

## 4.5 Glitter layers

A 151 rendszerben külön DOM-réteg:

```text
card__glitter
card__glitter::before
card__glitter::after
```

A két extra csillámréteg:

- eltérő textúrát használhat;
- egymással ellentétes irányban mozoghat;
- külön opacity görbével működhet;
- pointer top/left értékből parallaxist kap.

Godot-megfelelő:

```text
glitter_a_texture
glitter_b_texture
glitter_a_parallax
glitter_b_parallax
glitter_a_opacity_curve
glitter_b_opacity_curve
```

## 4.6 Glare layer

Pointerkövető radial gradient.

Funkciója:

- lokális fényfolt;
- csillanás;
- felület térbeliségének visszajelzése;
- hover/tilt kapcsolat láthatóvá tétele.

Godot-megfelelő:

```text
light_uv
glare_radius
glare_softness
glare_intensity
glare_color
glare_darkening
```

## 4.7 Secondary glare

A 151 változat egyes profiljai második glare-réteget is használnak.

Ez lehet:

- mask alapján korlátozott;
- screen/overlay/multiply jellegű;
- a középponttól mért távolságból vezérelt;
- ritkaságspecifikus.

## 4.8 Edge glow

A webes box-shadow rétegek:

- fehér él;
- arany vagy típusfüggő él;
- színes glow;
- fekete mélységi árnyék.

Godotban ezt nem célszerű ugyanabba a holo fragmentbe erőltetni.

Lehetséges külön:

```text
CardEdgeGlow
CardDropShadow
SelectionOutline
```

# 5. Interakciós koordinátamodell

## 5.1 Pointerből normalizált UV

A Card komponens:

1. lekéri a kártya képernyőtéglalapját;
2. kiszámítja a pointer lokális pozícióját;
3. százalékos 0–100 koordinátává alakítja;
4. középpont köré transzformálja;
5. clampeli és kerekíti;
6. több külön targetértékre remappeli.

AETERNA Godot-megfelelő:

```text
local_pointer = card_control.get_local_mouse_position()
uv = local_pointer / card_size
uv = clamp(uv, Vector2.ZERO, Vector2.ONE)
centered = uv * 2.0 - Vector2.ONE
```

## 5.2 Egy bemenetből több kimenet

Ugyanaz a pointer UV vezérli:

- a CardView dőlését;
- a spektrum background offsetet;
- a glare középpontját;
- a fóliaminta parallaxist;
- a középponttól mért intenzitást.

Ez fontos: a vizuális rétegek közös „fényirányból” kapják az adatot, ezért
összetartozónak érződnek.

## 5.3 Középponttól mért távolság

A webes logika:

```text
sqrt((x - 50)^2 + (y - 50)^2) / 50
```

AETERNA-megfelelő:

```text
pointer_from_center = clamp(length(uv - Vector2(0.5)) / 0.5, 0.0, 1.0)
```

Felhasználás:

- holo intensity;
- glitter opacity;
- saturation;
- brightness;
- edge glow;
- glare falloff.

## 5.4 Rugós simítás

A Svelte spring külön kezeli:

- rotation;
- glare;
- background offset;
- active-card translation;
- active-card scale;
- első popup extra rotációját.

Az interakció alatt feszesebb, visszaálláskor lágyabb springbeállításokat használ.

Godotban lehetséges:

- `SpringArm` jellegű saját numerikus simítás;
- kritikus csillapítás;
- exponential smoothing;
- Tween csak aktiválás/deaktiváláskor;
- frame-alapú shaderuniform-követés interakció alatt.

Javasolt:

```text
current = smooth_damp(current, target, velocity, smooth_time, delta)
```

## 5.5 Pointer event throttling

A fő repository legújabb commitja a pointeres springfrissítést
`requestAnimationFrame` ciklusba gyűjti.

Godot megfelelője:

- input event csak targetértéket ír;
- shaderuniformok legfeljebb egyszer frissülnek render frame-enként;
- nem minden `InputEventMouseMotion` hoz létre Tween objektumot;
- dirty flag használata.

```text
_input(event):
    target_uv = ...
    foil_dirty = true

_process(delta):
    if foil_dirty or animation_active:
        update_foil(delta)
```

# 6. Device orientation

A webes projekt mobilon:

- az első orientation readinget alaphelyzetnek tekinti;
- a későbbi beta/gamma értékeket ehhez képest számolja;
- clampelt ±16/±18 fokos tartományt használ;
- ugyanarra a tilt/glare/background rendszerre képezi.

AETERNA Godotban:

```text
Input.get_accelerometer()
Input.get_gravity()
Input.get_gyroscope()
```

csak platformfüggő adapteren keresztül használható.

Kötelező:

- kalibráció;
- zajszűrés;
- permission/platform fallback;
- reduced motion;
- desktop pointer fallback;
- giroszkóp nélküli eszköz fallback.

# 7. Kártya 3D-dőlés

A webes rendszer CSS perspective + rotateX/rotateY kombinációt használ.

A korábbi Fake3D Godot-audit tanulságával összhangban az AETERNA számára két
külön megoldás lehetséges:

## 7.1 CanvasItem fake-3D

- 2D Control;
- perspective shader;
- front/back TextureRect;
- Godot UI-layouttal jól együttműködik.

## 7.2 Valódi 3D Quad/Mesh

- pontosabb normál- és fénykezelés;
- drágább UI-integráció;
- külön SubViewport vagy 3D scene szükséges;
- több layer compositing bonyolultabb.

Első proofhoz CanvasItem ajánlott.

# 8. Maszkrendszer

A CSS projektek egyik legfontosabb technikája a maszkolás.

Nem minden fólia jelenik meg az egész kártyán.

Maszkolható például:

- csak az illusztráció ablaka;
- minden az illusztráció kivételével;
- teljes kártya;
- keret;
- külön EX-kontúr;
- karakterforma;
- ritkasági mintarégió;
- textúrázott szimbólumok.

## 8.1 CSS megoldás

- `mask-image`;
- luminance vagy alpha mask;
- `clip-path`;
- inverse polygon;
- több mask composite;
- pointerkövető radial mask.

## 8.2 AETERNA megoldás

A runtime package kártyánként vagy layouttemplate-enként hivatkozhat:

```text
foil_mask_id
art_window_mask_id
frame_mask_id
text_protection_mask_id
special_pattern_mask_id
```

A shader a maszk alapján:

```text
foil_strength *= mask.r
```

## 8.3 Szövegvédelem

A holografikus effekt nem ronthatja:

- képességszöveg;
- számérték;
- ikon;
- kulcsszó;
- célpontjelölés

olvashatóságát.

Javasolt külön `text_protection_mask`, amely az intenzitást csökkenti a kritikus UI-régiókban.

# 9. Foil és mask assetek

A webes projektek:

- kártyaképenként foil/mask URL-t fogadnak;
- több CDN-fóliatextúrát töltenek;
- véletlen seedből texture offsetet képeznek;
- külső Galaxy Holo és háttérforrásokat attribuálnak.

AETERNA production követelmény:

```text
asset_id
content_hash
source_provenance
license
author
allowed_use
package_version
```

Tilos a Pokémon-, Poké Ball-, Master Ball-, kártyahátlap- vagy más márkaazonos
vizuális asset átemelése.

# 10. Kozmetikai seed

A webes kártyák `Math.random()` értékből külön pattern offsetet kapnak.

Ez jó vizuális ötlet:

- nem minden lap csillog ugyanott;
- csökken az ismétlődés;
- természetesebb fizikai fóliaérzet.

AETERNA-ban azonban a seed legyen stabil:

```text
cosmetic_seed = hash(card_instance_id, foil_profile_id, presentation_seed)
```

Tulajdonságai:

- nem rules RNG;
- nem hat a MatchState-re;
- replay alatt stabil lehet;
- ugyanaz a lap ugyanúgy jelenhet meg;
- screenshot és visual regression reprodukálható.

# 11. Ritkaság mint material recipe

A repository nem pusztán rarity-színt állít.

A rarity meghatározza:

- hány layer aktív;
- milyen mask;
- milyen spectrum angle;
- milyen stripe pattern;
- milyen blend;
- milyen textúra;
- milyen glitter parallax;
- milyen glare;
- milyen brightness/contrast/saturation;
- milyen opacity görbe.

Ez közvetlenül `FoilProfile` Resource-modellé alakítható.

# 12. Javasolt AETERNA FoilProfile

```text
FoilProfile
- profile_id
- display_name
- shader_variant
- quality_floor
- enabled_layers
- spectrum_palette_id
- spectrum_angle
- spectrum_frequency
- spectrum_speed
- spectrum_intensity
- stripe_angle_a
- stripe_angle_b
- stripe_frequency
- stripe_width
- pattern_texture_id
- pattern_scale
- pattern_parallax
- noise_texture_id
- noise_scale
- glitter_texture_a_id
- glitter_texture_b_id
- glitter_parallax_a
- glitter_parallax_b
- glare_color
- glare_radius
- glare_intensity
- edge_glow_color
- edge_glow_intensity
- foil_mask_id
- text_protection_mask_id
- brightness
- contrast
- saturation
- reduced_motion_fallback_profile_id
```

# 13. Javasolt AETERNA-profilcsaládok

Ezek nem Pokémon-nevek és nem közvetlen CSS-másolatok.

## 13.1 `NONE`

- normál digitális kártya;
- nincs dinamikus fólia.

## 13.2 `SUBTLE_IRIDESCENT`

- egy spektrumréteg;
- enyhe radial glare;
- teljes kártya vagy keretmaszk;
- alacsony teljesítményköltség.

## 13.3 `ART_WINDOW_HOLO`

- csak az illusztrációablak csillog;
- szabályszöveg teljesen védett;
- spektrum + glare.

## 13.4 `REVERSE_FRAME_HOLO`

- az illusztráción kívüli keret és információs háttér fóliázott;
- invertált mask;
- visszafogott intensity.

## 13.5 `COSMIC_PARTICLE`

- több rétegű csillag-/szemcseminta;
- eltérő parallax;
- spektrum + glare;
- AETERNA-saját kozmikus textúra.

## 13.6 `FULL_ART_SPECTRAL`

- teljes kártyás spektrum;
- anisotropic stripe;
- grain;
- glare;
- szövegvédő maszk.

## 13.7 `ILLUSTRATION_GRAIN`

- művészeti nyomatérzet;
- finom szemcse;
- kettős highlight;
- kevésbé „szivárványos”.

## 13.8 `SIGIL_PATTERN`

- ismétlődő AETERNA-szimbólum;
- külső/belső pattern mask;
- kártyapéldányonként stabil offset.

## 13.9 `DUAL_PARALLAX_GLITTER`

- két ellentétes irányú glitterréteg;
- pointertop/left függő opacity;
- magas ritkaság.

## 13.10 `GILDED_HYPER`

- arany/platina spektrum;
- finom dombornyomat;
- edge glow;
- kettős glare;
- csak kiemelt nézetben teljes részletesség.

# 14. A profil nem gameplay-szabály

A fóliaprofil:

- nem növeli a kártya erejét;
- nem módosít legal actiont;
- nem része az authoritative MatchState mechanikai állapotának;
- nem vezérelheti a rules engine-t.

Lehetséges adatkapcsolat:

```text
CardPrintingDefinition
- printing_id
- art_asset_id
- frame_asset_id
- foil_profile_id
- cosmetic_tags
```

A `CardDefinition` és a `CardPrintingDefinition` külön maradjon.

# 15. Viewer projection és rejtett információ

Face-down vagy ellenfélkézben lévő lap esetén:

- a kliens nem kaphatja meg a front asset ID-t;
- nem kaphat kártyaspecifikus maskot;
- nem kaphat rarityból kikövetkeztethető profilt;
- csak a közös card back presentation jelenhet meg.

A `FoilProfile` csak a viewer projection által látható printinghez aktiválható.

# 16. Godot shaderkompozíciós lehetőségek

A CSS blend mode-ok nem fordíthatók át egyenként automatikusan Godotba.

## 16.1 Egy nagy combined shader

Előny:

- kevés draw call;
- egy material;
- közös paraméterezés.

Hátrány:

- sok branch;
- sok texture sample;
- nehéz profilozás;
- variant explosion;
- mobilon drága;
- karbantarthatatlan „univerzális monster shader”.

## 16.2 Több CanvasItem layer

```text
BaseCard
SpectrumLayer
PatternLayer
GlitterLayerA
GlitterLayerB
GlareLayer
EdgeGlow
```

Előny:

- jól megfelel a forrás fogalmi struktúrájának;
- rétegenként ki-/bekapcsolható;
- könnyebb authoring;
- külön shaderprofil.

Hátrány:

- több draw call;
- blendek és alpha sorrend érzékeny;
- sok aktív kártyánál drága.

## 16.3 Profilonként shader variant

Ajánlott középút:

- néhány jól definiált shadercsalád;
- `FoilProfile` csak paraméterez;
- high-end profil több layert használ;
- low-end fallback kevesebbet.

# 17. Javasolt Godot node-struktúra

```text
CardFoilView
├── BaseCard
├── FoilMaskSource
├── SpectrumLayer
├── PatternLayer
├── GlitterLayerA
├── GlitterLayerB
├── GlareLayer
├── EdgeGlowLayer
└── InteractionController
```

Alternatíva: a nem használt layer node-ok ne létezzenek, ne csak láthatatlanná váljanak.

# 18. Javasolt runtime-architektúra

```text
Aeterna.Engine
└── ViewerProjection
        │
        ▼
Aeterna.GodotBridge
├── CardViewModelAdapter
├── PrintingPresentationAdapter
└── VisibilityPolicyAdapter
        │
        ▼
Aeterna.Godot
├── CardView
├── CardTiltController
├── CardFoilController
├── FoilProfileRegistry
├── FoilMaterialFactory
├── FoilPerformancePolicy
└── ReducedMotionPolicy
```

# 19. Javasolt CardFoilController

Feladata:

- pointer UV;
- device orientation UV;
- hover/active state;
- target tilt;
- smooth tilt;
- glare UV;
- background UV;
- center distance;
- cosmetic time;
- dirty update;
- quality policy;
- shader paraméterek frissítése.

Nem feladata:

- card play;
- legal action;
- selection authority;
- zone mutation;
- rarity rules;
- MatchState mutation.

# 20. Input és interaction contract

```text
FoilInteractionState
- is_hovered
- is_focused
- is_selected
- is_zoomed
- pointer_uv
- tilt
- glare_uv
- activity
- reduced_motion
- quality_level
```

A fólia csak presentation-visszajelzés.

A legal target kiemelés külön vizuális csatorna, hogy ne keveredjen a ritkasági fóliával.

# 21. Teljesítmény

A szerző maga is súlyos teljesítménykockázatként kezeli a teljes demót.

A webes költséges elemek:

- CSS 3D transform;
- preserve-3d;
- sok `will-change`;
- több gradientszámítás;
- blend mode;
- filter;
- mask;
- pseudo-element layer;
- több nagy textúra;
- pointerenkénti spring update;
- folyamatos showcase animation.

Godotban hasonló kockázat:

- sok shader texture sample;
- több draw call;
- teljes képernyős blend;
- minden kártya frame-enkénti material write;
- sok külön material példány;
- háttérben is futó időanimáció;
- SubViewport túlhasználat.

# 22. Kötelező performance policy

## 22.1 `OFF`

- nincs foil shader;
- normál kártyakép.

## 22.2 `LOW`

- egy spektrumréteg;
- egyszerű radial glare;
- nincs glitter;
- nincs noise animation.

## 22.3 `MEDIUM`

- spectrum;
- egy pattern;
- glare;
- egy mask;
- korlátozott update rate.

## 22.4 `HIGH`

- profile szerinti teljes layerkészlet;
- kettős glitter;
- noise/grain;
- edge glow;
- dinamikus parallax.

# 23. Aktiválási szabály

Teljes dinamikus effekt egyszerre csak kevés kártyán fusson.

Javasolt prioritás:

1. nagyított/inspect kártya;
2. aktívan húzott lap;
3. hovered vagy fókuszált lap;
4. selected lap;
5. boardon lévő többi fóliás lap csak statikus vagy low mód;
6. képernyőn kívüli lapok teljesen leállítva.

# 24. Update scheduling

Nem szabad minden input eseményben minden uniformot írni.

```text
event:
  target_pointer_uv = new_value
  dirty = true

frame:
  smooth current state
  update material only when changed
```

További optimalizáció:

- epsilon threshold;
- cached ShaderMaterial parameter set;
- shared profile textures;
- profile material template;
- offscreen process disable;
- animation time csak aktív profilnál;
- card count budget.

# 25. Automatikus showcase animáció

A fő webes projekt egy showcase lapot periodikusan körkörösen dönt és mozgatja a glare-t.

Ez demóban jó.

AETERNA-ban:

- collection/reward reveal során használható;
- játéktáblán folyamatosan nem;
- reduced motion mellett tiltandó;
- időkorlátos;
- inputra azonnal megszakítható.

# 26. Accessibility és reduced motion

Kötelező opciók:

- holografikus effekt kikapcsolása;
- kártyadőlés kikapcsolása;
- auto animation kikapcsolása;
- reduced flash;
- glare intensity csökkentése;
- colorblind-safe selection;
- legal target ne csak színnel jelenjen meg;
- szövegkontraszt védelme.

A webes forrás jó mintát ad a keyboard focusra és ARIA button szerepre, de a Godotban
külön gamepad- és keyboard-navigation rendszer kell.

# 27. Offline és runtime package

A 151 source több fóliatextúrát külső CDN URL-ről tölt.

AETERNA production buildben ez nem elfogadható.

Követelmény:

- saját asset;
- lokálisan csomagolt;
- content hash;
- package schema;
- cache key;
- licence record;
- nincs futásidejű külső függés;
- nincs eltűnő CDN;
- nincs felhasználókövetés.

# 28. Licenc- és márkakockázat

## 28.1 GPL-3.0

Mindkét Pokémon CSS repository GPL-3.0.

A teljes CSS/JS/Svelte forrás közvetlen beemelése:

- nem illeszkedik az AETERNA jelenlegi production licencirányához;
- source distribution és license propagation kérdést okozna;
- ezért elutasítandó.

## 28.2 Pokémon assetek

Nem használható:

- Pokémon kártyakép;
- Pokémon logo;
- Pokémon kártyahátlap;
- Poké Ball/Master Ball márkaazonos pattern;
- Pokémon API-ból származó artwork;
- eredeti rarity elnevezések, ha márkaazonos presentationként jelennének meg.

## 28.3 Külső texture provenance

A README külön Galaxy Holo és Vecteezy forrást említ.

A 151 CSS külső CDN-ről több iridescent/noise/pattern assetet hivatkozik.

Ezek nem tekinthetők automatikusan újrafelhasználhatónak.

## 28.4 Clean-room határ

Átvehető mint elv:

- pointerből normalizált UV;
- spektrumfüggvény;
- radial glare;
- maszk;
- parallax;
- több réteg;
- ritkaságalapú material profile;
- stabil kozmetikai seed;
- quality tier.

Nem másolható:

- CSS deklaráció;
- Svelte/JS kód;
- exact gradient recipe;
- exact clip polygon;
- texture asset;
- Pokémon név;
- Pokémon minta.

# 29. AETERNA-saját vizuális identitás

A rendszer ne Pokémon-fólia-utánzat legyen.

Lehetséges AETERNA-specifikus vizuális családok:

- birodalmi heraldika;
- klánpecsét;
- elemi spektrum;
- Aeternal csillám;
- vérvonal-rúna;
- repedő kristály;
- mágikus áramkör;
- szakrális aranyozás;
- árnyékfólia;
- jeges diffrakció;
- villámvezető fólia;
- lávakő irizálás.

A `FoilProfile` társítható:

- ritkasághoz;
- kártyakiadáshoz;
- alternatív artworkhöz;
- prémium printinghez;
- eseményjutalomhoz;
- booster-változathoz.

De ne legyen mechanikai előny.

# 30. A birodalmi identitás használata

A profil paraméterezhető birodalmi palettával:

```text
foil_profile = FULL_ART_SPECTRAL
palette = IGNIS
pattern = imperial_sigils/ignis
```

Ezzel ugyanaz a shadercsalád eltérő identitást kap.

Javasolt külön:

```text
FoilProfile
FoilPalette
FoilPattern
FoilMaskTemplate
```

Ne minden kombinációhoz külön shader készüljön.

# 31. Authoring workflow

## 31.1 Kártyatervező kimenetek

Egy fóliás printinghez:

1. base card image;
2. optional foil mask;
3. optional text protection mask;
4. optional character/art mask;
5. pattern ID;
6. profile ID;
7. palette ID;
8. seed policy;
9. fallback profile;
10. performance tier minimum.

## 31.2 Preview eszköz

Godot editor tool:

- kártyakép kiválasztása;
- profile választása;
- pointer UV kézi mozgatása;
- tilt angle;
- mask preview;
- layer solo;
- low/medium/high preview;
- mobile budget preview;
- screenshot export.

## 31.3 Validation

A content compiler ellenőrizze:

- profile létezik;
- mask mérete megfelelő;
- texture hash;
- forbidden external URL;
- licence metadata;
- fallback megadva;
- shader variant támogatott;
- texture sample budget.

# 32. Javasolt assetformátum

```text
res://presentation/foil/
├── profiles/
├── palettes/
├── patterns/
├── noise/
├── masks/
├── shaders/
└── previews/
```

Runtime package:

```text
foil_profiles.json
foil_asset_manifest.json
foil_profiles.hash
```

# 33. Shaderparaméter-javaslat

```text
uniform sampler2D base_texture;
uniform sampler2D foil_mask;
uniform sampler2D text_protection_mask;
uniform sampler2D pattern_texture;
uniform sampler2D noise_texture;
uniform sampler2D glitter_texture_a;
uniform sampler2D glitter_texture_b;

uniform vec2 pointer_uv;
uniform vec2 background_uv;
uniform vec2 tilt;
uniform float pointer_from_center;
uniform float activity;
uniform float time_phase;
uniform float cosmetic_seed;

uniform vec4 spectrum_colors[6];
uniform float spectrum_angle;
uniform float spectrum_frequency;
uniform float stripe_frequency;
uniform float stripe_width;
uniform float glare_radius;
uniform float glare_intensity;
uniform float glitter_intensity;
uniform float brightness;
uniform float contrast;
uniform float saturation;
```

# 34. CSS blend módok Godot-megfeleltetése

Nincs mindig pontos egy-egy megfelelés.

| CSS-fogalom | Lehetséges Godot/shader megoldás |
|---|---|
| overlay | saját overlay blend függvény |
| screen | `1 - (1-a)(1-b)` |
| multiply | `a * b` |
| color-dodge | saját dodge, clampelt nevezővel |
| hard-light | conditional blend függvény |
| luminosity | HSL/HSV vagy luminance csere |
| plus-lighter | additive blend |
| exclusion | `a + b - 2ab` |
| difference | `abs(a-b)` |
| soft-light | saját soft-light függvény |

A shaderben minden blendet linear/sRGB tér szempontjából is vizsgálni kell.

# 35. Color pipeline

A webes CSS filterek sorrendje:

- brightness;
- contrast;
- saturation;
- blend mode.

Godotban:

- textúra sRGB;
- shader linear számítás;
- output color space;
- HDR/tonemap;
- glow/bloom

más eredményt adhat.

Kötelező visual calibration.

# 36. Teljesítményteszt-javaslat

## 36.1 Kártyaszám

- 1 inspect lap;
- 5 aktív kézlap;
- 20 boardlap;
- 50 collection lap;
- 100 collection thumbnail.

## 36.2 Minőségi mód

- OFF;
- LOW;
- MEDIUM;
- HIGH.

## 36.3 Platform

- Windows Vulkan;
- Compatibility/OpenGL;
- Linux;
- alacsonyabb GPU;
- Steam Deck;
- mobil, ha célplatform.

## 36.4 Mérés

- FPS;
- frame time;
- draw calls;
- material changes;
- texture memory;
- shader compilation;
- GPU time;
- CPU process;
- input latency.

# 37. Visual regression

Minden profilhoz rögzített:

```text
pointer_uv
tilt
seed
time_phase
quality
```

állapotból screenshot készíthető.

Tesztpontok:

- center;
- top-left;
- top-right;
- bottom-left;
- bottom-right;
- half tilt;
- maximum tilt;
- reduced motion;
- text readability;
- mask edge.

# 38. Biztonsági és platformhatár

A fóliarendszer:

- nem tölthet külső URL-t runtimeban;
- nem futtathat shader source-t contentből;
- csak allowlistelt shader variantot használhat;
- profile JSON nem adhat arbitrary resource pathot;
- minden asset ID manifestből oldódjon fel;
- package hash ellenőrzött legyen.

# 39. Konkrét AETERNA proof-of-concept sorrend

## P0 – alap

1. `SUBTLE_IRIDESCENT`;
2. pointer UV;
3. tilt smoothing;
4. radial glare;
5. egy mask;
6. text protection;
7. OFF/LOW/HIGH switch.

## P1 – profilrendszer

1. `FoilProfile` Resource;
2. profile registry;
3. spectrum palette;
4. pattern texture;
5. stable cosmetic seed;
6. editor preview.

## P2 – magas ritkaság

1. dual parallax glitter;
2. full-art mask;
3. edge glow;
4. cosmic particles;
5. reveal animation.

## P3 – production hardening

1. content manifest;
2. licence inventory;
3. visual regression;
4. performance budget;
5. mobile fallback;
6. accessibility.

# 40. Javasolt első három AETERNA-prototípus

## 40.1 `AETERNA_IRIDESCENT_STANDARD`

- teljes keret vagy art window mask;
- egy spektrumréteg;
- egy glare;
- alacsony költség.

## 40.2 `AETERNA_SIGIL_PATTERN`

- AETERNA-saját pecsétminta;
- stabil per-card seed;
- két patternparallax;
- közepes költség.

## 40.3 `AETERNA_AETERNAL_PREMIUM`

- full-art spectral;
- dual glitter;
- text protection;
- edge glow;
- reveal animation;
- csak inspect/reward nézetben teljes minőség.

# 41. Kód- és komponenshatár

A Godot komponens ne kapjon teljes MatchState-et.

Elég:

```text
CardFoilViewModel
- card_instance_id
- visible
- foil_profile_id
- foil_palette_id
- foil_mask_asset_id
- text_mask_asset_id
- cosmetic_seed
- quality_override?
```

A user input csak presentation adatot módosít.

# 42. Összekapcsolás a korábbi Fake3D-audittal

A korábban vizsgált Godot Fake3D projektből az AETERNA számára már kijelöltük:

- CardTiltView;
- front/back kezelés;
- shadow layer;
- selection treatment;
- performance policy.

A jelenlegi audit ehhez új réteget ad:

```text
CardTiltView
+ FoilProfile
+ PatternMask
+ GlitterParallax
+ SpectralMaterial
+ GlareMaterial
```

Ez nem külső projektek egymáshoz való rangsorolása, hanem az AETERNA már
meghatározott presentation-komponenseinek pontosítása.

# 43. Forrásspecifikus teljesítménymegfigyelések

## 43.1 Elsődleges repository

A legutóbbi commit:

- frame-enként egy pointer update-re korlátozza a springfrissítést;
- pending update-et tárol;
- interaction endnél megszakítja a pending frame-et;
- 3D z-translationnel emeli az aktív lapot;
- módosítja az isolation kezelést.

Ez mutatja, hogy az effektlánc aktív optimalizációt igényel.

## 43.2 151 repository

A vizsgált Card komponens közvetlenül frissíti a springeket pointermozgáskor.

Godot-adaptációban már az első verzióban frame-throttled megoldás szükséges.

# 44. Forrásspecifikus lifecycle-kockázatok

A Card komponens document/window eventlistenereket használ.

A vizsgált részben a `visibilitychange` listenerhez nem látható explicit
component cleanup.

A Godot megfelelőnél:

- `_exit_tree()` cleanup;
- process disable;
- input unregistration;
- material release;
- view pooling reset

kötelező.

# 45. CI és tesztérettség

Az elsődleges vizsgált commit:

- Vercel failure statust mutat;
- kapcsolt GitHub Actions workflow run nem található.

A 151 vizsgált commit:

- combined status nem található;
- kapcsolt workflow run nem található.

Ez nem jelenti, hogy a demók használhatatlanok, de nincs production minőségű
automatizált bizonyíték.

# 46. AETERNA-átvételi döntéstábla

| Terület | Döntés | Indok |
|---|---|---|
| Pointer UV modell | clean-room átvehető | általános interakciós elv |
| Device orientation mapping | clean-room átvehető | általános presentationelv |
| Rugós smoothing | saját implementáció | általános mozgáselv |
| Többrétegű foil composition | clean-room átvehető | fő vizuális tanulság |
| Rarity/profile adatmodell | kiemelten ajánlott | skálázható AETERNA-rendszer |
| Mask-alapú régiókezelés | kiemelten ajánlott | szövegvédelem és art/frame különválasztás |
| Per-card cosmetic seed | ajánlott | természetes variáció és reprodukálhatóság |
| CSS forrás | nem vehető át | GPL és webspecifikus összefonódás |
| Svelte/JS forrás | nem vehető át | GPL és Godot-inkompatibilitás |
| Exact gradient recipe | nem másolandó | clean-room és saját identitás |
| Pokémon assetek | tilos | márka- és szerzői jog |
| CDN foil assetek | nem használhatók automatikusan | külön provenance/licenc |
| Hover Tilt dependency | nem szükséges | webkomponens, Godotban saját controller |
| Dinamikus effect minden kártyán | elutasítva | performance |
| Full effect inspect kártyán | ajánlott | látvány/performance egyensúly |

# 47. Konkrét kockázatlista

1. GPL-3.0.
2. Pokémon márkaassetek.
3. külső texture provenance.
4. CDN runtime dependence.
5. CSS/JS/Svelte erős összekapcsolása.
6. szerző szerint showcase, nem modul.
7. szerző szerint nagyon nehéz effekt.
8. sok blend és filter.
9. sok layer.
10. nagy textúramemória.
11. minden pointer event frissítési költsége.
12. random seed reprodukálhatatlanság.
13. clip path Pokémon-geometriához kötött.
14. szöveg olvashatósága.
15. mobil performance.
16. reduced motion hiánya production szinten.
17. külső analytics/web függések.
18. nincs Godot shaderbizonyíték.
19. nincs engine-integrációs relevancia.
20. nincs hidden-information modell.
21. Vercel failure status a vizsgált fő commitnál.
22. nincs Actions proof.
23. exact CSS blend Godotban eltérhet.
24. material variant explosion.
25. minden kártyához külön mask authoring költsége.

# 48. Legfontosabb használható tanulságok

1. A holografikus hatás több réteg együttese.
2. Egy közös pointer/light koordináta tartja össze a rétegeket.
3. A fóliaprofil adat, nem hardcoded kártyaosztály.
4. A mask legalább olyan fontos, mint a szivárványszín.
5. A textúraseed megszünteti a digitális ismétlődést.
6. A két ellentétes parallaxissal mozgó glitter rendkívül erős mélységhatást ad.
7. A glare és a spectrum külön jelenség.
8. A ritkaság layerreceptet, nem puszta színt jelent.
9. A full effect csak az aktív kártyán fusson.
10. Az inputot frame-enként kell összegyűjteni.
11. Kell low/reduced-motion fallback.
12. A fólia teljesen presentation-only.
13. A printing és a mechanikai CardDefinition külön kezelendő.
14. Az asseteket saját forrásból kell elkészíteni.
15. A Godot port clean-room munka.

# 49. AETERNA-javaslatok

| # | Javaslat | Réteg | Prioritás |
|---:|---|---|:---:|
| 1 | `FoilProfile` adatmodell | Godot/Data | P0 |
| 2 | `CardFoilController` | Godot | P0 |
| 3 | pointer UV és spring smoothing | Godot | P0 |
| 4 | `SUBTLE_IRIDESCENT` proof | Godot | P0 |
| 5 | mask + text protection proof | Godot/Art | P0 |
| 6 | OFF/LOW/MEDIUM/HIGH policy | Godot | P0 |
| 7 | stable cosmetic seed | Godot/Bridge | P0 |
| 8 | inspect-only high quality | Godot | P0 |
| 9 | visual regression seed/pointer matrix | Tests | P0 |
| 10 | shader profiler 1/5/20/50/100 card | Tests | P0 |
| 11 | AETERNA saját spectrum palette | Art | P1 |
| 12 | AETERNA saját sigil pattern | Art | P1 |
| 13 | dual glitter profile | Godot | P1 |
| 14 | cosmic particle profile | Godot | P1 |
| 15 | reduced motion | Accessibility | P0 |
| 16 | gamepad/keyboard inspect | Accessibility | P1 |
| 17 | runtime asset manifest/hash | Tooling | P0 |
| 18 | external URL tiltás | Security | P0 |
| 19 | foil asset licence inventory | Legal | P0 |
| 20 | clean-room implementation record | Legal/Process | P0 |
| 21 | Godot editor foil preview | Tooling | P1 |
| 22 | collection/reward reveal animation | Godot | P2 |
| 23 | folytatás `Valyreon/seven-card-game-godot` audittal | Learning | P1 |

# 50. Bizonyítékjegyzék

| ID | Állítás | Forrás |
|---|---|---|
| E-001 | elsődleges repo public/main | GitHub repository metadata |
| E-002 | vizsgált commit és performance patch | commit `acb119763...` |
| E-003 | CSS transforms/gradients/blends/filters | elsődleges README |
| E-004 | demo, nem modul | issue #19 |
| E-005 | rendkívüli performance figyelmeztetés | issue #19 |
| E-006 | GPL-3.0 | elsődleges LICENSE |
| E-007 | Galaxy Holo és Vecteezy attribution | elsődleges README |
| E-008 | Svelte springs és pointer mapping | `Card.svelte` |
| E-009 | requestAnimationFrame batching | `Card.svelte`, latest commit |
| E-010 | device orientation | `orientation.js`, `Card.svelte` |
| E-011 | dynamic CSS variables | `Card.svelte` |
| E-012 | shine + glare DOM layer | `Card.svelte` |
| E-013 | base perspective/front/back | `base.css` |
| E-014 | spectrum palette | `base.css` |
| E-015 | mask/clip rendszer | `base.css`, `cards.css` |
| E-016 | regular holo | `regular-holo.css` |
| E-017 | reverse holo | `reverse-holo.css` |
| E-018 | cosmos holo | `cosmos-holo.css` |
| E-019 | 151 repo és demo | 151 README |
| E-020 | 151 GPL-3.0 | 151 LICENSE |
| E-021 | shine/glitter/glare/glare2 | 151 `Card.svelte` |
| E-022 | CDN iri/noise/pattern assets | 151 `cards.css` |
| E-023 | 151 regular holo | 151 `regular-holo.css` |
| E-024 | EX full art | 151 `ex-full-art.css` |
| E-025 | illustration rare | 151 `illustration-rare.css` |
| E-026 | pattern stamp / ball profiles | 151 `poke-ball-holo.css` |
| E-027 | special illustration glitter | 151 `ex-special-illustration-rare.css` |
| E-028 | hyper rare glitter | 151 `hyper-rare.css` |
| E-029 | nincs Actions workflow proof | connector workflow query |
| E-030 | Hover Tilt külön komponens | Hover Tilt README |
| E-031 | Hover Tilt MPL-2.0 | Hover Tilt README |

# 51. Nyitott kérdések

1. Mely Godot renderert célozza elsőként az AETERNA?
2. Mekkora a tipikus egyidejű CardView-szám?
3. A fólia a táblán is aktív legyen, vagy csak inspect módban?
4. Kell mobil támogatás?
5. Milyen kártyaméret és textúrafelbontás lesz productionben?
6. Egyetlen combined shader vagy layer stack ad jobb teljesítményt?
7. Mely blend módokat kell ténylegesen újraalkotni?
8. Szükséges-e per-card mask vagy layouttemplate elég?
9. Hogyan készül a text protection mask?
10. Mely AETERNA rarity/printing típus kap profilt?
11. Lesznek alternatív prémium printingek?
12. Kell booster reveal animation?
13. Mekkora texture atlas használható?
14. Stable cosmetic seed mely adatból készül?
15. Screenshotokban és replayben azonos fóliaállapot szükséges-e?
16. Mely AETERNA-szimbólumok alkalmasak ismétlődő patternre?
17. Kell teljesen kikapcsolható accessibility mód?
18. Hogyan kezeljük a Steam Deck teljesítményt?
19. Milyen licence alá kerülnek a saját foil assetek?
20. A következő programozási körben Codex készítsen-e külön shader proofot?

# 52. Következő ellenőrzési és fejlesztési lépések

## 52.1 Dokumentációs lépések

1. jelen elemzés elfogadása;
2. katalógus és forráslista GitHubra töltése;
3. GitHub fájl- és verzióellenőrzés;
4. `FoilProfile` tervezési dokumentum;
5. asset provenance sablon;
6. performance acceptance criteria.

## 52.2 Godot proof

1. egy AETERNA tesztkártya;
2. egy saját grayscale mask;
3. saját spectrum palette;
4. pointer UV;
5. simple glare;
6. iridescent spectrum;
7. low/high mód;
8. profiler;
9. screenshot matrix.

## 52.3 Későbbi Codex-feladat

Csak a proof implementációjához:

- Godot 4 shader;
- CardFoilController;
- FoilProfile Resource;
- editor preview;
- performance test scene;
- visual regression seed harness.

# 53. Végső minősítés

- **Vizuális tanulási érték:** nagyon magas
- **Kártyadizájn-érték:** nagyon magas
- **Godot presentation relevancia:** nagyon magas
- **Interakciós koordinátamodell:** magas
- **Adatvezérelt profilrendszer:** nagyon magas
- **Performance érettség:** demonstrációs; külön production hardening szükséges
- **Engine/rules relevancia:** nincs; presentation-only
- **Multiplayer/hidden information:** nincs megoldva
- **Közvetlen kódintegráció:** elutasítandó
- **Közvetlen assetintegráció:** elutasítandó
- **Clean-room Godot újraimplementáció:** kiemelten ajánlott
- **Legfontosabb AETERNA-eredmény:** létrehozható egy saját `FoilProfile` és
  `CardFoilController` rendszer, amely maszkokból, spektrumból, mintából,
  glitterből, glare-ből és performance policyból épít prémium kártyamegjelenítést
- **Elemzés státusza:** első teljes source-family audit elkészült
- **Normál learning sorozat következő eleme:** `Valyreon/seven-card-game-godot`

# 54. Változásnapló

## 0.1 – 2026-07-25

- elkészült a `simeydotme/pokemon-cards-css` első teljes AETERNA-központú auditja;
- ellenőrzésre került az aktuális `main` commit;
- feldolgozásra került a szerző „showcase, nem modul” figyelmeztetése;
- feldolgozásra került a CSS transform, gradient, mask, blend és filter rendszer;
- feldolgozásra került a pointer- és orientation-vezérelt koordinátamodell;
- feldolgozásra került a Svelte spring és requestAnimationFrame frissítési modell;
- feldolgozásra került a regular, reverse és cosmos fóliaprofil;
- azonosításra került a külön `pokemon-cards-151` repository;
- feldolgozásra került a shine, glitter, glare és glare2 rétegmodell;
- feldolgozásra került a 151 regular, EX full art, illustration, pattern stamp,
  special illustration és hyper profile;
- ellenőrzésre került mindkét Pokémon CSS repository GPL-3.0 licence;
- rögzítésre kerültek a külső asset- és Pokémon-márkakockázatok;
- rögzítésre került a külön MPL-2.0 Hover Tilt komponens;
- rögzítésre került a hiányzó GitHub Actions proof;
- rögzítésre került az elsődleges commit Vercel failure státusza;
- elkészült az AETERNA `FoilProfile`, `CardFoilController`, mask-, cosmetic seed-,
  quality tier- és runtime package-javaslata;
- elkészült a clean-room átvehetőségi döntéstábla;
- a normál learning sorozat következő eleme változatlanul
  `Valyreon/seven-card-game-godot`.
