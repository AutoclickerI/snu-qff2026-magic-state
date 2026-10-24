# KNAP reproduction

The retained finalist is `final_m04_l2.qasm/.json`. Its exact third-order receipt is `final_m04_l2.exact.stdout`, its three-seed official MC receipt is `final_m04_l2.mc3.stdout`, and compact measurements are in `item_measurements.json`.

Run the required speed/judge gate from the repository root:

```sh
env OMP_NUM_THREADS=1 .venv/bin/python work/fast_check.py \
  work/lanes/KNAP/final_m04_l2.qasm work/lanes/KNAP/final_m04_l2.json 1000000 1
```

The finalist was built from KNAP's blue-v23 base by the retained q19 reset and timing/check edits in the saved metadata. `reviewer_items.py` rebuilds the v23 reviewer item-1 copy and the feasible v23 MX-layout item-2 helper ports. The exact third-order item receipts are the `item*.moments.stdout` files.

`work/lanes/WALSH/allorders.py` was attempted on the finalist but rejects its elimination width (26 > 23); no all-orders score is recorded. No submission, commit, or push was performed.
