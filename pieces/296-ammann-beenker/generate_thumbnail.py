"""Generate thumbnail.svg for the Ammann-Beenker tiling piece."""

import math
import pathlib

DELTA = 1 + math.sqrt(2)
SIZE = 400
CX = SIZE / 2
CY = SIZE / 2
STEPS = 4
# Seed tiles start large; each deflation shrinks by 1/δ.
# After STEPS deflations, final edge ≈ SEED_EDGE / δ^STEPS ≈ 192/34 ≈ 5.6 px.
SEED_EDGE = SIZE * 0.48

BG = "#f5f0e8"
SQ = "#c8882a"
RH = "#3a5a8a"
ST = "#1a1a1a"


def lerp(a, b, t):
    return (a[0] + t * (b[0] - a[0]), a[1] + t * (b[1] - a[1]))


def make_seed(edge):
    tiles = []
    for k in range(8):
        theta = k * math.pi / 4
        a1, a2 = theta, theta + math.pi / 4
        v0 = (0.0, 0.0)
        v1 = (edge * math.cos(a1), edge * math.sin(a1))
        v3 = (edge * math.cos(a2), edge * math.sin(a2))
        v2 = (v1[0] + v3[0], v1[1] + v3[1])
        tiles.append(("R", [v0, v1, v2, v3]))
    return tiles


def add_rhombus(tip, d1, d2, side, out):
    v1 = (tip[0] + d1[0] * side, tip[1] + d1[1] * side)
    v3 = (tip[0] + d2[0] * side, tip[1] + d2[1] * side)
    v2 = (v1[0] + d2[0] * side, v1[1] + d2[1] * side)
    out.append(("R", [tip, v1, v2, v3]))


def inflate_square(v, f, out):
    A, B, C, D = v
    L = math.hypot(B[0] - A[0], B[1] - A[1])
    s = L * f
    ab = ((B[0] - A[0]) / L, (B[1] - A[1]) / L)
    ad = ((D[0] - A[0]) / L, (D[1] - A[1]) / L)

    center = lerp(A, C, 0.5)
    h = s / 2
    sq = [
        (center[0] - h * ab[0] - h * ad[0], center[1] - h * ab[1] - h * ad[1]),
        (center[0] + h * ab[0] - h * ad[0], center[1] + h * ab[1] - h * ad[1]),
        (center[0] + h * ab[0] + h * ad[0], center[1] + h * ab[1] + h * ad[1]),
        (center[0] - h * ab[0] + h * ad[0], center[1] - h * ab[1] + h * ad[1]),
    ]
    out.append(("S", sq))

    bc2 = (-ab[1], ab[0])
    add_rhombus(A, ab, ad, s, out)
    ba = (-ab[0], -ab[1])
    add_rhombus(B, ba, bc2, s, out)
    cb2 = (ab[1], -ab[0])
    cd2 = (-ab[0], -ab[1])
    add_rhombus(C, cb2, cd2, s, out)
    da2 = ((A[0] - D[0]) / L, (A[1] - D[1]) / L)
    dc_v = ((C[0] - D[0]) / L, (C[1] - D[1]) / L)
    add_rhombus(D, da2, dc_v, s, out)


def inflate_rhombus(v, f, out):
    A, B, C, D = v
    L = math.hypot(B[0] - A[0], B[1] - A[1])
    s = L * f

    ab = ((B[0] - A[0]) / L, (B[1] - A[1]) / L)
    ad = ((D[0] - A[0]) / L, (D[1] - A[1]) / L)
    cb = ((B[0] - C[0]) / L, (B[1] - C[1]) / L)
    cd = ((D[0] - C[0]) / L, (D[1] - C[1]) / L)

    Aab = (A[0] + ab[0] * s, A[1] + ab[1] * s)
    Ccb = (C[0] + cb[0] * s, C[1] + cb[1] * s)

    center = lerp(A, C, 0.5)
    acLen = math.hypot(C[0] - A[0], C[1] - A[1])
    bdLen = math.hypot(D[0] - B[0], D[1] - B[1])
    acDir = ((C[0] - A[0]) / acLen, (C[1] - A[1]) / acLen)
    bdDir = ((D[0] - B[0]) / bdLen, (D[1] - B[1]) / bdLen)
    halfAC = (acLen * f) / 2
    halfBD = (bdLen * f) / 2
    rA = (center[0] - acDir[0] * halfAC, center[1] - acDir[1] * halfAC)
    rC = (center[0] + acDir[0] * halfAC, center[1] + acDir[1] * halfAC)
    rB = (center[0] - bdDir[0] * halfBD, center[1] - bdDir[1] * halfBD)
    rD = (center[0] + bdDir[0] * halfBD, center[1] + bdDir[1] * halfBD)
    out.append(("R", [rA, rB, rC, rD]))

    perp_ab = (-ab[1], ab[0])
    dot_check = ad[0] * perp_ab[0] + ad[1] * perp_ab[1]
    sign = 1 if dot_check >= 0 else -1
    sq_A = [
        A,
        Aab,
        (Aab[0] + sign * perp_ab[0] * s, Aab[1] + sign * perp_ab[1] * s),
        (A[0]   + sign * perp_ab[0] * s, A[1]   + sign * perp_ab[1] * s),
    ]
    out.append(("S", sq_A))

    perp_cb = (-cb[1], cb[0])
    dot_check2 = cd[0] * perp_cb[0] + cd[1] * perp_cb[1]
    sign2 = 1 if dot_check2 >= 0 else -1
    sq_C = [
        C,
        Ccb,
        (Ccb[0] + sign2 * perp_cb[0] * s, Ccb[1] + sign2 * perp_cb[1] * s),
        (C[0]   + sign2 * perp_cb[0] * s, C[1]   + sign2 * perp_cb[1] * s),
    ]
    out.append(("S", sq_C))

    ba = (-ab[0], -ab[1])
    bc = ((C[0] - B[0]) / L, (C[1] - B[1]) / L)
    B_opp = (B[0] + ba[0] * s + bc[0] * s, B[1] + ba[1] * s + bc[1] * s)
    B_s1  = (B[0] + ba[0] * s, B[1] + ba[1] * s)
    B_s2  = (B[0] + bc[0] * s, B[1] + bc[1] * s)
    out.append(("R", [B_opp, B_s1, B, B_s2]))

    dc = (-cd[0], -cd[1])
    da = ((A[0] - D[0]) / L, (A[1] - D[1]) / L)
    D_opp = (D[0] + dc[0] * s + da[0] * s, D[1] + dc[1] * s + da[1] * s)
    D_s1  = (D[0] + dc[0] * s, D[1] + dc[1] * s)
    D_s2  = (D[0] + da[0] * s, D[1] + da[1] * s)
    out.append(("R", [D_opp, D_s1, D, D_s2]))


def inflate(tiles):
    out = []
    f = 1.0 / DELTA
    for typ, v in tiles:
        if typ == "S":
            inflate_square(v, f, out)
        else:
            inflate_rhombus(v, f, out)
    return out


def pts(v):
    return " ".join(f"{CX + x:.2f},{CY + y:.2f}" for x, y in v)


def is_visible(v, clip=SIZE / 2 + 4):
    return any(abs(x) < clip and abs(y) < clip for x, y in v)


def main():
    tiles = make_seed(SEED_EDGE)
    for _ in range(STEPS):
        tiles = inflate(tiles)

    sq_polys = []
    rh_polys = []
    for typ, v in tiles:
        if not is_visible(v):
            continue
        poly = f'<polygon points="{pts(v)}"/>'
        (sq_polys if typ == "S" else rh_polys).append(poly)

    lines = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {SIZE} {SIZE}" width="{SIZE}" height="{SIZE}">',
        f'<rect width="{SIZE}" height="{SIZE}" fill="{BG}"/>',
        f'<g fill="{SQ}" stroke="{ST}" stroke-width="0.6" stroke-linejoin="round">',
    ] + sq_polys + [
        "</g>",
        f'<g fill="{RH}" stroke="{ST}" stroke-width="0.6" stroke-linejoin="round">',
    ] + rh_polys + [
        "</g>",
        "</svg>",
    ]

    out = pathlib.Path(__file__).parent / "thumbnail.svg"
    out.write_text("\n".join(lines))
    print(f"Wrote {out} ({len(sq_polys)} squares, {len(rh_polys)} rhombi)")


if __name__ == "__main__":
    main()
