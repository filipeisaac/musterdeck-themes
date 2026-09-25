# MusterDeck themes

**Optional Crew themes. This is not MusterDeck itself.**

MusterDeck is a desktop app for running many Claude Code sessions at once. It lives at
[**filipeisaac/musterdeck-releases**](https://github.com/filipeisaac/musterdeck-releases),
which is where you download it and where its issues belong. You do not need anything here
to use it: it ships with two Crew themes of its own (a space colony and a samurai
village) and they are the ones most people will ever see.

This repository is a side shelf. It holds the themes that **cannot** ship inside the app,
each for a reason of its own, and everything in it is opt-in: nothing here is installed by
default, nothing here is required, and removing a theme leaves the app exactly as it was.

A theme is **one JSON file** — no code, no executable, no assets. Drop it in MusterDeck's
runtime themes folder and the app picks it up with no rebuild and no restart of anything
but the view.

| Theme | What it is | Needs | Why it is not in the app |
|---|---|---|---|
| `jedi-enclave` | An enclave on a temple world. Every repo is a training hall, the arrival point is the Millennium Falcon. The crew is Rey (blue blade), Qui-Gon (green) and Vader (red). | MusterDeck 0.2.85 | Third-party IP |
| `galley-kitchen` | A brigade kitchen at service. Every repo is a station, every session a cook, every thread a ticket on the rail. The crew is the Brigade: commis, chef de partie, chef de cuisine. | MusterDeck 0.2.82 | One company's branding |

Both were reviewed and approved on 2026-09-24, crew and buildings.

`themes/index.json` lists them for tools: id, name, blurb, file, `sha256` of the file,
`minApp` (the oldest MusterDeck that can load it) and a line on the crew.

## Installing one

The easy way: in a Claude Code session on a machine with MusterDeck, run
`/musterdeck-install-custom-theme`. It lists what is here, says which you already have and
whether yours is current, installs the ones you pick, and tells you when your app is too
old for one. The skill comes from MusterDeck's plugin:

```
/plugin marketplace add filipeisaac/musterdeck-releases
/plugin install musterdeck@musterdeck
```

(MusterDeck 1.0.0 and earlier installed that skill itself instead; either way you have it.)

By hand:

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

**An app older than `minApp` refuses the theme** (it cannot validate what the file uses),
and a refused theme simply does not appear. Update MusterDeck first.

## Where they come from

Neither theme is hand-written. Every offset is computed from the measured character rig
and asserted before the file is emitted, which is the only way a kit reliably ends up
*on* the body rather than inside it. The generators need the rig tooling in the MusterDeck
repository, so they live there, and this repository is published from it:

```bash
# in the MusterDeck repo
python3 tools/crew-sheet/evolve/jedi_cast.py         # the Enclave's crew
python3 tools/crew-sheet/evolve/kitchen_brigade.py   # the Brigade
python3 tools/crew-sheet/publish-themes.py <this checkout>
```

## What these are, and are not

Each theme here is a description of a world: colours, shapes, the words on the status
pills, and where things stand. They are fan work and brand work respectively, made for
one desktop app's decorative 3D view, and they are not affiliated with, endorsed by or
sponsored by anyone.

- **Jedi Enclave** is fan work. Star Wars and its characters, vehicles and worlds are
  trademarks of Lucasfilm Ltd.; nothing here is official, and no Lucasfilm asset is
  included or redistributed. It is geometry and colour describing an homage, written from
  scratch against MusterDeck's own rig. That is exactly why it is not in the app.
- **Galley Kitchen** uses the palette and vocabulary of Galley Solutions, which is why it
  is not in the app either.

If you own something here and would rather it were not, open an issue and it comes down.

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
