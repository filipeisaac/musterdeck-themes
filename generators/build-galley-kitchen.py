# -*- coding: utf-8 -*-
"""
Build the Galley Kitchen Crew theme.

    "A brigade kitchen at service: whites, a warm pass, and every station on the line."

Galley Solutions is a restaurant management platform, and a `galley` is a ship's kitchen,
so the Crew's own vocabulary already maps onto a brigade with nothing forced:

    a repo    -> a STATION      the sauté station, garde manger, pastry
    a session -> a COOK working that station
    a thread  -> a TICKET on the rail
    archived  -> struck off the board

Every colour in here is Galley's own, read out of `jelly-frontend/tailwind.config.js`
rather than eyeballed off a screenshot. That file is the product's palette, so the theme
cannot drift from the brand without the brand moving first.

THE RIG, MEASURED (references/measurements.md; re-probe with /bones.html if assets move).

    head      y 1.228   axes ~ identity        chest     y 0.959   axes ~ identity
    hips      y 0.392   axes ~ identity        hand.l/r  local +Y points DOWN
    upperarm.l/r  local +Y down the arm, ~20 degrees off the arm's own line
    lowerleg.l/r  local +Y down the shin, the FRONT of the shin is local -Z

    torso     y 0.45 .. 1.24, about 0.72 wide and 0.53 deep, centred z +0.01
    arm       radius 0.10       thigh 0.105       shin 0.095
    the mannequin's head mesh is DROPPED: the body stops at y 1.244 and the kit's own
    head sphere (r 0.42 at head-local y 0.42, world 1.648) is the whole head

THE RANK LADDER, and it is carried by SILHOUETTE, not by ornament:

    0  Commis          a flat skull cap.       Nothing above the head but the head.
    1  Chef de partie  a toque.                Half a head taller.
    2  Executive chef  a TALL pleated toque.   Half a body taller again.

A brigade already ranks its cooks by hat height, which is why this works at forty pixels
where a difference in trim never would. Everything else -- the double breast, the
epaulettes, the knife roll, the bib apron's length -- is confirmation, not the signal.

WHERE THE PER-AGENT COLOUR LIVES. `crew.body.tint` is "none": whites over a body painted
in the effort colour is a spacesuit in an apron. The effort heat goes on the APRON (large,
high, moves) and the NECKERCHIEF (small, central), both of which are genuinely coloured in
a real kitchen, so the signal reads as costume rather than as a status light.
"""
import json
import math
import os
import sys

# ── Galley's brand, from jelly-frontend/tailwind.config.js ────────────────────────────
# Named exactly as the product names them, so a reader can grep either way.
WHITE          = '#F7EBDC'   # antiqueWhite  -- chef whites, the toque, the plates
WHITE_WARM     = '#EFE0CC'   # antiqueWhite, one stop down: shadow side of the whites
PRIMARY        = '#2F4F4F'   # brand.primary -- dark slate green. Aprons, the range.
GOLD           = '#936F39'   # brand.gold    -- buttons, fittings, the pass rail
MARLIN         = '#4C6F81'   # brand.marlin  -- cool steel
CORNFLOWER     = '#2E5AAC'   # brand.cornflower
PUMPKIN        = '#D68C45'   # brand.pumpkin -- the heat lamps, copper
MAHOGANY       = '#b95000'   # brand.mahogany / semantic.warning -- full flame
AURO           = '#617979'   # brand.auroMetalSaurus -- stainless
SPROUT         = '#D4DFC8'   # brand.sprout  -- produce, pale greens
DARK_SPROUT    = '#9AB47E'   # brand.dark-sprout -- herbs
BROCCOLI       = '#F3F6EF'   # brand.broccoli-water -- the palest surface
NUTMEG         = '#7F492F'   # brand.nutmeg  -- timber, boards
LIGHT_BLUE     = '#A4C3D1'   # brand.light-blue
TEXT_GREY      = '#4D4D4D'   # brand.text
ICON_STROKE    = '#1A1A18'   # brand.icon-stroke -- the darkest line
ACCENT_BLUE    = '#3B82F6'   # brand.accent
SUCCESS        = '#287D3C'   # semantic.success
ERROR          = '#DA1414'   # semantic.error
GREY_400       = '#858C94'
GREY_800       = '#394452'
GREY_900       = '#1F2937'

# ── the rig, measured ─────────────────────────────────────────────────────────────────
HEAD_BONE_Y = 1.228
CHEST_Y     = 0.959
HIPS_Y      = 0.392
HEAD_R      = 0.42
HEAD_UP     = 0.42          # head sphere centre, in the head bone's frame
TORSO_W     = 0.72
TORSO_D     = 0.53
TORSO_Z     = 0.01
TORSO_TOP   = 1.24
TORSO_BOT   = 0.45
ARM_R       = 0.10
SHIN_R      = 0.095

PI = round(math.pi, 7)

# The face patch, in the head bone's frame. NOTHING may cross this.
FACE_TOP    = 0.625
FACE_BOT    = 0.215
FACE_HALF_X = 0.33


def r(x):
    return round(x + 0.0, 4)


def chest(y):
    """A world height, in the chest bone's frame."""
    return r(y - CHEST_Y)


def hips(y):
    return r(y - HIPS_Y)


def head_local(y):
    return r(y - HEAD_BONE_Y)


def head_radius_at(y):
    """The head sphere's xz radius at head-local height `y`, or 0 outside it."""
    dy = abs(y - HEAD_UP)
    return math.sqrt(max(0.0, HEAD_R * HEAD_R - dy * dy))


def assert_clears_face(name, bottom_y, half_width_at_bottom):
    """
    A hat may dip below the top of the face ONLY while it is still inside the head.

    The samurai kit's first pass put a band at head-local 0.31 and turned a general's
    expression into a pair of eyes over a gold bar. The face is the only thing on the
    figure that says what a session is doing, so this is the one assertion worth making
    twice.
    """
    if bottom_y >= FACE_TOP:
        return
    inside = head_radius_at(bottom_y)
    assert half_width_at_bottom <= inside + 1e-6, (
        f'{name}: reaches down to head-local y={bottom_y:.3f}, which is inside the face '
        f'patch (top {FACE_TOP}), and is {half_width_at_bottom:.3f} wide there against a '
        f'head only {inside:.3f} wide -- it would cross the expression.'
    )


def _luminance(hex_colour):
    """WCAG relative luminance, for the contrast check below."""
    h = hex_colour.lstrip('#')
    ch = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    lin = [c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4 for c in ch]
    return 0.2126 * lin[0] + 0.7152 * lin[1] + 0.0722 * lin[2]


def assert_tones_read(body, tones, floor=3.0):
    """
    Every effort colour must separate from the BODY it is worn over.

    The apron is the large carrier of the effort heat and the body is what is behind it,
    so a tone close to the body's colour is a tone that does not exist: the first pass
    put a slate body (#39464A) behind marlin `low`, and a commis on low effort wore a
    blue-grey apron over blue-grey legs with nothing to see. It rendered, it validated,
    and the one garment that was supposed to report something reported nothing.

    Contrast rather than hue distance, because that is what survives being drawn forty
    pixels tall in a dusk lighting pass.
    """
    lb = _luminance(body)
    for name, tone in tones.items():
        ratio = (_luminance(tone) + 0.05) / (lb + 0.05)
        assert ratio >= floor, (
            f'effort "{name}" ({tone}) is {ratio:.2f}:1 against the body ({body}); '
            f'the apron carrying it would not separate from the legs behind it'
        )


def encloses_torso(name, radius, z_stretch):
    """Armour and jackets must ENCLOSE the body, not sit at it."""
    w = radius * 2
    d = radius * 2 * z_stretch
    assert w >= TORSO_W, f'{name}: {w:.3f} wide over a {TORSO_W} torso -- it is inside it'
    assert d >= TORSO_D, f'{name}: {d:.3f} deep over a {TORSO_D} torso -- it is inside it'


# ══ the crew kit ══════════════════════════════════════════════════════════════════════

def crew_parts():
    parts = []

    # ── the head itself ───────────────────────────────────────────────────────────────
    # Dark, because the expression is drawn over it as emissive and a pale head swallows
    # the glow. The mannequin's own head is dropped by the rig, so without this the crew
    # are headless.
    parts.append({
        'id': 'head', 'bone': 'head', 'at': [0, HEAD_UP, 0],
        'shape': {'sphere': [HEAD_R, 14, 10]},
        'material': {'roughness': 0.84, 'metalness': 0.02, 'color': '#3b322b'},
        'wear': [True, True, True],
    })

    # The expression. Engine shader, same geometry every theme uses: a patch a shade
    # proud of the head so it never z-fights with it.
    parts.append({
        'id': 'face', 'bone': 'head', 'material': 'face', 'tint': 'eye',
        'at': [0, HEAD_UP, 0], 'shadow': False,
        'shape': {'cap': [HEAD_R + 0.008, 1.78, 1.02, 16, 10]},
        'wear': [True, True, True],
    })

    # ── rank: the hat is the silhouette ───────────────────────────────────────────────
    #
    # A commis wears a skull cap, a chef de partie a toque, an executive chef a tall one.
    # Real brigade kit, and it happens to be the one difference that survives being drawn
    # forty pixels tall.

    # COMMIS: a shallow dome that emerges from the crown and NOWHERE ELSE.
    #
    # An ellipsoid on a sphere is the one hat shape where "does it cross the face" cannot
    # be answered by looking at its lowest point: the dome dips well below the face's top
    # edge, but it is INSIDE the head all the way down, so none of that is visible. So the
    # check samples the silhouette -- where the cap's radius overtakes the head's -- which
    # is the only height that matters.
    cap_y, cap_r, cap_squash, cap_wide = 0.70, 0.335, 0.55, 1.05

    def cap_radius_at(y):
        t = (y - cap_y) / (cap_r * cap_squash)
        return 0.0 if abs(t) >= 1 else cap_r * cap_wide * math.sqrt(1 - t * t)

    emerges = None
    for i in range(400):
        y = cap_y - cap_r * cap_squash + i * (2 * cap_r * cap_squash) / 399
        if cap_radius_at(y) > head_radius_at(y) + 1e-6:
            emerges = y
            break
    assert emerges is not None, 'the skullcap never emerges from the head: invisible'
    assert emerges > FACE_TOP, (
        f'the skullcap becomes visible at head-local y={emerges:.3f}, below the face top '
        f'({FACE_TOP}) -- it would cut across the expression'
    )
    parts.append({
        'id': 'skullcap', 'bone': 'head', 'at': [0, cap_y, 0],
        'shape': {'sphere': [cap_r, 14, 8],
                  'stretch': [cap_wide, cap_squash, cap_wide]},
        'material': {'roughness': 0.88, 'metalness': 0, 'vertexColors': True,
                     'color': WHITE},
        'wear': [True, None, None],
    })

    def toque(part_id, column_h, crown_r, tiers):
        """
        A toque: a band, a pleated column, a puffed crown.

        Authored from the band up, so the only number that changes between the two ranks
        is the column's height -- which is the whole point of the rank ladder. The band's
        bottom is the number the face assertion cares about.
        """
        band_h = 0.09
        band_bottom = 0.685                 # clear of the face top (0.625) by 0.06
        band_y = band_bottom + band_h / 2
        band_r = 0.305
        assert_clears_face(part_id, band_bottom, band_r)
        column_y = band_bottom + band_h + column_h / 2
        crown_y = band_bottom + band_h + column_h + crown_r * 0.42
        pieces = [
            # The band, sitting on the head.
            {'cyl': [band_r, band_r + 0.012, band_h, 16], 'shift': [0, band_y - 0, 0],
             'color': WHITE_WARM},
            # The pleated column. Twelve segments read as pleats at map distance and as
            # a cylinder up close, which is the right way round for this.
            {'cyl': [band_r + 0.014, band_r - 0.004, column_h, 12],
             'shift': [0, column_y, 0], 'color': WHITE},
            # The puff.
            {'sphere': [crown_r, 14, 9], 'stretch': [1, 0.62, 1],
             'shift': [0, crown_y, 0], 'color': WHITE},
        ]
        top = crown_y + crown_r * 0.62
        return {
            'id': part_id, 'bone': 'head', 'at': [0, 0, 0],
            'shape': {'parts': pieces},
            'material': {'roughness': 0.9, 'metalness': 0, 'vertexColors': True},
            'wear': tiers,
        }, top

    toque_mid, top_mid = toque('toque', 0.30, 0.33, [None, True, None])
    toque_tall, top_tall = toque('toqueTall', 0.62, 0.37, [None, None, True])
    # The ladder has to be a LADDER. A chef de partie stands clearly above a commis and an
    # executive clearly above both, measured at the top of the hat rather than asserted in
    # a comment.
    head_top = HEAD_UP + HEAD_R
    assert top_mid > head_top + 0.22, 'the toque does not read as taller than a bare head'
    assert top_tall > top_mid + 0.28, 'the two toques are not distinguishable in outline'
    parts.append(toque_mid)
    parts.append(toque_tall)

    # ── the neckerchief: small, central, and the effort colour ────────────────────────
    #
    # It has to sit OVER the collar, not at it. The first pass used a torus of outer
    # radius 0.235 on a jacket collar of 0.355 and the whole thing rendered inside the
    # coat -- the same mistake as a cuirass narrower than the torso it is worn on, one
    # layer further out. Sized against the collar it is worn over, and asserted.
    #
    # Squashed in z because a neck is not round in plan and a true torus reads as a life
    # ring.
    neck_ring, neck_tube = 0.315, 0.072
    collar_r = 0.40 - 0.045          # the jacket's collar band, below
    assert neck_ring + neck_tube > collar_r + 0.01, (
        f'the neckerchief is {neck_ring + neck_tube:.3f} over a {collar_r:.3f} collar: '
        f'it would be inside the jacket'
    )
    parts.append({
        'id': 'neckerchief', 'bone': 'chest', 'tint': 'suit',
        'at': [0, chest(1.232), TORSO_Z],
        'shape': {'parts': [
            {'torus': [neck_ring, neck_tube, 8, 10, 6.2832], 'rotate': [PI / 2, 0, 0],
             'stretch': [1, 1, 0.78], 'tint': True},
            # The knot, in the hollow of the throat.
            {'sphere': [0.075, 8, 6], 'shift': [0, -0.045, 0.235], 'tint': True},
            {'cone': [0.062, 0.15, 6], 'rotate': [0.3, 0, 0],
             'shift': [0, -0.15, 0.225], 'tint': True},
        ]},
        'material': {'roughness': 0.85, 'metalness': 0, 'vertexColors': True,
                     'color': WHITE},
        'wear': [None, True, True],
    })

    # ── the jacket ────────────────────────────────────────────────────────────────────
    # Sized to ENCLOSE a 0.72 x 0.53 torso. A cylinder radius 0.40 is 0.80 across; squash
    # z to 0.75 for 0.60 deep. Both clear the body, which is the whole lesson of the
    # first samurai pass.
    jacket_r, jacket_z = 0.40, 0.75
    encloses_torso('jacket', jacket_r, jacket_z)
    jacket_top, jacket_bot = 1.255, 0.70
    jacket_h = jacket_top - jacket_bot
    jacket_y = chest((jacket_top + jacket_bot) / 2)
    front_z = jacket_r * jacket_z                 # where the buttons have to sit
    parts.append({
        'id': 'jacket', 'bone': 'chest', 'at': [0, jacket_y, TORSO_Z],
        'shape': {'parts': [
            {'cyl': [jacket_r - 0.012, jacket_r, jacket_h, 14],
             'stretch': [1, 1, jacket_z], 'color': WHITE},
            # The double-breasted placket: a panel a shade proud and a shade darker, set
            # off-centre the way a real one laps over.
            {'rbox': [0.30, jacket_h - 0.06, 0.03, 0.012],
             'shift': [0.035, 0, front_z - 0.012], 'color': WHITE_WARM},
            # The collar band.
            {'cyl': [jacket_r - 0.055, jacket_r - 0.045, 0.075, 14],
             'stretch': [1, 1, jacket_z], 'shift': [0, jacket_h / 2 - 0.02, 0],
             'color': WHITE_WARM},
            # The hem, one stop darker so the jacket has a bottom edge at distance.
            {'cyl': [jacket_r, jacket_r + 0.008, 0.05, 14],
             'stretch': [1, 1, jacket_z], 'shift': [0, -jacket_h / 2 + 0.02, 0],
             'color': WHITE_WARM},
        ]},
        'material': {'roughness': 0.88, 'metalness': 0, 'vertexColors': True},
        'wear': [True, True, True],
    })

    # Buttons. Gold, and they take the session colour, so the one thing that follows the
    # session on the jacket is its FITTINGS -- mask furniture, never material.
    btn_z = front_z + 0.012
    single = [{'at': [0.035, 0.17 - i * 0.145, btn_z]} for i in range(3)]
    double = []
    for i in range(4):
        y = 0.21 - i * 0.135
        double.append({'at': [0.105, y, btn_z - 0.004]})
        double.append({'at': [-0.035, y, btn_z - 0.004]})
    parts.append({
        'id': 'buttons', 'bone': 'chest', 'tint': 'suit',
        'at': [0, chest((jacket_top + jacket_bot) / 2), TORSO_Z],
        'shape': {'parts': [
            {'sphere': [0.030, 8, 6], 'stretch': [1, 1, 0.6], 'tint': True},
        ]},
        'material': {'roughness': 0.42, 'metalness': 0.35, 'vertexColors': True,
                     'color': GOLD},
        # A commis has one row of three; the ranks above are double-breasted, which is
        # the actual difference between a cook's jacket and a chef's.
        'wear': [{'copies': single}, {'copies': double}, {'copies': double}],
    })

    # Epaulettes: rank tabs, executive only. Mirrored, so one entry makes the pair.
    parts.append({
        'id': 'epaulette', 'bone': 'chest', 'tint': 'suit',
        'at': [0.285, chest(1.175), 0.0],
        'shape': {'parts': [
            {'rbox': [0.15, 0.035, 0.115, 0.016], 'color': WHITE_WARM},
            {'box': [0.10, 0.012, 0.028], 'shift': [0, 0.024, 0.0], 'tint': True},
        ]},
        'material': {'roughness': 0.6, 'metalness': 0.3, 'vertexColors': True,
                     'color': GOLD},
        'wear': [None, None, {'mirror': True}],
    })

    # ── the apron: large, high, moving, and the loudest thing about the figure ────────
    #
    # This is where the effort heat lives. A chef's apron is genuinely coloured, so it
    # carries the signal without reading as a status light bolted to a costume -- and it
    # is the biggest flat area on the body, which is what "reads at map distance" means.
    def apron(part_id, height, tiers, bib):
        top = 1.12 if bib else 0.60
        centre = top - height / 2
        return {
            'id': part_id, 'bone': 'chest', 'tint': 'suit',
            'at': [0, chest(centre), TORSO_Z + 0.30],
            'shape': {'box': [0.52 if bib else 0.58, height, 0.018]},
            'material': {'roughness': 0.93, 'metalness': 0, 'double': True},
            # Pinned at the waist tie for a waist apron and at the neck loop for a bib, so
            # the hem is the part that swings either way.
            'flex': {'from': 'top', 'dir': [0, 0, -1], 'side': [1, 0, 0],
                     'sway': 0.03, 'rate': 2.0, 'wave': 2.2,
                     'lean': 0.22, 'curl': 0.03, 'turn': 0.16, 'bias': 1.9},
            'wear': tiers,
        }

    parts.append(apron('apronWaist', 0.44, [True, None, None], bib=False))
    # The executive's is longer -- a bistro apron to mid-shin. Scale rather than a third
    # part, because it is the same garment.
    parts.append(apron('apronBib', 0.80, [None, True, {'scale': 1.16}], bib=True))

    # The waist tie, which is what an apron actually hangs from. Linen, not tinted: two
    # tinted things at the waist would fight.
    parts.append({
        'id': 'apronTie', 'bone': 'hips', 'at': [0, hips(0.66), TORSO_Z],
        'shape': {'cyl': [0.385, 0.385, 0.055, 14], 'stretch': [1, 1, 0.76]},
        'material': {'roughness': 0.92, 'metalness': 0, 'color': WHITE_WARM},
        'wear': [True, True, True],
    })

    # ── the side towel: linen, not a signal ───────────────────────────────────────────
    # Deliberately NOT tinted. It is the third thing a cook always has, and leaving it
    # plain is what keeps the apron and the neckerchief legible as the two that mean
    # something. Over the LEFT shoulder: the character's left is +X.
    parts.append({
        'id': 'sideTowel', 'bone': 'chest', 'at': [0.245, chest(1.095), 0.0],
        'rot': [0, 0, -0.16],
        'shape': {'box': [0.155, 0.40, 0.016]},
        'material': {'roughness': 0.95, 'metalness': 0, 'double': True,
                     'color': BROCCOLI},
        'flex': {'from': 'top', 'dir': [0, 0, -1], 'side': [1, 0, 0],
                 'sway': 0.045, 'rate': 2.7, 'wave': 3.0,
                 'lean': 0.3, 'curl': 0.05, 'turn': 0.26, 'bias': 1.7},
        'wear': [None, True, True],
    })

    # The knife roll, on the right hip. Executive only: it is the thing you own after
    # years, and it loads the tier-2 silhouette on the opposite side to the towel.
    parts.append({
        'id': 'knifeRoll', 'bone': 'hips', 'at': [-0.34, hips(0.56), -0.05],
        'rot': [0, 0, 0.22],
        'shape': {'parts': [
            {'cyl': [0.075, 0.075, 0.30, 10], 'rotate': [0, 0, PI / 2],
             'color': NUTMEG},
            {'cyl': [0.078, 0.078, 0.035, 10], 'rotate': [0, 0, PI / 2],
             'shift': [0.07, 0, 0], 'color': ICON_STROKE},
            {'cyl': [0.078, 0.078, 0.035, 10], 'rotate': [0, 0, PI / 2],
             'shift': [-0.07, 0, 0], 'color': ICON_STROKE},
        ]},
        'material': {'roughness': 0.78, 'metalness': 0.05, 'vertexColors': True},
        'wear': [None, None, True],
    })

    # ── sleeves ───────────────────────────────────────────────────────────────────────
    # Short bands AROUND the arm, never plates on one face of it: a limb bone's local Z
    # is neither up nor forward, and its +Y is about 20 degrees off the arm's own line,
    # so anything long walks off the arm.
    for side in ('l', 'r'):
        parts.append({
            'id': f'cuff{side.upper()}', 'bone': f'upperarm.{side}',
            'at': [0, 0.27, 0],
            'shape': {'parts': [
                {'cyl': [ARM_R + 0.042, ARM_R + 0.030, 0.15, 10], 'color': WHITE},
                {'cyl': [ARM_R + 0.050, ARM_R + 0.048, 0.045, 10],
                 'shift': [0, 0.085, 0], 'color': WHITE_WARM},
            ]},
            'material': {'roughness': 0.9, 'metalness': 0, 'vertexColors': True},
            'wear': [True, True, True],
        })

    # ── clogs ─────────────────────────────────────────────────────────────────────────
    # Kitchen clogs, white, with a dark sole. The FRONT of the shin is local -Z, which is
    # the one fact that decides which way the toe points.
    for side in ('l', 'r'):
        parts.append({
            'id': f'clog{side.upper()}', 'bone': f'lowerleg.{side}',
            'at': [0, 0.21, 0],
            'shape': {'parts': [
                {'cyl': [SHIN_R + 0.032, SHIN_R + 0.026, 0.13, 10], 'color': WHITE},
                # The toe box, forward of the shin.
                {'rbox': [0.145, 0.085, 0.17, 0.03], 'shift': [0, -0.03, -0.075],
                 'color': WHITE},
                {'rbox': [0.15, 0.035, 0.19, 0.014], 'shift': [0, -0.072, -0.07],
                 'color': GREY_800},
            ]},
            'material': {'roughness': 0.72, 'metalness': 0.02, 'vertexColors': True},
            'wear': [True, True, True],
        })

    # ── the hands, and the pair that share one ────────────────────────────────────────
    #
    # `when: working` and `when: resting` are opposites, so the knife and the pan can
    # occupy the same hand and never both be there. It is worth it for the READ as much
    # as the geometry: a cook who has put the knife down and picked up a pan is visibly
    # cooking, which is the thing the map exists to show.
    #
    # A hand's local +Y points at the FLOOR, so anything held needs rot z = PI, and then
    # a NEGATIVE rot[0] splays it outward where you can see it (positive tips it across
    # the body, behind the arm).
    parts.append({
        'id': 'knife', 'bone': 'hand.r', 'when': 'resting',
        'at': [0, -0.03, 0.03], 'rot': [-0.38, 0, PI],
        'shape': {'parts': [
            # The handle, in the fist.
            {'rbox': [0.045, 0.14, 0.038, 0.014], 'shift': [0, 0.055, 0],
             'color': ICON_STROKE},
            {'cyl': [0.026, 0.026, 0.022, 8], 'rotate': [PI / 2, 0, 0],
             'shift': [0, 0.135, 0], 'color': GOLD, 'tint': True},
            # The blade: a wedge, wider at the heel, tapering to the tip.
            {'box': [0.012, 0.40, 0.115], 'shift': [0, 0.355, 0.018],
             'color': '#d5dae0'},
            {'cone': [0.062, 0.13, 4], 'rotate': [0, PI / 4, 0],
             'stretch': [0.2, 1, 1], 'shift': [0, 0.60, 0.0],
             'color': '#d5dae0'},
        ]},
        'material': {'roughness': 0.3, 'metalness': 0.55, 'vertexColors': True},
        'tint': 'suit',
        'wear': [True, True, {'scale': 1.06}],
    })

    parts.append({
        'id': 'pan', 'bone': 'hand.r', 'when': 'working',
        'at': [0, -0.04, 0.02], 'rot': [-0.22, 0, PI],
        'shape': {'parts': [
            # The handle, running up out of the fist.
            {'cyl': [0.026, 0.030, 0.34, 6], 'shift': [0, 0.16, 0], 'color': ICON_STROKE},
            # The pan: a shallow open shell, so it reads as a vessel rather than a disc.
            {'cyl': [0.215, 0.165, 0.075, 14], 'shift': [0, 0.36, 0.20],
             'color': '#3a3a3c'},
            {'cyl': [0.205, 0.16, 0.02, 14], 'shift': [0, 0.40, 0.20],
             'color': MAHOGANY, 'tint': True},
        ]},
        'material': {'roughness': 0.45, 'metalness': 0.4, 'vertexColors': True},
        'tint': 'suit',
        'wear': [True, True, True],
    })

    # The off hand carries a plate while working: the other half of service, and it gives
    # the two senior ranks something the commis does not have.
    parts.append({
        'id': 'servicePlate', 'bone': 'hand.l', 'when': 'working',
        'at': [0, -0.02, 0.06], 'rot': [0.0, 0, PI],
        'shape': {'parts': [
            {'cyl': [0.20, 0.135, 0.028, 14], 'shift': [0, 0.055, 0], 'color': WHITE},
            {'cyl': [0.205, 0.20, 0.014, 14], 'shift': [0, 0.075, 0],
             'color': WHITE_WARM},
            {'cyl': [0.10, 0.09, 0.030, 10], 'shift': [0, 0.095, 0], 'tint': True},
        ]},
        'material': {'roughness': 0.35, 'metalness': 0.05, 'vertexColors': True},
        'tint': 'suit',
        'wear': [None, True, True],
    })

    return parts


# ══ the atlas ═════════════════════════════════════════════════════════════════════════
#
# Drawn from a list, so the theme needs no art at all: 32 flat swatches, indexed from the
# BOTTOM-LEFT, left to right, bottom to top. A cell index is a stable name for a colour,
# which is what lets every building in the kitchen be one merged geometry with one
# material and still have a copper pan on a slate range.
ATLAS = [
    ICON_STROKE,    # 0  the void, and anything that wants to be a shadow
    WHITE,          # 1  WHITE      glazed tile, plates, whites
    AURO,           # 2  STEEL      stainless benches, hoods, sinks
    PRIMARY,        # 3  SLATE      the brand's dark green: ranges, cabinet carcasses
    NUTMEG,         # 4  TIMBER     chopping blocks, crates, shelving
    PUMPKIN,        # 5  COPPER     pans, the warm metal
    MAHOGANY,       # 6  FLAME      the burner, the fire
    GOLD,           # 7  GOLD       rails, taps, fittings
    DARK_SPROUT,    # 8  HERB       planted greens
    SPROUT,         # 9  PRODUCE    the pale side of the produce
    BROCCOLI,       # 10 CHALK      the palest surface: paper, tickets, chalkboard frame
    PUMPKIN,        # 11 TRIM       THE ACCENT CELL. Repainted per zone, lit after dark.
    GREY_400,       # 12 GREY
    GREY_900,       # 13 DARK
    MARLIN,         # 14 MARLIN     cool steel, the walk-in door
    '#FFD9A0',      # 15 LAMP       the heat lamp's filament. Emissive.
    '#233B3B',      # 16 TILE_DARK  the shadow side of the slate
    '#E6D8C2',      # 17 LINEN      cloths, aprons at rest
    '#C8A97E',      # 18 BOARD      a scrubbed maple cutting board
    '#9C7B52',      # 19 CRATE      a produce crate
    '#BFD4DD',      # 20 GLASS      jars, the pass sneeze guard
    '#2B2723',      # 21 CHAR       the inside of an oven
    '#B08D57',      # 22 BRASS      older fittings
    SUCCESS,        # 23 GREEN
    ERROR,          # 24 RED
    LIGHT_BLUE,     # 25 ICE        the walk-in's cold light
    CORNFLOWER,     # 26 BLUE
    TEXT_GREY,      # 27 INK        chalkboard text, the rail
    '#F2E6D2',      # 28 PAPER      the ticket
    '#6E5A3E',      # 29 SACK       flour and dry goods
    '#8E9BA0',      # 30 ZINC
    '#151A1A',      # 31 SHADOW
]

CELLS = {
    'WHITE': 1, 'STEEL': 2, 'SLATE': 3, 'TIMBER': 4, 'COPPER': 5, 'FLAME': 6,
    'GOLD': 7, 'HERB': 8, 'PRODUCE': 9, 'CHALK': 10, 'TRIM': 11, 'GREY': 12,
    'DARK': 13, 'MARLIN': 14, 'LAMP': 15, 'TILE_DARK': 16, 'LINEN': 17,
    'BOARD': 18, 'CRATE': 19, 'GLASS': 20, 'CHAR': 21, 'BRASS': 22, 'GREEN': 23,
    'RED': 24, 'ICE': 25, 'BLUE': 26, 'INK': 27, 'PAPER': 28, 'SACK': 29,
    'ZINC': 30, 'SHADOW': 31,
}

# `[roughness, metalness]`. Keep metalness low on anything PAINTED: a fully metallic
# surface has no diffuse term and turns black under nothing but a soft sky.
SURFACES = {
    'WHITE': [0.35, 0.02], 'STEEL': [0.28, 0.75], 'SLATE': [0.55, 0.08],
    'TIMBER': [0.85, 0], 'COPPER': [0.32, 0.68], 'FLAME': [0.55, 0.1],
    'GOLD': [0.3, 0.72], 'HERB': [0.9, 0], 'PRODUCE': [0.88, 0],
    'CHALK': [0.92, 0], 'TRIM': [0.45, 0.1], 'MARLIN': [0.4, 0.35],
    'LAMP': [0.6, 0], 'BOARD': [0.8, 0], 'GLASS': [0.12, 0.2],
    'CHAR': [0.95, 0], 'ZINC': [0.35, 0.6], 'TILE_DARK': [0.5, 0.06],
}

# ══ the stations ══════════════════════════════════════════════════════════════════════
#
# Authored on a 2-unit module grid and scaled once by `world.scale` (1.4). A zone's middle
# slot has 6.18 units of clearance and its six ring slots have 1.81, so:
#
#     authored 2.0 wide -> 2.80 on the map -> middle slot; shrunk to fit a ring slot
#     authored 1.2 wide -> 1.68 on the map -> fits ANY slot, untouched
#
# The four that must keep their detail (prep, larder, dish pit, herb bed) are authored
# under 1.2 so they are never scaled at all. The four big ones accept being shrunk into
# outbuildings on the ring, which is what a kitchen looks like anyway: one range against
# the wall and benches around it. `lint_recipes` checks both claims rather than trusting
# this comment.
#
# THREE THINGS THE EVALUATOR DOES THAT THE DOC DOES NOT SAY, all read out of
# `world/recipes.js` and all of which fail SILENTLY:
#
#   1. `ring` and `grid` DROP the container's own x/y/z. `runStep` re-invokes with
#      `{...step.ring, x: <computed>, z: <computed>}`, so a height has to live INSIDE the
#      inner step and a group can never be moved off the recipe's centre line. Written at
#      the container, `y` does nothing at all and the row lands on the floor.
#   2. `ring` also overwrites the inner step's `ry` with its own tangent angle.
#   3. `cell` is resolved by `cellIndex`, which takes a NAME or a NUMBER and nothing else
#      -- the `["pick", ...]` form every other number accepts falls through to the
#      default cell. Use `any` to vary a colour.


def ring(inner, count, radius, **kw):
    """A ring, with the height where the evaluator will actually read it."""
    assert 'y' not in kw, 'ring: y belongs INSIDE the inner step (trap 1)'
    assert 'x' not in kw and 'z' not in kw, 'ring: the container cannot be moved (trap 1)'
    return {'ring': inner, 'count': count, 'radius': radius, **kw}


def grid(inner, cols, rows, dx, dz, **kw):
    """A grid, same rule."""
    assert 'y' not in kw, 'grid: y belongs INSIDE the inner step (trap 1)'
    assert 'x' not in kw and 'z' not in kw, 'grid: the container cannot be moved (trap 1)'
    return {'grid': inner, 'cols': cols, 'rows': rows, 'dx': dx, 'dz': dz, **kw}


def recipes():
    """
    Ten stations. EVERY `y` HERE IS A BOTTOM, not a centre -- see the note in `_walk`.
    Each one is written so the reader can stack it in their head: a plate on the ground,
    a carcass on the plate, a worktop on the carcass, and whatever stands on the worktop.
    `unsupported()` checks that reading against the geometry on every build.
    """
    return [
        # ── the pass: where a ticket becomes a plate ─────────────────────────────────
        {'id': 'pass', 'label': 'The pass', 'steps': [
            {'plate': [2.0, 1.1, 0.08], 'cell': 'TILE_DARK'},
            {'box': [1.9, 0.62, 0.9], 'cell': 'STEEL', 'y': 0.08},
            {'box': [1.96, 0.06, 0.96], 'cell': 'ZINC', 'y': 0.70},
            # The gantry, standing on the worktop.
            {'cyl': [0.045, 0.045, 0.86, 8], 'cell': 'GOLD', 'x': -0.82, 'y': 0.76},
            {'cyl': [0.045, 0.045, 0.86, 8], 'cell': 'GOLD', 'x': 0.82, 'y': 0.76},
            {'box': [1.8, 0.1, 0.34], 'cell': 'TRIM', 'y': 1.62},
            # Heat lamps, hung UNDER the gantry: their tops meet its underside.
            grid({'cyl': [0.07, 0.07, 0.1, 8], 'cell': 'LAMP', 'emissive': 1, 'y': 1.52},
                 3, 1, 0.62, 0),
            # The ticket rail, spanning post to post, and tickets hanging off it.
            {'box': [1.72, 0.03, 0.03], 'cell': 'INK', 'y': 1.40, 'z': 0.14},
            {'box': [0.11, 0.15, 0.006], 'cell': 'PAPER', 'x': -0.42, 'y': 1.26,
             'z': 0.14},
            {'box': [0.11, 0.15, 0.006], 'cell': 'PAPER', 'x': -0.05, 'y': 1.26,
             'z': 0.14, 'chance': 0.8},
            {'box': [0.11, 0.15, 0.006], 'cell': 'PAPER', 'x': 0.33, 'y': 1.26,
             'z': 0.14, 'chance': 0.55},
            # On the worktop: plates stacked, and one under the lamps ready to go.
            {'cyl': [0.17, 0.17, 0.13, 12], 'cell': 'WHITE', 'x': -0.68, 'y': 0.76},
            {'cyl': [0.19, 0.15, 0.03, 12], 'cell': 'WHITE', 'x': 0.24, 'y': 0.76,
             'chance': 0.7},
            {'cyl': [0.1, 0.08, 0.02, 10], 'cell': 'HERB', 'x': 0.24, 'y': 0.79,
             'chance': 0.5},
        ]},

        # ── the range: the hot line ──────────────────────────────────────────────────
        {'id': 'range', 'label': 'The range', 'steps': [
            {'plate': [1.9, 1.0, 0.08], 'cell': 'TILE_DARK'},
            {'box': [1.75, 0.8, 0.82], 'cell': 'SLATE', 'y': 0.08},
            {'box': [1.8, 0.07, 0.88], 'cell': 'DARK', 'y': 0.88},
            grid({'cyl': [0.16, 0.17, 0.04, 10], 'cell': 'DARK', 'y': 0.95},
                 3, 2, 0.52, 0.34),
            grid({'cyl': [0.09, 0.06, 0.05, 8], 'cell': 'FLAME', 'emissive': 0.85,
                  'y': 0.99, 'chance': 0.75}, 3, 2, 0.52, 0.34),
            {'cyl': [0.22, 0.21, 0.34, 12], 'cell': 'STEEL', 'x': -0.52, 'y': 0.95,
             'chance': 0.8},
            {'cyl': [0.24, 0.18, 0.07, 12], 'cell': 'COPPER', 'x': 0.5, 'y': 0.95,
             'chance': 0.6},
            # The splashback carries the hood, so the hood needs no legs of its own.
            {'box': [1.78, 0.72, 0.07], 'cell': 'WHITE', 'y': 0.95, 'z': -0.42},
            {'box': [1.86, 0.1, 1.0], 'cell': 'ZINC', 'y': 1.67},
            {'prism': [1.9, 0.34, 1.05], 'cell': 'STEEL', 'y': 1.77},
            {'cyl': [0.16, 0.16, 0.42, 8], 'cell': 'STEEL', 'x': 0.42, 'y': 2.05,
             'z': -0.2},
        ]},

        # ── the grill: charcoal, and the only station with an open fire ─────────────
        {'id': 'grill', 'label': 'The grill', 'steps': [
            {'plate': [1.85, 1.05, 0.08], 'cell': 'TILE_DARK'},
            {'box': [1.6, 0.58, 0.86], 'cell': 'DARK', 'y': 0.08},
            # The firebox, open at the top, with the coals in it.
            {'box': [1.42, 0.22, 0.7], 'cell': 'CHAR', 'y': 0.66},
            grid({'sphere': [0.055, 6, 5], 'cell': 'FLAME', 'emissive': 0.95,
                  'sy': 0.5, 'y': 0.70}, 5, 3, 0.26, 0.19),
            # The bars, which are what makes it a grill and not a brazier.
            grid({'cyl': [0.022, 0.022, 0.66, 6], 'rotate': [1.5707963, 0, 0],
                  'cell': 'ZINC', 'y': 0.88}, 9, 1, 0.155, 0),
            {'box': [1.5, 0.04, 0.74], 'cell': 'STEEL', 'y': 0.84, 'z': 0},
            # The salamander: a hood on two uprights, with a rack of skewers under it.
            {'cyl': [0.045, 0.045, 0.78, 6], 'cell': 'STEEL', 'x': -0.72, 'y': 0.90,
             'z': -0.3},
            {'cyl': [0.045, 0.045, 0.78, 6], 'cell': 'STEEL', 'x': 0.72, 'y': 0.90,
             'z': -0.3},
            {'box': [1.62, 0.09, 0.66], 'cell': 'ZINC', 'y': 1.68, 'z': -0.14},
            {'cyl': [0.026, 0.026, 0.34, 6], 'cell': 'STEEL', 'x': 0.0, 'y': 1.77,
             'z': -0.14},
            # Tools hung off the upright, and a tray of what is waiting to go on. The
            # tool has to OVERLAP the upright in plan or it hangs in the air beside it.
            {'box': [0.05, 0.34, 0.05], 'cell': 'TIMBER', 'x': -0.72, 'y': 1.28,
             'z': -0.29, 'chance': 0.7},
            {'box': [0.44, 0.05, 0.3], 'cell': 'CRATE', 'x': 0.5, 'y': 0.70,
             'z': 0.46, 'chance': 0.7},
            {'sphere': [0.06, 6, 5], 'cell': 'FLAME', 'sy': 0.6, 'x': 0.44,
             'y': 0.75, 'z': 0.46, 'chance': 0.7},
            {'sphere': [0.06, 6, 5], 'cell': 'FLAME', 'sy': 0.6, 'x': 0.58,
             'y': 0.75, 'z': 0.46, 'chance': 0.5},
        ]},

        # ── the bar: the other side of the pass, where service meets the room ───────
        {'id': 'bar', 'label': 'The bar', 'steps': [
            {'plate': [2.0, 1.2, 0.08], 'cell': 'TILE_DARK'},
            # The counter, with a timber front and a zinc top: a real bar.
            {'box': [1.86, 0.92, 0.62], 'cell': 'TIMBER', 'y': 0.08, 'z': -0.12},
            {'box': [1.96, 0.07, 0.78], 'cell': 'ZINC', 'y': 1.00, 'z': -0.05},
            {'box': [1.9, 0.06, 0.06], 'cell': 'GOLD', 'y': 0.88, 'z': 0.21},
            # The back shelf, standing on the counter, with the bottles on it.
            {'cyl': [0.04, 0.04, 0.72, 6], 'cell': 'GOLD', 'x': -0.8, 'y': 1.07,
             'z': -0.34},
            {'cyl': [0.04, 0.04, 0.72, 6], 'cell': 'GOLD', 'x': 0.8, 'y': 1.07,
             'z': -0.34},
            {'box': [1.74, 0.05, 0.26], 'cell': 'TIMBER', 'y': 1.45, 'z': -0.34},
            grid({'cyl': [0.055, 0.05, 0.30, 8], 'cell': 'GLASS', 'y': 1.50},
                 6, 1, 0.28, 0),
            grid({'cyl': [0.022, 0.022, 0.07, 6], 'cell': 'TRIM', 'y': 1.80},
                 6, 1, 0.28, 0),
            # Taps on the counter, and a lamp over it.
            {'cyl': [0.05, 0.05, 0.26, 8], 'cell': 'STEEL', 'x': -0.42, 'y': 1.07,
             'z': -0.05},
            {'cyl': [0.03, 0.03, 0.14, 6], 'rotate': [1.5707963, 0, 0], 'cell': 'STEEL',
             'x': -0.42, 'y': 1.26, 'z': 0.04},
            {'cyl': [0.05, 0.05, 0.26, 8], 'cell': 'STEEL', 'x': -0.28, 'y': 1.07,
             'z': -0.05},
            {'cyl': [0.03, 0.03, 0.14, 6], 'rotate': [1.5707963, 0, 0], 'cell': 'STEEL',
             'x': -0.28, 'y': 1.26, 'z': 0.04},
            # Glasses waiting, upside down as they are kept.
            grid({'cyl': [0.05, 0.062, 0.13, 8], 'cell': 'GLASS', 'y': 1.07},
                 3, 1, 0.17, 0),
            # Stools, which is the thing that says BAR rather than counter.
            {'cyl': [0.16, 0.14, 0.05, 10], 'cell': 'TIMBER', 'x': -0.5, 'y': 0.62,
             'z': 0.58},
            {'cyl': [0.045, 0.045, 0.62, 6], 'cell': 'DARK', 'x': -0.5, 'y': 0.0,
             'z': 0.58},
            {'cyl': [0.16, 0.14, 0.05, 10], 'cell': 'TIMBER', 'x': 0.1, 'y': 0.62,
             'z': 0.58, 'chance': 0.85},
            {'cyl': [0.045, 0.045, 0.62, 6], 'cell': 'DARK', 'x': 0.1, 'y': 0.0,
             'z': 0.58, 'chance': 0.85},
            {'cyl': [0.16, 0.14, 0.05, 10], 'cell': 'TIMBER', 'x': 0.68, 'y': 0.62,
             'z': 0.58, 'chance': 0.6},
            {'cyl': [0.045, 0.045, 0.62, 6], 'cell': 'DARK', 'x': 0.68, 'y': 0.0,
             'z': 0.58, 'chance': 0.6},
        ]},

        # ── the prep table: authored ring-safe, so it never loses its detail ─────────
        {'id': 'prep', 'label': 'Prep table', 'steps': [
            ring({'cyl': [0.035, 0.035, 0.78, 6], 'cell': 'STEEL', 'y': 0.0},
                 4, 0.48, jitter=0, startAngle=0.7854),
            {'box': [1.0, 0.05, 0.5], 'cell': 'STEEL', 'y': 0.22},
            {'box': [1.1, 0.06, 0.62], 'cell': 'ZINC', 'y': 0.78},
            {'box': [0.46, 0.035, 0.3], 'cell': 'BOARD', 'x': -0.2, 'y': 0.84},
            {'sphere': [0.055, 6, 5], 'cell': 'HERB', 'x': -0.3, 'y': 0.875},
            {'sphere': [0.05, 6, 5], 'cell': 'PRODUCE', 'x': -0.16, 'y': 0.875,
             'chance': 0.85},
            {'sphere': [0.045, 6, 5], 'cell': 'COPPER', 'x': -0.08, 'y': 0.875,
             'chance': 0.6},
            {'box': [0.16, 0.008, 0.026], 'cell': 'ZINC', 'x': -0.22, 'y': 0.875,
             'ry': 0.4, 'chance': 0.7},
            # A crate on the under-shelf, not hovering beside the legs.
            {'box': [0.34, 0.2, 0.28], 'cell': 'CRATE', 'x': 0.3, 'y': 0.27,
             'chance': 0.7},
        ]},

        # ── the walk-in ───────────────────────────────────────────────────────────────
        {'id': 'walkin', 'label': 'Walk-in', 'steps': [
            {'box': [1.5, 1.7, 1.3], 'cell': 'MARLIN', 'y': 0},
            {'box': [1.54, 0.12, 1.34], 'cell': 'ZINC', 'y': 1.7},
            {'box': [0.72, 1.4, 0.06], 'cell': 'ICE', 'y': 0.04, 'z': 0.64},
            {'cyl': [0.035, 0.035, 0.34, 8], 'cell': 'STEEL', 'x': 0.26, 'y': 0.62,
             'z': 0.69},
            {'box': [0.05, 1.3, 0.02], 'cell': 'GLASS', 'x': -0.38, 'y': 0.06,
             'z': 0.68, 'emissive': 0.5, 'chance': 0.4},
            {'box': [0.2, 0.13, 0.03], 'cell': 'DARK', 'x': -0.45, 'y': 1.42,
             'z': 0.63},
            {'box': [0.14, 0.07, 0.01], 'cell': 'ICE', 'x': -0.45, 'y': 1.45,
             'z': 0.65, 'emissive': 1},
            {'box': [1.2, 0.06, 0.06], 'cell': 'TRIM', 'y': 1.5, 'z': 0.64},
        ]},

        # ── the deck oven ─────────────────────────────────────────────────────────────
        {'id': 'oven', 'label': 'Deck oven', 'steps': [
            {'plate': [1.5, 1.0, 0.1], 'cell': 'TILE_DARK'},
            {'box': [1.35, 0.55, 0.85], 'cell': 'SLATE', 'y': 0.10},
            {'box': [1.35, 0.55, 0.85], 'cell': 'SLATE', 'y': 0.65},
            {'box': [1.1, 0.34, 0.04], 'cell': 'CHAR', 'y': 0.18, 'z': 0.42},
            {'box': [1.1, 0.34, 0.04], 'cell': 'CHAR', 'y': 0.73, 'z': 0.42},
            {'box': [0.96, 0.2, 0.02], 'cell': 'FLAME', 'y': 0.25, 'z': 0.44,
             'emissive': 0.9},
            {'box': [0.96, 0.2, 0.02], 'cell': 'FLAME', 'y': 0.80, 'z': 0.44,
             'emissive': 0.9, 'chance': 0.6},
            # Handles, laid across each door. `rotate` puts the cylinder along X and the
            # shape is still stood on `y`, so `y` is the underside of the bar.
            {'cyl': [0.028, 0.028, 1.15, 6], 'rotate': [0, 0, 1.5707963],
             'cell': 'BRASS', 'y': 0.50, 'z': 0.45},
            {'cyl': [0.028, 0.028, 1.15, 6], 'rotate': [0, 0, 1.5707963],
             'cell': 'BRASS', 'y': 1.05, 'z': 0.45},
            {'box': [1.4, 0.1, 0.9], 'cell': 'ZINC', 'y': 1.20},
            {'cyl': [0.13, 0.15, 1.1, 8], 'cell': 'DARK', 'x': 0.48, 'y': 1.30},
            {'cyl': [0.18, 0.18, 0.1, 8], 'cell': 'ZINC', 'x': 0.48, 'y': 2.40},
            # Split wood, stacked on the oven's own top.
            ring({'cyl': [0.09, 0.07, 0.13, 6], 'cell': 'TIMBER', 'y': 1.30},
                 3, 0.42, chance=0.7),
        ]},

        # ── the dry store: ring-safe ─────────────────────────────────────────────────
        {'id': 'larder', 'label': 'Dry store', 'steps': [
            ring({'cyl': [0.035, 0.035, 1.2, 6], 'cell': 'STEEL', 'y': 0.0},
                 4, 0.48, jitter=0, startAngle=0.7854),
            {'box': [1.1, 0.05, 0.42], 'cell': 'TIMBER', 'y': 0.28},
            {'box': [1.1, 0.05, 0.42], 'cell': 'TIMBER', 'y': 0.70},
            {'box': [1.1, 0.05, 0.42], 'cell': 'TIMBER', 'y': 1.12},
            grid({'cyl': [0.075, 0.075, 0.19, 8], 'cell': 'GLASS', 'y': 0.33},
                 4, 1, 0.26, 0),
            grid({'cyl': [0.078, 0.078, 0.02, 8], 'cell': 'TRIM', 'y': 0.52},
                 4, 1, 0.26, 0),
            grid({'cyl': [0.075, 0.075, 0.19, 8], 'cell': 'GLASS', 'y': 0.75,
                  'chance': 0.8}, 4, 1, 0.26, 0),
            # Sacks on the floor, where a sack of flour goes.
            ring({'sphere': [0.13, 7, 6], 'cell': 'SACK', 'sy': 0.8, 'y': 0.0},
                 3, 0.3, chance=0.85),
        ]},

        # ── the dish pit: ring-safe ──────────────────────────────────────────────────
        {'id': 'dishpit', 'label': 'Dish pit', 'steps': [
            {'box': [1.1, 0.7, 0.55], 'cell': 'STEEL', 'y': 0},
            {'box': [1.14, 0.06, 0.6], 'cell': 'ZINC', 'y': 0.70},
            # Basins standing on the bench, which reads as two sinks and, unlike a recess
            # cut into a solid worktop, is actually visible.
            grid({'box': [0.42, 0.15, 0.38], 'cell': 'SHADOW', 'y': 0.76},
                 2, 1, 0.48, 0),
            {'cyl': [0.028, 0.028, 0.36, 8], 'cell': 'GOLD', 'y': 0.76, 'z': -0.2},
            {'cyl': [0.024, 0.024, 0.22, 8], 'rotate': [1.5707963, 0, 0],
             'cell': 'GOLD', 'y': 1.10, 'z': -0.1},
            {'box': [0.42, 0.06, 0.4], 'cell': 'CRATE', 'x': 0.34, 'y': 0.91,
             'chance': 0.8},
            # Written out rather than gridded: a `grid` would drop the x and stand the
            # plates on the centre line instead of in the rack (trap 1).
            {'cyl': [0.13, 0.13, 0.02, 12], 'rotate': [1.5707963, 0, 0], 'cell': 'WHITE',
             'x': 0.34, 'y': 0.97, 'z': -0.12, 'chance': 0.85},
            {'cyl': [0.13, 0.13, 0.02, 12], 'rotate': [1.5707963, 0, 0], 'cell': 'WHITE',
             'x': 0.34, 'y': 0.97, 'z': -0.04, 'chance': 0.85},
            {'cyl': [0.13, 0.13, 0.02, 12], 'rotate': [1.5707963, 0, 0], 'cell': 'WHITE',
             'x': 0.34, 'y': 0.97, 'z': 0.04, 'chance': 0.7},
            {'cyl': [0.13, 0.13, 0.02, 12], 'rotate': [1.5707963, 0, 0], 'cell': 'WHITE',
             'x': 0.34, 'y': 0.97, 'z': 0.12, 'chance': 0.55},
        ]},

        # ── the herb bed: ring-safe, and the reason a kitchen has a yard ─────────────
        {'id': 'herbs', 'label': 'Herb bed', 'steps': [
            {'box': [1.15, 0.26, 0.7], 'cell': 'TIMBER', 'y': 0},
            {'box': [1.0, 0.08, 0.56], 'cell': 'SACK', 'y': 0.26},
            ring({'sphere': [0.13, 7, 6], 'cell': 'HERB', 'sy': 0.75, 'y': 0.34},
                 6, 0.34),
            ring({'sphere': [0.09, 6, 5], 'cell': 'PRODUCE', 'sy': 0.8, 'y': 0.34},
                 3, 0.16),
            {'box': [0.02, 0.2, 0.14], 'cell': 'CHALK', 'x': 0.42, 'y': 0.34,
             'chance': 0.7},
        ]},
    ]


# ══ the yard the kitchen stands in ════════════════════════════════════════════════════
#
# Two times of day rather than two planets, because a kitchen HAS two: the long cool prep
# before anybody arrives, and service. They are the same ground under different light,
# which is also the cheapest honest way to give a theme two worlds.

WORLDS = {
    'service': {
        'id': 'service', 'name': 'Service',
        'blurb': 'Golden hour, every station lit, tickets on the rail.',
        # Dry grass and stone, NOT earth. The first pass made the yard warm brown, which
        # is within a stop of the terracotta tile: from map height the zones stopped
        # reading as floors and the whole crew looked like Mars with furniture on it.
        # A zone has to sit AGAINST its ground.
        'ground': {'low': '#414737', 'high': '#8a8f6d', 'tint': '#a9ad86'},
        'rock': '#8a8279',
        'horizon': '#e2c59c',
        'sky': {'top': '#27456a', 'bottom': '#efcda1'},
        'fog': {'color': '#c9ab86', 'near': 92, 'far': 238},
        'sun': {'color': '#ffd7a4', 'intensity': 2.45, 'night': 0.17},
        'ambient': {'sky': '#d3b391', 'ground': '#474d38', 'intensity': 1.0},
        'atmosphere': 1, 'craters': 0, 'roughness': 0.62,
        'scatter': 'kitchengarden',
        'companion': {'name': 'Evening moon', 'color': '#f4ecd8', 'size': 3.0,
                      'glow': '#fff6e2'},
        'dust': 0.22,
    },
    'daybreak': {
        'id': 'daybreak', 'name': 'Daybreak',
        'blurb': 'Deliveries in, nothing fired yet. The quiet hour before service.',
        'ground': {'low': '#4f5a4c', 'high': '#8d9b7e', 'tint': '#b4c3a2'},
        'rock': '#7d8279',
        'horizon': '#d2dee5',
        'sky': {'top': '#37699b', 'bottom': '#dfeaf1'},
        'fog': {'color': '#bac9d3', 'near': 104, 'far': 268},
        'sun': {'color': '#fff6e8', 'intensity': 2.6, 'night': 0.12},
        'ambient': {'sky': '#bdd2e2', 'ground': '#4b5546', 'intensity': 1.05},
        'atmosphere': 1, 'craters': 0, 'roughness': 0.5,
        'scatter': 'kitchengarden',
        'companion': {'name': 'Morning moon', 'color': '#e8edf2', 'size': 2.2,
                      'glow': '#f4f8fb'},
        'dust': 0.12,
    },
}

# What grows around a kitchen: herbs, salad, a few crates' worth of green, and the odd
# stone. Parts are nodes from the shipped `forest` kit, which is the only kit this theme
# loads -- everything built is a primitive.
#
# The triple-form tints are the ones that matter. The kit's foliage is painted GREEN and
# the tint MULTIPLIES it, so a hex can only ever darken it: a channel above 1.0 is the
# only way to lift a bush toward Galley's pale sprout rather than sinking it to olive.
SCATTERS = {
    'kitchengarden': [
        {'part': 'Bush_1_E_Color1', 'weight': 6, 'size': [0.45, 0.9], 'sink': 0.07,
         'upright': True, 'tint': [1.25, 1.35, 0.95]},
        {'part': 'Bush_3_B_Color1', 'weight': 5, 'size': [0.4, 0.85], 'sink': 0.07,
         'upright': True, 'tint': [1.1, 1.3, 0.85]},
        {'part': 'Grass_2_D_Color1', 'weight': 8, 'size': [0.55, 1.2], 'sink': 0.05,
         'upright': True, 'tint': [1.2, 1.35, 0.9]},
        {'part': 'Grass_1_A_Color1', 'weight': 6, 'size': [0.5, 1.1], 'sink': 0.05,
         'upright': True, 'tint': [1.15, 1.3, 0.95]},
        # A few fruit trees at the edge of the yard, kept small: this is a kitchen garden,
        # not an orchard, and a tall tree beside a one-storey range breaks the scale.
        {'part': 'Tree_1_A_Color1', 'weight': 2, 'size': [0.32, 0.55], 'sink': 0.02,
         'upright': True, 'tint': [1.1, 1.25, 0.85]},
        {'part': 'Rock_1_D_Color1', 'weight': 2, 'size': [0.35, 0.8], 'sink': 0.32,
         'tint': True},
        {'part': 'Rock_3_A_Color1', 'weight': 1, 'size': [0.3, 0.7], 'sink': 0.34,
         'tint': True},
    ],
}

# ══ the arrival point: the front door of Galley ═══════════════════════════════════════
#
# Not the service entrance any more, the FRONT of house: a classical restaurant
# entrance, with the Galley wordmark over it, so arriving on the map is arriving at
# Galley. Awning, glass doors, brass lanterns, bay trees, a menu case, three steps.
#
# The wordmark is built from STROKES rather than pixels. A block-letter grid needs
# about ninety boxes for six letters; the same letters as strokes -- a bar per limb,
# an arc for the G -- need sixteen, read better at size, and keep the whole gate one
# merged hull. The pan-handle device left of the G is the half of the mark people
# recognise, so it gets its taper and its hanging hole.

LETTER_H = 0.78          # cap height
STROKE = 0.17            # the wordmark is a heavy geometric sans
LETTER_W = 0.62
LETTER_GAP = 0.30
SIGN_Z = 0.13            # how far the letters stand off their panel
SIGN_WALL_FRONT = 3.275  # the front face of the stone the sign hangs on


def _bar(x, y, z, w, h, *, rot=0.0, paint='mark'):
    """
    One stroke of a letter, standing proud of the sign panel.

    `base: False` ON EVERY STROKE, and this is the second time the same rule has bitten:
    `ship.js` does `base: step.base !== false` exactly as `recipes.js` does, so an
    arrival-point step is stood on the ground and `y` is its BOTTOM. Glyphs are built
    around a centre line -- a crossbar sits at the middle of a stem, not on top of it --
    so every stroke has to opt out, or the letters come apart and read upside down,
    which is what the sign did on its first render.
    """
    step = {'box': [r(w), r(h), SIGN_Z], 'paint': paint, 'base': False,
            'x': r(x), 'y': r(y), 'z': r(z)}
    if rot:
        step['rotate'] = [0, 0, r(rot)]
    return step


def _letter(ch, x, y, z):
    """
    One letter, as strokes, centred on `x` at baseline `y`.

    `y` is the BASELINE: every glyph is built upward from it, which is the only way a
    row of them sits on one line without each being nudged by hand.
    """
    h, sw, hw = LETTER_H, STROKE, LETTER_W / 2
    mid = y + h / 2
    out = []
    if ch == 'G':
        # An almost-closed ring with the bar into the middle: the Galley G.
        out.append({'torus': [hw - sw / 2, sw / 2, 20, 8, 5.34], 'rotate': [0, 0, -0.28],
                    'paint': 'mark', 'base': False, 'x': r(x), 'y': r(mid), 'z': r(z),
                    'stretch': [1, h / (2 * (hw - sw / 2) + sw), 1]})
        out.append(_bar(x + hw * 0.42, mid - h * 0.06, z, hw * 0.72, sw))
        out.append(_bar(x + hw * 0.72, mid - h * 0.20, z, sw, h * 0.34))
    elif ch == 'A':
        # THE SIGNS WERE THE WRONG WAY ROUND and it rendered as a V. A positive Z
        # rotation is counter-clockwise, so it throws a bar's TOP toward -X: the left
        # leg needs a NEGATIVE angle to lean its top in toward the apex, and the right
        # leg a positive one. Backwards, the legs meet at the foot instead of the peak.
        out.append(_bar(x - hw * 0.40, mid, z, sw, h, rot=-0.20))
        out.append(_bar(x + hw * 0.40, mid, z, sw, h, rot=0.20))
        out.append(_bar(x, y + h * 0.30, z, LETTER_W * 0.58, sw))
    elif ch == 'L':
        out.append(_bar(x - hw + sw / 2, mid, z, sw, h))
        out.append(_bar(x - sw * 0.1, y + sw / 2, z, LETTER_W * 0.86, sw))
    elif ch == 'E':
        out.append(_bar(x - hw + sw / 2, mid, z, sw, h))
        out.append(_bar(x + sw * 0.2, y + h - sw / 2, z, LETTER_W * 0.78, sw))
        out.append(_bar(x + sw * 0.05, mid, z, LETTER_W * 0.66, sw))
        out.append(_bar(x + sw * 0.2, y + sw / 2, z, LETTER_W * 0.78, sw))
    elif ch == 'Y':
        out.append(_bar(x - hw * 0.46, y + h * 0.75, z, sw, h * 0.52, rot=0.34))
        out.append(_bar(x + hw * 0.46, y + h * 0.75, z, sw, h * 0.52, rot=-0.34))
        out.append(_bar(x, y + h * 0.24, z, sw, h * 0.50))
    return out


def galley_wordmark(*, cx, y, z, scale=1.0):
    """
    GALLEY, with the pan device, centred on `cx` at baseline `y`.

    Returns plain arrival-point steps, so the whole sign merges into the gate's one
    hull -- a sign is not a thing that needs its own draw call.
    """
    word = 'GALLEY'
    pitch = LETTER_W + LETTER_GAP
    # The device sits a full pitch to the left of the G, as it does in the mark.
    total = pitch * (len(word) - 1) + LETTER_W + pitch * 1.05
    left = cx - total / 2 + pitch * 1.05
    steps = []

    # The pan: a tapering handle with the hanging hole at its far end. This is the half
    # of the wordmark anybody recognises without reading it.
    hx = left - pitch * 0.72
    steps.append({'box': [0.60, 0.30, SIGN_Z], 'paint': 'mark', 'base': False,
                  'x': r(hx), 'y': r(y + 0.30), 'z': r(z)})
    steps.append({'cyl': [0.19, 0.19, SIGN_Z, 16], 'rotate': [1.5707963, 0, 0],
                  'paint': 'mark', 'base': False,
                  'x': r(hx - 0.28), 'y': r(y + 0.30), 'z': r(z)})
    # The hole, punched through in the panel's own colour.
    steps.append({'cyl': [0.072, 0.072, SIGN_Z * 1.8, 12], 'rotate': [1.5707963, 0, 0],
                  'paint': 'signface', 'base': False,
                  'x': r(hx - 0.28), 'y': r(y + 0.30), 'z': r(z + 0.01)})

    for i, ch in enumerate(word):
        steps += _letter(ch, left + i * pitch, y, z)

    if scale != 1.0:
        for st in steps:
            for k in ('x', 'y'):
                st[k] = r((st.get(k, 0) - (cx if k == 'x' else y)) * scale
                          + (cx if k == 'x' else y))
            for key in ('box', 'cyl', 'torus'):
                if key in st:
                    st[key] = [r(v * scale) if n < (2 if key == 'torus' else 3) else v
                               for n, v in enumerate(st[key])]
    # The sign was invisible the first time because `z` was a parameter this function
    # accepted and never used: every stroke landed at z 0, inside the building, and the
    # panel above the awning rendered blank. Assert the letters are actually ON it.
    assert all(abs(st.get('z', 0) - z) < 0.2 for st in steps), \
        'the wordmark is not on its panel'
    assert all(st.get('base') is False for st in steps), \
        'a wordmark stroke would be stood on the ground rather than centred'
    # In FRONT of the fascia, which is in front of the wall. Two solids in the same
    # space are resolved by the viewing angle, which is how the logo went missing.
    assert z >= SIGN_WALL_FRONT + 0.1, (
        f'the wordmark sits at z={z}, not clear of the wall it hangs on '
        f'({SIGN_WALL_FRONT}); which of the two you see would depend on where you stand')
    return steps


SHIP = {
    'surfaces': {
        'stone': '#CFC3AE',      # the facade
        'stoneDark': '#A8997F',
        'trim': PRIMARY,         # the brand green: awning, doors, planters
        'trimDark': '#22403F',
        'brass': GOLD,
        'glass': '#BFD4DD',
        'mark': PRIMARY,         # the wordmark itself
        'signface': '#F6EFE2',   # the panel it stands on, and the punched hole
        'mat': '#2A2724',
        'shadow': ICON_STROKE,
        'lamp': '#FFD9A0',
        'leaf': DARK_SPROUT,
        'soil': '#4A3C2E',
    },
    'lights': {
        'beacon': [2.6, 1.9, 0.8],      # the lanterns
        'pad': [1.05, 0.85, 0.55],
        'glass': [1.35, 1.0, 0.6],      # the door glass and the sign
        'rampStrip': [1.0, 0.75, 0.35],
    },
    'door': [0, 0, 4.6],
    'recipe': {'steps': [
        # ── the forecourt and three steps up ────────────────────────────────────────
        {'plate': [11.0, 8.0, 0.3], 'paint': 'stoneDark', 'z': 1.1},
        {'plate': [10.2, 7.2, 0.16], 'paint': 'stone', 'z': 1.1, 'y': 0.3},
        {'plate': [5.4, 0.62, 0.22], 'paint': 'stoneDark', 'z': 4.55, 'y': 0.30},
        {'plate': [5.0, 0.58, 0.22], 'paint': 'stoneDark', 'z': 4.05, 'y': 0.52},
        {'plate': [4.6, 0.56, 0.22], 'paint': 'stoneDark', 'z': 3.58, 'y': 0.74},
        {'plate': [4.4, 1.5, 0.12], 'paint': 'mat', 'z': 4.9, 'y': 0.44},

        # ── the facade: two piers and a lintel, so the doorway is a real opening ────
        {'box': [2.6, 6.2, 0.55], 'paint': 'stone', 'base': True,
         'x': -3.3, 'y': 0.38, 'z': 3.1},
        {'box': [2.6, 6.2, 0.55], 'paint': 'stone', 'base': True,
         'x': 3.3, 'y': 0.38, 'z': 3.1},
        {'box': [4.2, 1.0, 0.55], 'paint': 'stone', 'y': 5.6, 'z': 3.1},
        {'box': [9.2, 0.34, 0.72], 'paint': 'stoneDark', 'y': 6.40, 'z': 3.1},
        # The wall the sign hangs on. Its FRONT FACE is 3.275, and everything in the
        # sign block has to sit in front of that -- see the note on the fascia.
        {'box': [8.8, 2.3, 0.45], 'paint': 'stone', 'y': 6.72, 'z': 3.05},
        # The dark of the room behind, so the glass has something to read against.
        {'box': [4.0, 5.2, 0.12], 'paint': 'shadow', 'base': True, 'y': 0.9, 'z': 2.76},

        # ── the doors: two leaves, mostly glass, with brass push-bars ───────────────
        {'box': [1.94, 4.5, 0.16], 'paint': 'trim', 'base': True,
         'x': -1.01, 'y': 0.96, 'z': 3.36},
        {'box': [1.94, 4.5, 0.16], 'paint': 'trim', 'base': True,
         'x': 1.01, 'y': 0.96, 'z': 3.36},
        {'box': [1.44, 3.1, 0.06], 'paint': 'glass', 'lit': 'glass',
         'x': -1.01, 'y': 3.45, 'z': 3.44},
        {'box': [1.44, 3.1, 0.06], 'paint': 'glass', 'lit': 'glass',
         'x': 1.01, 'y': 3.45, 'z': 3.44},
        {'cyl': [0.055, 0.055, 1.5, 8], 'paint': 'brass', 'x': -0.20, 'y': 2.55,
         'z': 3.50},
        {'cyl': [0.055, 0.055, 1.5, 8], 'paint': 'brass', 'x': 0.20, 'y': 2.55,
         'z': 3.50},
        # Kick plates: the bottom of a restaurant door is always brass.
        {'box': [1.94, 0.7, 0.2], 'paint': 'brass', 'x': -1.01, 'y': 1.15, 'z': 3.36},
        {'box': [1.94, 0.7, 0.2], 'paint': 'brass', 'x': 1.01, 'y': 1.15, 'z': 3.36},
        # The transom over them, lit from inside.
        {'box': [4.0, 0.66, 0.08], 'paint': 'glass', 'lit': 'glass', 'y': 5.62,
         'z': 3.34},

        # ── the awning ──────────────────────────────────────────────────────────────
        {'prism': [7.4, 0.85, 1.9], 'paint': 'trim', 'y': 5.75, 'z': 4.2},
        {'box': [7.4, 0.34, 0.1], 'paint': 'trimDark', 'y': 5.62, 'z': 5.12},
        # The scalloped valance, which is the detail that says awning and not roof.
        {'ring': {'cyl': [0.19, 0.19, 0.1, 12], 'rotate': [1.5707963, 0, 0],
                  'paint': 'trimDark', 'y': 5.50}, 'count': 9, 'radius': 3.3,
         'jitter': 0, 'z': 5.12},
        {'cyl': [0.07, 0.07, 1.4, 6], 'rotate': [0.9, 0, 0], 'paint': 'brass',
         'x': -3.4, 'y': 5.70, 'z': 4.5},
        {'cyl': [0.07, 0.07, 1.4, 6], 'rotate': [0.9, 0, 0], 'paint': 'brass',
         'x': 3.4, 'y': 5.70, 'z': 4.5},

        # ── the sign, over the awning ───────────────────────────────────────────────
        # THE SIGN BLOCK, AND ITS Z IS THE POINT.
        #
        # The first pass put the fascia at z 3.1 with a depth of 0.26, so it spanned
        # 2.97 .. 3.23 -- entirely INSIDE the stone wall behind it (2.825 .. 3.275). Two
        # solids occupying the same space do not compose, they argue, and which one you
        # see is decided by depth order and the angle you are standing at: the probe's
        # perspective view showed the cream fascia with its letters, and the artifact's
        # orthographic plate showed a blank stone wall. Same geometry, same frame, two
        # answers. That is what "it is missing the logo" was.
        #
        # `y` is a bottom here (base semantics) and `z` is a centre, so the block now
        # stacks in BOTH axes: wall front 3.275, then fascia 3.29..3.55, then the
        # letters proud of that again.
        {'box': [8.5, 0.15, 0.36], 'paint': 'brass', 'y': 7.00, 'z': 3.40},
        {'box': [8.2, 1.58, 0.26], 'paint': 'signface', 'lit': 'glass', 'y': 7.15,
         'z': 3.42},
        {'box': [8.5, 0.15, 0.36], 'paint': 'brass', 'y': 8.73, 'z': 3.40},

        # ── brass lanterns either side of the door ─────────────────────────────────
        {'box': [0.34, 0.34, 0.34], 'paint': 'brass', 'x': -2.45, 'y': 4.3, 'z': 3.42},
        {'cyl': [0.30, 0.22, 0.62, 6], 'paint': 'lamp', 'lit': 'beacon',
         'x': -2.45, 'y': 3.6, 'z': 3.55},
        {'cone': [0.30, 0.26, 6], 'paint': 'brass', 'x': -2.45, 'y': 4.2, 'z': 3.55},
        {'box': [0.34, 0.34, 0.34], 'paint': 'brass', 'x': 2.45, 'y': 4.3, 'z': 3.42},
        {'cyl': [0.30, 0.22, 0.62, 6], 'paint': 'lamp', 'lit': 'beacon',
         'x': 2.45, 'y': 3.6, 'z': 3.55},
        {'cone': [0.30, 0.26, 6], 'paint': 'brass', 'x': 2.45, 'y': 4.2, 'z': 3.55},

        # ── bay trees in planters, which is the other thing a restaurant door has ──
        {'cyl': [0.46, 0.40, 0.72, 8], 'paint': 'trim', 'x': -3.5, 'y': 0.46, 'z': 4.9},
        {'cyl': [0.40, 0.40, 0.1, 8], 'paint': 'soil', 'x': -3.5, 'y': 1.16, 'z': 4.9},
        {'cyl': [0.075, 0.075, 0.8, 6], 'paint': 'soil', 'x': -3.5, 'y': 1.2, 'z': 4.9},
        {'sphere': [0.58, 12, 9], 'paint': 'leaf', 'x': -3.5, 'y': 1.9, 'z': 4.9},
        {'cyl': [0.46, 0.40, 0.72, 8], 'paint': 'trim', 'x': 3.5, 'y': 0.46, 'z': 4.9},
        {'cyl': [0.40, 0.40, 0.1, 8], 'paint': 'soil', 'x': 3.5, 'y': 1.16, 'z': 4.9},
        {'cyl': [0.075, 0.075, 0.8, 6], 'paint': 'soil', 'x': 3.5, 'y': 1.2, 'z': 4.9},
        {'sphere': [0.58, 12, 9], 'paint': 'leaf', 'x': 3.5, 'y': 1.9, 'z': 4.9},

        # ── the menu case, on the left pier, because every restaurant has one ──────
        {'box': [1.0, 1.4, 0.12], 'paint': 'brass', 'x': -3.0, 'y': 2.6, 'z': 3.42},
        {'box': [0.84, 1.22, 0.06], 'paint': 'signface', 'lit': 'glass',
         'x': -3.0, 'y': 2.69, 'z': 3.48},

        # ── the threshold, brighter while somebody is walking in ───────────────────
        {'plate': [3.6, 0.4, 0.1], 'paint': 'lamp', 'lit': 'rampStrip', 'z': 3.62,
         'y': 0.92},
        {'plate': [9.0, 0.34, 0.08], 'paint': 'lamp', 'lit': 'pad', 'z': -2.0,
         'y': 0.44},
    # Baseline 7.68 with a 0.87 cap height puts the letters at 7.68 .. 8.55, centred in
    # a panel that runs 7.20 .. 9.10. The first pass had them at 6.42, below the panel
    # entirely and behind the awning: `y` is a BOTTOM for the panel and a BASELINE for
    # the glyphs, and the two have to be reconciled by hand.
    ] + galley_wordmark(cx=0, y=7.52, z=3.62, scale=0.98)},
}


# ══ lint: compute where it lands, before anybody renders it ═══════════════════════════
#
# "Ten lines in a throwaway script that print the world position of the thing you just
# placed will settle in one second what a render cycle settles in two minutes -- and it
# tells you WHY, which a render does not."
#
# So this measures every recipe the way `buildings.js` does (a HALF-extent from the
# recipe's origin, max over |x| and |z|), checks every cell name resolves, and checks the
# kit against the rig. It runs on every build and refuses to write a theme that fails.

BONES = {'head', 'chest', 'hips', 'hand', 'hand.l', 'hand.r',
         'upperarm.l', 'upperarm.r', 'lowerleg.l', 'lowerleg.r'}
RING_CLEARANCE = 1.81
MIDDLE_CLEARANCE = 6.18
COOK_HEIGHT = 2.2 * 0.56          # the character, at this theme's crew.scale


def _half(step):
    """The primitive's half-extents, after its own modifiers. None if it draws nothing."""
    hx = hy = hz = None
    for k, v in step.items():
        if k in ('box', 'rbox', 'prism'):
            hx, hy, hz = v[0] / 2, v[1] / 2, v[2] / 2
        elif k == 'plate':
            hx, hy, hz = v[0] / 2, v[2] / 2, v[1] / 2
        elif k in ('cyl', 'shell'):
            rr = max(v[0], v[1]); hx, hy, hz = rr, v[2] / 2, rr
        elif k == 'sphere' or k == 'cap':
            hx = hy = hz = v[0]
        elif k == 'cone':
            hx, hy, hz = v[0], v[1] / 2, v[0]
        elif k == 'torus':
            hx, hy, hz = v[0] + v[1], v[1], v[0] + v[1]
        else:
            continue
        break
    if hx is None:
        return None
    rot = step.get('rotate')
    if isinstance(rot, list):
        rx, ry, rz = (list(rot) + [0, 0, 0])[:3]
        if abs(abs(rx) - math.pi / 2) < 0.1: hy, hz = hz, hy
        if abs(abs(rz) - math.pi / 2) < 0.1: hx, hy = hy, hx
        if abs(abs(ry) - math.pi / 2) < 0.1: hx, hz = hz, hx
    st = step.get('stretch')
    if isinstance(st, list):
        hx, hy, hz = hx * st[0], hy * st[1], hz * st[2]
    s = step.get('s', 1)
    sx, sy, sz = step.get('sx', s), step.get('sy', s), step.get('sz', s)
    if isinstance(sx, (int, float)): hx *= sx
    if isinstance(sy, (int, float)): hy *= sy
    if isinstance(sz, (int, float)): hz *= sz
    return hx, hy, hz


SHAPE_KEYS = ('box', 'rbox', 'plate', 'prism', 'cyl', 'shell', 'sphere', 'cone',
              'torus', 'cap')


def _worst(v):
    """The largest value a `["range"|"int"|"pick", ...]` form can draw."""
    if isinstance(v, (int, float)):
        return float(v)
    if isinstance(v, list) and v:
        if v[0] in ('range', 'int'):
            return float(v[2])
        if v[0] == 'pick':
            return max(float(x) for x in v[1:] if isinstance(x, (int, float)))
    if v == 'rand':
        return 1.0
    return 0.0


def _walk(step, out, ox=0.0, oz=0.0, cells_seen=None, yaw=0.0):
    """
    Accumulate every placed box, in the recipe's own frame.

    `yaw` is carried because `ring` DOES NOT just move its members, it turns them:
    `runStep` re-invokes with `ry: a + PI/2`, so a member's local X ends up tangential
    and its local Z radial. A lint that ignores that measures a non-square box the wrong
    way round and reports a fin as floating when the fin crosses its column perfectly
    well -- which is exactly what it did to the vaporator's blades.
    """
    if not isinstance(step, dict):
        return
    if isinstance(step.get('cell'), str) and cells_seen is not None:
        cells_seen.add(step['cell'])
    if isinstance(step.get('any'), list):
        for s in step['any']:
            _walk(s, out, ox, oz, cells_seen, yaw)
        return
    if isinstance(step.get('group'), list):
        for s in step['group']:
            _walk(s, out, ox, oz, cells_seen, yaw)
        return
    if step.get('ring'):
        rad = _worst(step.get('radius', 1.4))
        # `jitter` defaults to 1 and pushes a member out by up to 15% of the radius.
        if step.get('jitter', 1):
            rad *= 1.15
        for ang in (0, math.pi / 2, math.pi, 3 * math.pi / 2):
            _walk(step['ring'], out, math.cos(ang) * rad, math.sin(ang) * rad,
                  cells_seen, yaw + ang + math.pi / 2)
        return
    if step.get('grid'):
        cols, rows = int(_worst(step.get('cols', 2))), int(_worst(step.get('rows', 2)))
        dx, dz = _worst(step.get('dx', 1)), _worst(step.get('dz', 1))
        for i in range(cols):
            for j in range(rows):
                _walk(step['grid'], out,
                      ox + (i - (cols - 1) / 2) * dx,
                      oz + (j - (rows - 1) / 2) * dz, cells_seen, yaw)
        return
    h = _half(step)
    if not h:
        return
    # A quarter turn about Y swaps a box's x and z extents. `ring` supplies one; a step
    # may add its own `ry` on top.
    total_yaw = yaw + _worst(step.get('ry', 0))
    if abs(math.sin(total_yaw)) > 0.7:
        h = (h[2], h[1], h[0])
    x = ox + _worst(step.get('x', 0))
    y = _worst(step.get('y', 0))
    z = oz + _worst(step.get('z', 0))
    # IN A RECIPE, `y` IS THE BOTTOM. `primitive()` in `world/recipes.js` passes
    # `base: step.base !== false` to every shape, so a building step is stood on the
    # ground and then lifted by `y` -- it is NOT centred on `y` the way a crew part is.
    # This lint modelled it as centred, which put every reported height out by half the
    # shape and, worse, was used to "correct" recipe heights that had been right. That is
    # what "some items are just floating" was.
    out.append({
        'lo': (x - h[0], y, z - h[2]),
        'hi': (x + h[0], y + 2 * h[1], z + h[2]),
        'what': next((k for k in step if k in SHAPE_KEYS), '?'),
        'cell': step.get('cell'),
    })


GROUND_TOL = 0.06        # a bottom this close to the deck is standing on it
TOUCH_TOL = 0.05         # how big a gap counts as air


def unsupported(boxes):
    """
    Which pieces have NOTHING under them, and nothing over them either.

    "Some items are just floating" -- and they were, because the heights had been
    authored against a lint that thought `y` was a centre. A piece is fine if it stands
    on the deck, if something it overlaps in plan reaches up to its bottom, or if
    something it overlaps HANGS over its top (a ticket clipped to a rail, a lamp slung
    under a gantry). Anything else is in the air.
    """
    bad = []
    for i, b in enumerate(boxes):
        if b['lo'][1] <= GROUND_TOL:
            continue
        held = False
        for j, o in enumerate(boxes):
            if i == j:
                continue
            if o['hi'][0] < b['lo'][0] or o['lo'][0] > b['hi'][0]:
                continue
            if o['hi'][2] < b['lo'][2] or o['lo'][2] > b['hi'][2]:
                continue
            # Stood on it, or hung from it.
            if o['hi'][1] >= b['lo'][1] - TOUCH_TOL and o['lo'][1] <= b['lo'][1] + TOUCH_TOL:
                held = True
                break
            if o['lo'][1] <= b['hi'][1] + TOUCH_TOL and o['hi'][1] >= b['hi'][1] - TOUCH_TOL:
                held = True
                break
            # Or simply inside/through it.
            if o['lo'][1] <= b['lo'][1] and o['hi'][1] >= b['lo'][1]:
                held = True
                break
        if not held:
            bad.append(f"{b['what']}({b['cell']}) floats, bottom at y={b['lo'][1]:.2f}")
    return bad


def lint_recipes(recs, scale, cells):
    print(f'  recipes, at world.scale {scale} '
          f'(ring slot {RING_CLEARANCE}, middle slot {MIDDLE_CLEARANCE}):')
    print(f'    {"id":10} {"half":>6} {"tall":>6} {"cooks":>6}  slot')
    problems = []
    for rec in recs:
        out, seen = [], set()
        for s in rec['steps']:
            _walk(s, out, cells_seen=seen)
        assert out, f'{rec["id"]}: no geometry at all'
        half = max(max(abs(b['lo'][0]), abs(b['hi'][0]), abs(b['lo'][2]), abs(b['hi'][2]))
                   for b in out) * scale
        tall = max(b['hi'][1] for b in out) * scale
        for msg in unsupported(out):
            problems.append(f'{rec["id"]}: {msg}')
        unknown = seen - set(cells)
        if unknown:
            problems.append(f'{rec["id"]}: unknown cell name(s) {sorted(unknown)} -- '
                            f'`cellIndex` takes a name or a number only, and anything '
                            f'else falls silently back to the default cell')
        if half > MIDDLE_CLEARANCE:
            problems.append(f'{rec["id"]}: {half:.2f} does not fit even the middle slot')
        if tall > COOK_HEIGHT * 5:
            problems.append(f'{rec["id"]}: {tall / COOK_HEIGHT:.1f} cooks tall; '
                            f'the tallest thing in the samurai village is 4.4')
        fits = half <= RING_CLEARANCE
        slot = 'any' if fits else f'middle (ring shrinks it to {100 * RING_CLEARANCE / half:.0f}%)'
        print(f'    {rec["id"]:10} {half:6.2f} {tall:6.2f} {tall / COOK_HEIGHT:6.1f}  {slot}')
    # A theme with nothing that fits a ring slot has no outbuildings, and every zone is
    # one shrunken building alone in the middle of an empty yard.
    ring_safe = sum(1 for rec in recs if _half_extent(rec) * scale <= RING_CLEARANCE)
    if ring_safe < 3:
        problems.append(f'only {ring_safe} recipe(s) fit a ring slot untouched; '
                        f'a zone needs outbuildings that keep their detail')
    return problems


def _collect(rec):
    out = []
    for s in rec['steps']:
        _walk(s, out)
    return out


def _half_extent(rec):
    """The recipe's footprint as `buildings.js` measures it: a half-extent from origin."""
    out = _collect(rec)
    if not out:
        return 0.0
    return max(max(abs(b['lo'][0]), abs(b['hi'][0]), abs(b['lo'][2]), abs(b['hi'][2]))
               for b in out)


def lint_crew(parts):
    problems = []
    ids = [p['id'] for p in parts]
    if len(ids) != len(set(ids)):
        problems.append('duplicate crew part ids')
    for p in parts:
        if p['bone'] not in BONES:
            problems.append(f'{p["id"]}: bone "{p["bone"]}" is not one of the nine')
        if len(p.get('wear', [])) != 3:
            problems.append(f'{p["id"]}: `wear` must have one entry per rank')
    if not any(p.get('material') == 'face' for p in parts):
        problems.append('no `face` part: nothing on the figure would say what it is doing')
    if not any(p['id'] == 'head' for p in parts):
        problems.append('no head part: the rig DROPS the mannequin\'s own head')
    # Every rank must wear something, and the three must differ.
    worn = [set(p['id'] for p in parts if p['wear'][t] is not None) for t in range(3)]
    for t, w in enumerate(worn):
        if not w:
            problems.append(f'tier {t} wears nothing at all')
    if worn[0] == worn[1] or worn[1] == worn[2]:
        problems.append('two ranks wear exactly the same kit -- they are not '
                        'distinguishable in silhouette or anywhere else')

    # A GLOWING PART IS ONE COLOUR, and the descriptor gives you no way to find out.
    #
    # `material: 'glow'` is not configurable: `_partMaterial` returns a flat
    # MeshBasicMaterial with NO `vertexColors`, because the point of it is to be unlit
    # and over-bright for the bloom pass. A composite carries its per-piece colours in a
    # vertex-colour attribute, so on a glow part they are read by nothing -- every piece
    # comes out the instance colour and the hexes in the descriptor are dead text.
    #
    # A lightsabre found it. Hilt and blade were one glowing part, and the machined steel
    # and the black grip both rendered as a bar of pure crystal colour: a sabre with no
    # handle. The fix is two parts sharing an `at`, a `rot` and a `wear`.
    def _pieces(shape):
        for piece in (shape or {}).get('parts', []):
            yield piece
            yield from _pieces(piece)

    for p in parts:
        if p.get('material') != 'glow':
            continue
        for piece in _pieces(p.get('shape')):
            if 'color' in piece:
                problems.append(f'{p["id"]}: a `glow` part discards piece colours '
                                f'({piece["color"]}) -- split the lit part off its own')
                break
        if any(piece.get('tint') for piece in _pieces(p.get('shape'))):
            problems.append(f'{p["id"]}: a `glow` part has no vertexColors, so a tint '
                            f'mask on its pieces is baked and never read')
    return problems


# ══ the theme ═════════════════════════════════════════════════════════════════════════

# CHOSEN BY MEASURING, and the number is much smaller than the other two themes'.
#
# A crew builds ARCHITECTURE and a village builds houses, so both want a scale that puts
# an eave two people up. A kitchen builds FURNITURE. Counter height is about 0.6 of a
# person, and the first pass at 1.9 gave a prep bench 1.4 cooks tall -- a table you could
# not see over, which reads as a crate.
#
# At 1.05 every proportion lands where a kitchen's does: the prep table at 0.7 cooks, the
# pass counter at 0.75, the hood at 1.5, the walk-in at 1.5, the oven's flue at 2.1. The
# consequence is that NO recipe exceeds the ring slot's 1.81, so nothing is ever scaled
# down to fit and every station keeps its detail in all seven slots -- which is the
# outcome `docs/crew-themes.md` recommends aiming for and neither shipped theme reaches.
#
# What a zone looks like is then seven pieces of equipment spread around a tiled yard
# rather than one building in the middle of it. For a kitchen that is not a compromise,
# it is the correct picture.
WORLD_SCALE = 1.05


def theme():
    return {
        'id': 'galley-kitchen',
        'name': 'Galley Kitchen',
        'blurb': 'A brigade kitchen at service. Every repo is a station, every session a '
                 'cook, every thread a ticket on the rail.',
        'planets': ['service', 'daybreak'],
        'worlds': WORLDS,
        'scatters': SCATTERS,

        # The eight KEYS are the status vocabulary and are not a theme's to change; the
        # words are. A kitchen already has a precise word for each of these states, which
        # is most of the reason this theme works at all.
        'status': {
            'working': 'On the line',        # it is cooking right now
            'waiting': 'On the pass',        # plated, waiting for the chef to look at it
            'blocked': "86'd",               # kitchen for "off, stop, we cannot"
            'celebrating': 'Served',
            'idle': 'Mise en place',         # prepped, ready, nothing to do yet
            'sleeping': 'In the walk-in',    # put away cold
            'spawning': 'Clocking in',
            'leaving': 'Breaking down',      # the end-of-shift clean
        },

        # One accent per station, hashed off the repo name. Galley's own palette, ordered
        # so that any two ADJACENT entries are far apart in hue -- a zone's neighbour is
        # frequently its successor in this list.
        'plotPalette': [
            PUMPKIN, MARLIN, DARK_SPROUT, MAHOGANY, CORNFLOWER, GOLD,
            SUCCESS, NUTMEG, LIGHT_BLUE, PRIMARY, ERROR, AURO,
        ],

        'crew': {
            'scale': 0.56,
            # The mannequin is the cook underneath: dark trousers and a dark undershirt,
            # with the whites worn OVER it. `tint: none` is the whole reason this reads as
            # a kitchen rather than as a spacesuit with an apron on.
            #
            # NEAR-BLACK, and that is the second attempt. The first was #39464A, a dark
            # slate within a stop of `low`'s marlin -- so a commis on low effort wore a
            # blue-grey apron over blue-grey legs and the one garment carrying its effort
            # simply disappeared. The body has to be darker than the whole effort ladder,
            # not merely different from the middle of it.
            'body': {'color': '#241F1D', 'roughness': 0.88, 'metalness': 0.02,
                     'tint': 'none'},
            'look': {
                'working':     {'trim': SUCCESS,     'eye': [0.4, 2.4, 1.0]},
                'waiting':     {'trim': CORNFLOWER,  'eye': [0.5, 1.4, 3.0]},
                'blocked':     {'trim': ERROR,       'eye': [3.0, 0.5, 0.4]},
                'celebrating': {'trim': PUMPKIN,     'eye': [2.9, 2.0, 0.6]},
                'idle':        {'trim': AURO,        'eye': [1.2, 1.4, 1.5]},
                'sleeping':    {'trim': MARLIN,      'eye': [0.6, 0.8, 1.5]},
                'spawning':    {'trim': DARK_SPROUT, 'eye': [1.4, 2.4, 0.9]},
                'leaving':     {'trim': GREY_400,    'eye': [1.0, 1.1, 1.0]},
            },
            # The heat of the burner, which is what effort is. Cool steel at the bottom,
            # full flame at the top, all of it Galley's own palette.
            'effortTones': {
                'low': MARLIN,
                'medium': DARK_SPROUT,
                'high': PUMPKIN,
                'xhigh': MAHOGANY,
                'max': ERROR,
                # NOT on the heat ladder on purpose. Ultracode is a different way of
                # working rather than a hotter one, so it gets a cool colour instead of a
                # redder red nobody could tell from `max`.
                #
                # The BRIGHT brand blue, not cornflower: cornflower came out at 2.5:1
                # against the near-black body, so the apron carrying it barely separated
                # from the legs behind it. `assert_tones_read` keeps that honest.
                'ultracode': ACCENT_BLUE,
            },
            # Asserts no temperature: the statusline has not confirmed a level yet.
            'effortUnknownTone': '#6E7276',
            'suitTones': [MARLIN, NUTMEG, DARK_SPROUT, GOLD, AURO],
            'parts': crew_parts(),
        },

        'hud': {
            'accent': MAHOGANY, 'green': SUCCESS, 'blue': CORNFLOWER,
            'amber': PUMPKIN, 'red': ERROR, 'teal': MARLIN,
        },
        'sky': {
            'nightFloor': '#0A0F12',
            'duskThick': '#E0913C',
            'duskThin': '#43506B',
            'fill': '#A9BFD2',
        },
        'ship': SHIP,
        'buildings': {'scaffold': DARK_SPROUT, 'fallbackAccent': PUMPKIN},
        'world': {
            'scale': WORLD_SCALE,
            'deck': 1.0,
            # Quarry tile. `plate` draws a panel grid with cut seams and studs, which on a
            # kitchen floor is exactly tiles, grout and the studs of a drainage channel.
            #
            # `tint` is the number to think about. At 1 the accent owns the floor, which is
            # right for neutral grey panels; at 0.45 the tile stays warm terracotta with
            # the station's colour cast over it, so two stations still read apart without
            # either of them getting a floor in a hue no kitchen ever had.
            'floor': {
                'kind': 'plate',
                'base': '#7A6A5C',      # grout, in the gutters between tiles
                'panel': '#A9846A',     # the tile itself -- honoured since 5.16
                'seam': 'rgba(58,44,36,0.8)',
                'bolt': 'rgba(228,214,190,0.55)',
                'tint': 0.45,
                'roughness': 0.6,
                'metalness': 0.04,
                'relief': 0.55,
            },
            # Replaced, not merged: naming only the forest kit means no space station is
            # inherited. Everything built here is a primitive; the kit is only what grows.
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
    print(f'Galley Kitchen -- {len(t["world"]["recipes"])} stations, '
          f'{len(t["crew"]["parts"])} worn parts, {len(t["worlds"])} worlds')

    assert len(ATLAS) == t['world']['atlas']['cols'] * t['world']['atlas']['rows'], \
        f'the atlas is {len(ATLAS)} swatches in a ' \
        f'{t["world"]["atlas"]["cols"]}x{t["world"]["atlas"]["rows"]} grid'
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

    assert_tones_read(t['crew']['body']['color'], t['crew']['effortTones'])
    problems = lint_crew(t['crew']['parts'])
    problems += lint_recipes(t['world']['recipes'], WORLD_SCALE, CELLS)
    if problems:
        print('\n  PROBLEMS:')
        for p in problems:
            print(f'    - {p}')
        sys.exit(1)

    where = sys.argv[1:] or ['themes/unshipped/galley-kitchen.json']
    for path in where:
        os.makedirs(os.path.dirname(path) or '.', exist_ok=True)
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(t, f, indent=1)
            f.write('\n')
        print(f'  wrote {path}  ({os.path.getsize(path) / 1024:.0f} KB)')


if __name__ == '__main__':
    main()
