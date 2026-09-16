# MusterDeck themes

Crew themes that do not ship in the default MusterDeck app.

A theme is **one JSON file**. Drop it in MusterDeck's runtime themes folder and the
app picks it up with no rebuild and no restart of anything but the view.

| Theme | What it is | Why it is not in the app |
|---|---|---|
| `jedi-enclave` | An enclave on a temple world. Every repo is a training hall, the arrival point is the Millennium Falcon, and the rank ladder is Padawan / Luke / Vader. | Third-party IP |
| `galley-kitchen` | A brigade kitchen at service. Every repo is a station, every session a cook, every thread a ticket on the rail. Built in Galley Solutions' own brand palette. | One company's branding |

Both are complete and validated. Neither is abandoned: the generators that produce
them are here too, and both still pass the app's own theme tests.

## Installing one

```bash
# macOS  (the data directory is legacy-named; this is deliberate and frozen)
DATA_DIR="$HOME/Library/Application Support/Claude Conductor"
# Windows  %LOCALAPPDATA%/Claude Command Center
# Linux    ~/.claude-conductor/data

mkdir -p "$DATA_DIR/themes/jedi-enclave"
cp themes/jedi-enclave.json "$DATA_DIR/themes/jedi-enclave/theme.json"
```

Then open the Crew view and choose **Reload themes** from its view menu.

**The folder name becomes the theme id**, and MusterDeck persists your chosen theme by
id. Use the folder names above (`jedi-enclave`, `galley-kitchen`) so the id matches what
each file declares, or the theme will load once and silently fall back on the next launch.

## Regenerating

Neither theme is hand-written. Every offset is computed from the measured character rig
and asserted before the file is emitted, which is the only way a kit reliably ends up
*on* the body rather than inside it.

```bash
python3 generators/build-jedi-enclave.py   themes/jedi-enclave.json
python3 generators/build-galley-kitchen.py themes/galley-kitchen.json
```

## Credits

A theme is a description of a world for an engine somebody else wrote. The Crew is built
on **Bot Crossing** by Jarren Rocks ([botcrossing.com](https://botcrossing.com), MIT):
its character rig, its instanced-mesh crew, its hex plot lattice and its recipe-driven
buildings are what every theme here is authored against, and the measurements in
`THEME-REFERENCE.md` are measurements of that rig. The app itself grew out of **Claude
Command Center** (MIT), which is where the multi-session workbench these themes decorate
came from.

The theme system, the descriptor format and the generators in this repository are
MusterDeck's own work on top of that engine.

## Writing your own

`THEME-REFERENCE.md` is the complete reference for every key a theme can set: the shape
vocabulary, the nine attachment bones and their local frames, the body envelope a worn
part has to enclose, the face patch nothing may cross, the hex-cell clearances a building
has to fit, and the cloth model.

Two things in there will save you an afternoon each:

- **A theme that fails validation is refused whole** and simply never appears in the
  picker. Nothing throws and nothing renders wrong. Check the console first.
- **You cannot judge a theme by reading it.** It is geometry. Every mistake worth making
  produces JSON that validates, loads, throws nothing, and looks wrong.
