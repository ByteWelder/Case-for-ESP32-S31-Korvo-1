"""
ESP32-S31-Korvo-1 V1.1 + 4.3" LCD subboard (ESP32-S3-LCD-EV-Board-SUB3) case.

Parametric build123d model. Run:  .venv-cad/bin/python case.py
Outputs STEP into ./step and STL into ./stl

Coordinate system = Espressif dimension drawing (mm):
  X: 0..106.5 along the long edge (LCD header at X~7, USB ports at X=106.5)
  Y: 0..83.2 (function buttons at Y~4, module/SD/camera at the top, tab up to 89.2)
  Z: 0 = outside of the case back, +Z towards the display front

Parts
  shell         back tray. No inserts, everything is through-hole and flush:
                - 4 countersunk M3 from the back, through the floor and the main
                  board corner holes, into the board's own standoffs
                - 4 columns with a through hole and a recessed nut trap in the
                  back for the bezel screws
  bezel         front plate: LCD window, camera/mic/LED holes, button guides,
                tongues that close the port slots
  button_long   4x  SET / MODE / VOL- / VOL+ plungers (stand proud)
  button_short  2x  RESET / BOOT plungers (recessed, press with a pen)

Values marked MEASURE are not in Espressif's drawings; check them on the real
board with calipers before printing.
"""
from pathlib import Path
from build123d import *

ROOT = Path(__file__).parent
STEP, STL = ROOT / "step", ROOT / "stl"

# ----------------------------------------------------------------------------
# Board facts (from esp32-s31-korvo-1-dimensions.dxf and the SUB3 PCB layout)
# ----------------------------------------------------------------------------
PCB_X, PCB_Y = 106.5, 83.2
TAB_X0, TAB_Y = 75.6, 89.2                 # camera/reset/boot tab
PCB_T = 1.6
CORNER_HOLES = [(4.0, 4.0), (96.0, 4.0), (4.0, 79.2), (96.0, 79.2)]  # stack standoffs
INNER_HOLES = [(24.625, 22.5), (81.875, 22.5)]                       # free -> case mount
LCD_C = (53.27, 41.6)                      # LCD module centre on the stack
LCD_W, LCD_H, LCD_T = 105.5, 67.2, 4.68    # WKS43246 module
CAM = (83.135, 84.664)
FUNC_BTNS = [(44.3, 3.8), (50.8, 3.8), (57.3, 3.8), (63.8, 3.8)]  # SET MODE VOL- VOL+
SYS_BTNS = [(93.4, 86.6), (101.7, 86.6)]                           # RESET BOOT
MICS = [(34.1, 5.1), (75.3, 5.1)]
RGB_LED = (17.5, 4.0)
SPK_X = [25.1, 83.6]                       # speaker connectors (bottom edge)

# ---- MEASURE ---------------------------------------------------------------
STACK_GAP = 11.0     # main PCB top -> LCD subboard bottom (standoff length)
BTN_H = 2.5          # tact switch actuator top above main PCB
BACK_CLR = 3.0       # room under main PCB for THT pin ends
FRONT_NUT_H = 4.6    # standoff stud + nut above LCD subboard (bezel has pockets)

# ---- Print / hardware ------------------------------------------------------
WALL = 2.4
FLOOR = 2.0
BEZEL_T = 2.4
LCD_RECESS = 0.6     # bezel face stands this far in front of the LCD glass
FIT = 0.5            # board <-> wall clearance
SCREW_D = 3.4        # M3 clearance
CSK_D = 6.6          # M3 countersunk head recess diameter (90 deg)
NUT_AF = 5.7         # M3 hex nut across flats + clearance
NUT_T = 2.4
BEZEL_SCREW_LEN = 20.0   # countersunk M3 through bezel + column into the nut
COL_R = 3.5          # bezel screw column radius
CHIN = 7.0           # extra room below the board (bezel screws, speaker plugs)

# ---- Derived Z levels ------------------------------------------------------
Z_PCB = FLOOR + BACK_CLR                 # main PCB underside
Z_PCB_TOP = Z_PCB + PCB_T
Z_SUB = Z_PCB_TOP + STACK_GAP            # subboard underside
Z_SUB_TOP = Z_SUB + PCB_T
Z_LCD = Z_SUB_TOP + LCD_T + 0.1          # LCD glass front (0.1 adhesive)
Z_TOP = Z_LCD + LCD_RECESS               # bezel front face
Z_SPLIT = Z_TOP - BEZEL_T                # shell wall top / bezel underside

# ---- Derived XY ------------------------------------------------------------
IX0, IX1 = -FIT, PCB_X + FIT             # cavity
IY0, IY1 = -FIT - CHIN, TAB_Y + FIT
OX0, OX1, OY0, OY1 = IX0 - WALL, IX1 + WALL, IY0 - WALL, IY1 + WALL
BEZEL_SCREWS = [
    (IX0 + COL_R, -FIT - COL_R), (IX1 - COL_R, -FIT - COL_R),      # chin corners
    (IX0 + COL_R, PCB_Y + FIT + COL_R), (51.0, PCB_Y + FIT + COL_R),  # top strip
]

# Right-wall port slots: (y0, y1, z_bottom, z_top_of_opening). Open to the top
# so the board drops straight in; the bezel tongues close them.
PORT_SLOTS = [
    (10.9, 25.2, Z_PCB_TOP - 0.3, Z_PCB_TOP + 7.6),    # USB-A
    (29.3, 39.1, Z_PCB_TOP - 0.3, Z_PCB_TOP + 6.0),    # power slide switch
    (41.7, 68.5, Z_PCB_TOP - 2.2, Z_PCB_TOP + 5.4),    # 2x USB-C incl. plug overmould
]
SD_WIN = (56.5, 74.5, Z_PCB_TOP - 0.6, Z_PCB_TOP + 5.4)   # x0, x1, z0, z1 (top wall)
SPK_WIN = (8.0, Z_PCB_TOP - 0.5, Z_PCB_TOP + 5.5)         # width, z0, z1 (bottom wall)


# ----------------------------------------------------------------------------
def box(x0, x1, y0, y1, z0, z1):
    return Pos((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2) * Box(x1 - x0, y1 - y0, z1 - z0)


def cyl(x, y, r, z0, z1):
    return Pos(x, y, (z0 + z1) / 2) * Cylinder(r, z1 - z0)


def rrect(x0, x1, y0, y1, r, z0, z1):
    sk = Pos((x0 + x1) / 2, (y0 + y1) / 2, z0) * RectangleRounded(x1 - x0, y1 - y0, r)
    return extrude(sk, z1 - z0)


def prism(pts, z0, z1):
    return extrude(Pos(0, 0, z0) * make_face(Polyline(*pts, close=True)), z1 - z0)


def csk(x, y, z, up):
    """90 deg countersink cone with its wide end on the surface at z."""
    h = (CSK_D - SCREW_D) / 2
    if up:      # surface faces -Z (case back)
        return Pos(x, y, z + h / 2 - 0.01) * Cone(CSK_D / 2, SCREW_D / 2, h + 0.02)
    return Pos(x, y, z - h / 2 + 0.01) * Cone(SCREW_D / 2, CSK_D / 2, h + 0.02)


def fuse(parts):
    out = parts[0]
    for p in parts[1:]:
        out = out + p
    return out


MAIN_OUTLINE = [(0, 0), (PCB_X, 0), (PCB_X, TAB_Y), (TAB_X0, TAB_Y), (TAB_X0, PCB_Y), (0, PCB_Y)]
SUB_OUTLINE = [(0, 0), (10, 0), (10, 6), (15, 6), (15, 10.5), (99, 10.5), (99, 7.5), (92, 7.5),
               (92, 0), (106.5, 0), (106.5, 83.2), (90, 83.2), (90, 77.2), (10, 77.2),
               (10, 83.2), (0, 83.2)]


def board_keepout(z0, z1):
    """Volume the board stack sweeps when dropped in from the front."""
    return (box(-FIT, PCB_X + FIT, -FIT, PCB_Y + FIT, z0, z1)
            + box(TAB_X0 - FIT, PCB_X + FIT, PCB_Y, TAB_Y + FIT, z0, z1))


# ----------------------------------------------------------------------------
def make_shell():
    outer = rrect(OX0, OX1, OY0, OY1, 4.0, 0, Z_SPLIT)
    outer = chamfer(outer.edges().group_by(Axis.Z)[0], 0.8)
    s = outer - rrect(IX0, IX1, IY0, IY1, 1.6, FLOOR, Z_SPLIT)

    # bezel screw columns (clipped to the outside shape, cleared for the board)
    cols = fuse([cyl(x, y, COL_R, FLOOR, Z_SPLIT) for x, y in BEZEL_SCREWS])
    s += (cols & outer) - board_keepout(FLOOR, Z_SPLIT)

    # main board supports: bosses at the corner holes, plain pads at the inner holes
    s += fuse([cyl(x, y, 3.0, FLOOR, Z_PCB) for x, y in INNER_HOLES])
    s += fuse([cyl(x, y, 4.0, FLOOR, Z_PCB) for x, y in CORNER_HOLES]) & outer
    for x, y in CORNER_HOLES:                 # countersunk M3 from the back into the standoff
        s -= cyl(x, y, SCREW_D / 2, -0.1, Z_PCB + 0.1)
        s -= csk(x, y, 0.0, up=True)
    nut_z = Z_TOP - BEZEL_SCREW_LEN + NUT_T + 0.6   # nut seat: screw tip ends 0.6 past the nut
    for x, y in BEZEL_SCREWS:
        s -= cyl(x, y, SCREW_D / 2, -0.1, Z_SPLIT + 0.1)
        s -= Pos(x, y, 0) * extrude(RegularPolygon(NUT_AF / 2, 6, major_radius=False), nut_z)

    # openings
    for y0, y1, z0, _ in PORT_SLOTS:
        s -= box(IX1 - 0.1, OX1 + 0.1, y0, y1, z0, Z_SPLIT)
    x0, x1, z0, z1 = SD_WIN
    s -= box(x0, x1, IY1 - 0.1, OY1 + 0.1, z0, z1)
    w, z0, z1 = SPK_WIN
    for x in SPK_X:
        s -= box(x - w / 2, x + w / 2, OY0 - 0.1, IY0 + 0.1, z0, z1)
    return s


def make_bezel():
    plate = rrect(OX0, OX1, OY0, OY1, 4.0, Z_SPLIT, Z_TOP)
    plate = chamfer(plate.edges().group_by(Axis.Z)[-1], 0.8)
    b = plate

    under = []
    # tongues closing the port slots above the connectors
    for y0, y1, _, ztop in PORT_SLOTS:
        under.append(box(IX1 + 0.1, OX1, y0 + 0.25, y1 - 0.25, ztop, Z_SPLIT))
    # locating lips just inside the bottom and top walls
    lz = Z_SPLIT - 3.0
    under.append(box(9.0, 98.0, IY0 + 0.25, IY0 + 1.45, lz, Z_SPLIT))
    under.append(box(9.0, 45.0, IY1 - 1.45, IY1 - 0.25, lz, Z_SPLIT))
    under.append(box(57.0, 74.0, IY1 - 1.45, IY1 - 0.25, lz, Z_SPLIT))
    # button guide tubes
    tube_z = Z_PCB_TOP + BTN_H + 3.5
    for x, y in FUNC_BTNS:
        under.append(cyl(x, y, 3.5, tube_z, Z_SPLIT))
    for x, y in SYS_BTNS:     # squeezed between the LCD subboard edge and the top wall
        under.append(cyl(x, y, 3.4, tube_z, Z_SPLIT)
                     & box(x - 5, x + 5, PCB_Y + 0.3, IY1 - 0.3, tube_z - 1, Z_SPLIT + 1))
    for u in under:
        b += u

    # LCD window
    cx, cy = LCD_C
    b -= box(cx - LCD_W / 2 - 0.5, cx + LCD_W / 2 + 0.5,
             cy - LCD_H / 2 - 0.5, cy + LCD_H / 2 + 0.5, Z_SPLIT - 0.1, Z_TOP + 0.1)
    # pockets over the standoff nuts on the LCD subboard corners
    for x, y in CORNER_HOLES:
        b -= cyl(x, y, 4.0, Z_SPLIT - 0.1, max(Z_SUB_TOP + FRONT_NUT_H, Z_SPLIT + 0.2))
    # camera: through hole with a flared front
    b -= cyl(*CAM, 4.75, Z_SPLIT - 0.1, Z_TOP + 0.1)
    b -= Pos(CAM[0], CAM[1], Z_TOP - 0.75) * Cone(4.75, 6.3, 1.5 + 0.02)
    # buttons, mics, LED
    for x, y in FUNC_BTNS + SYS_BTNS:
        b -= cyl(x, y, 2.3, 0, Z_TOP + 0.1)
    for x, y in MICS:
        b -= cyl(x, y, 1.0, Z_SPLIT - 0.1, Z_TOP + 0.1)
    b -= cyl(*RGB_LED, 1.5, Z_SPLIT - 0.1, Z_TOP + 0.1)
    # countersunk M3 screws
    for x, y in BEZEL_SCREWS:
        b -= cyl(x, y, SCREW_D / 2, Z_SPLIT - 0.1, Z_TOP + 0.1)
        b -= csk(x, y, Z_TOP, up=False)
    return b


def make_button(proud):
    """Plunger at the origin: foot at z=0 rests on the tact switch."""
    tube_bottom = BTN_H + 3.5                    # above main PCB top, see make_bezel
    z_fl1 = tube_bottom - 0.5 - BTN_H            # flange top (0.5 play to the tube)
    z_fl0 = z_fl1 - 1.0
    top = (Z_TOP - Z_PCB_TOP - BTN_H) + proud
    p = Pos(0, 0, (z_fl0 - 1.5) / 2) * Cylinder(1.6, z_fl0 - 1.5)                  # foot
    p += Pos(0, 0, z_fl0 - 0.75) * Cone(1.6, 3.1, 1.5)                             # printable flare
    p += Pos(0, 0, (z_fl0 + z_fl1) / 2) * Cylinder(3.1, z_fl1 - z_fl0)             # flange
    p += Pos(0, 0, (z_fl1 + top) / 2) * Cylinder(2.05, top - z_fl1)                # shaft
    return chamfer(p.edges().group_by(Axis.Z)[-1], 0.4)


def make_board_ref():
    """Simplified board stack, for fit checks and the assembly STEP only."""
    zt = Z_PCB_TOP
    main = prism(MAIN_OUTLINE, Z_PCB, zt)
    for x, y in CORNER_HOLES + INNER_HOLES:
        main -= cyl(x, y, 1.6, Z_PCB - 1, zt + 1)
    parts = [
        box(20, 42, 63.5, 89.2, zt, zt + 3.2),             # ESP32-S31-WROOM-3
        box(57.5, 72.5, 69.5, 84.5, zt, zt + 1.9),         # microSD
        box(78.9, 87.4, 80.4, 88.9, zt, zt + 6.0),         # camera
        box(99.3, 107.0, 43.9, 52.55, zt, zt + 3.2),       # USB-C UART
        box(99.3, 107.0, 57.7, 66.35, zt, zt + 3.2),       # USB-C power
        box(93.56, 107.56, 11.49, 24.62, zt, zt + 7.0),    # USB-A
        box(95.0, 105.4, 27.5, 40.9, zt, zt + 5.0),        # slide switch
        box(105.4, 109.3, 32.2, 36.2, zt + 1.0, zt + 4.0),  # switch lever
        box(4.2, 9.8, 15.4, 67.8, zt, Z_SUB),              # 2x20 header + socket
    ]
    for x in SPK_X:
        parts.append(box(x - 3.4, x + 3.4, -0.8, 7.5, zt, zt + 5.5))
    for x, y in FUNC_BTNS + SYS_BTNS:
        parts.append(box(x - 2, x + 2, y - 1.5, y + 1.5, zt, zt + BTN_H))
    for x, y in CORNER_HOLES:
        parts.append(cyl(x, y, 2.75, zt, Z_SUB))                             # standoff
        parts.append(cyl(x, y, 3.2, Z_SUB_TOP, Z_SUB_TOP + FRONT_NUT_H))     # front nut + stud
    sub = prism(SUB_OUTLINE, Z_SUB, Z_SUB_TOP)
    cx, cy = LCD_C
    lcd = box(cx - LCD_W / 2, cx + LCD_W / 2, cy - LCD_H / 2, cy + LCD_H / 2, Z_SUB_TOP, Z_LCD)
    return main, fuse(parts), sub, lcd


def build():
    shell, bezel = make_shell(), make_bezel()
    btn_long, btn_short = make_button(1.0), make_button(-1.0)
    main, comps, sub, lcd = make_board_ref()
    return dict(shell=shell, bezel=bezel, button_long=btn_long, button_short=btn_short,
                main=main, comps=comps, sub=sub, lcd=lcd)


def placed_buttons(p):
    z = Z_PCB_TOP + BTN_H
    return ([Pos(x, y, z) * p["button_long"] for x, y in FUNC_BTNS]
            + [Pos(x, y, z) * p["button_short"] for x, y in SYS_BTNS])


if __name__ == "__main__":
    STEP.mkdir(exist_ok=True)
    STL.mkdir(exist_ok=True)
    p = build()

    def named(shape, label, color):
        shape.label, shape.color = label, Color(color)
        return shape

    export_step(p["shell"], STEP / "korvo_case_shell.step")
    export_step(p["bezel"], STEP / "korvo_case_bezel.step")
    export_step(p["button_long"], STEP / "korvo_case_button_long.step")
    export_step(p["button_short"], STEP / "korvo_case_button_short.step")

    board = Compound(label="board_stack_reference", children=[
        named(p["main"], "main_pcb", "darkgreen"), named(p["comps"], "components", "silver"),
        named(p["sub"], "lcd_subboard", "darkgreen"), named(p["lcd"], "lcd", "black")])
    export_step(board, STEP / "korvo_board_stack_reference.step")
    asm = Compound(label="korvo_case_assembly", children=[
        named(p["shell"], "shell", "dimgray"), named(p["bezel"], "bezel", "orange"), board,
        *[named(b, f"button_{i}", "white") for i, b in enumerate(placed_buttons(p))]])
    export_step(asm, STEP / "korvo_case_assembly.step")

    # STLs in print orientation (bezel face down, buttons foot down)
    export_stl(p["shell"], STL / "print_shell.stl", tolerance=0.02, angular_tolerance=0.2)
    export_stl(Pos(0, 0, Z_TOP) * Rot(180, 0, 0) * p["bezel"], STL / "print_bezel.stl",
               tolerance=0.02, angular_tolerance=0.2)
    export_stl(p["button_long"], STL / "print_button_long_x4.stl", tolerance=0.01, angular_tolerance=0.1)
    export_stl(p["button_short"], STL / "print_button_short_x2.stl", tolerance=0.01, angular_tolerance=0.1)

    print(f"case outer: {OX1-OX0:.1f} x {OY1-OY0:.1f} x {Z_TOP:.1f} mm")
    print(f"z levels: pcb {Z_PCB:.1f}  sub {Z_SUB:.1f}  lcd front {Z_LCD:.2f}  split {Z_SPLIT:.2f}  top {Z_TOP:.2f}")
