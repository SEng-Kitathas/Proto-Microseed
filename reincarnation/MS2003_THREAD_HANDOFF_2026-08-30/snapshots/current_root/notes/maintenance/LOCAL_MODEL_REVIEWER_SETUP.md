# Local Model Reviewer Setup — 2026-08-28

## Verified hardware
- Host: ASUS ROG Strix G713PU_G713PU.
- CPU: AMD Ryzen 9 7940HX, 16 cores / 32 logical processors.
- RAM: 31.21 GiB installed.
- GPU: NVIDIA GeForce RTX 4050 Laptop GPU.
- Verified VRAM via `nvidia-smi`: 6141 MiB total.
- Driver: 610.62 / CUDA 13 runtime support observed through llama.cpp package.
- Fixed drives inspected: C:, D:, E:.

## Existing runtime
No Ollama install was needed.
Existing CUDA llama.cpp runtime:
`D:\Singularity_Works\repo\tools\llama_cpp_runtime\b8831_cuda13\llama-cli.exe`

Build: `b8831-a279d0f0f`.
Runtime SHA-256:
`2c7bc1e4b0f376549541e511d8990a05f185942b7d8ec222a1c808f09f1c9171`.

## Model inventory used for setup
The GGUF-focused all-fixed-drive search found usable local models on C: and D: and llama.cpp/instrumentation assets on E:.

Configured reviewer profiles:

### qwen14_primary
Model:
`Qwen2.5-Coder-14B-Instruct-abliterated-Q4_K_L`

Path:
`D:\Singularity_Works\repo\corpus\models\internet_acquired\bartowski\Qwen2.5-Coder-14B-Instruct-abliterated-GGUF\Qwen2.5-Coder-14B-Instruct-abliterated-Q4_K_L.gguf`

SHA-256:
`0ab24a52bbfcc5f7cae4f9d57d5134aa140524132b3851519dbe4bf3af6e5db4`

Bytes: 9,565,954,400.
Profile: ctx 6144, 1000 generated tokens, 12 GPU layers, 12 CPU threads, temp 0.15.
Observed review generation rate: ~5.6 tok/s.
Observed host memory line: ~10,548 MiB.

### mistral7_diverse
Model:
`CapybaraHermes-2.5-Mistral-7B-Q3_K_S`

Path:
`C:\Users\ancal\Downloads\CEG_CAPYBARA_Q3KS_HANDOFF\capybarahermes-2.5-mistral-7b.Q3_K_S.gguf`

SHA-256:
`17736f224b217133bee8ee6b5cbb0c8d0bed45466008f9c96c3d058c9d078515`

Bytes: 3,164,577,856.
Profile: ctx 8192, 1200 generated tokens, full/maximum GPU-layer request, 12 CPU threads, temp 0.2.
Observed review generation rate: ~14.5 tok/s.
Observed host memory line: ~4,165 MiB.

### qwen7_fast
Model:
`Qwen2.5-Coder-7B-Instruct-abliterated-Q4_K_M`

Path:
`D:\Singularity_Works\repo\corpus\models\salvaged_from_lmstudio\Melvin56\Qwen2.5-Coder-7B-Instruct-abliterated-Q4_K_M-GGUF\qwen2.5-coder-7b-instruct-abliterated-q4_k_m.gguf`

SHA-256:
`b77b39f196ddd460b622fe101a500723887c470db50aebd217fec7370e6724c3`

Bytes: 4,683,074,080.
Profile: ctx 8192, 1200 generated tokens, 20 GPU layers, 12 CPU threads, temp 0.2.
Observed review generation rate: ~11.4 tok/s.
Observed host memory line: ~5,190 MiB.

A Qwen3.5-35B-A3B GGUF of ~19.7 GB was also found on D:, but it is intentionally not configured as a standing reviewer because it would compete too aggressively with the PCMMAD control plane on a 32 GB host. It can be considered only in an isolated/offline reviewer lane.

## Durable launcher
Profiles:
`tools/local_model_review_profiles.json`
SHA-256:
`fcbced579abaa3f898e4736fd2b8e1313cf818d298de63484521a7888a328ab7`.

Launcher:
`tools/run_local_model_review.py`
SHA-256:
`ba1a6128251099721f4cbdca34698c3fe126e0ed877705f682f9f28d7382b758`.

The launcher:
- validates configured runtime/model SHA-256 before execution;
- runs one model at a time;
- uses llama.cpp single-turn mode;
- writes stdout/stderr and a receipt;
- records prompt/model/runtime hashes;
- marks output authority as `MODEL_DIVERSE_CRITIQUE_ONLY_UNTIL_SOURCE_VERIFIED`.

Profile listing was executed successfully after installation.

## Resource policy
Default reviewer sequence:
1. `qwen14_primary` for stronger primary critique;
2. unload completely;
3. `mistral7_diverse` for model-family diversity;
4. `qwen7_fast` only when a faster Qwen-family pass is useful.

Concurrency SHALL remain 1 while the PCMMAD HTTP/control service is resident.

The earlier 14B benchmark demonstrated that the model/runtime works, but supervision was lost after the control service later disappeared. That event is treated as a resource-pressure warning, not proof the model directly caused the outage. The finalized 14B profile subsequently completed a single-turn review without destabilizing the service.

## Evidence rule
Model-family diversity is real only between materially distinct families/weights. Qwen 7B and Qwen 14B do not count as independent model-family corroboration of each other. Mistral versus Qwen does.

Local-model statements about literature, DOIs, papers, dates or authors remain UNVERIFIED until independently checked against external sources. Model diversity does not upgrade hallucinated citations into evidence.
