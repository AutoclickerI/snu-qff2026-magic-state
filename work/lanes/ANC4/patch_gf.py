from pathlib import Path
p=Path(__file__).with_name('gf33.py');s=p.read_text().replace('HERE, "..", "..", "EARLY"','HERE, "..", "EARLY"').replace('HERE, "..", "..", "DR"','HERE, "..", "DR"')
s=s.replace('choices=["sep", "ver", "flag"]','choices=["sep", "ver", "flag", "anc4", "direct4", "redundant7"]')
s=s.replace('open(a.out + ".qasm", "w").write(build(a.variant, a.R, a.vgap, tuple(map(int, a.flag_set.split(","))), tuple(map(int, a.enc_order.split(",")))))','''if a.variant in ("anc4", "direct4", "redundant7"):
        from generate import build as build_checker
        text = build_checker(a.variant, a.R)
    else:
        text = build(a.variant, a.R, a.vgap, tuple(map(int, a.flag_set.split(","))), tuple(map(int, a.enc_order.split(","))))
    open(a.out + ".qasm", "w").write(text)''')
p.write_text(s)
