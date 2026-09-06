# LANG-C08G — Native B2 Ordered Composition

Status: `C08G_NATIVE_B2_ORDERED_COMPOSITION_REEMBODIED`

## Why C08G exists
Historical C03 had a sound bounded idea—two current independent B1 references can form an order-sensitive tuple—but its operands were old C01/C02 `SIG-X` / `SIG-Y` executable token capabilities. C08F repaired observed-token->native-referent grounding, so C08G asks whether the useful composition mechanism can be rebuilt entirely over that native evidence path.

## Mechanism
1. C08F supplies a durable two-token/two-operational-referent binding earned from paired evidence.
2. Two opaque token observations occur in the current runtime. The caller does not supply token operands or their order to the composition function.
3. C08G selects the latest two current-runtime opaque-token observations and preserves their durable append order.
4. Each observed token must map through the C08F binding to a distinct operational referent signature and a current native referent-profile witness.
5. Generic opaque-evidence association currentness is confirmed for each operand.
6. The composition content identity hashes only the ordered operational-referent signatures + arity + operational-equivalence-class scope, not the arbitrary token bytes.
7. The resulting ordered tuple and exact token/profile evidence refs are persisted as evidence with zero authority gain.

## Pressure
XY and YX produce different composition content digests. Duplicate referent operands and unseen token operands fail closed. Restart plus fresh token observations without fresh native referent profiles fails closed; after explicit body reattachment and fresh post-BOOT profiles, XY and YX rederive the same respective composition digests. Token-surface permutation and sensor channel/sign transformations preserve the grounded composition identity.

## Results
- C08G+C08F+historical C03 focused: 7/7 PASS;
- MS2046+C01-C08G language adjacency: 29/29 PASS;
- independent restart/currentness: 15/15 PASS;
- selected positive-path loss mutants: 9/9 killed.

## Authority ceiling
C08G has zero `microseed/` delta. It adds no token capability, grammar registry, predicate/meaning registry, semantic roles, language module, planner, or generic faculty. It earns bounded ordered operational-reference composition only. It does **not** earn grammar, semantic predication, proposition, systematic recombination, language competence, numerical identity, endogenous qualification, tamper-evident ledger sequence, or canon promotion.

`ORDERED_COMPOSITION != SEMANTIC_PREDICATION`.
`BOUNDED_ORDER_SENSITIVITY != SYSTEMATIC_RECOMBINATION`.

## Next
Review whether the next tighter blocker is native relation/composition recombination or organism-owned qualification of the existing token/referent/relation bindings. Do not advance by language-milestone numbering alone.
