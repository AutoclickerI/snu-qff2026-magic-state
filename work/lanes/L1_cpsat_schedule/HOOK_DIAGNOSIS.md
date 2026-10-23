# Obsolete Stop-hook continuation loop

The optimization was completed and its exports audited before this diagnosis.

- The installed hook repository deliberately deleted `hooks/keep_going.py` in commit `31183a75b97cbb0ad6c99f58509ecf06f6fd8832` at 19:34 KST on 2026-10-23.
- The current `/home/jihoon/.codex/hooks.json` contains SessionStart and UserPromptSubmit hooks, with no Stop hook.
- The running turn repeatedly invokes the removed Stop hook. Python's missing-file failure returns exit code 2; Codex's [documented Stop-hook behavior](https://learn.chatgpt.com/docs/hooks#stop) treats that as a request to continue. Stale running-turn hook state is the inferred cause.
- Local Codex 0.163.0 protocol inspection exposes `hooks/list`, but no hook-registry reload method. The current broker permits a thread-specific `turn/interrupt` during its active stream.
- The target was verified from this thread's own rollout and environment: thread `01a167fa-f875-71b1-a5f4-f2ad741c8a7e`, active turn `01a167fa-fb4e-7151-b085-e1636b5e5ac9`.

The corrective action is to interrupt only this completed turn, not restart the shared broker or restore the intentionally removed script. `hook_interrupt_receipt.json` records whether the interrupt was acknowledged. No global hook configuration or scripts were modified. A future session may still require a fresh Codex runtime if its old hook state is retained.
