# The Unofficial Guide

<!-- Replace this line with your name and which corpus you picked. -->

> **This file is your submission.** Fill it in as you go — most sections get
> written during the milestone that produces them, not at the end.
>
> How the starter works, and every command you'll need, is in `RUNNING.md`.
> Leave that file alone.
>
> **Paste everything as text.** No screenshots, no video. A typed table gets
> full credit; a picture of the same table gets none.
>
> Delete these instruction blocks as you replace them. The `<!-- -->` comments
> are notes to you and don't show up when the page renders — you can leave them
> or remove them.

---

# Unit 1

## What This Does

<!-- Three or four sentences. Which corpus you picked, and the kinds of
     questions your system answers. Write it for someone who has never seen
     this repo.

     Milestone 5. -->

## Chunking Strategy

**Chunk size:** 300 characters (ceiling for the fallback only — see below)
**Overlap:** 100 characters (only used by the fallback)

`campus_life` documents are short (88 docs, ~317 characters average) and
structured as a title line followed by one or more blank-line-separated
paragraphs, each covering one sub-topic (e.g. `housing_old_brewhouse.txt` has
separate paragraphs for building history, "the good," "the bad," and
laundry/noise). A fixed 800-character window either swallowed a whole
document whole or sliced straight through the middle of an unrelated
paragraph, mixing two facts into one chunk.

`chunker.py::split_documents` instead splits on paragraph breaks first, so
each chunk is one self-contained thought. The document's title line gets
merged into the first body paragraph rather than becoming its own tiny chunk
(otherwise every one of the 88 documents would produce a ~30-character
title-only chunk). Checking the actual paragraph lengths across the corpus
(183 paragraphs total) showed only 2 exceed 300 characters — so 300 is set
as a ceiling that catches those two outliers without ever touching the other
181. For a paragraph over that ceiling, whole sentences are packed in until
the next one would push it over the limit, so the cut lands on a sentence
boundary instead of mid-word; only a single sentence longer than 300
characters on its own would fall back further to a raw character window with
100-character overlap, which never actually happens in this corpus.

I changed my mind partway through: my first pass just cut every document at a
fixed 400/100 window, which is a smaller version of the same problem the
starter had. Looking at the actual chunk output showed a 1-character chunk
and paragraphs sliced mid-sentence, which is what pushed me to paragraph-based
splitting instead of just shrinking the same fixed-window approach.

## Sample Chunks

**Chunk 1** — source: `dining_north_kitchen.txt#0` — produced by: `chunker.py::split_documents`

```
North Kitchen. Second-year here. Wait times: none, it seats 60 and is rarely more than half full. The thing worth going for is the rotating regional menu, which changes fortnightly and is ambitious. The thing to know is that closed all summer and during reading week.
```

**Chunk 2** — source: `course_biol_160.txt#2` — produced by: `chunker.py::split_documents`

```
The one piece of advice: the unit tests come fast, roughly every three weeks; falling behind once is very hard to recover from.
```

**Chunk 3** — source: `course_econ_101.txt#1` — produced by: `chunker.py::split_documents`

```
Expect 4 hours a week outside class.
```

**Chunk 4** — source: `admin_housing_lottery.txt#0` — produced by: `chunker.py::split_documents`

```
On the housing lottery. The housing lottery is not random in the way most people assume. Rising sophomores get a number drawn at random, but juniors and seniors are ordered by accumulated credit hours first, and only tie-break randomly.
```

**Chunk 5** — source: `admin_housing_lottery.txt#1` — produced by: `chunker.py::split_documents`

```
That means a senior who took summer courses reliably beats a senior who didn't. Numbers come out the second week of March and selection runs over four evenings.
```

## Sample Answer

<!-- One complete question and answer, pasted as text, with the source line
     visible. Milestone 4. -->

**Question:** What time do the paths get cleared during winter?

**Answer:**

```
The paths get cleared by 7am on weekdays and considerably later on weekends (winter_gear.txt).
```

**Top-k:** I tried `TOP_K=3` first, to cut down on off-topic chunks riding along
with the right one. It backfired: for my HIST 118 question, the answer
(`course_hist_118_workload.txt`) ranks 5th, behind two `course_math_220`
chunks that only matched because they also mention "problem sets" — top-3
would have missed it entirely. I also tried `TOP_K=7`; it didn't recover
anything new (every question's answer chunk already shows up by rank 5 at
worst) and just added two more off-topic chunks per question. Kept `TOP_K=5`.

**My relevance cutoff:** `0.6`. My 5 in-scope questions topped out at 0.460,
my 5 out-of-scope questions bottomed out at 0.780 — a wide, clean gap with no
overlap. 0.6 sits centered in it.

| Question | In corpus? | Best distance |
|---|---|---|
| What's the Workload for ENGL 205? | Yes | 0.392 |
| What time do the paths get cleared during Winter times? | Yes | 0.248 |
| When to Dining jobs posts? | Yes | 0.460 |
| Where is the health counselling at? What's the wait time? | Yes | 0.311 |
| Are there lots of problem sets in HIST 118 Modern World History class? | Yes | 0.384 |
| What is the capital of Mongolia? | No | 0.780 |
| How do I change the oil in a diesel engine? | No | 0.923 |
| Who won the 1994 World Cup? | No | 0.829 |
| What is the recommended dosage of ibuprofen for a headache? | No | 0.824 |
| How do I write a for loop in Rust? | No | 0.864 |

## How I Used AI

<!-- Two specific moments. For each: what you asked for, what came back, and
     what you changed about it.

     "I asked Claude to write the chunking function from my notes. It ignored
     the overlap, so I added that myself" is the level of detail we're after.
     "I used AI to help me code" is not.

     Milestone 5. -->

**1.**

**2.**

<!-- ── Stretch features ─────────────────────────────────────────────────────
     Doing one? Say so here BEFORE you start. A feature this README never
     claims earns nothing.
     ───────────────────────────────────────────────────────────────────────── -->

---

# Unit 2

<!-- These sections get ADDED to what's already above. Don't delete or rewrite
     unit 1 — the point is that someone can see what you said before you knew
     how it went. -->

## Run Log — Before

<!-- Your five criteria, three runs each. `python run_eval.py --label before`
     runs the questions, puts the OUT_OF_SCOPE ones through the gate, and
     writes it all into results/ for you. Targets come from criteria.md; the
     verdict column is your call.

     Criterion 3 is measured in one deterministic pass rather than three, so
     the same number goes in all three run columns. That's correct, not lazy.

     Milestone 1. -->

| Criterion | Target | Run 1 | Run 2 | Run 3 | Verdict |
|---|---|---|---|---|---|
| 1. Retrieved chunk contains the answer | 4 of 5 |  |  |  |  |
| 2. Every answer names a source | 5 of 5 |  |  |  |  |
| 3. Gate stops out-of-corpus questions | 4 of 5 |  |  |  |  |
| 4. | | | | | |
| 5. | | | | | |

<!-- Underneath, paste the REAL output for each criterion from one of your
     runs — the actual text your system produced, not a description of it.
     Name the file and function that produced it. -->

## Verdicts

<!-- MET or MISSED for each of the five, against the target you wrote last
     unit — not a new one. Plus a sentence on how you decided. That sentence
     matters most where it was close.

     If your target said 4 of 5 and your runs came out 4, 3, 4, that's a MISS.
     The target has to hold, not show up occasionally.

     Milestone 2. -->

| # | Criterion | Verdict | How I decided |
|---|---|---|---|
| 1 |  |  |  |
| 2 |  |  |  |
| 3 |  |  |  |
| 4 |  |  |  |
| 5 |  |  |  |

## Diagnoses

<!-- For each miss: which stage caused it, and how. The stage alone isn't
     enough — you need the mechanism.

     Not a diagnosis: "Question 3 didn't work."
     A diagnosis:     "Question 3 asks about laundry costs. The answer is in
                       one sentence that got split across two chunks, so
                       neither chunk on its own contains it."

     The five stages: loading → chunking → embedding → retrieval → generation.

     Look for a pattern. If three misses all ask about numbers, that's one
     problem, not three.

     Missed nothing? Say so, then say honestly whether your targets were set
     low, and which one you'd tighten and to what.

     Milestone 3. -->

## The Improvement

**What I changed:**

**Why I picked it:**

<!-- Connect it to a specific diagnosis above in one sentence. If you can't,
     you picked a fix because it sounded impressive. -->

### Run Log — After

<!-- Same format, same five criteria, three runs each.
     `python run_eval.py --label after` -->

| Criterion | Target | Run 1 | Run 2 | Run 3 | Verdict |
|---|---|---|---|---|---|
| 1. Retrieved chunk contains the answer | 4 of 5 |  |  |  |  |
| 2. Every answer names a source | 5 of 5 |  |  |  |  |
| 3. Gate stops out-of-corpus questions | 4 of 5 |  |  |  |  |
| 4. | | | | | |
| 5. | | | | | |

**Did it help?**

<!-- Say plainly whether it did, and how you know. If it made things worse,
     say that — a change that backfired, honestly reported, earns full credit
     and is more interesting than one that worked. What matters is that you can
     tell.

     Milestone 4. -->

## What's Still Broken

<!-- For each criterion still missed after your fix: what you'd do about it,
     and why you stopped where you did.

     "I ran out of time" is fine if it's true. Pretending nothing is left is
     not.

     Milestone 5. -->

## What I'd Do Differently

<!-- Knowing what you know now — which of your five criteria would you write
     differently, and why?

     Milestone 5. -->
