# Wave 1 Runtime

Autonomous Wave 1 is research-only. It may inspect and derive, and EMBODY only bounded research artifacts/experiment specifications. It may not modify `microseed/` production code. Each arm is isolated on its own branch/worktree. Primary cognition uses the qualified offline Qwen2.5-Coder-7B model; CSC shadow audit uses a separate offline Qwen2.5-Coder-1.5B reviewer. Model agreement is not evidence. Results remain research-only until externally reviewed and embodied under explicit later gates.

## Runtime scar 001
The first attempted A_TARGET P01 under job `job-9aa5b7e270bc` was rejected as process-invalid before any arm commit. A punctuation-order validator defect could rewrite NEXT to the seed and permit a self-loop; retrieval also over-weighted arm campaign state. The controller was terminated deliberately. The rejected pass is preserved in `WAVE1_RUNTIME_SCAR_001_INVALID_A_TARGET_P01.json`; it carries no scientific or authority effect. Runtime was hardened before restart.

## Runtime scar 002
Terminating the first scheduler controller did not terminate child arm runner PID 37156. A later hardened controller and child therefore collided with the orphan in A_TARGET, creating impossible mixed pass artifacts. Both trees were killed explicitly and all arm worktrees reset/cleaned. Locked execution scar: `CONTROLLER_TERMINATED != CHILD_RUNNER_TERMINATED`. The committed controller now records each child PID, and the arm runner validates/resumes exact existing pass chains rather than overwriting them.
