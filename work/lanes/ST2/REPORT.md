**New gated finalist `pop36b/zebra/g11_4d68c83e084107`: all-orders 4.113045283023e-05, acceptance 0.501392425; judge PASS, acceptance 0.500720, 2.623s/1e6; XTIM FAST 4.329s/1e6; MC3 pending.**

**New gated finalist `pop36b/zebra/g10_a3319e808875ce`: all-orders 4.114131602295e-05, acceptance 0.501562940; judge PASS, acceptance 0.501025, 2.885s/1e6; XTIM FAST 5.390s/1e6; MC3 pending.**

**New gated finalist `pop36b/zebra/g09_fdb22a16815587`: all-orders 4.114142181469e-05, acceptance 0.501562494; judge PASS, acceptance 0.501360, 3.062s/1e6; XTIM FAST 5.609s/1e6; MC3 pending.**

**New gated finalist `pop36b/zebra/g06_1cd82cef4d5711`: all-orders 4.114998435901e-05, acceptance 0.500898428; judge PASS, acceptance 0.500463, 2.869s/1e6; XTIM FAST 4.819s/1e6; MC3 pending.**

**New gated finalist `pop36b/zebra/g05_68249cb83c3226`: all-orders 4.115155943777e-05, acceptance 0.502727838; judge PASS, acceptance 0.502084, 2.758s/1e6; XTIM FAST 4.532s/1e6; MC3 pending.**

**New gated finalist `pop36b/zebra/g03_443718ea8b4aa8`: all-orders 4.116688653704e-05, acceptance 0.502726396; judge PASS, acceptance 0.501859, 3.005s/1e6; XTIM FAST 4.747s/1e6; MC3 pending.**

**New gated finalist `pop36b/zebra/g02_6c10d584c70ab4`: all-orders 4.117099249547e-05, acceptance 0.502091884; judge PASS, acceptance 0.501981, 3.046s/1e6; XTIM FAST 5.375s/1e6; MC3 pending.**

**New gated finalist `pop36b/zebra/g01_c9fd18bfee1795`: all-orders 4.117109080915e-05, acceptance 0.504038576; judge PASS, acceptance 0.503918, 5.610s/1e6; XTIM FAST 9.984s/1e6; MC3 pending.**

**New gated finalist `pop36b/seed0/winner_Xlong_40_41_42`: all-orders 4.117324036151e-05, acceptance 0.503031129; judge PASS, acceptance 0.502674, 3.106s/1e6; XTIM FAST 4.962s/1e6; MC3 pending.**

**New gated finalist `pop36b/seed1/winner_Xlong_40_41`: all-orders 4.117324067830e-05, acceptance 0.503870118; judge PASS, acceptance 0.502851, 9.209s/1e6; XTIM FAST 17.412s/1e6; MC3 pending.**

# ST2 — v36b population (active)

Base `MAIN/v36b`: all-orders 4.129326085269341e-5, acceptance 0.5014386391688026, 211 CX, R44, 47 native ticks. Candidate floor: **0.5002**. Incumbent reporting threshold v36a: 4.146051958326e-5.

Generation-0 seeds re-derive the previous winners' mechanisms on the actual v36b schedule: later q7–q13 echoes, folded q15–q21 readout, shorter q20–q21 window, guard274/275 measured-init parities, restored initial checks, q1 checked MX at7, q16→q22 Tdag transfer, and acceptance-rich initialization removals. The current q7 interval and q20 tick35 conflict require different windows, not copied tick recipes.

All candidates receive the FRESH static dispatch screen (lane-local copy) before exact all-orders acceptance/loss. Finalists receive unchanged judge1e6, measured XTIM speed and three100M-shot seeds. Populations retain lower-loss and acceptance-rich alternatives, with measured crossovers and two nonimproving generations as the stopping condition.

[Prior v35b report](pop36b/REPORT_before_v36.md). Current artifacts: `pop36b/`; native seed recipes: `pop36_seeds.py`. Only ST2 writes; no submissions, commits, pushes, credentials or collaboration tools.
