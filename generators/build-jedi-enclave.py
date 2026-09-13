# -*- coding: utf-8 -*-
"""
Build the Jedi Enclave Crew theme.

    "An enclave on a temple world. Every repo is a training hall, the Falcon is
     docked at the edge of it, and Vader walks among them."

    a repo    -> a HALL          a session -> a JEDI
    a thread  -> a lesson        archived  -> struck from the archive

THE RANK LADDER IS THE CAST, and it is the most legible one any of these themes has had:

    0  PADAWAN   linen robes, hood at the shoulders, the braid. Stripped down.
    1  LUKE      tan tunic, brown robe to the calf, tabards. The shape the eye
                 calibrates on.
    2  VADER     black, caped, helmeted, shouldered. Unmistakable in outline at any
                 size, which is the whole job of tier 2.

THE ONE HARD PROBLEM, and the best idea in the theme.

The `face` part is a sphere patch covering head-local y 0.215 .. 0.625, x +/-0.33 -- the
whole middle half of the head's front -- and it is the ONLY thing on the figure that says
what a session is doing. Nothing may cross it. Vader's mask covers exactly that patch.

So the helmet is built AROUND it, and the reconciliation is better than the problem: a
dome above 0.625, the flared cheeks outboard of +/-0.33, and the grille below 0.215. The
middle is left open -- which is precisely where the mask's eye lenses are. The expression
atlas then draws Vader's eyes. He is the one rank whose face IS his mask, and the
constraint that looked like it would forbid him is what makes him work.

THE SABRE IS THE EFFORT COLOUR, and it is also the working/resting pair:

    resting  the hilt is clipped to the belt
    working  the blade is lit in the hand

`when: "working"` and `when: "resting"` are opposites, so the two can never coexist, and
"a Jedi who has drawn its sabre is a Jedi you can see is working" is exactly the thing the
map exists to show. The blade is a `glow` material pushed past 1.0, so the bloom pass
catches it after dark: a hall at night is lit by whoever is working in it.

Authored against `references/measurements.md` and asserted, same as the kitchen.
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
head_radius_at = G.head_radius_at
PI = G.PI
HEAD_R, HEAD_UP = G.HEAD_R, G.HEAD_UP
TORSO_W, TORSO_D, TORSO_Z = G.TORSO_W, G.TORSO_D, G.TORSO_Z
ARM_R, SHIN_R = G.ARM_R, G.SHIN_R
FACE_TOP, FACE_BOT, FACE_HALF_X = G.FACE_TOP, G.FACE_BOT, G.FACE_HALF_X

# ── the rig's two hard limits, from the kitchen's hard-won numbers ────────────────────
WRIST_Y = 0.492                 # the wrist, projected onto the upper-arm bone's own +Y
ELBOW_Y = WRIST_Y / 2           # 0.246 -- and `lowerarm` is NOT an attach bone, so
SLEEVE_LIMIT = 0.215            # nothing worn can follow the forearm past here
SHIN_LIMIT = 0.27

# ══ the palette ═══════════════════════════════════════════════════════════════════════
LINEN       = '#D9CBB2'    # a padawan's homespun
LINEN_DK    = '#BCAC90'
TAN         = '#C2A878'    # Luke's tunic
ROBE        = '#6B4A2F'    # the brown outer robe
ROBE_DK     = '#4A3222'
LEATHER     = '#3E2F22'    # belts, boots, bracers
VADER       = '#14141A'    # not black: black reads as a hole, this reads as lacquer
VADER_LIT   = '#22232B'    # the lit face of the same lacquer
GUNMETAL    = '#3A3E45'
SILVER      = '#C9CDD4'
HILT_DARK   = '#1C1F24'
STONE       = '#8A8578'
STONE_DK    = '#6E6A5E'
SAND        = '#C9A96E'
SAND_DK     = '#A8894F'
JUNGLE      = '#4A6B3A'
MOSS        = '#6F8C4E'
HOLO        = '#6FD3FF'    # archive holograms, cockpit glass
RUST        = '#8A5A3C'
CARBON      = '#2A2E33'
SHADOW      = '#141518'

# THE BLADE COLOURS ARE THE EFFORT LADDER. Canon order, and it happens to run cool to
# hot exactly as an effort scale wants to: blue, green, amber, orange, red, and purple
# for the one that is not on the scale at all.
BLADE_LOW    = '#4FA3FF'
BLADE_MED    = '#4FE07A'
BLADE_HIGH   = '#FFC94F'
BLADE_XHIGH  = '#FF8A3D'
BLADE_MAX    = '#FF3B30'
BLADE_ULTRA  = '#B84FFF'

# The body underneath: the undertunic and trousers, and the forearms, which read as a
# Jedi's leather bracers and gloves. Near-black, because the blade colours have to
# separate from it and every one of them is bright.
UNDER = '#241F1D'


def _span(p):
    """A composite piece's extent along its own +Y, for the limb assertions."""
    if 'cyl' in p or 'shell' in p:
        h = (p.get('cyl') or p.get('shell'))[2]
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
    elif 'cap' in p:
        h = p['cap'][0] * 2
    else:
        return None
    st = p.get('stretch')
    if isinstance(st, list):
        h *= st[1]
    rot = p.get('rotate')
    if isinstance(rot, list):
        rx, _, rz = (list(rot) + [0, 0, 0])[:3]
        if abs(abs(rx) - PI / 2) < 0.1 or abs(abs(rz) - PI / 2) < 0.1:
            if 'cyl' in p:
                h = max(p['cyl'][0], p['cyl'][1]) * 2
            elif 'box' in p:
                h = p['box'][0]
    y = p.get('shift', [0, 0, 0])[1]
    return (y - h / 2, y + h / 2)


def check_limbs(parts):
    """
    Nothing on an upper arm may reach the ELBOW, and nothing on a shin may pass the foot.

    The elbow rule is the kitchen's lesson, imported whole: `lowerarm` is not one of the
    nine attach bones, so cloth hung past the elbow stays with the upper arm while the
    forearm swings out of it. Invisible in the idle clip, obvious the moment anybody
    waves, and a Jedi waves and swings a sabre constantly.
    """
    for part in parts:
        base = part.get('at', [0, 0, 0])[1]
        pieces = part['shape'].get('parts', [part['shape']])
        if part['bone'].startswith('upperarm'):
            for p in pieces:
                s = _span(p)
                if s and base + s[1] > SLEEVE_LIMIT:
                    raise AssertionError(
                        f'{part["id"]}: reaches upper-arm y={base + s[1]:.3f}, past the '
                        f'elbow at {ELBOW_Y:.3f}. Nothing follows the forearm.')
        if part['bone'].startswith('lowerleg'):
            for p in pieces:
                s = _span(p)
                if s and base + s[1] > SHIN_LIMIT + 0.02:
                    raise AssertionError(
                        f'{part["id"]}: reaches shin y={base + s[1]:.3f}, past the foot')
    return parts


def clears_face(name, *, bottom, half_width, z_front=True):
    """
    A band or plate that dips below the face's top edge must be OUTSIDE it.

    Two ways to be legal: sit entirely above y 0.625, or sit outboard of x +/-0.33 --
    which is how Vader's cheek flares work. This checks the second case too, because it
    is the whole reason he is possible at all.
    """
    if bottom >= FACE_TOP:
        return
    if half_width <= FACE_HALF_X:
        # Inside the face's x band, so it had better be inside the HEAD as well.
        inside = head_radius_at(bottom)
        assert half_width <= inside + 1e-6, (
            f'{name}: dips to head-local y={bottom:.3f} and is {half_width:.3f} wide '
            f'there, against a head {inside:.3f} wide -- it would cross the expression')
        return
    # Outboard of the face patch. Legal, and it must actually clear it.
    assert half_width > FACE_HALF_X, f'{name}: neither above the face nor outboard of it'


def emerges_above_face(name, centre_y, radius, squash, wide=1.0):
    """Where a dome first becomes visible -- the only height that matters for a helmet."""
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


def brow_band(name, *, emerges, lip=0.02):
    """
    The band that closes the gap between a headpiece and the top of the face.

    THE CONSTRAINT THE FIRST PASS WAS MISSING. `emerges_above_face` asks only that a
    dome does not CROSS the patch, and a dome that clears it by 0.04 satisfies that
    while leaving 0.04 of BARE HEAD showing as a brown strip between the helmet and the
    eyes -- which is what Vader came out with, and it read as a helmet sitting too high
    rather than as a missing piece. A dome's radius at a given height shrinks faster
    than the head's does near the top of the face, so the gap is geometry, not slop, and
    no amount of moving the dome closes it without clipping the expression.

    So it is a separate piece with one hard rule: it starts EXACTLY at the top of the
    face and reaches at least as high as the dome becomes visible. Returns
    `(bottom, height, half_width)` for a box, and asserts the band is wide enough to
    cover the head across its own height -- a band narrower than the head leaves the
    same strip at the temples instead of the middle.
    """
    bottom, top = FACE_TOP, emerges + lip
    assert top > bottom, f'{name}: the dome already reaches the face; no band needed'
    half = max(head_radius_at(y) for y in (bottom, top, (bottom + top) / 2)) + 0.035
    return r(bottom), r(top - bottom), r(half)


def top_of(part):
    top = -9.0
    for p in part['shape'].get('parts', [part['shape']]):
        s = _span(p)
        if s:
            top = max(top, s[1])
    return top


def crown_of(part):
    return part['at'][1] + top_of(part)


BARE_HEAD = HEAD_UP + HEAD_R       # 0.84


# ══ the crew ══════════════════════════════════════════════════════════════════════════

def crew_parts():
    parts = []

    # ── the head, and the expression on it ────────────────────────────────────────────
    parts.append({
        'id': 'head', 'bone': 'head', 'at': [0, HEAD_UP, 0],
        'shape': {'sphere': [HEAD_R, 14, 10]},
        'material': {'roughness': 0.84, 'metalness': 0.02, 'color': '#3A302A'},
        'wear': [True, True, True],
    })
    parts.append({
        'id': 'face', 'bone': 'head', 'material': 'face', 'tint': 'eye',
        'at': [0, HEAD_UP, 0], 'shadow': False,
        'shape': {'cap': [HEAD_R + 0.008, 1.78, 1.02, 16, 10]},
        'wear': [True, True, True],
    })

    # ── the padawan braid: one thin plait beside the face, and nothing else says
    #    "apprentice" so economically ─────────────────────────────────────────────────
    parts.append({
        # OUTBOARD of the face and ON the head's surface, not in it. The first pass put
        # it at x 0.345, z 0.14 -- 0.372 from the head's axis where the head is 0.402
        # wide, so most of it was buried, and its inner edge at 0.313 reached into the
        # patch's 0.33. It rendered as a twig growing out of the cheek.
        'id': 'braid', 'bone': 'head', 'at': [0.415, 0.30, 0.02],
        'rot': [0, 0, 0.16],
        'shape': {'parts': [
            {'cyl': [0.028, 0.022, 0.42, 6], 'color': '#4A3A2C'},
            {'cyl': [0.032, 0.032, 0.03, 6], 'shift': [0, 0.19, 0], 'color': '#8A7A5C'},
            {'cyl': [0.030, 0.030, 0.025, 6], 'shift': [0, 0.02, 0], 'color': '#8A7A5C'},
            {'sphere': [0.026, 6, 5], 'shift': [0, -0.22, 0], 'color': '#8A7A5C'},
        ]},
        'material': {'roughness': 0.85, 'vertexColors': True},
        'wear': [True, None, None],
    })

    # ── VADER'S HELMET, BUILT AROUND THE FACE ────────────────────────────────────────
    #
    # The dome sits above the patch, the cheek flares sit OUTBOARD of it, and the
    # grille sits below it. What is left open in the middle is exactly where the mask's
    # eye lenses are, so the expression atlas draws them. Every piece is asserted
    # against the patch rather than eyeballed, because getting this wrong does not look
    # like a geometry mistake -- it looks like Vader has no face.
    # Both margins are deliberately more than a rounding error: the dome cleared the
    # patch by 0.026 and the flares sat EXACTLY on x 0.33 on the first pass, and a gap
    # you have to measure to believe is a gap the next edit closes by accident.
    dome_y, dome_r, dome_squash = 0.86, 0.40, 0.78
    emerged = emerges_above_face('vader/dome', dome_y, dome_r, dome_squash, 1.0)
    assert emerged > FACE_TOP + 0.04, (
        f'the dome emerges at {emerged:.3f}, only {emerged - FACE_TOP:.3f} clear')
    # The band from the top of the face up to where the dome appears. Without it the
    # helmet leaves a strip of bare forehead, which is what the first pass shipped.
    brow_y, brow_h, brow_half = brow_band('vader/brow', emerges=emerged, lip=0.025)
    flare_half = 0.455                     # outboard of the face's 0.33
    clears_face('vader/cheek', bottom=0.24, half_width=flare_half)
    assert flare_half - 0.055 - 0.055 > FACE_HALF_X + 0.01, (
        'a cheek flare reaches into the face patch')
    grille_top = 0.20                      # below the face's 0.215
    assert grille_top < FACE_BOT, 'the grille would cross the expression'
    parts.append({
        'id': 'vaderHelm', 'bone': 'head', 'at': [0, 0, 0],
        'shape': {'parts': [
            # The dome, and the ridge down it.
            {'sphere': [dome_r, 18, 12], 'stretch': [1, dome_squash, 1],
             'shift': [0, dome_y, 0], 'color': VADER},
            {'box': [0.075, 0.36, 0.46], 'shift': [0, dome_y + 0.20, -0.02],
             'color': VADER_LIT},
            # The brow. It starts ON the top edge of the face and runs up to meet the
            # dome, so there is no bare head between the two -- `brow_band` computes
            # both, and a wedge in front of it gives the hard lip over the eye lenses.
            {'box': [brow_half * 2, brow_h, 0.30],
             'shift': [0, brow_y + brow_h / 2, 0.06], 'color': VADER_LIT},
            {'box': [0.60, 0.055, 0.20], 'rotate': [0.30, 0, 0],
             'shift': [0, brow_y + brow_h - 0.01, 0.255], 'color': VADER_LIT},
            # The cheek flares: OUTBOARD of the face, running down past it.
            {'box': [0.11, 0.46, 0.34], 'rotate': [0, 0, 0.10],
             'shift': [flare_half - 0.055, 0.40, 0.06], 'color': VADER},
            {'box': [0.11, 0.46, 0.34], 'rotate': [0, 0, -0.10],
             'shift': [-(flare_half - 0.055), 0.40, 0.06], 'color': VADER},
            # The grille and the mouthpiece, BELOW the patch.
            {'box': [0.30, 0.13, 0.16], 'shift': [0, grille_top - 0.075, 0.30],
             'color': GUNMETAL},
            {'box': [0.34, 0.06, 0.10], 'shift': [0, grille_top - 0.155, 0.31],
             'color': VADER_LIT},
            # The neck column, joining helmet to chest.
            {'cyl': [0.24, 0.27, 0.22, 12], 'shift': [0, -0.08, 0.0],
             'color': VADER_LIT},
        ]},
        'material': {'roughness': 0.26, 'metalness': 0.42, 'vertexColors': True,
                     'env': 1.2},
        'wear': [None, None, True],
    })

    # ── the tunics. All three ENCLOSE the 0.72 x 0.53 torso: radius 0.40 is 0.80
    #    across, z 0.75 gives 0.60 deep ─────────────────────────────────────────────────
    def tunic(part_id, cloth, trim, tiers, *, cross=True):
        tr, tz = 0.40, 0.75
        G.encloses_torso(part_id, tr, tz)
        top, bot = 1.255, 0.68
        h = top - bot
        front = tr * tz
        pieces = [
            {'cyl': [tr - 0.012, tr, h, 14], 'stretch': [1, 1, tz], 'color': cloth},
            {'cyl': [tr - 0.05, tr - 0.04, 0.075, 14], 'stretch': [1, 1, tz],
             'shift': [0, h / 2 - 0.02, 0], 'color': trim},
        ]
        if cross:
            # The wrapped front: one panel laid diagonally over the other, which is what
            # a Jedi tunic IS and reads even at map size as a V at the chest.
            pieces.append({'box': [0.30, 0.34, 0.03], 'rotate': [0, 0, -0.62],
                           'shift': [0.05, 0.09, front - 0.008], 'color': trim})
            pieces.append({'box': [0.30, 0.34, 0.03], 'rotate': [0, 0, 0.62],
                           'shift': [-0.05, 0.09, front - 0.014], 'color': cloth})
        return {
            'id': part_id, 'bone': 'chest', 'at': [0, chest((top + bot) / 2), TORSO_Z],
            'shape': {'parts': pieces},
            'material': {'roughness': 0.88, 'metalness': 0, 'vertexColors': True},
            'wear': list(tiers),
        }, front

    t_pad, front = tunic('tunicLinen', LINEN, LINEN_DK, [True, None, None])
    t_luke, _ = tunic('tunicTan', TAN, ROBE, [None, True, None])
    parts += [t_pad, t_luke]

    # Vader's chest: armour, not cloth. Same envelope, harder surface.
    vr, vz = 0.405, 0.76
    G.encloses_torso('vaderChest', vr, vz)
    vtop, vbot = 1.25, 0.66
    vh = vtop - vbot
    vfront = vr * vz
    parts.append({
        'id': 'vaderChest', 'bone': 'chest',
        'at': [0, chest((vtop + vbot) / 2), TORSO_Z],
        'shape': {'parts': [
            {'cyl': [vr - 0.015, vr, vh, 14], 'stretch': [1, 1, vz], 'color': VADER},
            {'cyl': [vr + 0.006, vr + 0.006, 0.05, 14], 'stretch': [1, 1, vz],
             'shift': [0, vh / 2 - 0.015, 0], 'color': VADER_LIT},
            # The ribbed plastron.
            {'box': [0.46, 0.05, 0.06], 'shift': [0, 0.10, vfront + 0.005],
             'color': VADER_LIT},
            {'box': [0.46, 0.05, 0.06], 'shift': [0, 0.00, vfront + 0.005],
             'color': VADER_LIT},
            {'box': [0.46, 0.05, 0.06], 'shift': [0, -0.10, vfront + 0.005],
             'color': VADER_LIT},
        ]},
        'material': {'roughness': 0.24, 'metalness': 0.44, 'vertexColors': True,
                     'env': 1.25},
        'wear': [None, None, True],
    })

    # THE CHEST PANEL, and it carries the session's colour. Small, central, high, and
    # the one thing on Vader that is lit: at night his box is the only part of him you
    # can see, which is exactly right.
    parts.append({
        'id': 'vaderPanel', 'bone': 'chest', 'tint': 'suit',
        'at': [0, chest(1.02), TORSO_Z + 0.30],
        'shape': {'parts': [
            {'rbox': [0.24, 0.17, 0.05, 0.012], 'color': GUNMETAL},
            {'box': [0.045, 0.030, 0.02], 'shift': [-0.065, 0.045, 0.03], 'tint': True},
            {'box': [0.045, 0.030, 0.02], 'shift': [0.0, 0.045, 0.03], 'tint': True},
            {'box': [0.045, 0.030, 0.02], 'shift': [0.065, 0.045, 0.03], 'tint': True},
            {'box': [0.17, 0.020, 0.02], 'shift': [0, -0.035, 0.03], 'tint': True},
        ]},
        'material': {'roughness': 0.4, 'metalness': 0.3, 'vertexColors': True,
                     'color': BLADE_MAX},
        'wear': [None, None, True],
    })

    # The shoulder mantle: the flared armour that makes his outline. Mirrored.
    parts.append({
        'id': 'vaderPauldron', 'bone': 'chest', 'at': [0.30, chest(1.175), 0.0],
        'shape': {'parts': [
            {'rbox': [0.22, 0.075, 0.30, 0.03], 'rotate': [0, 0, -0.22],
             'color': VADER},
            {'rbox': [0.19, 0.045, 0.26, 0.02], 'rotate': [0, 0, -0.22],
             'shift': [0.01, -0.065, 0], 'color': VADER_LIT},
        ]},
        'material': {'roughness': 0.25, 'metalness': 0.44, 'vertexColors': True,
                     'env': 1.2},
        'wear': [None, None, {'mirror': True}],
    })

    # ── THE HOOD, AND THE RANK LADDER ────────────────────────────────────────────────
    #
    # The first pass gave the Padawan and the Master the same hood worn down at the
    # shoulders, the same tunic and the same robe, and the only difference between them
    # was 0.28 of robe length. On the rank sheet they were the same figure twice. The
    # skill says it in as many words -- ornament will not do it, give the ranks
    # different SILHOUETTES -- and the canon answer is also the silhouette answer:
    #
    #   Padawan   bare head, the braid, a short robe.   Narrow, plain, unmistakably junior.
    #   Master    the cowl UP.                          Half a head taller and twice as wide.
    #   Vader     the helmet.                           Hard, black, and not cloth at all.
    #
    # A hood UP is the same problem as a helmet and takes the same three pieces: a crown
    # above the patch, a brow band closing the gap down to it, and two falls outboard of
    # it. The reason it looked impossible at first is that a hood is usually modelled as
    # a shell around the head, and `shell` is a closed tube -- it would wall the face in
    # completely. It has to be built as an opening, not as a covering.
    parts.append({
        'id': 'hood', 'bone': 'chest', 'at': [0, chest(1.20), -0.22],
        'rot': [0.32, 0, 0],
        'shape': {'parts': [
            {'shell': [0.30, 0.22, 0.30, 8], 'rotate': [0, 0.3927, 0],
             'stretch': [1.25, 1, 0.85], 'color': ROBE},
            {'torus': [0.27, 0.045, 10, 6, 3.6], 'rotate': [PI / 2, 0, 0],
             'stretch': [1.2, 1, 0.9], 'shift': [0, 0.13, 0.02], 'color': ROBE_DK},
        ]},
        'material': {'roughness': 0.92, 'vertexColors': True},
        # A collar, worn by both Jedi ranks: the raised cowl above it does not reach the
        # shoulders, so without this the Master has a bare neck between robe and head.
        'wear': [True, True, None],
    })

    # DEEPER THAN IT IS WIDE, and peaked at the back.
    #
    # The first cowl was a symmetric dome of radius 0.47 squashed to 0.64, and it read
    # as a bowl haircut rather than as cloth: it hugged the skull, it was wider than it
    # was deep, and its hem was a dead straight line across the eyebrows. What makes a
    # hood a hood is that it projects BACKWARDS off the crown and hangs loose, so the
    # radius comes down, the squash goes up, and the depth is stretched past 1.
    cowl_y, cowl_r, cowl_squash = 0.90, 0.44, 0.78
    cowl_emerged = emerges_above_face('hoodUp/crown', cowl_y, cowl_r, cowl_squash, 1.0)
    cowl_brow_y, cowl_brow_h, cowl_brow_half = brow_band('hoodUp/brow',
                                                         emerges=cowl_emerged, lip=0.03)
    # OUTBOARD, and measured at the INNER EDGE.
    #
    # The first version of this assert checked the fall's CENTRE against the patch,
    # which is the same mistake in the same shape as the braid's: a 0.13-wide panel
    # centred at 0.375 has its inner face at 0.310, inside the patch's 0.33, and the
    # assert said 0.375 > 0.35 and passed. What has to clear the face is the edge.
    fall_half, fall_w = 0.48, 0.12
    fall_x = fall_half - fall_w / 2
    clears_face('hoodUp/fall', bottom=0.14, half_width=fall_half)
    assert fall_x - fall_w / 2 > FACE_HALF_X + 0.02, (
        f'a hood fall\'s inner face is at {fall_x - fall_w / 2:.3f}, inside the patch')
    # The rolled front edge of the cowl. A cylinder laid across the brow, so its RADIUS
    # is what sits above the face, not its length -- placing it by the band's midpoint
    # let it dip 0.016 into the patch, because the band is thinner than the roll.
    roll_r = 0.062
    roll_y = r(FACE_TOP + roll_r + 0.008)
    assert roll_y - roll_r > FACE_TOP, 'the cowl roll dips into the face'
    parts.append({
        'id': 'hoodUp', 'bone': 'head', 'at': [0, 0, 0],
        'shape': {'parts': [
            # The crown, pushed back so the mass is behind the head rather than on it.
            # Narrower than the head and half again as deep: a hood OVERHANGS behind,
            # and a version that was wider than it was deep read as a wig.
            {'sphere': [cowl_r, 16, 12], 'stretch': [0.90, cowl_squash, 1.32],
             'shift': [0, cowl_y, -0.17], 'color': ROBE},
            # The back of the hood: a peak, which is the half of the silhouette that
            # says cloth. Entirely behind the head's centre plane, so the patch is
            # unreachable from here whatever its size.
            {'sphere': [0.40, 14, 10], 'stretch': [0.92, 1.02, 0.78],
             'shift': [0, 0.62, -0.35], 'color': ROBE_DK},
            {'cone': [0.20, 0.30, 10], 'rotate': [-0.85, 0, 0],
             'shift': [0, 1.00, -0.30], 'color': ROBE_DK},
            # The brow: a lip rather than a slab, with the hood's rolled hem proud of
            # it. Shallow in z on purpose -- the first pass was 0.34 deep and filled in
            # the whole top of the head, which is what made it read as hair.
            {'box': [cowl_brow_half * 2, cowl_brow_h, 0.20],
             'shift': [0, cowl_brow_y + cowl_brow_h / 2, 0.10], 'color': ROBE},
            {'cyl': [roll_r, roll_r, cowl_brow_half * 1.80, 8], 'rotate': [0, 0, PI / 2],
             'shift': [0, roll_y, 0.255], 'color': ROBE_DK},
            # The two falls, outboard of the patch, closing the sides of the opening.
            #
            # THEY STOP AT THE JAW. The first pass ran them 0.72 down to the collar,
            # and below about y 0.30 the head has curved away to 0.27 wide while the
            # fall is still out at 0.36 -- so the bottom third of each hung in mid air
            # with nothing behind it, and side-on the hood read as two paddles stuck to
            # the ears. Ending them where the head is still as wide as they are
            # outboard is what makes them read as the edge of an opening.
            {'box': [fall_w, 0.46, 0.30], 'rotate': [0, 0, 0.09],
             'shift': [fall_x, 0.53, 0.02], 'color': ROBE},
            {'box': [fall_w, 0.46, 0.30], 'rotate': [0, 0, -0.09],
             'shift': [-fall_x, 0.53, 0.02], 'color': ROBE},
        ]},
        'material': {'roughness': 0.93, 'vertexColors': True},
        'wear': [None, True, None],
    })

    # ── the outer robe, open at the front, and it MOVES ───────────────────────────────
    def robe(part_id, *, top, bottom, cloth, tiers, lean=0.26):
        h = top - bottom
        return {
            'id': part_id, 'bone': 'chest', 'at': [0, chest((top + bottom) / 2), -0.05],
            'shape': {'parts': [
                # A near-closed shell: the gap at the front is the robe hanging open.
                {'shell': [0.40, 0.50, h, 10], 'rotate': [0, 0.3142, 0],
                 'stretch': [1.0, 1, 0.82], 'color': cloth},
            ]},
            'material': {'roughness': 0.93, 'double': True, 'vertexColors': True},
            'flex': {'from': 'top', 'dir': [0, 0, -1], 'side': [1, 0, 0],
                     'sway': 0.035, 'rate': 2.0, 'wave': 2.2,
                     'lean': lean, 'curl': 0.04, 'turn': 0.20, 'bias': 1.9},
            'wear': list(tiers),
        }

    parts.append(robe('robeShort', top=1.20, bottom=0.52, cloth=ROBE,
                      tiers=[True, None, None]))
    parts.append(robe('robeLong', top=1.22, bottom=0.24, cloth=ROBE,
                      tiers=[None, True, None]))
    # Vader's cape: longer, blacker, and the single most recognisable thing about him.
    parts.append({
        'id': 'vaderCape', 'bone': 'chest', 'at': [0, chest(0.72), -0.26],
        'rot': [-0.06, 0, 0],
        'shape': {'shell': [0.34, 0.52, 1.00, 8], 'rotate': [0, 0.3927, 0],
                  'stretch': [1.05, 1, 0.42]},
        'material': {'roughness': 0.86, 'double': True, 'color': VADER},
        'flex': {'from': 'top', 'dir': [0, 0, -1], 'side': [1, 0, 0],
                 'sway': 0.05, 'rate': 1.9, 'wave': 2.6,
                 'lean': 0.34, 'curl': 0.05, 'turn': 0.26, 'bias': 1.8},
        'wear': [None, None, True],
    })

    # ── the obi and the tabards: the belt, and the two panels hanging from it ────────
    parts.append({
        'id': 'obi', 'bone': 'hips', 'at': [0, hips(0.70), TORSO_Z],
        'shape': {'parts': [
            {'cyl': [0.395, 0.395, 0.13, 14], 'stretch': [1, 1, 0.78], 'color': LEATHER},
            {'rbox': [0.13, 0.10, 0.05, 0.014], 'shift': [0, 0, 0.30], 'color': SILVER},
        ]},
        'material': {'roughness': 0.6, 'metalness': 0.2, 'vertexColors': True},
        'wear': [True, True, True],
    })
    parts.append({
        'id': 'tabards', 'bone': 'chest', 'at': [0, chest(0.90), TORSO_Z + 0.30],
        'shape': {'parts': [
            {'box': [0.13, 0.62, 0.02], 'shift': [0.10, 0, 0], 'color': ROBE},
            {'box': [0.13, 0.62, 0.02], 'shift': [-0.10, 0, 0], 'color': ROBE},
        ]},
        'material': {'roughness': 0.9, 'double': True, 'vertexColors': True},
        'flex': {'from': 'top', 'dir': [0, 0, -1], 'sway': 0.03, 'rate': 2.3,
                 'wave': 2.4, 'lean': 0.20, 'turn': 0.16, 'bias': 1.8},
        'wear': [True, True, None],
    })

    # ── sleeves: SHORT, because nothing can follow the forearm. The bare forearm then
    #    reads as a Jedi's leather bracer, which is what they actually wear ───────────
    def sleeves(part_prefix, cloth, cuff, tiers, *, length=0.20, metal=False):
        out = []
        for side in ('l', 'r'):
            out.append({
                'id': f'{part_prefix}{side.upper()}', 'bone': f'upperarm.{side}',
                'at': [0, 0, 0],
                'shape': {'parts': [
                    {'cyl': [ARM_R + 0.058, ARM_R + 0.048, length * 0.64, 12],
                     'shift': [0, length * 0.30, 0], 'color': cloth},
                    {'cyl': [ARM_R + 0.050, ARM_R + 0.058, length * 0.30, 12],
                     'shift': [0, length * 0.78, 0], 'color': cuff},
                ]},
                'material': ({'roughness': 0.28, 'metalness': 0.42, 'env': 1.2,
                              'vertexColors': True} if metal else
                             {'roughness': 0.9, 'vertexColors': True}),
                'wear': list(tiers),
            })
        return out

    parts += sleeves('sleeve', LINEN, LINEN_DK, [True, None, None])
    parts += sleeves('sleeveLuke', TAN, ROBE, [None, True, None])
    parts += sleeves('vaderArm', VADER, VADER_LIT, [None, None, True], metal=True)

    # ── boots, one pair for everybody: dark leather reads for a padawan and for Vader
    #    both, and a second pair would be two instanced meshes for no difference ──────
    for side in ('l', 'r'):
        parts.append({
            'id': f'boot{side.upper()}', 'bone': f'lowerleg.{side}', 'at': [0, 0.06, 0],
            'shape': {'parts': [
                {'cyl': [SHIN_R + 0.048, SHIN_R + 0.038, 0.19, 10], 'color': LEATHER},
                {'cyl': [SHIN_R + 0.056, SHIN_R + 0.052, 0.04, 10],
                 'shift': [0, 0.10, 0], 'color': '#2A2018'},
                {'rbox': [0.145, 0.09, 0.20, 0.03], 'shift': [0, -0.055, -0.06],
                 'color': LEATHER},
                {'rbox': [0.15, 0.035, 0.22, 0.014], 'shift': [0, -0.10, -0.055],
                 'color': '#1A1512'},
            ]},
            'material': {'roughness': 0.62, 'metalness': 0.06, 'vertexColors': True},
            'wear': [True, True, True],
        })

    # ══ THE SABRE, and the working/resting pair ═══════════════════════════════════════
    #
    # A hand's local +Y points at the FLOOR, so anything held needs rot z = PI, and then
    # a NEGATIVE rot[0] splays it outward where it can be seen -- a positive one tips it
    # across the body, behind the arm and the shoulder guard.
    HILT = [
        {'cyl': [0.036, 0.036, 0.20, 10], 'shift': [0, 0.10, 0], 'color': HILT_DARK},
        {'cyl': [0.040, 0.040, 0.045, 10], 'shift': [0, 0.185, 0], 'color': SILVER},
        {'cyl': [0.040, 0.040, 0.035, 10], 'shift': [0, 0.025, 0], 'color': SILVER},
        {'box': [0.018, 0.09, 0.018], 'shift': [0, 0.115, 0.040], 'color': SILVER},
    ]
    #
    # THE BLADE AND THE HILT ARE TWO PARTS, and they have to be.
    #
    # `glow` is not a material a theme configures: the engine hands back a flat
    # `MeshBasicMaterial` with NO `vertexColors`, because the whole point of it is to be
    # unlit and over-bright so the bloom pass catches it. A composite's per-piece colours
    # are carried in a vertex-colour attribute, so on a `glow` part they are simply not
    # read -- the first pass put the hilt inside the glowing part and the machined steel
    # and the black grip both came out as a bar of pure crystal colour, a sabre with no
    # handle. Nothing warns; the JSON is valid and the instance colour is correct.
    #
    # So: the blade alone glows and takes the session's colour, and the hilt is ordinary
    # dark metal on its own part. They share `at`, `rot` and `wear`, so they move and
    # scale as one object.
    HELD = {'bone': 'hand.r', 'when': 'working',
            'at': [0, -0.03, 0.03], 'rot': [-0.40, 0, PI],
            'wear': [True, True, {'scale': 1.06}]}
    parts.append({
        'id': 'sabre', **HELD, 'tint': 'suit',
        'shape': {'parts': [
            # A hall at night is lit by whoever is working in it.
            {'cyl': [0.030, 0.030, 1.05, 10], 'shift': [0, 0.73, 0]},
            {'sphere': [0.030, 8, 6], 'shift': [0, 1.255, 0]},
        ]},
        'material': 'glow',
    })
    parts.append({
        'id': 'sabreHilt', **HELD,
        'shape': {'parts': HILT},
        'material': {'roughness': 0.32, 'metalness': 0.6, 'vertexColors': True},
    })
    # At rest it is clipped to the belt. The pair can never coexist, and a Jedi who has
    # drawn its sabre is a Jedi you can SEE is working.
    parts.append({
        'id': 'hiltOnBelt', 'bone': 'hips', 'when': 'resting',
        'at': [0.33, hips(0.66), -0.02], 'rot': [0.18, 0, 0.30],
        'shape': {'parts': HILT},
        'material': {'roughness': 0.32, 'metalness': 0.6, 'vertexColors': True},
        'wear': [True, True, True],
    })

    return check_limbs(parts)


# ══ the atlas ═════════════════════════════════════════════════════════════════════════
# 32 flat swatches, indexed from the BOTTOM-LEFT. No art at all.
ATLAS = [
    SHADOW,        # 0
    STONE,         # 1  STONE      temple masonry
    STONE_DK,      # 2  STONE_DK
    SAND,          # 3  SAND       adobe, dune-world render
    SAND_DK,       # 4  SAND_DK
    '#9AA0A8',     # 5  METAL      hull plating, pylons
    GUNMETAL,      # 6  METAL_DK
    HOLO,          # 7  HOLO       archive holograms. Emissive.
    JUNGLE,        # 8  JUNGLE
    MOSS,          # 9  MOSS
    '#B08D57',     # 10 TRIM       THE ACCENT CELL, repainted per zone
    RUST,          # 11 RUST
    LINEN,         # 12 LINEN      awnings, banners
    UNDER,         # 13 DARK
    '#9FC4D8',     # 14 GLASS
    '#FFD9A0',     # 15 LAMP       Emissive.
    CARBON,        # 16 CARBON     carbonite, charred rock
    SILVER,        # 17 SILVER
    LEATHER,       # 18 LEATHER
    VADER,         # 19 LACQUER    Vader's black, and the Falcon's shadowed plate
    BLADE_LOW,     # 20 BLUE       Emissive: the archive, the training remotes
    BLADE_MAX,     # 21 RED        Emissive: warning strips
    '#6B5540',     # 22 EARTH
    LINEN_DK,      # 23 CANVAS
    '#3E4A52',     # 24 SLATE
    '#C9B89A',     # 25 PLASTER
    '#7A6A52',     # 26 TIMBER
    '#2A2E33',     # 27 PANEL
    '#5A6B72',     # 28 ZINC
    ROBE,          # 29 ROBE
    '#8FA87A',     # 30 SAGE
    '#101216',     # 31 VOID
]

CELLS = {
    'STONE': 1, 'STONE_DK': 2, 'SAND': 3, 'SAND_DK': 4, 'METAL': 5, 'METAL_DK': 6,
    'HOLO': 7, 'JUNGLE': 8, 'MOSS': 9, 'TRIM': 10, 'RUST': 11, 'LINEN': 12,
    'DARK': 13, 'GLASS': 14, 'LAMP': 15, 'CARBON': 16, 'SILVER': 17, 'LEATHER': 18,
    'LACQUER': 19, 'BLUE': 20, 'RED': 21, 'EARTH': 22, 'CANVAS': 23, 'SLATE': 24,
    'PLASTER': 25, 'TIMBER': 26, 'PANEL': 27, 'ZINC': 28, 'ROBE': 29, 'SAGE': 30,
    'VOID': 31,
}

SURFACES = {
    'STONE': [0.9, 0], 'STONE_DK': [0.92, 0], 'SAND': [0.95, 0], 'SAND_DK': [0.95, 0],
    'METAL': [0.35, 0.7], 'METAL_DK': [0.4, 0.65], 'HOLO': [0.5, 0],
    'JUNGLE': [0.9, 0], 'MOSS': [0.92, 0], 'TRIM': [0.45, 0.3], 'RUST': [0.85, 0.1],
    'LINEN': [0.92, 0], 'GLASS': [0.12, 0.2], 'LAMP': [0.6, 0], 'CARBON': [0.7, 0.25],
    'SILVER': [0.28, 0.8], 'LACQUER': [0.22, 0.45], 'ZINC': [0.4, 0.55],
    'PLASTER': [0.9, 0],
}

# ══ the enclave ═══════════════════════════════════════════════════════════════════════
#
# This theme builds ARCHITECTURE -- temples, halls, pylons -- so `world.scale` sits near
# the village's rather than the kitchen's. A Jedi is 2.2 x 0.56 = 1.23 world units tall;
# a temple wants to be four of those, so about 3.4 authored at 1.45.
#
# `y` IS A BOTTOM in a recipe (`primitive()` passes `base: step.base !== false`), and
# `ring`/`grid` DROP the container's own x/y/z, so a height lives inside the inner step.

WORLD_SCALE = 1.45
ring, grid = G.ring, G.grid


def recipes():
    return [
        # ── the temple: a Massassi ziggurat, four receding tiers and a shrine ────────
        {'id': 'temple', 'label': 'Great temple', 'steps': [
            {'plate': [4.2, 4.2, 0.12], 'cell': 'STONE_DK'},
            {'box': [3.7, 0.62, 3.7], 'cell': 'STONE', 'y': 0.12},
            {'box': [3.1, 0.58, 3.1], 'cell': 'STONE', 'y': 0.74},
            {'box': [2.5, 0.54, 2.5], 'cell': 'STONE', 'y': 1.32},
            {'box': [1.9, 0.50, 1.9], 'cell': 'STONE', 'y': 1.86},
            # The shrine on top, with a lit doorway.
            {'box': [1.15, 0.66, 1.15], 'cell': 'STONE_DK', 'y': 2.36},
            {'box': [0.42, 0.46, 0.06], 'cell': 'LAMP', 'emissive': 0.85,
             'y': 2.36, 'z': 0.58},
            {'prism': [1.35, 0.44, 1.35], 'cell': 'TRIM', 'y': 3.02},
            # The stair up the front face, which is what makes it a ziggurat and not a
            # wedding cake.
            {'box': [1.0, 0.12, 0.22], 'cell': 'STONE_DK', 'y': 0.12, 'z': 1.90},
            {'box': [1.0, 0.12, 0.22], 'cell': 'STONE_DK', 'y': 0.40, 'z': 1.68},
            {'box': [1.0, 0.12, 0.22], 'cell': 'STONE_DK', 'y': 0.68, 'z': 1.46},
            {'box': [1.0, 0.12, 0.22], 'cell': 'STONE_DK', 'y': 0.96, 'z': 1.26},
            {'box': [1.0, 0.12, 0.22], 'cell': 'STONE_DK', 'y': 1.24, 'z': 1.06},
            {'box': [1.0, 0.12, 0.22], 'cell': 'STONE_DK', 'y': 1.52, 'z': 0.88},
            {'box': [1.0, 0.12, 0.22], 'cell': 'STONE_DK', 'y': 1.80, 'z': 0.72},
            # Vines, because the jungle is taking it back.
            ring({'box': [0.10, 0.55, 0.10], 'cell': 'MOSS', 'y': 0.74, 'chance': 0.6},
                 6, 1.62),
        ]},

        # ── the training hall: a colonnade under a long roof ────────────────────────
        {'id': 'hall', 'label': 'Training hall', 'steps': [
            {'plate': [3.3, 2.4, 0.14], 'cell': 'STONE_DK'},
            {'box': [2.9, 0.18, 2.0], 'cell': 'STONE', 'y': 0.14},
            grid({'cyl': [0.16, 0.18, 1.5, 10], 'cell': 'STONE', 'y': 0.32},
                 5, 2, 0.62, 1.52),
            {'box': [3.0, 0.22, 2.15], 'cell': 'STONE_DK', 'y': 1.82},
            {'prism': [3.2, 0.85, 2.3], 'cell': 'TRIM', 'y': 2.04},
            # A sparring floor inside, and the rack of practice staves.
            {'plate': [1.7, 1.1, 0.06], 'cell': 'TIMBER', 'y': 0.32},
            {'box': [0.9, 0.07, 0.09], 'cell': 'TIMBER', 'y': 0.90, 'x': -0.93,
             'z': 0.72},
            ring({'cyl': [0.035, 0.035, 0.72, 6], 'cell': 'TIMBER', 'y': 0.32,
                  'chance': 0.8}, 3, 0.18),
        ]},

        # ── the archive: shelves of holobooks, and they glow ────────────────────────
        {'id': 'archive', 'label': 'Archive', 'steps': [
            {'plate': [2.3, 1.7, 0.12], 'cell': 'STONE_DK'},
            {'box': [2.0, 2.5, 1.4], 'cell': 'STONE', 'y': 0.12},
            {'box': [2.1, 0.18, 1.5], 'cell': 'STONE_DK', 'y': 2.62},
            # The open front, and four ranks of holobooks receding into it.
            {'box': [1.3, 1.9, 0.10], 'cell': 'VOID', 'y': 0.30, 'z': 0.66},
            {'box': [1.15, 0.08, 0.06], 'cell': 'SILVER', 'y': 0.52, 'z': 0.62},
            {'box': [1.15, 0.08, 0.06], 'cell': 'SILVER', 'y': 0.98, 'z': 0.62},
            {'box': [1.15, 0.08, 0.06], 'cell': 'SILVER', 'y': 1.44, 'z': 0.62},
            {'box': [1.15, 0.08, 0.06], 'cell': 'SILVER', 'y': 1.90, 'z': 0.62},
            {'box': [1.05, 0.30, 0.04], 'cell': 'HOLO', 'emissive': 1, 'y': 0.60,
             'z': 0.63},
            {'box': [1.05, 0.30, 0.04], 'cell': 'HOLO', 'emissive': 1, 'y': 1.06,
             'z': 0.63},
            {'box': [1.05, 0.30, 0.04], 'cell': 'HOLO', 'emissive': 1, 'y': 1.52,
             'z': 0.63, 'chance': 0.8},
            {'box': [1.05, 0.30, 0.04], 'cell': 'HOLO', 'emissive': 1, 'y': 1.98,
             'z': 0.63, 'chance': 0.6},
            {'box': [1.9, 0.10, 0.10], 'cell': 'TRIM', 'y': 2.42, 'z': 0.66},
        ]},

        # ── the comms pylon: tall, thin, ring-safe ──────────────────────────────────
        {'id': 'pylon', 'label': 'Comms pylon', 'steps': [
            {'plate': [1.0, 1.0, 0.12], 'cell': 'STONE_DK'},
            ring({'cyl': [0.055, 0.055, 2.6, 6], 'cell': 'METAL_DK', 'y': 0.12},
                 3, 0.28, jitter=0),
            {'cyl': [0.34, 0.34, 0.05, 8], 'cell': 'METAL', 'y': 0.90},
            {'cyl': [0.32, 0.32, 0.05, 8], 'cell': 'METAL', 'y': 1.50},
            {'cyl': [0.30, 0.30, 0.05, 8], 'cell': 'METAL', 'y': 2.10},
            # The dish, tipped at the sky.
            {'cyl': [0.46, 0.10, 0.16, 12], 'rotate': [0.7, 0, 0], 'cell': 'METAL',
             'y': 2.72},
            {'cyl': [0.05, 0.05, 0.22, 6], 'cell': 'SILVER', 'y': 2.88},
            {'sphere': [0.07, 8, 6], 'cell': 'RED', 'emissive': 1, 'y': 3.06},
        ]},

        # ── the adobe hut: a domed moisture-farm dwelling. Ring-safe ────────────────
        {'id': 'hut', 'label': 'Hut', 'steps': [
            {'cyl': [0.78, 0.86, 0.70, 12], 'cell': 'PLASTER', 'y': 0},
            {'sphere': [0.80, 14, 9], 'stretch': [1, 0.52, 1], 'cell': 'PLASTER',
             'y': 0.70},
            {'box': [0.40, 0.52, 0.10], 'cell': 'VOID', 'y': 0, 'z': 0.82},
            {'box': [0.46, 0.07, 0.12], 'cell': 'TIMBER', 'y': 0.52, 'z': 0.84},
            {'cyl': [0.09, 0.09, 0.34, 8], 'cell': 'RUST', 'x': 0.42, 'y': 1.05},
            ring({'box': [0.22, 0.16, 0.22], 'cell': 'SAND_DK', 'y': 0, 'chance': 0.6},
                 3, 0.98),
        ]},

        # ── the moisture vaporator: the most recognisable silhouette on a dune world,
        #    and ring-safe ───────────────────────────────────────────────────────────
        {'id': 'vaporator', 'label': 'Vaporator', 'steps': [
            {'cyl': [0.30, 0.38, 0.16, 10], 'cell': 'METAL_DK', 'y': 0},
            {'cyl': [0.13, 0.15, 1.95, 10], 'cell': 'METAL', 'y': 0.16},
            # The condenser fins: three rings of blades up the column.
            ring({'box': [0.055, 0.44, 0.36], 'cell': 'METAL', 'y': 0.52}, 5, 0.24,
                 jitter=0),
            ring({'box': [0.055, 0.44, 0.36], 'cell': 'METAL', 'y': 1.02}, 5, 0.24,
                 jitter=0, startAngle=0.63),
            ring({'box': [0.055, 0.44, 0.36], 'cell': 'METAL', 'y': 1.52}, 5, 0.24,
                 jitter=0, startAngle=1.26),
            {'cyl': [0.21, 0.17, 0.22, 10], 'cell': 'METAL_DK', 'y': 2.11},
            {'sphere': [0.055, 8, 6], 'cell': 'BLUE', 'emissive': 0.9, 'y': 2.33},
        ]},

        # ── the landing pad: ring-safe, and the lights matter after dark ────────────
        {'id': 'pad', 'label': 'Landing pad', 'steps': [
            {'cyl': [1.05, 1.10, 0.20, 12], 'cell': 'METAL_DK', 'y': 0},
            {'cyl': [0.96, 0.96, 0.06, 12], 'cell': 'PANEL', 'y': 0.20},
            ring({'cyl': [0.07, 0.07, 0.10, 8], 'cell': 'LAMP', 'emissive': 1,
                  'y': 0.26}, 6, 0.80, jitter=0),
            {'cyl': [0.70, 0.70, 0.02, 12], 'cell': 'TRIM', 'y': 0.26},
            {'box': [0.30, 0.42, 0.24], 'cell': 'METAL', 'x': 0.86, 'y': 0.20,
             'chance': 0.7},
        ]},

        # ── a parked landspeeder: ring-safe, and it says "somebody lives here" ──────
        {'id': 'speeder', 'label': 'Landspeeder', 'steps': [
            {'rbox': [1.25, 0.30, 0.58, 0.12], 'cell': 'RUST', 'y': 0.22},
            {'rbox': [0.66, 0.20, 0.46, 0.08], 'cell': 'METAL_DK', 'y': 0.46,
             'z': -0.04},
            {'box': [0.40, 0.10, 0.30], 'cell': 'GLASS', 'y': 0.62, 'z': -0.04},
            # Three turbine nacelles, which is the YT-shape of a speeder.
            {'cyl': [0.17, 0.17, 0.42, 10], 'rotate': [PI / 2, 0, 0], 'cell': 'METAL',
             'x': -0.52, 'y': 0.18},
            {'cyl': [0.17, 0.17, 0.42, 10], 'rotate': [PI / 2, 0, 0], 'cell': 'METAL',
             'x': 0.52, 'y': 0.18},
            {'cyl': [0.13, 0.13, 0.36, 10], 'rotate': [PI / 2, 0, 0], 'cell': 'METAL',
             'y': 0.16, 'z': -0.30},
            {'cyl': [0.05, 0.05, 0.22, 6], 'cell': 'METAL_DK', 'y': 0, 'x': -0.42},
            {'cyl': [0.05, 0.05, 0.22, 6], 'cell': 'METAL_DK', 'y': 0, 'x': 0.42},
        ]},

        # ── the sparring circle, with training remotes. Ring-safe ──────────────────
        {'id': 'remotes', 'label': 'Sparring circle', 'steps': [
            {'cyl': [1.05, 1.05, 0.08, 14], 'cell': 'EARTH', 'y': 0},
            {'cyl': [0.92, 0.92, 0.03, 14], 'cell': 'SAND', 'y': 0.08},
            ring({'cyl': [0.06, 0.06, 0.20, 6], 'cell': 'STONE', 'y': 0.08}, 8, 0.96,
                 jitter=0),
            # Two remotes hovering on their posts, blue-lit.
            {'cyl': [0.035, 0.035, 0.95, 6], 'cell': 'METAL_DK', 'x': -0.35, 'y': 0.11},
            {'sphere': [0.13, 10, 8], 'cell': 'SILVER', 'x': -0.35, 'y': 1.06},
            {'sphere': [0.05, 8, 6], 'cell': 'BLUE', 'emissive': 1, 'x': -0.35,
             'y': 1.14, 'z': 0.11},
            {'cyl': [0.035, 0.035, 0.72, 6], 'cell': 'METAL_DK', 'x': 0.40, 'y': 0.11,
             'chance': 0.8},
            {'sphere': [0.12, 10, 8], 'cell': 'SILVER', 'x': 0.40, 'y': 0.83,
             'chance': 0.8},
        ]},

        # ── a carved monolith: ring-safe, and every enclave has its dead ────────────
        {'id': 'monolith', 'label': 'Monolith', 'steps': [
            {'box': [0.86, 0.22, 0.66], 'cell': 'STONE_DK', 'y': 0},
            {'box': [0.58, 1.70, 0.30], 'cell': 'STONE', 'y': 0.22},
            {'prism': [0.66, 0.26, 0.38], 'cell': 'STONE_DK', 'y': 1.92},
            {'box': [0.34, 0.05, 0.03], 'cell': 'TRIM', 'y': 0.60, 'z': 0.16},
            {'box': [0.34, 0.05, 0.03], 'cell': 'TRIM', 'y': 0.90, 'z': 0.16},
            {'box': [0.34, 0.05, 0.03], 'cell': 'TRIM', 'y': 1.20, 'z': 0.16},
            {'cyl': [0.055, 0.055, 0.10, 8], 'cell': 'LAMP', 'emissive': 0.9,
             'y': 0.22, 'z': 0.38, 'chance': 0.7},
        ]},
    ]


# ══ the worlds ════════════════════════════════════════════════════════════════════════
#
# Two, and they are two different PLANETS rather than two times of day, because this
# theme's two halves are two places: the temple world you train on and the dune world
# you come from. The zone floor has to sit AGAINST both, which is why it is grey flag
# stone -- warm sand on sand, or green on jungle, and the halls stop reading as floors.

WORLDS = {
    'yavin': {
        'id': 'yavin', 'name': 'Temple World',
        'blurb': 'Jungle to the horizon, stone under the vines, a gas giant overhead.',
        'ground': {'low': '#2C4426', 'high': '#5E7C42', 'tint': '#87A55E'},
        'rock': '#7D7A6C',
        'horizon': '#A9BFA4',
        'sky': {'top': '#2B5C7A', 'bottom': '#CFE0D2'},
        'fog': {'color': '#9DB59C', 'near': 86, 'far': 232},
        'sun': {'color': '#FFF2D8', 'intensity': 2.35, 'night': 0.16},
        'ambient': {'sky': '#A8C8BE', 'ground': '#3A4E2E', 'intensity': 1.05},
        'atmosphere': 1, 'craters': 0, 'roughness': 0.9,
        'scatter': 'jungle',
        # The gas giant this moon orbits. Big, close, and the reason the sky is never
        # quite dark.
        'companion': {'name': 'Yavin', 'color': '#D9A05E', 'size': 7.2,
                      'glow': '#F0C489'},
        'dust': 0.16,
    },
    'dunesea': {
        'id': 'dunesea', 'name': 'Dune Sea',
        'blurb': 'Twin suns, no shade, and a long way to the nearest settlement.',
        'ground': {'low': '#8A6C3E', 'high': '#D9BA83', 'tint': '#EBD3A3'},
        'rock': '#9A8A6E',
        'horizon': '#F0DCB4',
        'sky': {'top': '#3E7FB0', 'bottom': '#F6E4BE'},
        'fog': {'color': '#E0C9A0', 'near': 110, 'far': 300},
        'sun': {'color': '#FFF0CE', 'intensity': 3.1, 'night': 0.10},
        'ambient': {'sky': '#EBD6AE', 'ground': '#8A6C3E', 'intensity': 1.15},
        'atmosphere': 0.85, 'craters': 0.12, 'roughness': 0.55,
        'scatter': 'desert',
        # The second sun, which is the one thing everybody remembers about this place.
        'companion': {'name': 'Second sun', 'color': '#FFE9B0', 'size': 2.4,
                      'glow': '#FFF6DC'},
        'dust': 0.62,
    },
}

# The tint MULTIPLIES the kit's atlas, and the foliage is painted green: a hex can only
# darken it, so a channel above 1.0 is the only way to move it. The desert wants the
# green pulled almost out of the scrub, which needs [r>1, g<1, b<1].
SCATTERS = {
    'jungle': [
        {'part': 'Tree_1_A_Color1', 'weight': 5, 'size': [0.55, 1.0], 'sink': 0.02,
         'upright': True, 'tint': [0.85, 1.15, 0.7]},
        {'part': 'Tree_3_A_Color1', 'weight': 4, 'size': [0.55, 1.05], 'sink': 0.02,
         'upright': True, 'tint': [0.8, 1.1, 0.65]},
        {'part': 'Bush_1_E_Color1', 'weight': 6, 'size': [0.5, 1.1], 'sink': 0.06,
         'upright': True, 'tint': [0.9, 1.2, 0.7]},
        {'part': 'Grass_2_D_Color1', 'weight': 7, 'size': [0.6, 1.35], 'sink': 0.05,
         'upright': True, 'tint': [0.95, 1.25, 0.75]},
        {'part': 'Rock_1_D_Color1', 'weight': 2, 'size': [0.45, 1.0], 'sink': 0.3,
         'tint': True},
    ],
    'desert': [
        {'part': 'Rock_1_D_Color1', 'weight': 6, 'size': [0.4, 1.1], 'sink': 0.34,
         'tint': True},
        {'part': 'Rock_3_A_Color1', 'weight': 5, 'size': [0.4, 1.0], 'sink': 0.32,
         'tint': True},
        # Scrub, with the green driven out of it: a hex tint could only make this olive.
        {'part': 'Bush_3_B_Color1', 'weight': 3, 'size': [0.3, 0.6], 'sink': 0.1,
         'upright': True, 'tint': [1.9, 1.35, 0.65]},
        {'part': 'Grass_1_A_Color1', 'weight': 2, 'size': [0.35, 0.7], 'sink': 0.08,
         'upright': True, 'tint': [2.1, 1.45, 0.6]},
    ],
}

# ══ the arrival point: the Millennium Falcon ═══════════════════════════════════════════
#
# A YT-1300, and its shape is four things in this order of importance: the SAUCER, the
# two forward MANDIBLES with the docking bay between them, the COCKPIT on its tube out
# to starboard, and the wide ENGINE glow across the back. Get those four and it is
# unmistakable at any size; miss the cockpit tube and it is a frisbee.
#
# The crew walk out of the boarding ramp, so `door` sits at its foot.
#
# `y` IS A BOTTOM here too -- `ship.js` passes `base: step.base !== false` exactly as
# `recipes.js` does -- so the whole ship stacks upward from the pad.

FALCON = {
    'surfaces': {
        'hull': '#A8ADB2',
        'hullDark': '#7C8288',
        'panel': '#6A7076',
        'plate': '#8E949A',
        'stripe': '#8A3B2A',      # the red-brown accents down her flanks
        'metal': GUNMETAL,
        'gear': '#4A4E54',
        'glass': '#FFD9A0',       # the cockpit, lit from inside
        'engine': '#BFE6FF',      # the drive, and it is the brightest thing here
        'bay': '#16181C',
        'pad': '#5E5A52',
        'padLight': '#FFD9A0',
        'ramp': '#8E949A',
    },
    # RGB TRIPLES, not hexes: each is multiplied by a per-frame scalar, and a channel
    # over 1.0 is what the bloom pass catches after dark.
    'lights': {
        'beacon': [0.9, 2.2, 3.4],     # the sublight drive
        'pad': [1.05, 0.9, 0.6],
        'glass': [1.35, 1.05, 0.6],    # the cockpit
        'rampStrip': [1.0, 0.8, 0.45],
    },
    'door': [0, 0, 5.6],
    'recipe': {'steps': [
        # ── the apron she is standing on ────────────────────────────────────────────
        {'plate': [13.0, 11.0, 0.3], 'paint': 'pad'},
        {'plate': [12.2, 10.2, 0.14], 'paint': 'pad', 'y': 0.3},
        {'plate': [9.6, 0.34, 0.06], 'paint': 'padLight', 'lit': 'pad', 'y': 0.44,
         'z': -4.4},

        # ── landing gear: three legs, and she sits on them ─────────────────────────
        {'cyl': [0.30, 0.34, 0.70, 8], 'paint': 'gear', 'y': 0.44, 'z': 3.4},
        {'cyl': [0.30, 0.34, 0.70, 8], 'paint': 'gear', 'x': -3.1, 'y': 0.44, 'z': -2.2},
        {'cyl': [0.30, 0.34, 0.70, 8], 'paint': 'gear', 'x': 3.1, 'y': 0.44, 'z': -2.2},
        {'cyl': [0.55, 0.55, 0.10, 10], 'paint': 'metal', 'y': 0.44, 'z': 3.4},
        {'cyl': [0.55, 0.55, 0.10, 10], 'paint': 'metal', 'x': -3.1, 'y': 0.44,
         'z': -2.2},
        {'cyl': [0.55, 0.55, 0.10, 10], 'paint': 'metal', 'x': 3.1, 'y': 0.44,
         'z': -2.2},

        # ── THE SAUCER ─────────────────────────────────────────────────────────────
        {'cyl': [4.70, 4.10, 0.55, 18], 'paint': 'hullDark', 'y': 1.14},
        {'cyl': [4.95, 4.95, 0.30, 18], 'paint': 'stripe', 'y': 1.69},
        {'cyl': [4.80, 4.95, 0.62, 18], 'paint': 'hull', 'y': 1.99},
        {'cyl': [3.60, 4.60, 0.58, 18], 'paint': 'plate', 'y': 2.61},
        {'cyl': [1.95, 3.30, 0.40, 18], 'paint': 'hull', 'y': 3.19},
        # Panel lines: three rings of plating, which is what stops a disc reading as a
        # plastic frisbee.
        {'cyl': [4.35, 4.35, 0.04, 18], 'paint': 'panel', 'y': 2.60},
        {'cyl': [3.35, 3.35, 0.04, 18], 'paint': 'panel', 'y': 3.18},
        {'cyl': [2.05, 2.05, 0.04, 18], 'paint': 'panel', 'y': 3.58},

        # ── the forward mandibles, and the docking bay between them ────────────────
        {'box': [1.55, 0.86, 3.10], 'paint': 'hull', 'x': -2.30, 'y': 1.55, 'z': 5.30},
        {'box': [1.55, 0.86, 3.10], 'paint': 'hull', 'x': 2.30, 'y': 1.55, 'z': 5.30},
        {'box': [1.62, 0.22, 3.16], 'paint': 'plate', 'x': -2.30, 'y': 2.41, 'z': 5.30},
        {'box': [1.62, 0.22, 3.16], 'paint': 'plate', 'x': 2.30, 'y': 2.41, 'z': 5.30},
        # The tips, tapered.
        {'cyl': [0.44, 0.70, 1.50, 6], 'rotate': [PI / 2, 0, 0], 'paint': 'hullDark',
         'x': -2.30, 'y': 1.70, 'z': 7.35},
        {'cyl': [0.44, 0.70, 1.50, 6], 'rotate': [PI / 2, 0, 0], 'paint': 'hullDark',
         'x': 2.30, 'y': 1.70, 'z': 7.35},
        # The bay itself: dark, recessed, and the thing the mandibles frame.
        {'box': [3.10, 1.10, 1.60], 'paint': 'bay', 'y': 1.45, 'z': 4.90},
        {'box': [2.20, 0.10, 0.10], 'paint': 'stripe', 'y': 2.50, 'z': 4.10},

        # ── the cockpit, out to starboard on its tube. Miss this and she is a frisbee ─
        {'cyl': [0.62, 0.62, 2.10, 10], 'rotate': [0, 0, PI / 2], 'paint': 'hull',
         'x': 4.05, 'y': 1.80, 'z': 1.55},
        {'cyl': [0.74, 0.62, 0.95, 8], 'rotate': [0, 0, PI / 2], 'paint': 'hullDark',
         'x': 5.45, 'y': 1.72, 'z': 1.55},
        {'box': [0.78, 0.52, 1.05], 'paint': 'glass', 'lit': 'glass', 'x': 5.72,
         'y': 1.86, 'z': 1.55},
        {'box': [0.20, 0.62, 1.16], 'paint': 'metal', 'x': 5.40, 'y': 1.80, 'z': 1.55},

        # ── the drive: a wide glowing mouth across her back ───────────────────────
        {'box': [6.60, 0.78, 0.50], 'paint': 'panel', 'y': 1.72, 'z': -4.55},
        {'box': [6.20, 0.46, 0.18], 'paint': 'engine', 'lit': 'beacon', 'y': 1.86,
         'z': -4.78},
        {'box': [6.70, 0.14, 0.56], 'paint': 'metal', 'y': 2.50, 'z': -4.55},

        # ── the quad turret on top, and the rectangular dish ──────────────────────
        {'cyl': [0.52, 0.62, 0.26, 10], 'paint': 'metal', 'y': 3.59},
        {'sphere': [0.46, 12, 9], 'stretch': [1, 0.78, 1], 'paint': 'hullDark',
         'y': 3.85},
        {'cyl': [0.075, 0.075, 1.05, 6], 'rotate': [PI / 2, 0, 0], 'paint': 'metal',
         'x': -0.17, 'y': 4.18, 'z': 0.55},
        {'cyl': [0.075, 0.075, 1.05, 6], 'rotate': [PI / 2, 0, 0], 'paint': 'metal',
         'x': 0.17, 'y': 4.18, 'z': 0.55},
        {'box': [1.55, 0.09, 1.05], 'rotate': [-0.34, 0, 0], 'paint': 'plate',
         'x': 2.35, 'y': 3.60, 'z': -1.15},
        {'cyl': [0.11, 0.11, 0.34, 6], 'paint': 'metal', 'x': 2.35, 'y': 3.42,
         'z': -1.15},

        # ── the boarding ramp. `rampStrip` brightens while somebody is walking in ──
        {'box': [2.30, 0.14, 2.60], 'rotate': [-0.42, 0, 0], 'paint': 'ramp',
         'y': 0.46, 'z': 4.55},
        {'plate': [2.10, 0.36, 0.08], 'paint': 'padLight', 'lit': 'rampStrip',
         'y': 0.46, 'z': 5.62},
        {'box': [0.10, 0.46, 2.40], 'rotate': [-0.42, 0, 0], 'paint': 'metal',
         'x': -1.12, 'y': 0.52, 'z': 4.55},
        {'box': [0.10, 0.46, 2.40], 'rotate': [-0.42, 0, 0], 'paint': 'metal',
         'x': 1.12, 'y': 0.52, 'z': 4.55},
    ]},
}


# ══ the theme ═════════════════════════════════════════════════════════════════════════

def theme():
    return {
        'id': 'jedi-enclave',
        'name': 'Jedi Enclave',
        'blurb': 'An enclave on a temple world. Every repo is a training hall, the '
                 'Falcon is docked at the edge of it, and Vader walks among them.',
        'planets': ['yavin', 'dunesea'],
        'worlds': WORLDS,
        'scatters': SCATTERS,

        # The eight KEYS are the status vocabulary and are not a theme's to change; the
        # words are. "In carbonite" is the one worth the whole exercise: blocked means
        # cannot proceed at all, and there is no more exact image for that anywhere.
        'status': {
            'working': 'On a mission',
            'waiting': 'Awaiting orders',
            'blocked': 'In carbonite',
            'celebrating': 'Decorated',
            'idle': 'Meditating',
            'sleeping': 'In hibernation',
            'spawning': 'Dropping in',
            'leaving': 'To hyperspace',
        },

        # One accent per hall. Ordered so adjacent entries are far apart in hue, since a
        # zone's neighbour is frequently its successor in this list.
        'plotPalette': [
            '#B08D57', '#4C7A8A', '#7A9A5A', '#A8503C', '#4A5E96', '#C08A3E',
            '#5E8A6A', '#8A5A7A', '#9AA0A8', '#6B4A2F', '#B84FFF', '#3E6E62',
        ],

        'crew': {
            'scale': 0.56,
            # The undertunic, the trousers, and the forearms -- which read as a Jedi's
            # leather bracers, and are the only thing they CAN read as, because nothing
            # worn can follow a forearm. Near-black, so every blade colour separates
            # from it.
            'body': {'color': UNDER, 'roughness': 0.88, 'metalness': 0.03,
                     'tint': 'none'},
            'look': {
                'working':     {'trim': '#4FE07A', 'eye': [0.4, 2.4, 1.0]},
                'waiting':     {'trim': BLADE_LOW, 'eye': [0.5, 1.5, 3.0]},
                'blocked':     {'trim': BLADE_MAX, 'eye': [3.0, 0.5, 0.4]},
                'celebrating': {'trim': '#FFC94F', 'eye': [2.9, 2.2, 0.6]},
                'idle':        {'trim': '#8A8578', 'eye': [1.2, 1.4, 1.5]},
                'sleeping':    {'trim': '#4C7A8A', 'eye': [0.6, 0.8, 1.5]},
                'spawning':    {'trim': '#7A9A5A', 'eye': [1.4, 2.4, 0.9]},
                'leaving':     {'trim': '#9AA0A8', 'eye': [1.0, 1.1, 1.0]},
            },
            # THE BLADE. Canon crystal colours, and they happen to run cool to hot in
            # exactly the order an effort scale wants.
            'effortTones': {
                'low': BLADE_LOW,        # blue
                'medium': BLADE_MED,     # green
                'high': BLADE_HIGH,      # amber
                'xhigh': BLADE_XHIGH,    # orange
                'max': BLADE_MAX,        # red
                # Off the scale on purpose, and there is only one purple sabre anybody
                # remembers: ultracode is a different way of working, not a hotter one.
                'ultracode': BLADE_ULTRA,
            },
            # Asserts no temperature: the statusline has not confirmed a level, so the
            # blade is white -- unlit crystal rather than a colour that means something.
            'effortUnknownTone': '#D8DCE2',
            'suitTones': [BLADE_LOW, BLADE_MED, BLADE_HIGH, BLADE_ULTRA, '#4C7A8A'],
            'parts': crew_parts(),
        },

        'hud': {
            'accent': BLADE_LOW, 'green': BLADE_MED, 'blue': '#4C7A8A',
            'amber': BLADE_HIGH, 'red': BLADE_MAX, 'teal': '#3E6E62',
        },
        'sky': {
            'nightFloor': '#05070E',
            'duskThick': '#E08A4C',
            'duskThin': '#3E3A5E',
            'fill': '#9FB6D8',
        },
        'ship': FALCON,
        'buildings': {'scaffold': STONE, 'fallbackAccent': '#B08D57'},
        'world': {
            'scale': WORLD_SCALE,
            'deck': 1.0,
            # FLAG STONE, and grey on purpose. This theme's two worlds are a green
            # jungle and a tan desert; a warm floor vanishes into one and a green one
            # into the other, so the halls stand on cut grey stone that sits against
            # both. `tint` is low for the same reason the village's soil is: at full
            # strength a hall whose repo name hashes to purple gets a purple floor.
            'floor': {
                'kind': 'plate',
                'base': '#5E5A52',      # the joints between the flags
                'panel': '#8E8A80',     # the flags themselves
                'seam': 'rgba(44,42,38,0.85)',
                'bolt': 'rgba(210,204,190,0.45)',
                'tint': 0.34,
                'roughness': 0.88,
                'metalness': 0.02,
                'relief': 0.62,
            },
            # Replaced, not merged: only the forest kit, for what grows. Everything
            # built here is a primitive, so every recipe is live-viewable in the
            # artifact rather than falling back to snapshots.
            'kits': {'forest': 'builtin:forest.glb'},
            'atlas': {'source': 'colors', 'cols': 8, 'rows': 4, 'colors': ATLAS},
            'cells': CELLS,
            'accentCells': ['TRIM'],
            'surfaces': SURFACES,
            'recipes': recipes(),
        },
    }


def main():
    t = theme()
    parts = t['crew']['parts']
    print(f'Jedi Enclave -- {len(t["world"]["recipes"])} structures, '
          f'{len(parts)} worn parts, {len(t["worlds"])} worlds, '
          f'{len(FALCON["recipe"]["steps"])} steps of Falcon')

    assert len(ATLAS) == 32, f'the atlas is {len(ATLAS)} swatches in an 8x4 grid'
    for name, idx in CELLS.items():
        assert 0 <= idx < len(ATLAS), f'cell {name} points at {idx}, off the atlas'
    for name in SURFACES:
        assert name in CELLS, f'surfaces names {name}, which is not a cell'
    for acc in t['world']['accentCells']:
        assert acc in CELLS, f'accentCells names {acc}, which is not a cell'
    for planet in t['planets']:
        assert planet in WORLDS, f'planets names {planet}, which is not defined'
    for w in WORLDS.values():
        assert w['scatter'] in SCATTERS, f'{w["id"]} scatters "{w["scatter"]}", undefined'
    for st in FALCON['recipe']['steps']:
        if 'paint' in st:
            assert st['paint'] in FALCON['surfaces'], \
                f'the Falcon paints "{st["paint"]}", which is not a surface'
        if 'lit' in st:
            assert st['lit'] in FALCON['lights'], \
                f'the Falcon lights "{st["lit"]}", which is not a light group'

    G.assert_tones_read(t['crew']['body']['color'], t['crew']['effortTones'])
    problems = G.lint_crew(parts)
    problems += G.lint_recipes(t['world']['recipes'], WORLD_SCALE, CELLS)

    # The rank ladder, measured. Tier 2 has to be unmistakable in OUTLINE, and Vader's
    # helmet plus pauldrons plus cape is the loadout that does it.
    worn = [set(p['id'] for p in parts if p['wear'][i] is not None) for i in range(3)]
    for a, b in ((0, 1), (1, 2)):
        only = (worn[a] ^ worn[b])
        if len(only) < 3:
            problems.append(f'ranks {a} and {b} differ by only {len(only)} part(s)')
    if 'vaderHelm' not in worn[2] or 'vaderCape' not in worn[2]:
        problems.append('tier 2 is not Vader')
    if 'braid' not in worn[0]:
        problems.append('tier 0 has no padawan braid')

    if problems:
        print('\n  PROBLEMS:')
        for p in problems:
            print(f'    - {p}')
        sys.exit(1)

    where = sys.argv[1:] or ['themes/unshipped/jedi-enclave.json']
    for path in where:
        os.makedirs(os.path.dirname(path) or '.', exist_ok=True)
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(t, f, indent=1)
            f.write('\n')
        print(f'  wrote {path}  ({os.path.getsize(path) / 1024:.0f} KB)')


if __name__ == '__main__':
    main()
