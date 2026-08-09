# AETERNA Game Engine

Az AETERNA digitális programegysége contract-first felosztásban működik.

## Architektúra

```text
Godot / GDScript
    = vizuális kliens, UI, input, animáció és debug

C# / .NET
    = egyetlen production authoritative rules engine

Python
    = adatpipeline, reference engine, fixture, AI, batch, audit és elemzés
```

## Aktuális állapot

Az aktuális commit-, mérföldkő- és következőlépés-információ egyetlen helyen található:

```text
../Aeterna dokumentációk/AETERNA_AKTUALIS_PROJEKTALLAPOT.md
```

## Fő mappák

- `C#/` – production engine, headless host, tesztek és történeti C# proofok.
- `python/` – runtime package tooling, reference engine, fixture, AI és audit.
- `Godot/` – visual client, runtime package fogyasztás, debug és bridge.
- `docs/` – tartós specifikációk, döntések és mérföldkőnapló.
- `runtime_comparison/` – canonical regressziós fixture-ek és artifactok.

## Dokumentáció

- index és működési szabály: `docs/README.md`
- architektúra: `docs/ARCHITECTURE.md`
- technológiai döntések: `docs/TECHNOLOGY_DECISIONS.md`
- mérföldkőnapló: `docs/checkpoints/CHECKPOINTS.md`
- aktuális projektállapot: `../Aeterna dokumentációk/AETERNA_AKTUALIS_PROJEKTALLAPOT.md`

Ez a README nem tartalmaz gyorsan avuló commit SHA-t, tesztszámot vagy roadmapet.
