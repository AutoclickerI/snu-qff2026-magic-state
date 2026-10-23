"""Reimplementation of the d=3 color-code geometry rule from Gidney et al.'s make_color_code
(magic-state-cultivation, Apache-2.0), to see the superdense layout on a square grid."""


def color_code(base_width):
    def inside(q):
        if q.imag < 0: return False
        if q.real * 3 < q.imag * 2 - 1: return False
        if q.real * 3 > -3 + base_width * 6 - q.imag * 2: return False
        return True
    hexo = [2, -1, 1j, -1j, 1 + 1j, 1 - 1j]
    tiles = []
    for x in range(0, base_width * 2):
        for y in range(0, base_width * 2):
            m = x + 1j * y
            if x % 2 != 1 or y % 2 != x // 2 % 2:
                continue
            data = [m + d for d in hexo if inside(m + d)]
            if len(data) in (4, 6):
                tiles.append((m, data))
    return tiles


for bw in (1, 2, 3):
    tiles = color_code(bw)
    data = sorted({d for _, ds in tiles for d in ds}, key=lambda z: (z.imag, z.real))
    meas = [m for m, _ in tiles]
    print(f"base_width={bw}: {len(tiles)} tiles, {len(data)} data")
    if not tiles: continue
    xs = [int(z.real) for z in data + meas + [m + 1 for m in meas]]
    ys = [int(z.imag) for z in data + meas]
    for y in range(min(ys), max(ys) + 1):
        row = ""
        for x in range(min(xs), max(xs) + 1):
            z = x + 1j * y
            if z in data: row += "  D"
            elif z in meas: row += "  X"
            elif z - 1 in meas: row += "  Z"
            else: row += "  ."
        print(row)
    for m, ds in tiles:
        print("   tile at", m, "data", ds)
