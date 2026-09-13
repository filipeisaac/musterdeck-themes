# -*- coding: utf-8 -*-
"""
The Galley Kitchen crew: chef's whites, researched rather than remembered.

ONE KIT NOW, AND IT WAS THREE. Escoffier, The Line and Patisserie were rendered as
options; Patisserie was chosen and shipped, and the other two were deleted in 5.19
together with The Pass and Batterie from `build-galley-crews.py`, which this file used
to import and which is gone. Five kits for a decision that had been made, and a
generator that can still emit four things nobody uses is four ways to put the wrong one
in the repo -- which is not hypothetical: it happened, as a 716-line diff that looked
like a rebuild and was a revert. The research below is what all five were authored
against and is the reason the shipped one looks the way it does, so it stays.

"I like the whites, but they can still improve a lot ... the Arm goes across the sleeve."

WHY THE ARM CROSSED THE SLEEVE, measured rather than guessed:

    upperarm.l rest (0.211, 1.093, -0.017), local +Y (0.610, -0.758, -0.228)
    hand.l     rest (0.481, 0.634,  0.072)
    the wrist, projected onto the arm bone's own +Y  ->  0.492
    the elbow, about halfway                         ->  0.246

The shipped sleeve was three bands at 0.055, 0.235 and 0.395. The last two reach
0.330 and 0.475 -- both PAST the elbow, on a bone that does not bend. There is no
`lowerarm` in `ATTACH` (nine bones: head, chest, hips, both hands, both upper arms,
both shins), so NOTHING WORN CAN FOLLOW THE FOREARM. The forearm swings and the
cloth stays, and the arm goes through its own sleeve.

It only shows when the elbow bends, which is why it survived the first look: the
idle clip is nearly straight and `wave`, `work`, `cheer` and `hit` are not. So
`assert_above_elbow` is a build-time rule now, and the verification renders every
rank in every clip rather than one pose.

A sleeve that ends at the elbow is not a workaround. It is how a cook wears one.

WHAT THE RESEARCH CHANGED (sources in the commit):

  - TOQUE HEIGHT IS RANK, and that is Escoffier's own system, introduced so that
    anyone walking into the kitchen could see who was in charge. The height ladder
    was the right instinct; it is also literally correct.
  - The pleats are not decoration. Each fold is said to stand for a technique
    mastered, so the column gets real ribs rather than a smooth cylinder.
  - BUTTON COLOUR IS RANK TOO: qualified chefs wear black, students wear white.
    The first pass used gold buttons on everybody, which is a livery button, not a
    chef's. They are KNOTTED CLOTH, chosen to survive boiling washes and hot pans.
  - The double breast is REVERSIBLE -- you re-button the flap to hide a stain
    mid-service. Worth showing as an actual overlapping panel.
  - Trousers are BLACK-AND-WHITE HOUNDSTOOTH, to disguise stains. The mannequin is
    one flat colour, and houndstooth averages to a mid grey at any distance you see
    this map from, so that is what the body is now: not "dark", a specific grey
    standing in for a specific check.
  - The neckerchief is military in origin and practical in use: it catches sweat
    before it reaches the food.
  - Clogs are backless and slip-resistant, which is why they read as a clog and not
    a shoe: the heel is open.

THE THREE, all classic whites, all a different kitchen:

  1 ESCOFFIER   The grand brigade. Starched pleated toques, long bistro aprons to
                the ankle, knotted buttons, a torchon at the waist. Formal.
  2 THE LINE    A working kitchen at service. Short sleeves, half aprons, a skull
                cap on the commis, nothing starched. Moving.
  3 PATISSERIE  The bakehouse. A long white coat instead of a jacket, soft
                mushroom toques instead of starched cylinders, a cross-back apron.
                A different silhouette entirely, still whites.
"""
import json
import math
import os
import sys
import importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location(
    'galley_base', os.path.join(HERE, 'build-galley-kitchen.py'))
G = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(G)

r, chest, hips = G.r, G.chest, G.hips
PI = G.PI
HEAD_R, HEAD_UP = G.HEAD_R, G.HEAD_UP
TORSO_Z, ARM_R, SHIN_R = G.TORSO_Z, G.ARM_R, G.SHIN_R
FACE_TOP = G.FACE_TOP
head_radius_at = G.head_radius_at
TORSO_W, TORSO_D = G.TORSO_W, G.TORSO_D
GREY_400, GREY_800 = G.GREY_400, G.GREY_800

# Galley's palette
WHITE, WHITE_WARM = G.WHITE, G.WHITE_WARM          # antiqueWhite, and a stop down
PRIMARY, GOLD, MARLIN = G.PRIMARY, G.GOLD, G.MARLIN
PUMPKIN, MAHOGANY, AURO = G.PUMPKIN, G.MAHOGANY, G.AURO
NUTMEG, BROCCOLI, ICON_STROKE = G.NUTMEG, G.BROCCOLI, G.ICON_STROKE

# ══ the shared crew kit, moved in from build-galley-crews.py ══════════════════
#
# These eight were shared with two OTHER kitchen crews -- The Pass and Batterie --
# which were offered as options, not chosen, and deleted in 5.19 along with the
# generator that held them. This file was their only remaining consumer, so they live
# here now and it is self-contained.
#
# `head_and_face` and `emerges_above_face` / `top_of` / `crown_of` / `BARE_HEAD` are
# the hat-clearance maths; `wrap_apron` is the one that matters most, because an apron
# is cloth on a body and the first pass was a flat box hanging in front of the chest
# like a card taped on -- reported as "the red rectangle is strange".

# ══ the two things every kit has to get right ═════════════════════════════════════════

def head_and_face(head_colour='#3b322b'):
    """
    The head, and the expression on it.

    The rig DROPS the mannequin's own head mesh, so a kit without these is a headless
    body with nothing saying what its session is doing.
    """
    return [
        {
            'id': 'head', 'bone': 'head', 'at': [0, HEAD_UP, 0],
            'shape': {'sphere': [HEAD_R, 14, 10]},
            'material': {'roughness': 0.84, 'metalness': 0.02, 'color': head_colour},
            'wear': [True, True, True],
        },
        {
            'id': 'face', 'bone': 'head', 'material': 'face', 'tint': 'eye',
            'at': [0, HEAD_UP, 0], 'shadow': False,
            'shape': {'cap': [HEAD_R + 0.008, 1.78, 1.02, 16, 10]},
            'wear': [True, True, True],
        },
    ]


def sleeves(colour, cuff_colour, tiers, prefix='sleeve', rolled=False):
    """
    A CLOTHED ARM, which is the fix for "the arm is bleeding over the sleeves".

    Three short bands rather than one long cylinder. `references/measurements.md`: a limb
    bone's local +Y is about twenty degrees off the limb's own line, so anything long
    walks off the far end of the arm -- but a stack of short ones each stay centred on
    the piece of arm they cover, and the seams read as a sleeve's folds.

    `rolled` stops the stack at the elbow and finishes it with a thick turned-back cuff,
    which is how a cook actually wears a shirt on the line.
    """
    bands = [
        (0.055, 0.20, ARM_R + 0.048),
        (0.235, 0.19, ARM_R + 0.042),
    ]
    if not rolled:
        bands.append((0.395, 0.16, ARM_R + 0.034))
    out = []
    for side in ('l', 'r'):
        pieces = [{'cyl': [rr, rr - 0.006, h, 10], 'shift': [0, y, 0], 'color': colour}
                  for (y, h, rr) in bands]
        last_y, last_h, last_r = bands[-1]
        pieces.append({
            'cyl': [last_r + 0.022, last_r + 0.018, 0.075 if rolled else 0.05, 10],
            'shift': [0, last_y + last_h / 2, 0], 'color': cuff_colour,
        })
        out.append({
            'id': f'{prefix}{side.upper()}', 'bone': f'upperarm.{side}', 'at': [0, 0, 0],
            'shape': {'parts': pieces},
            'material': {'roughness': 0.88, 'metalness': 0, 'vertexColors': True},
            'wear': list(tiers),
        })
    return out


def wrap_apron(part_id, *, top, bottom, colour, tiers, bib, tint='suit',
               material=None, flex_lean=0.22):
    """
    An apron that is CLOTH ON A BODY, which is the fix for "the red rectangle is strange".

    The first one was a flat box hanging in front of the chest. Three things make the
    difference, and none of them is detail: it WRAPS (a centre panel plus two panels
    angled back round the hips, so it has a silhouette from every angle rather than only
    from straight on), it is TIED (a band across the waist, which is what an apron hangs
    from and what stops the top edge floating), and the bib is NARROWER than the skirt,
    which is the shape that makes it read as an apron rather than as a rectangle.

    `top` and `bottom` are world heights; the part hangs off the chest bone.
    """
    height = top - bottom
    mid = (top + bottom) / 2
    bib_h = height * (0.42 if bib else 0)
    skirt_h = height - bib_h
    skirt_mid = -height / 2 + skirt_h / 2
    pieces = [
        # The skirt: centre panel, then two panels turned back round the hip. `rotate`
        # runs before `shift`, so each is turned on the spot and then moved out.
        {'box': [0.34, skirt_h, 0.02], 'shift': [0, skirt_mid, 0.305], 'tint': True},
        {'box': [0.22, skirt_h, 0.02], 'rotate': [0, -0.62, 0],
         'shift': [0.245, skirt_mid, 0.245], 'tint': True},
        {'box': [0.22, skirt_h, 0.02], 'rotate': [0, 0.62, 0],
         'shift': [-0.245, skirt_mid, 0.245], 'tint': True},
    ]
    if bib:
        # THE BIB WRAPS TOO, and it is narrower than the skirt.
        #
        # A flat panel across the chest was the original "the red rectangle is strange",
        # and moving it onto a wrapped skirt fixed the skirt and left the bib flat. So
        # the bib gets the same treatment -- a centre panel and two turned back toward
        # the ribs -- and it tapers, because the thing that makes an apron read as an
        # apron rather than as a board is that its top is narrower than its bottom.
        bib_y = height / 2 - bib_h / 2
        pieces.append({'box': [0.21, bib_h, 0.02], 'shift': [0, bib_y, 0.305],
                       'tint': True})
        pieces.append({'box': [0.13, bib_h, 0.02], 'rotate': [0, -0.58, 0],
                       'shift': [0.155, bib_y, 0.275], 'tint': True})
        pieces.append({'box': [0.13, bib_h, 0.02], 'rotate': [0, 0.58, 0],
                       'shift': [-0.155, bib_y, 0.275], 'tint': True})
        # Straps over the shoulders, which is what actually holds a bib up. Without
        # them the panel floats in front of the chest attached to nothing.
        for sx in (0.15, -0.15):
            pieces.append({'box': [0.055, 0.30, 0.018], 'rotate': [0.30, 0, 0],
                           'shift': [sx, bib_y + bib_h / 2 + 0.11, 0.20],
                           'tint': True})
    # The tie, over the top of the skirt. Not tinted: it is the one part of the garment
    # that is always linen, and it gives the apron a waistline.
    pieces.append({'cyl': [0.40, 0.40, 0.055, 14], 'stretch': [1, 1, 0.78],
                   'shift': [0, -height / 2 + skirt_h - 0.02, -0.30],
                   'color': WHITE_WARM})
    return {
        'id': part_id, 'bone': 'chest', 'tint': tint,
        'at': [0, chest(mid), TORSO_Z],
        'shape': {'parts': pieces},
        'material': material or {'roughness': 0.93, 'metalness': 0,
                                 'double': True, 'vertexColors': True, 'color': colour},
        'flex': {'from': 'top', 'dir': [0, 0, -1], 'side': [1, 0, 0],
                 'sway': 0.028, 'rate': 2.0, 'wave': 2.1,
                 'lean': flex_lean, 'curl': 0.03, 'turn': 0.15, 'bias': 2.0},
        'wear': list(tiers),
    }


def clogs(colour=WHITE, sole=GREY_800, tiers=(True, True, True)):
    out = []
    for side in ('l', 'r'):
        out.append({
            'id': f'clog{side.upper()}', 'bone': f'lowerleg.{side}', 'at': [0, 0.21, 0],
            'shape': {'parts': [
                {'cyl': [SHIN_R + 0.032, SHIN_R + 0.026, 0.13, 10], 'color': colour},
                {'rbox': [0.145, 0.085, 0.17, 0.03], 'shift': [0, -0.03, -0.075],
                 'color': colour},
                {'rbox': [0.15, 0.035, 0.19, 0.014], 'shift': [0, -0.072, -0.07],
                 'color': sole},
            ]},
            'material': {'roughness': 0.72, 'metalness': 0.02, 'vertexColors': True},
            'wear': list(tiers),
        })
    return out


def hands(knife_tiers=(True, True, True), pan_tiers=(True, True, True),
          handle=ICON_STROKE, blade='#d5dae0', fitting=GOLD):
    """
    The knife and the pan, sharing one hand.

    `when: resting` and `when: working` are opposites, so they can never both be there,
    and a cook who has put the knife down to pick up a pan is VISIBLY cooking -- which is
    the thing the map exists to show.

    A hand's local +Y points at the floor, so both need `rot z = PI`, and then a NEGATIVE
    `rot[0]` splays the tool outward where it can be seen (positive tips it across the
    body, behind the arm and the shoulder).
    """
    return [
        {
            'id': 'knife', 'bone': 'hand.r', 'when': 'resting',
            'at': [0, -0.03, 0.03], 'rot': [-0.38, 0, PI], 'tint': 'suit',
            'shape': {'parts': [
                {'rbox': [0.045, 0.14, 0.038, 0.014], 'shift': [0, 0.055, 0],
                 'color': handle},
                {'cyl': [0.026, 0.026, 0.022, 8], 'rotate': [PI / 2, 0, 0],
                 'shift': [0, 0.135, 0], 'color': fitting, 'tint': True},
                {'box': [0.012, 0.40, 0.115], 'shift': [0, 0.355, 0.018], 'color': blade},
                {'cone': [0.062, 0.13, 4], 'rotate': [0, PI / 4, 0],
                 'stretch': [0.2, 1, 1], 'shift': [0, 0.60, 0], 'color': blade},
            ]},
            'material': {'roughness': 0.3, 'metalness': 0.55, 'vertexColors': True},
            'wear': list(knife_tiers),
        },
        {
            'id': 'pan', 'bone': 'hand.r', 'when': 'working',
            'at': [0, -0.04, 0.02], 'rot': [-0.22, 0, PI], 'tint': 'suit',
            'shape': {'parts': [
                {'cyl': [0.026, 0.030, 0.34, 6], 'shift': [0, 0.16, 0], 'color': handle},
                {'cyl': [0.215, 0.165, 0.075, 14], 'shift': [0, 0.36, 0.20],
                 'color': '#3a3a3c'},
                {'cyl': [0.205, 0.16, 0.02, 14], 'shift': [0, 0.40, 0.20],
                 'color': MAHOGANY, 'tint': True},
            ]},
            'material': {'roughness': 0.45, 'metalness': 0.4, 'vertexColors': True},
            'wear': list(pan_tiers),
        },
    ]


# ══ assertions the three kits share ═══════════════════════════════════════════════════

def emerges_above_face(name, centre_y, radius, squash, wide=1.0):
    """
    Where a domed hat first becomes VISIBLE, which is the only height that matters.

    A dome on a sphere dips well below the face's top edge and is inside the head all the
    way down, so checking its lowest point answers the wrong question. This samples the
    silhouette for the height at which the hat's radius overtakes the head's.
    """
    def hat_r(y):
        t = (y - centre_y) / (radius * squash)
        return 0.0 if abs(t) >= 1 else radius * wide * math.sqrt(1 - t * t)

    lo, hi = centre_y - radius * squash, centre_y + radius * squash
    found = None
    for i in range(400):
        y = lo + i * (hi - lo) / 399
        if hat_r(y) > head_radius_at(y) + 1e-6:
            found = y
            break
    assert found is not None, f'{name}: never emerges from the head -- invisible'
    assert found > FACE_TOP, (
        f'{name}: becomes visible at head-local y={found:.3f}, below the face top '
        f'({FACE_TOP}) -- it would cut across the expression')
    return found


def top_of(part):
    """The highest point of a composite, in its bone's frame. Used for the rank ladder."""
    top = -9.0
    for p in part['shape']['parts']:
        if 'cyl' in p: h = p['cyl'][2] / 2
        elif 'sphere' in p: h = p['sphere'][0] * (p.get('stretch', [1, 1, 1])[1])
        elif 'cone' in p: h = p['cone'][1] / 2
        elif 'box' in p: h = p['box'][1] / 2
        elif 'rbox' in p: h = p['rbox'][1] / 2
        elif 'torus' in p: h = p['torus'][1]
        elif 'cap' in p: h = p['cap'][0]
        else: continue
        top = max(top, p.get('shift', [0, 0, 0])[1] + h)
    return top


def crown_of(part):
    """How high a hat reaches in the BONE's frame: its own offset plus its tallest piece.

    Two hats that sit at different offsets cannot be compared on `top_of` alone, and the
    rank ladder is exactly a comparison between two hats at different offsets.
    """
    return part['at'][1] + top_of(part)


BARE_HEAD = HEAD_UP + HEAD_R        # 0.84, the crown of a hatless cook


# ══ A. WHITES ═════════════════════════════════════════════════════════════════════════
#
# The brigade as it dresses itself, done properly this time. Rank is HEIGHT, and the gaps
# are the point: a commis wears a flat cap that barely clears the crown, a chef de partie
# a toque, an executive chef a toque half a head taller again. The first pass had 0.30 and
# 0.62 of column and they read as "a toque and a toque"; this one has 0.26 and 0.86, and
# the executive also gains a long coat and a floor-length apron so the two top ranks
# differ in LENGTH as well as height. One axis is what "too close" looks like.


CREAM = '#FBF3E6'          # the crown of a starched toque, catching the light
LINEN = '#E7DAC4'
FLOUR = '#F4ECDE'
BUTTON_DARK = '#22201E'    # a qualified chef's knotted button
BUTTON_LIGHT = '#EDE2CE'   # a student's

# THE TROUSERS ARE BLACK, and the check goes somewhere it can actually be a check.
#
# The first instinct was to make the body the mid grey a black-and-white houndstooth
# averages to. `assert_tones_read` refused it at 1.07:1 against `low`, and it was
# right: the apron carries the effort colour and a mid-grey leg behind a mid-blue
# apron is one shape, not two. Every grey down to near-black fails the same test --
# the effort ladder simply occupies the middle of the value range.
#
# So the body stays near-black, which is what most kitchens actually wear now, and
# the houndstooth appears as a real two-tone check on the trouser cuff, which is the
# only part of the leg you see below an apron anyway.
TROUSER = '#241F1D'
CHECK_PALE = '#CFC7B8'

# ── the rule the reported bug becomes ─────────────────────────────────────────────────
WRIST_Y = 0.492
ELBOW_Y = WRIST_Y / 2          # 0.246
SLEEVE_LIMIT = 0.215           # with margin, because the elbow is an estimate
SHIN_LIMIT = 0.27              # lowerleg bone at y 0.283, the foot at the floor


def _piece_span(p):
    """A composite piece's extent along its own +Y, from its shape and shift."""
    if 'cyl' in p or 'shell' in p:
        h = p['cyl'][2] if 'cyl' in p else p['shell'][2]
    elif 'box' in p:
        h = p['box'][1]
    elif 'rbox' in p:
        h = p['rbox'][1]
    elif 'sphere' in p:
        h = p['sphere'][0] * 2
    elif 'cone' in p:
        h = p['cone'][1]
    elif 'torus' in p:
        h = p['torus'][1] * 2
    else:
        return None
    st = p.get('stretch')
    if isinstance(st, list):
        h *= st[1]
    rot = p.get('rotate')
    if isinstance(rot, list):
        rx, _, rz = (list(rot) + [0, 0, 0])[:3]
        # A quarter turn about X or Z lays the piece down; its span along Y becomes
        # its width, which for everything used here is its radius or half-width.
        if abs(abs(rx) - PI / 2) < 0.1 or abs(abs(rz) - PI / 2) < 0.1:
            if 'cyl' in p:
                h = max(p['cyl'][0], p['cyl'][1]) * 2
            elif 'box' in p:
                h = p['box'][0]
    y = p.get('shift', [0, 0, 0])[1]
    return (y - h / 2, y + h / 2)


def assert_above_elbow(part):
    """
    NOTHING WORN ON AN UPPER ARM MAY REACH THE ELBOW.

    The whole of the reported bug, as a build-time rule. The forearm is driven by
    `lowerarm`, which is not one of the nine attach bones, so cloth hung past the
    elbow stays with the upper arm while the forearm swings out of it. Invisible in
    the idle clip; obvious the moment anybody waves.
    """
    if not part['bone'].startswith('upperarm'):
        return
    base = part.get('at', [0, 0, 0])[1]
    pieces = part['shape'].get('parts', [part['shape']])
    for p in pieces:
        span = _piece_span(p)
        if not span:
            continue
        far = base + span[1]
        assert far <= SLEEVE_LIMIT, (
            f'{part["id"]}: a piece reaches upper-arm y={far:.3f}, past the elbow at '
            f'{ELBOW_Y:.3f}. Nothing can follow the forearm -- there is no `lowerarm` '
            f'attach bone -- so it will be walked through the moment the arm bends.')


def assert_on_shin(part):
    if not part['bone'].startswith('lowerleg'):
        return
    base = part.get('at', [0, 0, 0])[1]
    for p in part['shape'].get('parts', [part['shape']]):
        span = _piece_span(p)
        if span and base + span[1] > SHIN_LIMIT + 0.02:
            raise AssertionError(
                f'{part["id"]}: reaches shin y={base + span[1]:.3f}, past the foot')


def check(parts):
    for p in parts:
        assert_above_elbow(p)
        assert_on_shin(p)
    return parts


# ── shared pieces ─────────────────────────────────────────────────────────────────────

def short_sleeve(colour, cuff_colour, tiers, length=0.20, prefix='sleeve'):
    """
    A sleeve that stops at the elbow, with a turned cuff to say it meant to.

    Two bands rather than one cylinder: a limb bone's +Y is about twenty degrees off
    the limb's own line, so even over this short a run two short pieces sit on the arm
    better than one long one.
    """
    out = []
    top = length
    for side in ('l', 'r'):
        out.append({
            'id': f'{prefix}{side.upper()}', 'bone': f'upperarm.{side}', 'at': [0, 0, 0],
            'shape': {'parts': [
                {'cyl': [ARM_R + 0.055, ARM_R + 0.048, top * 0.62, 12],
                 'shift': [0, top * 0.30, 0], 'color': colour},
                {'cyl': [ARM_R + 0.050, ARM_R + 0.060, top * 0.30, 12],
                 'shift': [0, top * 0.76, 0], 'color': cuff_colour},
            ]},
            'material': {'roughness': 0.88, 'metalness': 0, 'vertexColors': True},
            'wear': list(tiers),
        })
    return out


def wristband(colour, tiers):
    """
    A cuff at the WRIST, on the hand bone.

    The forearm cannot be dressed, so it is framed instead: cloth at the shoulder end
    and cloth at the wrist end, with the arm between them, which is exactly what a
    rolled sleeve looks like.
    """
    out = []
    for side in ('l', 'r'):
        out.append({
            'id': f'wrist{side.upper()}', 'bone': f'hand.{side}', 'at': [0, -0.075, 0],
            'shape': {'cyl': [ARM_R + 0.028, ARM_R + 0.022, 0.075, 10]},
            'material': {'roughness': 0.9, 'metalness': 0, 'color': colour},
            'wear': list(tiers),
        })
    return out


def toque(part_id, column_h, crown_r, tiers, *, pleats=10, band=WHITE_WARM,
          cloth=WHITE, crown=CREAM, soft=False):
    """
    A toque blanche.

    Escoffier set the heights to show rank; the pleats are said to count the
    techniques their wearer has mastered, so they are ribs on the column rather
    than a smooth wall. `soft` swaps the starched cylinder for the baker's
    mushroom: no band, a wider crown, and the column tucked under it.
    """
    band_h, band_bottom, band_r = 0.085, 0.685, 0.305
    assert band_bottom > FACE_TOP, f'{part_id}: the band would cross the face'
    pieces = []
    if not soft:
        pieces.append({'cyl': [band_r, band_r + 0.014, band_h, 16],
                       'shift': [0, band_bottom + band_h / 2, 0], 'color': band})
    col_bot = band_bottom + (band_h if not soft else 0.0)
    col_r = band_r + (0.012 if not soft else -0.03)
    pieces.append({'cyl': [col_r + (0.03 if soft else 0), col_r, column_h, 14],
                   'shift': [0, col_bot + column_h / 2, 0], 'color': cloth})
    # The pleats.
    for i in range(pleats):
        a = i * 2 * PI / pleats
        pieces.append({
            'box': [0.022, column_h * 0.92, 0.022],
            'shift': [r(math.cos(a) * (col_r + 0.012)), col_bot + column_h / 2,
                      r(math.sin(a) * (col_r + 0.012))],
            'color': band,
        })
    crown_y = col_bot + column_h + crown_r * (0.30 if not soft else 0.42)
    pieces.append({'sphere': [crown_r, 16, 10],
                   'stretch': [1, 0.80 if soft else 0.58, 1],
                   'shift': [0, crown_y, 0], 'color': crown})
    return {
        'id': part_id, 'bone': 'head', 'at': [0, 0, 0],
        'shape': {'parts': pieces},
        'material': {'roughness': 0.92, 'metalness': 0, 'vertexColors': True},
        'wear': tiers,
    }


def neckerchief(tiers, cloth=WHITE):
    """Over the collar, never inside it. Sized against the jacket's collar band."""
    collar_r = 0.40 - 0.045
    ring, tube = 0.315, 0.072
    assert ring + tube > collar_r + 0.01, 'the neckerchief is inside the jacket'
    return {
        'id': 'neckerchief', 'bone': 'chest', 'tint': 'suit',
        'at': [0, chest(1.232), TORSO_Z],
        'shape': {'parts': [
            {'torus': [ring, tube, 8, 10, 6.2832], 'rotate': [PI / 2, 0, 0],
             'stretch': [1, 1, 0.78], 'tint': True},
            {'sphere': [0.075, 8, 6], 'shift': [0, -0.045, 0.235], 'tint': True},
            {'cone': [0.062, 0.15, 6], 'rotate': [0.3, 0, 0],
             'shift': [0, -0.15, 0.225], 'tint': True},
        ]},
        'material': {'roughness': 0.85, 'metalness': 0, 'vertexColors': True,
                     'color': cloth},
        'wear': list(tiers),
    }


def buttons(front_z, mid_y, tiers_single, tiers_double, dark=True):
    """
    Knotted cloth buttons, and their colour is RANK: black for a qualified chef,
    white for a student. Not gold -- gold is a livery button, not a chef's.

    Knotted, so a little sphere with a cross seam rather than a flat disc.
    """
    single = [{'at': [0.035, 0.17 - i * 0.145, front_z]} for i in range(3)]
    double = []
    for i in range(4):
        y = 0.21 - i * 0.135
        double.append({'at': [0.105, y, front_z - 0.004]})
        double.append({'at': [-0.035, y, front_z - 0.004]})
    return {
        'id': 'buttons', 'bone': 'chest', 'at': [0, mid_y, TORSO_Z],
        'shape': {'parts': [
            {'sphere': [0.030, 8, 6], 'stretch': [1, 1, 0.62]},
            {'box': [0.052, 0.010, 0.012], 'shift': [0, 0, 0.014],
             'color': '#00000022'},
        ]},
        'material': {'roughness': 0.7, 'metalness': 0.05,
                     'color': BUTTON_DARK if dark else BUTTON_LIGHT},
        'wear': [{'copies': single}, {'copies': double}, {'copies': double}]
        if tiers_single else [None, {'copies': double}, {'copies': double}],
    }


def torchon(tiers, colour=BROCCOLI, at_x=-0.24):
    """The kitchen towel, tucked into the apron string. Every cook has one."""
    return {
        'id': 'torchon', 'bone': 'hips', 'at': [at_x, hips(0.62), 0.17],
        'shape': {'box': [0.14, 0.30, 0.022]},
        'material': {'roughness': 0.96, 'double': True, 'color': colour},
        'flex': {'from': 'top', 'dir': [0, 0, -1], 'sway': 0.04, 'rate': 2.8,
                 'wave': 3.0, 'lean': 0.26, 'turn': 0.22, 'bias': 1.7},
        'wear': list(tiers),
    }


def trouser_shins(dark, tiers, pale=None, checked=True):
    """
    The trouser cuff, with the houndstooth ON it.

    The body cannot be a check -- it is one flat colour for arms and legs both -- so
    the check goes on the one part of the leg an apron leaves visible. Eight facets
    round the cuff, alternating pale and dark: at the distance this map is read from
    that is exactly what a fine black-and-white check resolves to, and up close it is
    a plausible weave rather than a gradient.
    """
    pale = pale or CHECK_PALE
    out = []
    for side in ('l', 'r'):
        pieces = [{'cyl': [SHIN_R + 0.040, SHIN_R + 0.050, 0.20, 12], 'color': dark}]
        if checked:
            facets = 8
            for i in range(facets):
                a = i * 2 * PI / facets
                pieces.append({
                    'box': [0.042, 0.19, 0.020], 'rotate': [0, r(-a), 0],
                    'shift': [r(math.sin(a) * (SHIN_R + 0.050)), 0.0,
                              r(math.cos(a) * (SHIN_R + 0.050))],
                    'color': pale if i % 2 == 0 else dark,
                })
        # The hem, which is what stops the clog looking like a boot growing out of a
        # bare shin.
        pieces.append({'cyl': [SHIN_R + 0.056, SHIN_R + 0.050, 0.035, 12],
                       'shift': [0, 0.10, 0], 'color': dark})
        out.append({
            'id': f'cuff{side.upper()}', 'bone': f'lowerleg.{side}', 'at': [0, 0.04, 0],
            'shape': {'parts': pieces},
            'material': {'roughness': 0.9, 'vertexColors': True},
            'wear': list(tiers),
        })
    return out


def jacket(part_id, *, top, bottom, cloth=WHITE, trim=WHITE_WARM, double=True,
           tiers=(True, True, True)):
    """
    The double-breasted jacket: thick cotton, and REVERSIBLE -- you re-button the
    flap over a stain mid-service. Worth drawing as a panel that actually laps.

    Encloses the 0.72 x 0.53 torso: radius 0.40 is 0.80 across, z 0.75 is 0.60 deep.
    """
    jr, jz = 0.40, 0.75
    G.encloses_torso(part_id, jr, jz)
    jh = top - bottom
    front = jr * jz
    pieces = [
        {'cyl': [jr - 0.012, jr, jh, 16], 'stretch': [1, 1, jz], 'color': cloth},
        {'cyl': [jr - 0.055, jr - 0.045, 0.08, 16], 'stretch': [1, 1, jz],
         'shift': [0, jh / 2 - 0.02, 0], 'color': trim},
        {'cyl': [jr, jr + 0.008, 0.05, 16], 'stretch': [1, 1, jz],
         'shift': [0, -jh / 2 + 0.02, 0], 'color': trim},
    ]
    if double:
        # The lapping panel, off-centre, with a visible edge: this IS the double breast.
        pieces.append({'rbox': [0.33, jh - 0.07, 0.028, 0.012],
                       'shift': [0.05, 0, front - 0.010], 'color': cloth})
        pieces.append({'box': [0.014, jh - 0.07, 0.03],
                       'shift': [-0.115, 0, front - 0.004], 'color': trim})
    else:
        pieces.append({'box': [0.022, jh - 0.06, 0.03],
                       'shift': [0, 0, front - 0.004], 'color': trim})
    return {
        'id': part_id, 'bone': 'chest', 'at': [0, chest((top + bottom) / 2), TORSO_Z],
        'shape': {'parts': pieces},
        'material': {'roughness': 0.9, 'metalness': 0, 'vertexColors': True},
        'wear': list(tiers),
    }, front, chest((top + bottom) / 2)


# ══ 1. ESCOFFIER ══════════════════════════════════════════════════════════════════════
#
# The grand brigade, and the most literal reading of the research: Escoffier set toque
# heights to show rank, so that is the whole ladder -- 0.16, 0.46, 0.94 of starched
# pleated column. Long bistro aprons, knotted buttons (white on the commis because a
# student wears white, black on the two above), a torchon at the waist, neckerchiefs.

# ══ THE CREW: PÂTISSERIE ═════════════════════════════════════════════
#
# ONE KIT, because one was chosen. There were three: Escoffier (the starched brigade),
# The Line (a modern service kitchen), and this. Escoffier and The Line were deleted in
# 5.19 along with The Pass and Batterie from the other generator -- five researched
# options for a decision that was made, and a generator that can still emit four things
# nobody uses is four ways to put the wrong one in the repo.
#
# What Pâtisserie is: a long white coat instead of a cropped jacket and soft mushroom
# toques instead of starched cylinders, so the figure reads as a different SHAPE before
# any detail. Rank is still HEIGHT -- Escoffier's own system, introduced so anyone
# walking into the kitchen could see who was in charge -- and it runs beret, mushroom,
# grand mushroom.

def kit_patisserie():
    parts = head_and_face('#3b322b')

    # A soft beret, and it has to clear a bare head by a MARGIN rather than by a
    # rounding error: the first one topped out at 0.8599 against a crown of 0.84, which
    # passed by 0.0001 and read as a skullcap pressed flat.
    beret = {
        'id': 'beret', 'bone': 'head', 'at': [0, 0.745, 0],
        'shape': {'parts': [
            {'sphere': [0.355, 14, 8], 'stretch': [1.06, 0.46, 1.06], 'color': FLOUR},
            {'cyl': [0.305, 0.305, 0.05, 14], 'shift': [0, -0.07, 0], 'color': LINEN},
        ]},
        'material': {'roughness': 0.94, 'vertexColors': True},
        'wear': [True, None, None],
    }
    emerges_above_face('patisserie/beret', 0.745, 0.355, 0.46, 1.06)
    assert crown_of(beret) > BARE_HEAD + 0.05, (
        f'the beret clears a bare head by only {crown_of(beret) - BARE_HEAD:.4f}')
    mid = toque('mushroom', 0.16, 0.42, [None, True, None], pleats=8, soft=True,
                cloth=FLOUR, crown=FLOUR, band=LINEN)
    tall = toque('mushroomGrand', 0.56, 0.50, [None, None, True], pleats=10, soft=True,
                 cloth=FLOUR, crown=FLOUR, band=LINEN)
    # The generator's bars are TIGHTER than the test's, so the build is what fails first.
    # The grand mushroom cleared the middle one by 0.3976 against a test that wanted
    # 0.40: a gap you have to measure to believe is not a rank ladder.
    assert crown_of(mid) > crown_of(beret) + 0.30, (
        f'ranks 0 and 1 differ by only {crown_of(mid) - crown_of(beret):.3f}')
    assert crown_of(tall) > crown_of(mid) + 0.45, (
        f'ranks 1 and 2 differ by only {crown_of(tall) - crown_of(mid):.3f}')
    parts += [beret, mid, tall]

    # THE LONG COAT. This is the silhouette: it runs to the knee, where the other two
    # kits stop at the hip, so the figure reads as a different shape before any detail.
    coat, front, mid_y = jacket('coat', top=1.25, bottom=0.70, cloth=FLOUR, trim=LINEN,
                                double=False)
    parts.append(coat)
    parts.append({
        'id': 'coatSkirt', 'bone': 'chest', 'at': [0, chest(0.55), TORSO_Z],
        'shape': {'shell': [0.40, 0.44, 0.34, 12], 'stretch': [1, 1, 0.78]},
        'material': {'roughness': 0.92, 'double': True, 'color': FLOUR},
        'flex': {'from': 'top', 'dir': [0, 0, -1], 'side': [1, 0, 0], 'sway': 0.03,
                 'rate': 1.9, 'wave': 1.8, 'lean': 0.2, 'turn': 0.14, 'bias': 1.9},
        'wear': [True, True, True],
    })
    b = buttons(front + 0.012, mid_y, True, False, dark=False)
    b['wear'] = [{'copies': [{'at': [0.0, 0.20 - i * 0.135, front + 0.010]}
                             for i in range(4)]}] * 3
    parts.append(b)

    parts.append(neckerchief([None, True, True], cloth=LINEN))
    parts += short_sleeve(FLOUR, LINEN, [True, True, True], length=0.20)
    parts += wristband(LINEN, [True, True, True])

    # A cross-back apron: the straps cross behind, which is what you see from the map's
    # usual three-quarter view, and it is the apron a bakehouse actually wears.
    parts.append(wrap_apron('apronBaker', top=1.06, bottom=0.22, colour=LINEN,
                            tiers=[True, True, {'scale': 1.06}], bib=True))
    parts.append({
        'id': 'crossBack', 'bone': 'chest', 'at': [0, chest(1.05), -0.30],
        'shape': {'parts': [
            {'box': [0.07, 0.46, 0.02], 'rotate': [0, 0, 0.46], 'shift': [0.02, 0, 0],
             'color': LINEN},
            {'box': [0.07, 0.46, 0.02], 'rotate': [0, 0, -0.46], 'shift': [-0.02, 0, 0],
             'color': LINEN},
        ]},
        'material': {'roughness': 0.94, 'vertexColors': True},
        'wear': [True, True, True],
    })
    parts.append(torchon([True, True, True], colour=LINEN, at_x=0.26))
    parts += trouser_shins(TROUSER, [True, True, True], pale='#D8CDBA')
    parts += clogs(colour=FLOUR, sole='#3A342E')

    # A rolling pin instead of a knife at rest: this is a pastry section.
    parts += hands(knife_tiers=[True, True, True], handle='#8A6A44',
                   blade='#E4E9EE', fitting=NUTMEG)
    parts.append({
        'id': 'rollingPin', 'bone': 'hand.l', 'when': 'resting',
        'at': [0, -0.03, 0.03], 'rot': [-0.34, 0, PI],
        'shape': {'parts': [
            {'cyl': [0.075, 0.075, 0.40, 10], 'shift': [0, 0.34, 0], 'color': '#C8A97E'},
            {'cyl': [0.028, 0.028, 0.12, 8], 'shift': [0, 0.10, 0], 'color': '#9C7B52'},
            {'cyl': [0.028, 0.028, 0.12, 8], 'shift': [0, 0.60, 0], 'color': '#9C7B52'},
        ]},
        'material': {'roughness': 0.8, 'vertexColors': True},
        'wear': [None, True, True],
    })
    return check(parts)


KITS = {
    'w3-patisserie': ('Galley Kitchen · Pâtisserie', kit_patisserie),
}


def main():
    base = G.theme()
    out_dir = sys.argv[1] if len(sys.argv) > 1 else 'themes/unshipped'
    # A per-kit file is written only when an out-dir is named, because that is a review
    # artifact: three `galley-w*.json` beside the shipped themes were three themes in the
    # picker that nobody chose, in the folder that means "ships with the app".
    options = len(sys.argv) > 1
    for key, (name, build) in KITS.items():
        parts = build()
        problems = G.lint_crew(parts)
        if problems:
            print(f'{key}: PROBLEMS')
            for p in problems:
                print('   -', p)
            sys.exit(1)
        t = json.loads(json.dumps(base))
        t['id'] = f'galley-{key}'
        t['name'] = name
        t['crew']['parts'] = parts
        t['crew']['body'] = {'color': TROUSER, 'roughness': 0.9, 'metalness': 0.02,
                             'tint': 'none'}
        G.assert_tones_read(t['crew']['body']['color'], t['crew']['effortTones'])
        path = os.path.join(out_dir, f'galley-{key}.json')
        if options:
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(t, f, indent=1)
                f.write('\n')
        worn = [sum(1 for p in parts if p['wear'][i] is not None) for i in range(3)]
        arms = max((p['at'][1] + max(_piece_span(q)[1]
                                     for q in p['shape'].get('parts', [p['shape']])
                                     if _piece_span(q))
                    for p in parts if p['bone'].startswith('upperarm')), default=0)
        print(f'  {key:14} {len(parts):3} parts  worn/rank {worn}  '
              f'furthest sleeve y={arms:.3f} (elbow {ELBOW_Y:.3f})'
              + (f'  -> {path}' if options else ''))

    # The theme that ships carries one of them, so the Crew is never holding a kit
    # nobody has chosen.
    #
    # THE DEFAULT IS THE ONE THAT WAS CHOSEN, and it has to be. It was `w1-escoffier`
    # while the three were still options, and after Patisserie was picked and shipped a
    # plain re-run of this file silently put Escoffier back into the shipped theme --
    # a 716-line diff that looks like a rebuild and is a revert. A generator's default
    # output is the thing in the repo, or the generator is a trap.
    default_key = os.environ.get('GALLEY_CREW', 'w3-patisserie')
    if default_key in KITS:
        base['crew']['parts'] = KITS[default_key][1]()
        base['crew']['body'] = {'color': TROUSER, 'roughness': 0.9, 'metalness': 0.02,
                                'tint': 'none'}
        main_path = os.path.join(out_dir, 'galley-kitchen.json')
        with open(main_path, 'w', encoding='utf-8') as f:
            json.dump(base, f, indent=1)
            f.write('\n')
        print(f'  galley-kitchen.json carries "{default_key}"')


if __name__ == '__main__':
    main()
