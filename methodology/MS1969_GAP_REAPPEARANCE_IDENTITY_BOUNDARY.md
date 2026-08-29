# MS1969 — Gap Reappearance / Individual Persistence Boundary

Date: 2026-08-29 ET
Status: negative identity boundary; operational re-association survives
Parent: MS1968 `42fc1bfc5f81687262a4cce3481b365e617d1bc1`

## Discriminator
When an operational proto-referent disappears and later reappears with the same affordance-relative signature but no overlap/continuous observation, does signature equality establish that the same individual persisted?

Prewrite:
`SIGNATURE_REASSOCIATION != INDIVIDUAL_PERSISTENCE`.

## Adversarial twin worlds
Reality server:
`research/substrate_shadow/referent_gap_world_server.py`

Scratch:
`scratch/ms1969_gap_reappearance_identity_boundary.py`

Both cases expose the same four sensor channels and action-response dynamics.

### Continuous case
The two evaluator-only latent individuals remain the same across the invisible gap.
Evaluator generation ids remain `(0,0)`.

### Hidden substitution case
During the invisible gap, both evaluator-only individuals are replaced with new generations having the same observable/action-response dynamics.
Evaluator generations change `(0,0) -> (1,1)`.

No substitution marker is exposed to Microseed's operational evidence.

## Result
Durable job:
`job-4a1472ccef91`

Result: `BOUNDARY_CONFIRMED`, rc=0.

In both cases, before and after the gap:
- groups are `(0,1)` and `(2,3)`;
- affordance-relative signatures are exactly:
  - `314f07401e9d3341bb39f1faa422af7708b0ee17990e8210d5f92773872e461b`;
  - `7497dbe27db5f361e8383827ea071b09e347417d71f5c0be44fe55ff71a8959a`.

Thus operational evidence is identical whether evaluator-level individuals persisted or were silently replaced by same-affordance successors.

Earned:
`AFFORDANCE_SIGNATURE_REAPPEARANCE_SUPPORTS_OPERATIONAL_REASSOCIATION_BUT_CANNOT_ESTABLISH_INDIVIDUAL_PERSISTENCE_ACROSS_UNOBSERVED_SUBSTITUTION`.

## Authority ceiling
- operational re-association authority: `AFFORDANCE_RELATIVE_ONLY`;
- individual persistence authority: NONE;
- numerical identity authority: NONE;
- semantic reference authority: NONE;
- language authority: NONE.

## Consequence
A future language layer may lawfully bind a word to a current operational referent/re-associated affordance class only if its claim scope matches that evidence. It may not silently upgrade a reappearing operational signature into claims such as "the same individual object persisted" without extra continuity evidence.

No Microseed-core mutation is justified.

## Next discriminator
Split/merge ambiguity:
if one operational referent relation branches into two distinguishable current descendants—or two prior relations converge into one current relation—what continuity can be represented without fabricating numerical identity inheritance?
