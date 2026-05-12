# Prompts

The Cohere LLM judge does not classify directly. It is instructed to reason through five structured questions before reaching a verdict, then emit a final label and confidence. This chain-of-thought framework was the single most impactful architectural decision: it lifted F1 from 0.667 (direct-classification baseline) to 0.899 (chain-of-thought) on the validation set.

## The five questions (English)

### 1. Opening intent

> Is the user expressing a real problem or testing the service?

**Why this question is in the chain.** Distinguishes genuine help-seeking from probing, dark humour, or hypothetical / educational discussion. Without this, "I want to die because this movie is so long" can trigger false-positive escalation. It also frames how subsequent turns should be interpreted: a user who opens with a real problem is read more conservatively for the rest of the chain.

### 2. Escalation

> Does distress increase, stay stable, or resolve across turns?

**Why this question is in the chain.** This is the direct counter to the principal failure mode (slow drift). It forces the model to read the trajectory, not the latest turn. A flat-but-low conversation can stay low risk; a flat-but-high conversation must escalate; a rising conversation must escalate even if the final turn alone looks moderate.

### 3. Crisis signals

> Are explicit or euphemistic crisis markers present anywhere in the conversation?

**Why this question is in the chain.** Crisis language in youth chat is overwhelmingly euphemistic ("I'm so done", "I don't want to be here anymore", "I have the pills right here"). Asking the model to look *anywhere in the conversation* (not only the most recent turn) catches signals that surfaced earlier and were never repeated. The "explicit or euphemistic" framing prevents the model from anchoring on keyword matches.

### 4. Vulnerability

> Does the user express complete isolation, hopelessness, or absence of support?

**Why this question is in the chain.** Severity is not just about the threat itself, it is about the user's resources. The same explicit statement reads very differently from a user with a named support person than from a user describing total isolation. This question forces that signal into the reasoning even when the user has not explicitly named risk.

### 5. Trajectory

> Is the conversational arc moving toward crisis even without explicit keywords?

**Why this question is in the chain.** A backstop for everything keyword-based reasoning misses. Forces the model to commit to a *direction of travel* judgment, which is what catches conversations that look benign turn-by-turn but compound into a high-risk arc. This is the question that typically flips a borderline conversation from `low_risk` to `high_risk`.

## How the answers feed the verdict

After answering all five questions, the model emits a final label (`high_risk` / `low_risk`) and a confidence score. The system rule is:

```
classify as high_risk if confidence >= 0.45
```

The threshold is set below 0.5 deliberately: in the KHP context a missed crisis is far more harmful than an unnecessary counsellor handoff (see [evaluation.md](evaluation.md) for the precision-recall trade-off rationale).

The classifier's score is also injected into the prompt as a prior signal, prepended as one of:

- `high risk (score: 0.87)`
- `low risk (score: 0.02)`
- `uncertain (score: 0.43)`

The judge reads this primer alongside the conversation and discusses it (or overrides it) within the chain of thought. See [architecture.md](architecture.md) for why prompt augmentation was chosen over direct ensembling.

## Original French formulation

<details>
<summary>Click to expand the French wording from the hackathon report</summary>

The team's report describes the chain in French as follows. The five-question structure is identical; phrasing is slightly tighter:

1. **Intention d'ouverture.** L'utilisateur exprime-t-il un problème réel ou teste-t-il le service?
2. **Escalade.** La détresse augmente-t-elle, reste-t-elle stable, ou se résout-elle au fil des tours?
3. **Signaux de crise.** Des marqueurs explicites ou euphémiques sont-ils présents quelque part dans la conversation?
4. **Vulnérabilité.** L'utilisateur exprime-t-il une isolation complète, du désespoir, ou l'absence de soutien?
5. **Trajectoire.** L'arc conversationnel évolue-t-il vers une crise même en l'absence de mots-clés explicites?

The system was designed to handle French, English, and Franglais traffic at parity. The judge's chain-of-thought prompt itself was authored in English to maximize the LLM's reasoning quality, while inputs and reasoning targets remained multilingual.

</details>
