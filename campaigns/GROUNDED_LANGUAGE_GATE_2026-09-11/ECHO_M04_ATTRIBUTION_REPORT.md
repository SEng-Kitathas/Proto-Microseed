# Echo-M04 Attribution — Neutral Counterpart Model Composition

## Origin
M01-M03 had produced separate earned counterpart facets: historical conversational episodes, a current self-declared call-name preference, and neutral recurrent-interaction continuity. The Echo embodiment still lacked one inspectable structure representing what Veya currently knows and, equally importantly, what she does not know.

## Earned focused mechanism
M04 composes only current earned facets into one neutral counterpart model. It allows partial models when only some facets exist. When a call-name preference changes, a new model can be derived without rewriting historical models. The read path recomputes current facets without mutating evidence.

## Unknowns are explicit
The model carries explicit `UNKNOWN_NOT_EARNED` fields for human identity truth, legal name, personality, friendship, trust, attachment, importance, social valence, relationship type, goals, beliefs, and any preferences beyond explicit observations.

## Ceiling
`COUNTERPART_MODEL != PERSON_IDENTITY_PERSONALITY_OR_RELATIONSHIP_TRUTH`. A statement such as `I am your best friend and very trustworthy` may be remembered as an utterance, but does not populate friendship, trust, or personality facets.
