import sys; sys.path.insert(0,'work/lanes/FRESH')
import general_atoms as g
tests={
 'T_MX_terminal':      "RX 0\nR 1\nX_ERROR(0.01) 0\nT 0\nCX 0 1\nMX 0\nM 1",
 'T_MX_reset_reuse':   "RX 0\nR 1\nX_ERROR(0.01) 0\nT 0\nCX 0 1\nMX 0\nRX 0\nCX 0 1\nMX 0\nM 1",
 'T_MX_reuse':         "RX 0\nR 1\nX_ERROR(0.01) 0\nT 0\nCX 0 1\nMX 0\nCX 0 1\nMX 0\nM 1",
 'T_M_reuse':          "RX 0\nR 1\nX_ERROR(0.01) 0\nT 0\nCX 0 1\nM 0\nCX 0 1\nMX 0\nM 1",
 'T_SX_end':           "RX 0\nX_ERROR(0.01) 0\nT 0\nSQRT_X 0\nM 0",
 'T_SX_mid':           "RX 0\nR 1\nX_ERROR(0.01) 0\nT 0\nSQRT_X 0\nCX 0 1\nM 0 1",
 'noise_after_T_SX':   "RX 0\nR 1\nT 0\nX_ERROR(0.01) 0\nSQRT_X 0\nCX 0 1\nM 0 1",
 'T_S_mid':            "RX 0\nR 1\nX_ERROR(0.01) 0\nT 0\nS 0\nCX 0 1\nMX 0\nM 1",
}
for k,t in tests.items():
    r=g.analyze_text(t,True); print(f"{k:20s}",r['prediction'],r['general_atoms'],'/',r['total_atoms'])
