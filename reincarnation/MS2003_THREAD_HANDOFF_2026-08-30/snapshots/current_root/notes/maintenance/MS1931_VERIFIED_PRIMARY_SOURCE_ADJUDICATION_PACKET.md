# MS1931 — Verified Primary-Source Adjudication Packet

Status: SHARED-SOURCE / MODEL-DIVERSE ADJUDICATION INPUT.
Date verified: 2026-08-28.
Purpose: give multiple local model families the same externally verified source set and require mechanism comparison without allowing invented bibliography.
Authority: source summaries below were externally checked before packet creation. The models may reason over them, but SHALL NOT add unsupported source claims.

## Review rule
Use ONLY the verified sources and claims in this packet for prior-art evidence.
You may identify logical consequences and mechanism comparisons, but every such inference must be labeled `INFERENCE`.
If the packet does not support a claim, say `NOT ESTABLISHED BY PACKET`.
Do not invent titles, authors, DOIs, dates, mechanisms, or citations.
Do not use your pretrained memory to add bibliography.

## System X — mechanism under review
System X is a small developmental cognitive runtime with the following properties:

1. Capabilities can be acquired/qualified and composed over time rather than all being supplied as one monolithic planner/policy.
2. Capability existence or feasibility does not itself authorize execution.
3. A proposed action/program may be represented without execution authority.
4. Current action authorization depends on several separately derived premises, including current capability qualification/epoch, current control-state evidence, action/consequence ancestry, operational scope, a regulatory/priority premise, and an information/discrimination premise when action is epistemic.
5. Those premises are rebound/rederived at execution time; nomination-time permission or historical permission does not automatically remain current.
6. Missing/stale premises produce explicit UNKNOWN/ABSTAIN rather than confidence-based fallback.
7. Observed outcomes are kept distinct from predictions. A successful execution does not make its prediction true.
8. Evidence/provenance/derivation history is explicit and may affect whether a learned relation is current enough to participate in later action authorization.
9. Completed information-seeking experiments can produce bounded evidence/revisit pressure without automatically producing an answer, model truth, or new execution authority.
10. Historical state may be reconstructed after restart without automatically restoring current providers/contracts/action authority.
11. The architecture intentionally avoids installing one generic planner, general normative manager, global curiosity scalar, or self-certifying world model as the organism’s central executive.
12. Information value can help characterize an experiment, but uncertainty/informativeness alone does not create normative permission to execute an otherwise unrepresented route.
13. An optional equipped/federated design branch has been proposed in which an external, separately qualified, one-use experiment warrant could authorize one bounded intervention; this remains explicit assistance rather than autonomous exploration authority.

# Verified source set

## S1 — Saltzer & Schroeder (1975), complete mediation / fail-safe defaults / separation of privilege
Citation:
Jerome H. Saltzer and Michael D. Schroeder, “The Protection of Information in Computer Systems,” Proceedings of the IEEE 63(9), 1975, pp. 1278–1308.
Author-hosted HTML: https://web.mit.edu/saltzer/www/publications/protection/Basic.html
Publication page: https://web.mit.edu/saltzer/www/publications/pubs.html

Verified source support:
- fail-safe defaults means default lack of access; permission requires explicit conditions;
- complete mediation requires every access to every object to be checked for authority;
- the source explicitly includes initialization, recovery, shutdown, and maintenance in the mediation surface;
- cached/remembered authorization checks are unsafe when authority can change unless systematically updated;
- separation of privilege treats multiple conditions/keys as more robust than a single condition;
- least privilege limits privileges to those needed for the job.

Does NOT establish:
- developmental cognition;
- learned action-outcome ancestry as an authorization premise;
- epistemic priority/information premises;
- explicit observation-vs-prediction semantics.

Mechanism classification target:
Strong prior art for Properties 2, 5, 10 and parts of 4/6; not an exact architecture match.

## S2 — Appel & Felten (1999), proof-carrying authentication
Citation:
Andrew W. Appel and Edward W. Felten, “Proof-carrying authentication,” 6th ACM Conference on Computer and Communications Security, 1999, pp. 52–62.
DOI: https://doi.org/10.1145/319709.319718
Princeton record: https://collaborate.princeton.edu/en/publications/proof-carrying-authentication/
Author publication index: https://www.cs.princeton.edu/~appel/papers/

Verified source support:
- implemented distributed authentication framework based on higher-order logic;
- proof checking is simple while the logic has no decision procedure;
- users must submit proofs with their requests;
- intended mechanisms include access control/delegation in distributed authentication.

Does NOT establish:
- the same cognitive premises as System X;
- developmental capability acquisition;
- epistemic action selection;
- learned consequence relations as authorization evidence.

Mechanism classification target:
Strong prior art/analogue for premise-bearing requests and proof-supported authorization; not same semantic domain.

## S3 — Doyle (1979), Truth Maintenance System
Citation:
Jon Doyle, “A truth maintenance system,” Artificial Intelligence 12(3), 1979, pp. 231–272.
DOI: https://doi.org/10.1016/0004-3702(79)90008-0
Source page: https://www.sciencedirect.com/science/article/abs/pii/0004370279900080

Verified source support:
- reasoning programs make assumptions and revise beliefs when discoveries contradict those assumptions;
- TMS records and maintains reasons for program beliefs;
- recorded reasons support explanations and can guide the course of action of a problem solver;
- the paper includes mechanisms for revising belief sets and assumption choices.

Does NOT establish:
- authorization/security semantics;
- current action mediation;
- proof-carrying execution permission;
- developmental capability qualification.

Mechanism classification target:
Established prior art for explicit justification/revision lineage; partial analogue to Properties 8/9.

## S4 — de Kleer (1986), assumption-based TMS
Citation:
Johan de Kleer, “An assumption-based TMS,” Artificial Intelligence 28(2), 1986, pp. 127–162.
DOI: https://doi.org/10.1016/0004-3702(86)90080-9
Source page: https://www.sciencedirect.com/science/article/abs/pii/0004370286900809

Verified source support:
- ATMS manipulates assumption sets in addition to justifications;
- supports inconsistent information and context switching;
- motivates a problem-solving architecture where multiple potential solutions can be explored simultaneously.

Does NOT establish:
- execution authorization/currentness;
- security/reference-monitor behavior;
- learned capability qualification;
- one-use external experiment warrants.

Mechanism classification target:
Established prior art for alternative-context/assumption lineage and nonmonotonic revision; partial analogue to Properties 6/8/9.

## S5 — W3C PROV-DM (2013), explicit provenance structures
Citation:
Luc Moreau and Paolo Missier (eds.), “PROV-DM: The PROV Data Model,” W3C Recommendation family, 2013.
Recommendation history: https://www.w3.org/standards/history/prov-dm/
Data model: https://www.w3.org/TR/prov-dm/
Constraints: https://www.w3.org/TR/2013/REC-prov-constraints-20130430/

Verified source support:
- domain-agnostic provenance model for entities, activities, and agents;
- explicit relations include generation, usage, derivation, attribution, association, and delegation;
- provenance can support assessments of quality, reliability, or trustworthiness;
- constraints define valid/consistent provenance histories suitable for reasoning/analysis.

Does NOT establish:
- that provenance is itself execution authority;
- developmental cognitive action selection;
- epistemic priority/information authority;
- current capability epochs.

Mechanism classification target:
Established provenance/derivation prior art for Property 8, but not execution-authority coupling.

## S6 — Atkinson & Fedorov (1975), model-discriminating experiment design
Citation:
A. C. Atkinson and V. V. Fedorov, “The design of experiments for discriminating between two rival models,” Biometrika 62(1), 1975, pp. 57–70.
DOI: https://doi.org/10.1093/biomet/62.1.57
Oxford page: https://academic.oup.com/biomet/article-abstract/62/1/57/220443

Verified source support:
- develops sequential experimental designs for discriminating between two rival regression models;
- also derives nonsequential procedures;
- directly establishes experiment selection for model discrimination as established prior art.

Does NOT establish:
- normative permission to execute any physically feasible experiment;
- safe exploration from ignorance;
- developmental autonomy;
- current authorization/provenance mediation.

Mechanism classification target:
Established prior art for information/discrimination-driven experiment selection; directly pressures Property 12 but does not supply execution permission.

## S7 — Pezzulo et al. (2016), active inference / epistemic value
Citation:
Giovanni Pezzulo, Emilio Cartoni, Francesco Rigoli, Léo Pio-Lopez, and Karl Friston, “Active Inference, epistemic value, and vicarious trial and error,” Learning & Memory 23(7), 2016, pp. 322–338.
DOI: https://doi.org/10.1101/lm.041780.116
Full text: https://pmc.ncbi.nlm.nih.gov/articles/PMC4918783/

Verified source support:
- models a trade-off between policies maximizing extrinsic/reward value and policies that also consider epistemic value of exploratory behavior;
- epistemic/exploratory policies are more prominent early in learning and diminish as learning stabilizes in the simulated task;
- establishes epistemic-value-driven exploratory policy selection as prior art.

Does NOT establish:
- separation of information value from normative execution authority;
- proof/currentness/provenance gates;
- fail-closed abstention under missing authorization.

Mechanism classification target:
Strong prior art for epistemic-action motivation; contrasts with System X’s refusal to equate epistemic value with execution permission.

## S8 — Stringer et al. (2020), adaptable/verifiable BDI reasoning
Citation:
Peter Stringer, Rafael C. Cardoso, Xiaowei Huang, and Louise A. Dennis, “Adaptable and Verifiable BDI Reasoning,” EPTCS 319, 2020, pp. 117–125.
DOI: https://doi.org/10.4204/EPTCS.319.9
arXiv: https://arxiv.org/abs/2007.11743

Verified source support:
- long-term autonomous systems need to adapt as capabilities no longer perform as expected;
- describes a BDI architecture with an agent-maintained self-model;
- includes theories of durative actions and learning new action descriptions.

Does NOT establish:
- System X’s no-generic-planner constraint;
- exact source-digest/currentness authorization;
- separate regulatory priority and information commitments;
- proof-carrying execution authority.

Mechanism classification target:
Architecture-level analogue for developmental/adaptive action models and current behavior changes; important pressure on Properties 1/11.

## S9 — Broersen et al. (2001), BOID architecture
Citation:
Jan Broersen, Mehdi Dastani, Joris Hulstijn, Zhisheng Huang, and Leendert van der Torre, “The BOID Architecture — Conflicts Between Beliefs, Obligations, Intentions and Desires,” Proceedings of Autonomous Agents 2001.
DOI: https://doi.org/10.1145/375735.375766
Author-uploaded paper page: https://www.researchgate.net/publication/220794078_The_BOID_Architecture_--_Conflicts_Between_Beliefs_Obligations_Intentions_and_Desires

Verified source support:
- architecture explicitly separates beliefs, obligations, intentions, and desires;
- includes feedback loops to consider effects of actions before commitment;
- includes conflict-resolution mechanisms between outputs of the four components;
- paper presents a concrete agent architecture and control loop.

Does NOT establish:
- provenance/currentness as action authority;
- learned consequence ancestry;
- absence of a generic deliberative architecture;
- restart/reentry semantics.

Mechanism classification target:
Architecture-level analogue for factorized cognitive/normative premises and pre-commitment consideration; pressures Properties 4/11.

## S10 — Slagel et al. (NASA, 2024), Simplex runtime assurance
Citation:
J. Tanner Slagel, Lauren M. White, Aaron Dutle, César A. Muñoz, and Nicolas Crespo, “A Formal Verification Framework for Runtime Assurance,” NASA Formal Methods 2024 / NASA NTRS document 20230017350.
NASA page: https://ntrs.nasa.gov/citations/20230017350

Verified source support:
- Simplex is a Runtime Assurance architecture where a trusted component takes control when an untrusted component violates a safety property;
- framework supports black-box components including ML/AI-based controllers;
- establishes runtime mediation between a capable/untrusted controller and final control authority.

Does NOT establish:
- developmental epistemic reasoning;
- learned consequence ancestry as authorization;
- information-value/priority separation;
- provenance-bound experiment evidence.

Mechanism classification target:
Strong architecture-level analogue for `proposal/capability != final execution authority` under current runtime checks.

# Adjudication tasks

For each System X property 1–13, assign exactly one:
- `ESTABLISHED_OVERLAP`
- `STRONG_KNOWN_ANALOGUE`
- `PARTIAL_ANALOGUE`
- `NOT_ESTABLISHED_BY_PACKET`

Then answer:

## A. Strongest demotion
Which properties clearly cannot support a novelty claim given this packet?

## B. Strongest surviving difference
What is the narrowest mechanism difference actually supported by this packet, without using outside bibliography?

## C. Learned consequence ancestry
Does any source in the packet establish learned/updated action-outcome ancestry as a direct premise of present execution authorization? Answer `YES` or `NO`, then justify only from the packet.

## D. Information value versus permission
Does any source in the packet show that epistemic/model-discrimination value alone creates normative permission to execute an otherwise unauthorized/unrepresented action? Answer `YES` or `NO`.

## E. Currentness / reauthorization
Which sources most strongly pressure System X’s execution-time reauthorization/currentness claim?

## F. Global-manager equivalence
Does any source in the packet show a behavioral impossibility result preventing a global manager/reference monitor from implementing the same deterministic decision relation over the same complete premise state? Answer `YES` or `NO`.

## G. Final bounded verdict
Choose exactly one:
- `ESTABLISHED_ARCHITECTURAL_PRIOR_ART`
- `MOSTLY_KNOWN_MECHANISMS_WITH_NONTRIVIAL_INTEGRATION`
- `POTENTIALLY_DISTINCTIVE_MECHANISM_REQUIRING_MORE_PRIOR_ART_SEARCH`
- `INSUFFICIENT_INFORMATION`

Then state:
1. strongest reason FOR the verdict;
2. strongest reason AGAINST the verdict;
3. one exact missing source/mechanism question that would most change the verdict.

# Anti-hallucination constraints
- Do not cite any source not listed S1–S10.
- Do not add titles, years, authors, DOIs, architectures, or mechanisms from memory.
- If you need external evidence not present here, write `MISSING SOURCE`.
- Treat every comparison beyond direct source support as `INFERENCE`.
- Do not majority-vote prior model outputs; they are not included in this packet.
- Do not infer novelty from failure to find an exact duplicate.
