# Response Selection Rules — Protocol 6.3

## 1. One turn, one route, one prerecorded response

Each participant turn produces exactly one logical `routeCode`, and that route resolves to exactly one local prerecorded response. The router does not concatenate responses.

## 2. Regular Broad groups

The eight regular Broad groups use the same four information dimensions for each top:

| Dimension | First top | Second top |
|---|---|---|
| Overall appearance/material/physical details/fit | `G01_SHIRT_OVERVIEW` | `G05_HOODIE_OVERVIEW` |
| What the character likes / how it could be worn | `G02_SHIRT_LIKES` | `G06_HOODIE_LIKES` |
| Existing clothes / need filled / likely use | `G03_SHIRT_WARDROBE` | `G07_HOODIE_WARDROBE` |
| Overall replaceability/value | `G04_SHIRT_REPLACEABILITY` | `G08_HOODIE_REPLACEABILITY` |

`G09_CURRENT_PREFERENCE` is a special Broad group for an explicit overall request about what the character personally wants or leans toward. It is not required for final-recommendation eligibility.

## 3. Grounding

- The first top is introduced only after `G01_SHIRT_OVERVIEW` has played.
- The second top is introduced only after `G05_HOODIE_OVERVIEW` has played.
- If a participant asks for a Specific detail before the relevant top has been introduced, the relevant overview route is played first.
- The second-top overview is not played before the first top has been introduced because the recorded wording assumes the first option has already been described.

## 4. Broad Preferred/Alternative switching

For each Broad group, Unity keeps a local selection count `n`:

```text
odd n  -> Preferred
even n -> Alternative
```

The LLM returns only the Broad group code. Unity performs this variant selection locally.

## 5. Specific responses

After the relevant top is grounded, a narrow one-detail question can route directly to its `BC_SPC..` response. If the same item-specific detail is requested for both tops and answering both would require two recordings, use `BC_CTL02_CLARIFY_ITEM`.

Important boundary: `BC_SPC25_HOODIE_MATERIAL_FEEL` is for the material/fabric itself; `BC_SPC26_HOODIE_LINING` is for the inside/interior/lining, even if the participant asks how that inside layer feels.

## 6. Final-recommendation gate

Unity computes `finalRecommendationEnabled`. It becomes `true` only after **all G01-G08** have each been played at least once. G09 and Specific routes are not prerequisites. Once enabled, it remains true.

This gate only controls whether a recommendation can be accepted as final; information gathering remains allowed.

With no information request in the same turn:

- recommendation before enabled -> `BC_CTL07_CONTINUE_ASKING`;
- enabled + hoodie recommendation -> `BC_DEC01_HOODIE`;
- enabled + shirt recommendation -> `BC_DEC02_SHIRT`;
- enabled + both/neither/unclear single choice -> `BC_CTL06_FINAL_CHOICE`.

Either Decision response ends the conversation.
