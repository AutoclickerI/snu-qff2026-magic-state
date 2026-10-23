# PROXY

## Part 1 — completed validation and recorded-proxy rescore

Implementation: `exact_proxy.py`. X and Y transversal probes are evaluated independently. The decoder flips X for nonzero X-stabilizer syndrome, and Y for the XOR of the two nonzero-syndrome flags. `exact_loss` is the corrected second-order DEM proxy; `conditional_loss` evaluates the full independent DEM distribution by Walsh transform, without truncating the noise order. No changes to `work/proxy2.py` or GModel.

Finite-p DEM probabilities contain higher-order conversion terms. Thus the second-order proxy is not an all-orders prediction and differs slightly from the homogeneous physical p² coefficient.

Toy (all 8 physical fault subsets): old 9.99e-07; corrected finite-p second-order 1.998e-06; physical p² coefficient 2e-06; brute-force conditional all-orders 2.00399998397e-06; X/Y all-orders 2.00399998397e-06. The factor-of-two failure is reproduced.

Steane verified-block round: explicitly propagated 919 mutually exclusive Pauli branches from 147 physical channels, enumerated 416,631 cross-channel pairs. First order 0.0; brute physical second order 3.21907260444e-05; X/Y small-p coefficient 3.21907257061e-05 (absolute difference 3.38e-13). This independently validates physical fault labels and excludes same-channel pairs.

### Grid-free rounds

| Case | Old paired X/Z | Correct X/Y through order 2 | First order | Change | All-orders X/Y |
|---|---:|---:|---:|---:|---:|
| DR Steane verified block | 3.232381024e-05 | 3.218624029e-05 | 0.000e+00 | -0.42560% | 3.295058733e-05 |
| DR Steane ver [] | 3.601887929e-04 | 3.494065835e-04 | 2.334e-04 | -2.99349% | 3.493902796e-04 |
| DR Steane ver [[0, 1, 2]] | 2.246217307e-04 | 2.193895871e-04 | 1.334e-04 | -2.32931% | 2.197739156e-04 |
| DR Steane ver [[0, 1, 2], [2, 4, 5]] | 5.558190865e-05 | 5.544433870e-05 | 0.000e+00 | -0.24751% | 5.608762600e-05 |
| ST_TP std teleport=False | 3.232381024e-05 | 3.218624029e-05 | 0.000e+00 | -0.42560% | 3.295058733e-05 |
| ST_TP std teleport=True | 3.232381024e-05 | 3.218624029e-05 | 0.000e+00 | -0.42560% | 3.299546312e-05 |
| ST_TP s7307 teleport=False | 3.538590478e-05 | 3.512457215e-05 | 0.000e+00 | -0.73852% | 3.628781844e-05 |
| ST_TP s7307 teleport=True | 3.538590478e-05 | 3.512457215e-05 | 0.000e+00 | -0.73852% | 3.636960600e-05 |
| ST_TP exact teleport=False | 3.545309256e-05 | 3.518346537e-05 | 0.000e+00 | -0.76052% | 3.737342179e-05 |
| ST_TP exact teleport=True | 3.545309256e-05 | 3.518346537e-05 | 0.000e+00 | -0.76052% | 3.753240703e-05 |
| ST_AV A=std D=None pin=0 | 3.232381024e-05 | 3.218624029e-05 | 0.000e+00 | -0.42560% | 3.290761252e-05 |
| ST_AV A=std D=std pin=0 | 2.898609101e-05 | 2.898609101e-05 | 0.000e+00 | +0.00000% | 2.940067961e-05 |
| ST_AV A=std D=exact pin=0 | 2.898609101e-05 | 2.898609101e-05 | 0.000e+00 | +0.00000% | 2.950298263e-05 |
| ST_AV A=std D=None pin=0.005 | 3.343431859e-05 | 3.329711890e-05 | 0.000e+00 | -0.41036% | 3.574755407e-05 |
| ST_AV A=std D=std pin=0.005 | 2.898609101e-05 | 2.898609101e-05 | 0.000e+00 | +0.00000% | 3.081456831e-05 |
| ST_AV A=std D=exact pin=0.005 | 2.898609101e-05 | 2.898609101e-05 | 0.000e+00 | +0.00000% | 3.113229684e-05 |
| ST_AV A=std D=None pin=0.01 | 3.454855976e-05 | 3.441173159e-05 | 0.000e+00 | -0.39605% | 3.999270946e-05 |
| ST_AV A=std D=std pin=0.01 | 2.898609101e-05 | 2.898609101e-05 | 0.000e+00 | +0.00000% | 3.354668696e-05 |
| ST_AV A=std D=exact pin=0.01 | 2.898609101e-05 | 2.898609101e-05 | 0.000e+00 | +0.00000% | 3.418969552e-05 |
| ST_AV A=std D=None pin=0.02 | 3.678839285e-05 | 3.665231148e-05 | 0.000e+00 | -0.36990% | 5.458461733e-05 |
| ST_AV A=std D=std pin=0.02 | 2.898609101e-05 | 2.898609101e-05 | 0.000e+00 | +0.00000% | 4.483885982e-05 |
| ST_AV A=std D=exact pin=0.02 | 2.898609101e-05 | 2.898609101e-05 | 0.000e+00 | +0.00000% | 4.648225083e-05 |
| ST_AV A=s7307 D=None pin=0 | 3.538590478e-05 | 3.512457215e-05 | 0.000e+00 | -0.73852% | 3.628781844e-05 |
| ST_AV A=s7307 D=std pin=0 | 2.898609101e-05 | 2.898609101e-05 | 0.000e+00 | +0.00000% | 2.943315674e-05 |
| ST_AV A=s7307 D=exact pin=0 | 2.898609101e-05 | 2.898609101e-05 | 0.000e+00 | +0.00000% | 2.953821326e-05 |
| ST_AV A=s7307 D=None pin=0.005 | 3.716101335e-05 | 3.690018312e-05 | 0.000e+00 | -0.70189% | 4.018632568e-05 |
| ST_AV A=s7307 D=std pin=0.005 | 2.898609101e-05 | 2.898609101e-05 | 0.000e+00 | +0.00000% | 3.091652323e-05 |
| ST_AV A=s7307 D=exact pin=0.005 | 2.898609101e-05 | 2.898609101e-05 | 0.000e+00 | +0.00000% | 3.123911253e-05 |
| ST_AV A=s7307 D=None pin=0.01 | 3.894208872e-05 | 3.868176257e-05 | 0.000e+00 | -0.66850% | 4.564087660e-05 |
| ST_AV A=s7307 D=std pin=0.01 | 2.898609101e-05 | 2.898609101e-05 | 0.000e+00 | +0.00000% | 3.375374194e-05 |
| ST_AV A=s7307 D=exact pin=0.01 | 2.898609101e-05 | 2.898609101e-05 | 0.000e+00 | +0.00000% | 3.440431330e-05 |
| ST_AV A=s7307 D=None pin=0.02 | 4.252238320e-05 | 4.226307036e-05 | 0.000e+00 | -0.60983% | 6.312924997e-05 |
| ST_AV A=s7307 D=std pin=0.02 | 2.898609101e-05 | 2.898609101e-05 | 0.000e+00 | +0.00000% | 4.536955846e-05 |
| ST_AV A=s7307 D=exact pin=0.02 | 2.898609101e-05 | 2.898609101e-05 | 0.000e+00 | +0.00000% | 4.702778397e-05 |
| ST_AV A=exact D=None pin=0 | 3.545309256e-05 | 3.518346537e-05 | 0.000e+00 | -0.76052% | 3.737342179e-05 |
| ST_AV A=exact D=std pin=0 | 2.898609101e-05 | 2.898609101e-05 | 0.000e+00 | +0.00000% | 2.950346388e-05 |
| ST_AV A=exact D=exact pin=0 | 2.898609101e-05 | 2.898609101e-05 | 0.000e+00 | +0.00000% | 2.961215756e-05 |
| ST_AV A=exact D=None pin=0.005 | 3.700449096e-05 | 3.673536474e-05 | 0.000e+00 | -0.72728% | 4.199589099e-05 |
| ST_AV A=exact D=std pin=0.005 | 2.898609101e-05 | 2.898609101e-05 | 0.000e+00 | +0.00000% | 3.113339808e-05 |
| ST_AV A=exact D=exact pin=0.005 | 2.898609101e-05 | 2.898609101e-05 | 0.000e+00 | +0.00000% | 3.146506569e-05 |
| ST_AV A=exact D=None pin=0.01 | 3.856110418e-05 | 3.829248063e-05 | 0.000e+00 | -0.69662% | 4.845968752e-05 |
| ST_AV A=exact D=std pin=0.01 | 2.898609101e-05 | 2.898609101e-05 | 0.000e+00 | +0.00000% | 3.419162229e-05 |
| ST_AV A=exact D=exact pin=0.01 | 2.898609101e-05 | 2.898609101e-05 | 0.000e+00 | +0.00000% | 3.485886270e-05 |
| ST_AV A=exact D=None pin=0.02 | 4.169018779e-05 | 4.142257468e-05 | 0.000e+00 | -0.64191% | 6.887084693e-05 |
| ST_AV A=exact D=std pin=0.02 | 2.898609101e-05 | 2.898609101e-05 | 0.000e+00 | +0.00000% | 4.648647721e-05 |
| ST_AV A=exact D=exact pin=0.02 | 2.898609101e-05 | 2.898609101e-05 | 0.000e+00 | +0.00000% | 4.818333594e-05 |
| DR poc valid verified=False | 2.445716857e-04 | 2.312073439e-04 | 0.000e+00 | -5.46439% | 2.346841988e-04 |
| DR poc valid verified=True | 2.779847224e-04 | 2.779847224e-04 | 0.000e+00 | -0.00000% | 2.875329265e-04 |
| DR clean valid clean_z=False | 1.470398579e-04 | 1.334515606e-04 | 0.000e+00 | -9.24123% | — |
| DR clean valid clean_z=True | 4.797518483e-05 | 4.797518483e-05 | 0.000e+00 | -0.00000% | — |
| DR poc zfirst verified=False | 3.192556042e-03 | 2.407668882e-03 | 2.296e-03 | -24.58491% | 2.409436746e-03 |
| DR poc zfirst verified=True | 2.716442061e-04 | 2.716442061e-04 | 0.000e+00 | -0.00000% | 2.767648066e-04 |
| DR clean zfirst clean_z=False | 6.163152767e-05 | 5.788248872e-05 | 0.000e+00 | -6.08299% | — |
| DR clean zfirst clean_z=True | 4.493980776e-05 | 4.493980776e-05 | 0.000e+00 | -0.00000% | — |
| DR hybrid zfirst z=pair | 7.479463884e-05 | 7.016200327e-05 | 0.000e+00 | -6.19381% | — |
| DR hybrid zfirst z=cat1 | 5.445282247e-05 | 5.445282247e-05 | 0.000e+00 | +0.00000% | — |
| DR Steane single W3[0] | 2.246217307e-04 | 2.193895871e-04 | 1.334e-04 | -2.32931% | 2.197739156e-04 |
| DR Steane single W3[1] | 2.246913467e-04 | 2.194369347e-04 | 1.334e-04 | -2.33850% | 2.198574604e-04 |
| DR Steane single W3[2] | 3.195812793e-04 | 3.108099412e-04 | 2.334e-04 | -2.74463% | 3.113030347e-04 |
| DR Steane single W3[3] | 1.901329397e-04 | 1.861155553e-04 | 1.000e-04 | -2.11293% | 1.864808961e-04 |
| DR Steane single W3[4] | 7.849787773e-05 | 7.836030778e-05 | 0.000e+00 | -0.17525% | 7.889834259e-05 |
| DR Steane single W3[5] | 7.852994792e-05 | 7.839237797e-05 | 0.000e+00 | -0.17518% | 7.890529062e-05 |
| DR Steane single W3[6] | 1.723074249e-04 | 1.689934162e-04 | 1.000e-04 | -1.92331% | 1.696458829e-04 |
| DR Steane pair W3[0,3] | 6.338263818e-05 | 6.324506823e-05 | 0.000e+00 | -0.21705% | 6.380952683e-05 |
| DR Steane pair W3[0,4] | 5.670850251e-05 | 5.657093256e-05 | 0.000e+00 | -0.24259% | 5.722711931e-05 |
| DR Steane pair W3[0,5] | 6.425803282e-05 | 6.412046287e-05 | 0.000e+00 | -0.21409% | 6.465076678e-05 |
| DR Steane pair W3[0,6] | 5.558190865e-05 | 5.544433870e-05 | 0.000e+00 | -0.24751% | 5.608762600e-05 |
| DR Steane pair W3[1,4] | 6.660984758e-05 | 6.647227763e-05 | 0.000e+00 | -0.20653% | 6.700083922e-05 |
| DR Steane pair W3[1,6] | 5.711145700e-05 | 5.697388705e-05 | 0.000e+00 | -0.24088% | 5.760531415e-05 |
| DR Steane pair W3[2,3] | 1.697714478e-04 | 1.662812185e-04 | 1.000e-04 | -2.05584% | 1.667653732e-04 |
| DR Steane pair W3[2,6] | 1.525097627e-04 | 1.497229091e-04 | 1.000e-04 | -1.82733% | 1.503983042e-04 |
| DR poc xlast verified=False | 1.008095561e-03 | 9.581718083e-04 | 7.661e-04 | -4.95228% | 9.603423946e-04 |
| DR poc xlast verified=True | 2.921313668e-04 | 2.921313668e-04 | 0.000e+00 | -0.00000% | 2.991676773e-04 |
| DR clean xlast clean_z=False | 9.473570911e-05 | 8.569319407e-05 | 0.000e+00 | -9.54499% | — |
| DR clean xlast clean_z=True | 4.839199802e-05 | 4.839199802e-05 | 0.000e+00 | +0.00000% | — |
| ST_AV A=std D=std pin=0 gap=2 | 2.898609101e-05 | 2.898609101e-05 | 0.000e+00 | +0.00000% | 2.974165505e-05 |
| ST_AV A=std D=std pin=0 gap=6 | 2.898609101e-05 | 2.898609101e-05 | 0.000e+00 | +0.00000% | 3.084699944e-05 |
| ST_AV A=std D=exact pin=0 gap=2 | 2.898609101e-05 | 2.898609101e-05 | 0.000e+00 | +0.00000% | 2.984578068e-05 |
| ST_AV A=std D=exact pin=0 gap=6 | 2.898609101e-05 | 2.898609101e-05 | 0.000e+00 | +0.00000% | 3.095718494e-05 |
| ST_AV A=s7307 D=std pin=0 gap=2 | 2.898609101e-05 | 2.898609101e-05 | 0.000e+00 | +0.00000% | 2.977458083e-05 |
| ST_AV A=s7307 D=std pin=0 gap=6 | 2.898609101e-05 | 2.898609101e-05 | 0.000e+00 | +0.00000% | 3.088161951e-05 |
| ST_AV A=s7307 D=exact pin=0 gap=2 | 2.898609101e-05 | 2.898609101e-05 | 0.000e+00 | +0.00000% | 2.988200918e-05 |
| ST_AV A=s7307 D=exact pin=0 gap=6 | 2.898609101e-05 | 2.898609101e-05 | 0.000e+00 | +0.00000% | 3.099635434e-05 |
| ST_AV A=exact D=std pin=0 gap=2 | 2.898609101e-05 | 2.898609101e-05 | 0.000e+00 | +0.00000% | 2.984654800e-05 |
| ST_AV A=exact D=std pin=0 gap=6 | 2.898609101e-05 | 2.898609101e-05 | 0.000e+00 | +0.00000% | 3.095868820e-05 |
| ST_AV A=exact D=exact pin=0 gap=2 | 2.898609101e-05 | 2.898609101e-05 | 0.000e+00 | +0.00000% | 2.995912473e-05 |
| ST_AV A=exact D=exact pin=0 gap=6 | 2.898609101e-05 | 2.898609101e-05 | 0.000e+00 | +0.00000% | 3.108244477e-05 |

All-orders columns are explicitly evaluated only up to 21 parity bits; the larger cat circuits use the requested order-2 comparison. No all-orders claim is made for those rows. The `DR Steane ver []` row has nonzero first order; its cost includes the conditional normalization correction.

### Stored schedules and MC ranking

| Source | Old | Correct X/Y | MC mean over recorded variants |
|---|---:|---:|---:|
| res_A1_9_1792746145.json#0 | 1.143743174e-04 | 1.143743174e-04 | 1.252737686e-04 |
| L1_interleaved_top5_snapshot.json#4 | 1.133717995e-04 | 1.133717995e-04 | 1.250213492e-04 |
| L1_interleaved_top5_snapshot.json#0 | 1.127439921e-04 | 1.127439921e-04 | 1.239121450e-04 |
| res_A1_9b_1792752451.json#0 | 1.097989710e-04 | 1.097989710e-04 | 1.221325683e-04 |

Across all 14 stored three-seed MC means: Spearman old=0.834796, corrected=0.834796; Kendall old=0.694093, corrected=0.694093. Across the four distinct schedule sources, both Spearman correlations are 1. The corrected proxy does **not** improve the measured ranking on this dataset. It cannot distinguish different pre-stage ALAP schedules sharing a final cycle.

### Every distinct stored GModel schedule

| Source | Variant | Old | Correct X/Y |
|---|---|---:|---:|
| res_A1_10_1792746278.json#0 | A1 | 1.143743174e-04 | 1.143743174e-04 |
| res_A1_10_1792746278.json#1 | A1 | 1.143743174e-04 | 1.143743174e-04 |
| res_A1_10_1792746278.json#2 | A1 | 1.148545756e-04 | 1.148545756e-04 |
| res_A1_10_1792746278.json#3 | A1 | 1.173900784e-04 | 1.173900784e-04 |
| res_A1_10_1792746278.json#4 | A1 | 1.173900784e-04 | 1.173900784e-04 |
| res_A1_10_1792746278.json#5 | A1 | 1.222911625e-04 | 1.222911625e-04 |
| res_A1_10_1792746278.json#6 | A1 | 1.230543717e-04 | 1.230543717e-04 |
| res_A1_10_1792746278.json#7 | A1 | 1.239198484e-04 | 1.239198484e-04 |
| res_A1_10b_1792752930.json#0 | A1 | 1.097989710e-04 | 1.097989710e-04 |
| res_A1_10b_1792752930.json#1 | A1 | 1.097989710e-04 | 1.097989710e-04 |
| res_A1_8b_1792753307.json#4 | A1 | 1.100706597e-04 | 1.100706597e-04 |
| res_A1_8b_1792753307.json#5 | A1 | 1.163018665e-04 | 1.163018665e-04 |
| res_A1_9_1792746145.json#0 | A1 | 1.143743174e-04 | 1.143743174e-04 |
| res_A1_9_1792746145.json#1 | A1 | 1.143743174e-04 | 1.143743174e-04 |
| res_A1_9_1792746145.json#2 | A1 | 1.171459996e-04 | 1.171459996e-04 |
| res_A1_9_1792746145.json#3 | A1 | 1.199541729e-04 | 1.199541729e-04 |
| res_A1_9_1792746145.json#4 | A1 | 1.214330108e-04 | 1.214330108e-04 |
| res_A1_9_1792746145.json#5 | A1 | 1.232773840e-04 | 1.232773840e-04 |
| res_A1_9_1792746276.json#0 | A1 | 1.143743174e-04 | 1.143743174e-04 |
| res_A1_9_1792746276.json#1 | A1 | 1.154823895e-04 | 1.154823895e-04 |
| res_A1_9_1792746276.json#2 | A1 | 1.172530029e-04 | 1.172530029e-04 |
| res_A1_9_1792746276.json#3 | A1 | 1.172530029e-04 | 1.172530029e-04 |
| res_A1_9_1792746276.json#4 | A1 | 1.212389729e-04 | 1.212389729e-04 |
| res_A1_9_1792746276.json#5 | A1 | 1.215811366e-04 | 1.215811366e-04 |
| res_A1_9_1792746276.json#6 | A1 | 1.216881398e-04 | 1.216881398e-04 |
| res_A1_9_1792746276.json#7 | A1 | 1.249389002e-04 | 1.249389002e-04 |
| res_A1_9b_1792752455.json#0 | A1 | 1.102925821e-04 | 1.102925821e-04 |
| res_A1_9b_1792752455.json#1 | A1 | 1.158231335e-04 | 1.158231335e-04 |
| res_A1_9b_1792752455.json#2 | A1 | 1.162766846e-04 | 1.162766846e-04 |
| res_A1_9b_1792752460.json#3 | A1 | 1.100706597e-04 | 1.100706597e-04 |
| res_A1_9b_1792752460.json#4 | A1 | 1.148606404e-04 | 1.148606404e-04 |
| res_A1_9b_1792752460.json#5 | A1 | 1.148606404e-04 | 1.148606404e-04 |
| res_A1_9b_1792752903.json#2 | A1 | 1.102925821e-04 | 1.102925821e-04 |
| res_A1_L1map.json#0 | A1 | 1.128972613e-04 | 1.128972613e-04 |
| res_A1_L1map.json#1 | A1 | 1.131912197e-04 | 1.131912197e-04 |
| res_A1_L1map.json#2 | A1 | 1.132911787e-04 | 1.132911787e-04 |
| res_A1_L1map.json#3 | A1 | 1.135657654e-04 | 1.135657654e-04 |
| res_A1_L1map.json#4 | A1 | 3.173007646e-04 | 3.119515584e-04 |
| res_A2_9_1792746143.json#0 | A2 | 1.217975691e-04 | 1.217975691e-04 |
| res_A2_9_1792746143.json#1 | A2 | 1.233605649e-04 | 1.233605649e-04 |
| res_A2_9_1792746143.json#2 | A2 | 1.240844403e-04 | 1.240844403e-04 |
| res_A2_9_1792746143.json#3 | A2 | 1.325261350e-04 | 1.325261350e-04 |
| res_A2_9_1792746143.json#4 | A2 | 1.325261350e-04 | 1.325261350e-04 |
| res_A2_9_1792746143.json#5 | A2 | 1.356330613e-04 | 1.356330613e-04 |
| res_A2_9b_1792752907.json#0 | A2 | 1.196235204e-04 | 1.196235204e-04 |
| res_A2_9b_1792752907.json#1 | A2 | 1.213527857e-04 | 1.213527857e-04 |
| res_A2_9b_1792752907.json#2 | A2 | 1.226660305e-04 | 1.226660305e-04 |
| res_A3_9_1792746145.json#0 | A3 | 1.206976833e-04 | 1.206976833e-04 |
| res_A3_9_1792746145.json#1 | A3 | 1.226160885e-04 | 1.226160885e-04 |
| res_A3_9_1792746145.json#2 | A3 | 1.230548222e-04 | 1.230548222e-04 |
| res_A3_9_1792746145.json#3 | A3 | 1.313368614e-04 | 1.313368614e-04 |
| res_v6_8b_1792753306.json#0 | v6 | 1.127439921e-04 | 1.127439921e-04 |

Additional complete small-round validation: an ideal verified Steane round plus three physical tail depolarizing channels, all 64 physical branches: brute conditional loss 1.66562962963e-06; all-orders X/Y 1.66562962962e-06; acceptance 1.

### Explicit v11/v12-family GModel comparison

| Schedule | Old | Corrected order 2 | All orders | Recorded full-circuit MC |
|---|---:|---:|---:|---:|
| v11 | 1.097989710e-04 | 1.097989710e-04 | 1.105244710e-04 | 1.2189000e-04 |
| v12_normalized | 1.106555318e-04 | 1.106555318e-04 | 1.113807726e-04 | 1.1327000e-04 |

The v11 MC is the FINDINGS mean over 100 redraws; v12 is the requested three-seed mean. GModel normalizes the initial Bell preparations and resets retained ancillas, so mapping the actual v12 coupling schedule into GModel discards its boundary improvements. Both old and corrected GModel proxies rank this comparison backwards. The X/Y correction fixes ambiguous logical-fault pairing; it does not repair an incomplete full-circuit noise boundary. `reference_cycle_proxy.json` uses the actual v12 boundary with an ideal noiseless pre-stage.

The additional verifier scan explicitly rejected 15 recipes whose verification gates overlap their encoders or whose probes are nondeterministic; details are in `part1_infeasible.json`. The old 6.72e-5 two-verifier summary has no uniquely recorded builder parameters; the report instead enumerates all reproducible default single- and double-verifier recipes, including the later recorded 5.55819e-5 best pair. No matching recipe is invented for that older rounded summary.

The all-orders calculation also qualifies the ST_AV claim: with standard A and D, its order-2 value stays 2.8986091e-5 as input noise increases from 0 to 0.02, but its exact all-orders loss increases from 2.94006796e-5 to 4.48388598e-5. Likewise, teleport and star rounds agree at order 2 but differ slightly at higher orders. These are finite-noise effects, not new first-order failures.

## Part 2 — completed support filtering and physical schedule search

All 28 independent X triples and 28 independent Z triples were enumerated: 784 pairs. At fixed data positions, both the original layout and A1/v12 layout admit only the original support pair. Every other weight-four Z support lacks an adjacent Bell pair reaching its four data cells. Allowing one-hop X leaves adds no new support pair.

Extended filter: 5,460 collision-free one-hop data placements; 16 admit an adjacent Bell Z basis. Pair counts are **784 → 28 after Z adjacency → 1 after X adjacency → 1 after distinct ancilla availability → 1 after `relaxed.valid()` and Stim determinism**. The surviving pair is the original basis, with 16 physical placements. This is an exhaustive statement only for adjacent Bell pairs, one-hop X leaves and one fresh-cell hop per data qubit; arbitrary longer routes and Z-cat extensions are untested.

Searched 1184 configurations (all 16 placements, all eight Bell readout orientations and optional X leaves). 1184 produced circuits passing the full judge at 10^6 shots; all saved candidate QASM/JSON pairs contain this receipt. CP-SAT generates starts, then 3,000-proposal anneals use the exact all-orders Clifford X/Y objective. An additional 48 chains, 12,000 proposals each, refine the submitted v12 schedule and its best first continuation. Rejected nondeterministic schedules are explicitly excluded; no detector XOR relabel is counted as a support change.

The submitted `v12_L5lns12_r86.qasm` is the prefix source. Its 170 literal pre-stage lines, representing 137 native operations, keep their original native times. In particular, the three retained X measurements remain intact. Commuting Z couplings may precede final pre-stage T† gates exactly as in v12. Every saved candidate audits these native times and passes the real judge, including grid adjacency. The surrogate commutes the noiseless pre-stage earlier and omits its noise; only full-circuit exact/MC results establish performance.

All 48 refinement chains converged to the same emitted schedule. To test whether the surrogate missed a better nearby full circuit, 1,915 single-node shifts, conflict swaps and two-node swaps were enumerated. All 54 distinct feasible/deterministic neighbors passed the judge and were evaluated with the full second-order evaluator; none beat the winner. `neighbor_049` returns the original v12 physical schedule (its emitted gate order and classical bit numbering differ).

### Full-circuit finalists

| Candidate | Exact order 2 | Exact through order 3 | exp(-A1) | First order |
|---|---:|---:|---:|---:|
| cycle_0058 | 1.11331000e-04 | 1.13463000e-04 | 0.69052 | 1e-19 |
| neighbor_049 | 1.12195000e-04 | 1.14313000e-04 | 0.69052 | 1.4e-19 |
| reference_r86 | 1.12195000e-04 | 1.14313000e-04 | 0.69052 | 1.4e-19 |
| neighbor_006 | 1.12768000e-04 | 1.14933000e-04 | 0.69006 | 1e-19 |
| neighbor_048 | 1.13875000e-04 | 1.15925000e-04 | 0.69098 | 1e-19 |

The unmodified `EVAL/exact2.py --third` CLI generated each `.third.log`; only wrapper cache paths and worker counts were configured. Order-2 screening uses the same evaluator with batched expectation caching.

### Three-seed official MC

| Candidate | seed 0 | seed 1000 | seed 2000 | Mean ± MC SEM | Δ vs 1.1327e-4 | Acceptance mean |
|---|---:|---:|---:|---:|---:|---:|
| cycle_0058 | 1.146570393e-04 | 1.119603538e-04 | 1.136162587e-04 | 1.134112173e-04 ± 6.3e-07 | +0.125% | 0.6904811 |
| neighbor_049 | 1.117111670e-04 | 1.155311107e-04 | 1.132874770e-04 | 1.135099182e-04 ± 6.3e-07 | +0.212% | 0.6904829 |
| neighbor_006 | 1.149740468e-04 | 1.141188486e-04 | 1.153683680e-04 | 1.148204211e-04 ± 6.3e-07 | +1.369% | 0.6900340 |

Each MC row uses `fast_check.check(text, data_qubits, shots=10**8, seed=s, procs=N)` for seeds 0/1000/2000: N=3 on zebra for `cycle_0058`, N=15 in owl Docker for the two neighbors. Separate `tprep.check` receipts at 10^6 shots are retained. No credentials were read and no submissions were made. All created scripts, candidates, caches and receipts are confined to this lane.

### Result and limits

The best new schedule moves **`cx q[4],q[10]` from native step 37 to 35**, commuting it ahead of the fixed `tdg q[4]` at step 36. Everything in the pre-stage remains fixed. Its measured three-seed mean is **1.134112173e-04**, +0.125% versus the requested 1.1327e-4 target, so **there is no demonstrated improvement over v12**. The difference is smaller than MC uncertainty. Its seed-0 score is 1.146570393e-04, versus submitted r86's 1.126891519e-4. Third order predicts a small physical gain, which these three seeds do not establish.

`cycle_0058` and `neighbor_006` are the two best distinct new physical schedules by third order. The better-ranked `neighbor_049` is the original physical v12 schedule re-emitted with different simultaneous-gate order and classical labels, and is included as a baseline control, not claimed as a new cycle. The original r86 remains the preferred submitted text on the requested metric.

The retained five QASM/JSON pairs were rechecked at 10^6 shots and audited against their saved schedule and the submitted prefix (`artifact_audit.json`). All 2,564 other generated candidate files are preserved in the byte-verified `generated_candidates.tar.gz`; screening results remain directly readable. Searches are heuristic over schedules and exhaustive only over the stated local geometry/filter model. Longer routing, Z-only cat extensions and global schedule optimality remain unverified.

Primary implementation sources: [judge](../../../docs/reference/judge.md), [paired proxy](../../proxy2.py), [GModel](../me_layout/gmodel.py), [ordering validity](../DR/relaxed.py), [full exact evaluator](../EVAL/exact2.py), and [submitted v12](../../submissions/v12_L5lns12_r86.qasm). Results above are local measurements or enumerations; no literature-only performance claim is used.

Evidence: `part1_validation.json`, `small_validation.json`, `part1_rows.json`, `schedules_rescored.json`, `topology.json`, `relocations.json`, `prefix_audit.json`, `search_results_*.json`, `refine_results_*.json`, candidate `.json`, `.screen.json`, `.third.log` and `.mc.json`.
