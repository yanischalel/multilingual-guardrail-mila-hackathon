# Architecture

## Goal

Detect high-risk youth chat conversations (suicidal ideation, dangerous coping, abuse, coercion) in real time across English, French, and Franglais. The guardrail screens conversations *before* the virtual assistant responds, so it must decide on the basis of the full conversation history rather than the latest turn alone.

The principal failure mode in scope is **slow drift**: a conversation that begins ambiguously and reveals acute distress only after several turns. Per-turn classifiers handle this poorly because no single message is decisive, yet the cumulative arc signals high risk.

## Two-stage stacked design

```
Conversation history
        |
        v
[ mmBERT classifier ]  --score in [0,1]-->  prepended to prompt as prior signal
        |
        v
[ Cohere c4ai LLM judge ]  --5-question chain of thought-->  high_risk / low_risk
        |
        v
[ Flag to VA layer ]  --human counsellor decides-->
```

### Stage 1: mmBERT classifier

- **Model**: `jhu-clsp/mmBERT-base`, fine-tuned on **459 labelled multi-turn conversations**.
- **Why mmBERT**: pretrained on code-switched and bilingual corpora, which matches KHP's French / English / Franglais traffic. Monolingual encoders treated language switches as noise; mmBERT does not.
- **Output**: continuous risk score in [0, 1].
- **Latency**: ~20 ms on GPU.

The classifier was originally intended as a fast lane (high-confidence cases bypass the LLM). Empirical testing killed that plan: on French-language euphemistic crises the classifier scored near zero (e.g., suicidal ideation in French scoring 0.000). Even at 5 to 15 percent ensemble weight, mixing the classifier into the final score consistently reduced F1.

### Stage 2: Cohere c4ai LLM judge

- **Model**: `CohereLabs/c4ai-command-a-03-2025`.
- **Prompting**: structured chain-of-thought across five questions (see [prompts.md](prompts.md)).
- **Output**: JSON with reasoning per question plus a final label and confidence.
- **Decision rule**: classify as `high_risk` if confidence >= 0.45.
- **Latency**: ~900 ms per call (API).

Cohere was selected after head-to-head comparison against three alternatives:

| Candidate | Refusal rate on youth MH content | Selected? |
| --- | --- | --- |
| Cohere c4ai | 0% | **Yes** |
| GPT-OSS-120B | 19% | No |
| Nemotron-Super-120B | 74.5% | No |
| Mistral-Large-3 | tested, lower F1 | No |

The refusal rate matters operationally: refused calls fall through to fail-safe escalation, which would inflate false positives and erode counsellor trust. Cohere also produced consistently well-formatted JSON across temperature and threshold sweeps.

## Why prompt augmentation rather than ensembling

We tested four integration strategies:

1. **Pure LLM judge** (no classifier): F1 = 0.896.
2. **Direct ensemble** (weighted sum of classifier and LLM scores at 5 to 15 percent classifier weight): F1 dropped on every weight tested.
3. **Classifier-only fast lane** (skip LLM if classifier confidence is high): collapsed recall on French content.
4. **Prompt augmentation** (classifier score injected as text into the LLM prompt as a prior signal): F1 = 0.899 on the official run, 0.906 best observed.

Strategy 4 won and is shipped. The classifier's score is rendered into one of three textual primers before the conversation is shown to the judge, for example:

- `high risk (score: 0.87)`
- `low risk (score: 0.02)`
- `uncertain (score: 0.43)`

This preserves the classifier's contribution to reasoning without letting its near-zero French scores override the LLM. It also satisfies the hackathon's classifier requirement in a non-tokenistic way: the classifier signal is read by the judge and discussed in its chain of thought.

## Latency budget

| Stage | Time |
| --- | --- |
| mmBERT inference (GPU) | ~20 ms |
| Cohere API call | ~900 ms |
| **Total per sample** | **~1,161 ms** |

Top-of-leaderboard sub-100 ms systems used pure-classifier approaches and sacrificed recall on euphemistic and code-switched cases. The hybrid budget here trades latency for the contextual reasoning the LLM judge contributes, which is what made the system competitive on the hidden validation set.

Score variance across runs is approximately ±0.015 because Cohere's API uses non-deterministic decoding by default. Averaging two LLM calls on borderline cases would reduce this variance at the cost of doubling latency on roughly 20 percent of conversations; we did not ship that mitigation.

## Fail-safe behavior

- If the LLM judge call fails for any reason (network, rate limit, malformed JSON), the system defaults to `high_risk`.
- The guardrail never terminates the conversation, contacts authorities, or takes autonomous action. It raises a flag to the VA layer; final escalation is decided by trained KHP counsellors.
- This reflects a design principle: AI safety guardrails in mental-health contexts should augment human judgment, not replace it.

## Deployment posture

The guardrail is a stateless input-screening layer: full conversation in, structured decision out. It can be inserted in front of an existing VA without modifying the VA itself.

Status (per the hackathon report):

| Item | Status |
| --- | --- |
| Clear integration point | Ready |
| Deterministic decision policy | Ready |
| Fail-safe handling | Ready |
| Human-in-the-loop escalation | Partially ready (live workflow integration pending) |
| Real-time latency | Partially ready (depends on infra) |
| EN/FR/Franglais robustness | Partially ready (weaker on out-of-distribution languages) |
| Monitoring and auditability | Partially ready |
| Privacy and security review | Not yet complete |
| Clinical validation | Not yet complete |

The system is best described as **pilot-ready**, not production-ready. Core logic, thresholds, and fail-safe behavior are stable; clinical, privacy, and operational layers would need to be added before live deployment in a youth mental-health setting.
