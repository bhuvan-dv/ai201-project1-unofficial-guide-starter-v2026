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

This is a question-answering system over `campus_life`, a corpus of 88 short,
student-written posts about dorms, dining halls, courses, and campus admin
logistics. It answers concrete, factual questions like "what's the workload
for ENGL 205?", "when do dining jobs get posted?", or "is the housing lottery
actually random?" by pulling the answer from the specific post that covers it
and naming that file as its source. If a question falls outside what the
corpus covers (Mongolia's capital, changing motor oil), it says so instead of
guessing.

## Chunking Strategy

**Chunk size:** 300 characters (ceiling for the fallback only; see below)
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
(183 paragraphs total) showed only 2 exceed 300 characters, so 300 is set
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

**Chunk 1** (source: `dining_north_kitchen.txt#0`, produced by: `chunker.py::split_documents`)

```
North Kitchen. Second-year here. Wait times: none, it seats 60 and is rarely more than half full. The thing worth going for is the rotating regional menu, which changes fortnightly and is ambitious. The thing to know is that closed all summer and during reading week.
```

**Chunk 2** (source: `course_biol_160.txt#2`, produced by: `chunker.py::split_documents`)

```
The one piece of advice: the unit tests come fast, roughly every three weeks; falling behind once is very hard to recover from.
```

**Chunk 3** (source: `course_econ_101.txt#1`, produced by: `chunker.py::split_documents`)

```
Expect 4 hours a week outside class.
```

**Chunk 4** (source: `admin_housing_lottery.txt#0`, produced by: `chunker.py::split_documents`)

```
On the housing lottery. The housing lottery is not random in the way most people assume. Rising sophomores get a number drawn at random, but juniors and seniors are ordered by accumulated credit hours first, and only tie-break randomly.
```

**Chunk 5** (source: `admin_housing_lottery.txt#1`, produced by: `chunker.py::split_documents`)

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
chunks that only matched because they also mention "problem sets"; top-3
would have missed it entirely. I also tried `TOP_K=7`; it didn't recover
anything new (every question's answer chunk already shows up by rank 5 at
worst) and just added two more off-topic chunks per question. Kept `TOP_K=5`.

**My relevance cutoff:** `0.6`. My 5 in-scope questions topped out at 0.460,
my 5 out-of-scope questions bottomed out at 0.780, a wide, clean gap with no
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

**1.** I described my corpus to Claude (short posts, blank-line-separated
paragraphs, one long post (`housing_old_brewhouse.txt`) with four distinct
sub-topics) and asked it to help design and write the chunking function.
The first version paired paragraph-splitting with a raw character-window
fallback for oversized paragraphs. When we printed the actual fallback
output, it had cut a real sentence mid-word ("...beats a se"). I asked how a
sentence-boundary approach would compare instead, and had it add a
sentence-boundary tier before the character-window fallback so cuts land on
whole sentences.

**2.** I asked Claude to lower `TOP_K` from 5 to 3 to cut down on off-topic
chunks riding along with the right one. Instead of just changing it, it
tested the new value against all five of my test questions first: the
correct chunk for my HIST 118 question dropped out of the top 3 entirely,
outranked by two unrelated `course_math_220` chunks that only matched
because they also mention "problem sets." I kept `TOP_K=5` because of that.

**3.** I had Claude check `criteria.md` for problems. It caught a real
inconsistency (criterion 1 said "90%" but my stated target was 4-of-5, which
is 80%) and an unfinished sentence in criterion 2. It refused to write the
actual reasoning for any of the five criteria, pointing to the assignment's
own rule against letting AI write acceptance criteria, so I wrote and fixed
that part myself.

**Unit 2:**

**4.** I asked Claude to hand-score my 15 answers (5 questions × 3 runs)
against each question's `expects` field, since criterion 5's original F1
target had no scorer or labeled dataset behind it anywhere in the repo. It
came back with 4 of 5 questions correct in every run, and flagged that HIST
118 was wrong in all three — not a fluke, since the retrieved chunk had the
full answer every time and the model still only reported half of it. That
finding became my Milestone 3 diagnosis, not something I asked for directly.

**5.** I asked Claude to fix the HIST 118 problem. Instead of touching
retrieval or chunking, it traced the failure to the generation stage first
(the fact was in the cited chunk in every run, so the miss couldn't be
upstream of generation) and added one rule to the grounding prompt requiring
every relevant fact in the excerpt to be reported, not just a literal
yes/no. It re-ran the full test to confirm the other 4 questions didn't
regress before calling it done.

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
| 1. Retrieved chunk contains the answer | 4 of 5 | 5/5 | 5/5 | 5/5 | MET |
| 2. Every answer names a source | 5 of 5 | 5/5 | 5/5 | 5/5 | MET |
| 3. Gate stops out-of-corpus questions | 4 of 5 | 5/5 | 5/5 | 5/5 | MET |
| 4. No chunk under 40 / over 600 chars | 0 violations | 1 under 40 | 1 under 40 | 1 under 40 | MISSED |
| 5. Answers match `expects` (revised from F1) | 4 of 5 | 4/5 | 4/5 | 4/5 | MET |

Criteria 1 and 3 are identical across all three runs because retrieval and
the gate are both deterministic against a fixed index and a fixed cutoff —
only the generated answer's exact wording varies between runs, which is what
criterion 2 (and the hand-scoring behind criterion 5) actually exercises.

Real output, produced by `store.py::search` (criterion 1 — retrieved chunks
for "What's the Workload for ENGL 205?"):

```
0.392  course_engl_205_workload.txt  "Workload for ENGL 205 Writing for the Sciences. People keep asking so: 4 to 5 hours a week..."
0.468  course_phys_130_workload.txt  "Workload for PHYS 130 Mechanics..."
0.478  course_cs_210_workload.txt    "Workload for CS 210 Data Structures..."
```

Real output, produced by `generate.py::answer_from_chunks` (criterion 2 —
run 1, "Where is the health counselling at?"):

```
Counselling is in the same building as the health centre, and it has a wait time of usually three or four days for a first session.

Source: health_center.txt
```

Real output, produced by `gate.py::check` (criterion 3 — "What is the
capital of Mongolia?"):

```
best distance 0.780 is over the 0.6 cutoff — refusing
I don't have enough information about that.
```

Real output, produced by `chunker.py::split_documents` (criterion 4 — the
one chunk that misses the floor):

```
course_econ_101.txt#1  (36 chars)
"Expect 4 hours a week outside class."
```

Real output, produced by `generate.py::answer_from_chunks` (criterion 5 —
run 1, "Are there lots of problem sets in HIST 118 Modern World History
class?", expects: "No problem sets but there's a lot reading about 120
pages per week"):

```
No, there are no problem sets in HIST 118 Modern World History.

Sources: course_hist_118_workload.txt
```

## Verdicts

| # | Criterion | Verdict | How I decided |
|---|---|---|---|
| 1 | Retrieved chunk contains the answer | MET | All 5 questions' retrieved chunks contained the exact `expects` phrase, in all 3 runs (retrieval is deterministic), well clear of the 4-of-5 target. |
| 2 | Every answer names a source | MET | Read all 15 generated answers by hand; every one names at least one source file, in every run. |
| 3 | Gate stops out-of-corpus questions | MET | All 5 `OUT_OF_SCOPE` questions refused, at distances 0.780+ against the 0.6 cutoff, clear of the 4-of-5 target. |
| 4 | No chunk under 40 / over 600 chars | MISSED | One chunk (`course_econ_101.txt#1`, 36 chars) is under the floor. The target has no tolerance built in, so one violation is a miss, not a rounding error. |
| 5 | Answers match `expects` (revised from F1) | MET | Hand-scored all 15 answers against `expects`; 4 of 5 questions correct in every single run. The one consistent miss (HIST 118) is diagnosed below. |

## Diagnoses

**Criterion 4 — MISSED. Stage: chunking.**
`chunker.py::split_documents` treats every blank-line-separated paragraph as
one chunk, with no minimum-length check. `course_econ_101.txt`'s workload
paragraph is naturally a single short sentence — "Expect 4 hours a week
outside class." (36 characters) — so it becomes its own chunk, under the
40-character floor. The chunker has no step that merges a paragraph this
short into a neighbor.

**HIST 118 — a consistent pattern behind criterion 5's one miss. Stage:
generation.**
The retrieved chunk (`course_hist_118_workload.txt`) contains the full
fact in every run — "a lot of reading, about 120 pages a week, but no
problem sets" — so the information was never missing from what the model
saw. But `generate.py::answer_from_chunks`'s grounding prompt only
instructs the model to answer using the documents and name its source; it
never asks for every relevant fact in the chunk to be reported. Because the
question is phrased as a yes/no ("Are there lots of problem sets...?"), the
model answered the literal yes/no and dropped the reading-load clause from
the same sentence it cited — in all 3 runs, not once. That's a systematic
prompt gap, not noise, and it's the basis for this unit's improvement.

I didn't miss any criterion by a wide enough margin to think my targets were
set low overall — criteria 1, 2, and 3 all cleared their targets with margin
to spare (5/5 against 4-of-5 twice, and 5/5 against 5-of-5). Criterion 4 is
the one target that had zero tolerance built in, which is exactly why one
outlier chunk was enough to miss it.

## The Improvement

**What I changed:** Added one rule to `generate.py::GROUNDING_INSTRUCTION`:
if a question can be answered yes/no, the model must still report every
other relevant fact in the same cited excerpt, not just the literal
yes/no.

**Why I picked it:** It follows directly from the HIST 118 diagnosis above —
the chunk had the full fact in every run, but the model was dropping half of
it because nothing in the prompt asked for more than a literal answer to the
literal question.

### Run Log — After

| Criterion | Target | Run 1 | Run 2 | Run 3 | Verdict |
|---|---|---|---|---|---|
| 1. Retrieved chunk contains the answer | 4 of 5 | 5/5 | 5/5 | 5/5 | MET |
| 2. Every answer names a source | 5 of 5 | 5/5 | 5/5 | 5/5 | MET |
| 3. Gate stops out-of-corpus questions | 4 of 5 | 5/5 | 5/5 | 5/5 | MET |
| 4. No chunk under 40 / over 600 chars | 0 violations | 1 under 40 | 1 under 40 | 1 under 40 | MISSED |
| 5. Answers match `expects` (revised from F1) | 4 of 5 | 5/5 | 5/5 | 5/5 | MET |

Real output, produced by `generate.py::answer_from_chunks` (HIST 118, run 1,
after the change):

```
No, there are no problem sets in HIST 118 Modern World History, but there is a lot of reading (about 120 pages a week). This information comes from **course_hist_118_workload.txt**.
```

**Did it help?** Yes. Criterion 5 went from 4/5 to 5/5 in every run — HIST
118 now includes the reading-load fact every single time, and none of the
other 4 questions regressed (still 5/5 source-naming, same retrieval,
same gate behavior, since the change only touched the generation prompt).
Criterion 4 is untouched by this change, since it's a chunking-stage miss
and this fix was at the generation stage — still MISSED, exactly as before.

## What's Still Broken

**Criterion 4 (no chunk under 40 / over 600 chars) is still MISSED after my
fix.** The one violating chunk (`course_econ_101.txt#1`, 36 chars) is
untouched, because this unit's improvement targeted the generation stage
(the HIST 118 fact-dropping problem), and criterion 4's miss is a chunking-
stage problem — different stage, different fix, and this unit's rule is one
change only.

What I'd do about it: add a merge step to `chunker.py::split_documents` — if
a paragraph comes out under some floor (40 characters, or maybe a bit above
it), merge it into the previous chunk instead of leaving it standalone. I
stopped here because it's a single outlier out of 189 chunks, on a question
that isn't even one of my five test questions, and the generation-stage fix
had a clearer, more test-connected payoff this unit.

## Second Improvement (Stretch)

**Declaring this before building it:** attempting the stretch goal — a
second measured improvement. This one is a second chunking-strategy change,
aimed squarely at the one still-open miss above: adding a merge step to
`chunker.py::split_documents` so a paragraph under the 40-character floor
gets merged into the previous chunk instead of standing alone.

**What I changed:** Added `_merge_short_paragraphs` to `chunker.py`. Any
paragraph under `MIN_CHUNK_SIZE` (40 characters) now merges into the
previous chunk in the same document, instead of becoming its own chunk.

**Why I picked it:** It's a direct fix for criterion 4's diagnosis — the
chunker had no minimum-length check, and `course_econ_101.txt`'s "Expect 4
hours a week outside class." (36 chars) was the one paragraph short enough
to hit that gap.

### Run Log — After (second improvement)

| Criterion | Target | Run 1 | Run 2 | Run 3 | Verdict |
|---|---|---|---|---|---|
| 1. Retrieved chunk contains the answer | 4 of 5 | 5/5 | 5/5 | 5/5 | MET |
| 2. Every answer names a source | 5 of 5 | 5/5 | 5/5 | 5/5 | MET |
| 3. Gate stops out-of-corpus questions | 4 of 5 | 5/5 | 5/5 | 5/5 | MET |
| 4. No chunk under 40 / over 600 chars | 0 violations | 0 violations | 0 violations | 0 violations | MET |
| 5. Answers match `expects` (revised from F1) | 4 of 5 | 5/5 | 5/5 | 5/5 | MET |

Real output, produced by `chunker.py::split_documents` (criterion 4, after
the merge):

```
course_econ_101.txt#0  (247 chars)
"ECON 101 Introduction to Economics. Took this last spring. Format is large lecture, 300 people, with small discussion sections. Assessment: two midterms and a final, all multiple choice. Curved, and generously. Expect 4 hours a week outside class."
```

**Did it help?** Yes, cleanly — the corpus went from 189 chunks (1 under the
40-character floor) to 188 chunks (0 violations), and every other criterion
held at exactly the same result as the first improvement's run (same
retrieval distances, same gate behavior, same source-naming, HIST 118 still
correct). All five criteria are now MET, three runs each.

## What I'd Do Differently

Knowing what I know now:

- **Criterion 5** already got revised in `criteria.md` this unit — I'd write
  it as a plain, hand-checkable target from the start next time (something
  like matching against `expects`) instead of an F1 formula with no scorer
  or labeled dataset behind it. It sounded rigorous when I wrote it in unit
  1, but rigor that can't actually be computed isn't rigor.

- **Criterion 4**'s "no chunk under 40 or over 600" has zero tolerance built
  in — one outlier out of 189 chunks was enough to miss it outright. A rate-
  based target (something like "at least 95% of chunks fall between 40 and
  600 characters") would still catch a real problem without a single natural
  short sentence sinking the whole criterion.

- **Criterion 3** cleared with a lot of room to spare — all 5 out-of-scope
  distances landed at 0.780 or higher against a 0.6 cutoff, nowhere near the
  boundary. `hw2.md` is right that clearing everything easily usually means
  the target was safe, not that the system is excellent. I'd tighten this
  one next time, maybe to "5 of 5" instead of "4 of 5," since my corpus and
  cutoff give it that much margin.
