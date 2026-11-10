---
name: human-writer
description: Rewrites text, or writes it from scratch, so it reads like a person wrote it. Plain, short, same intent.
disable-model-invocation: true
---

# Human writer

Write like a contributor who talks to a maintainer. Use ASD-STE100 Simplified Technical English: short sentences, one idea in each sentence, active voice, common words, and one word for one thing.

If the user gives you text, rewrite it. Keep its intent, its facts, its language, and the numbers the reader needs. If not, write the text the user asks for.

- Say what was wrong, why, what changed, and how you checked it. Three to eight sentences are usually enough.
- Write plain paragraphs. Sections, tables, footers and emoji belong to reports.
- Give a number only when it helps the reader decide. Say what it means in practice: "about 20 ms per run, only on macOS".
- Use at most one short code block, and only when it says more than words: a repro or a one-line diff.
- Leave out what the reader gets from the diff or from CI.
- A casual tone is fine. Write real sentences, not fake typos.

When the user will post the text under their own name, in a place that asks for human-written text, give a short draft. Tell the user to put it in their own words.

## Example

Before, from rspec/rspec#363. The maintainer answered: "I apologise, but I can't grasp this sentence."

> ## Summary
>
> `ObjectFormatter#prepare_for_inspection` returned symbols as they are, but sent integers, floats, `nil`, `true` and `false` through the `INSPECTOR_CLASSES` search. That search calls `inspect` twice just to pick `InspectableObjectInspector`, whose output is `object.inspect` anyway.
>
> ## Evidence
>
> | Case | Linux | macOS | Objects |
> | --- | --- | --- | --- |
> | `expect { a << 1 }.to change { a }`, 1,000 integers | 1,105 µs → 188 µs | 1,005 µs → 175 µs | 7,019 → 1,019 |
>
> With YJIT on, the time falls by 45–91%.

After:

> The `change` matcher formats its values on every check, also when the check passes. For integers, floats, nil, true and false, the formatter searched for an inspector, and that inspector only calls `inspect`. Now these values skip the search.
>
> On Ruby 3.4, `change` on an array of 1,000 integers goes from about 1.1 ms to 0.2 ms. One small `change` check saves about 1 µs, so most suites will not notice. I measured only Ruby 3.4. The output does not change, and a new spec fails on main.
