# Acceptance criteria — The Unofficial Guide

Five criteria that say what "working" means for this system, written in unit 1
**before** any results existed.

An acceptance criterion names a target: a number, a count, a rate, or something
a person could plainly observe. *"Retrieval works"* is an opinion. *"For at
least 4 of my 5 test questions, the top results include a chunk containing the
answer"* is a criterion.

Under each one, write a sentence or two on **why that target** and not a
stricter or looser one. A reason that says something about your corpus or your
pipeline earns credit; *"80% seemed reasonable"* does not.

> Missing your own targets next unit costs you nothing. Setting a target so
> easy you can't miss it does.

---

## 1. Retrieved chunks contain the answer

For at least 4 of my 5 test questions, the retrieved chunks include one that
contains the answer.

**Why this target:**

This serves as a cut off point with 80% of the cases passing and producing relevant chunk associated with the prompt. If this is not the case our RAG system is actually hallucinating.

---

## 2. Every answer names a source

Every answer the system produces names at least one source document.

**Why this target:**

This is important so we know the retrieval is backed by a source of truth that is from the chunks and it is not made up. We need to show proof or citation for every single result we showcase at the retrieval step.

---

## 3. The relevance gate stops out-of-corpus questions

When I ask a question my documents clearly don't cover, the relevance gate
stops it and the system returns "I don't have enough information about that" —
in at least 4 of 5 tries.

<!-- The five questions are the ones in `OUT_OF_SCOPE` at the bottom of
     `questions.py`, and `run_eval.py` puts them through the gate and writes
     what happened into your run log. Swap them for your own if you'd rather —
     just keep five of them, or the "4 of 5" above has nothing to be 4 of. -->

**Why this target:**

We don't want to generate answers that are incorrect. Asking irrelevant questions should be marked as insufficient information because we don't have the relevant chunks in our system to back the retrieval. This is a guardrail to stop hallucinating.

## 4. Something about your chunks

No chunk is under 40 characters or over 600

<!-- YOU WRITE THIS ONE.

     How would you know if your chunks were the right size? Name something
     countable or observable.

     Examples of the right shape — don't copy these, they should come from
     what you actually saw in Milestone 3:
       - "At least 4 of 5 sampled chunks read as a complete thought, with no
          sentence cut in half at either end."
       - "No chunk is shorter than 200 characters, since anything below that
          in my corpus turned out to be a heading with no content under it." -->



**Why this target:**
Too many little chunks will cause more deviation of accuracy - meaning it will create confusion in the system while retrieving results we want our chunks to be of the right size so that we can pick the correct one instead of too many correct answers we are aiming for one correct answer.

Too larger chunks will force too much information in one chunk leading to cohesion same kind of confusion where retrieval will pick out the wrong chunk or will not be able to find the relevant chunk because there is too much information in one.


---

## 5. Your choice

<!-- YOU WRITE THIS ONE TOO.

     Pick something you actually care about getting right. It could be about
     speed, about refusals, about a particular kind of question your corpus
     handles badly, about source attribution being correct rather than merely
     present — anything, as long as it names a number or an observable
     outcome. -->
* **Formula Name:** This metric is called the **F1-Score for Factual Correctness**.
* **The Formula:** $$Score = \frac{TP}{TP + 0.5 \times (FP + FN)}$$
* **Target Threshold:** The RAG system must achieve a minimum average score of **0.75** across the golden test dataset.


**Why this target:**
A target of 0.75 to 1.0 mathematically ensures the LLM captures the majority of critical facts (high recall) while strictly limiting hallucinations and unverified claims (high precision).

**what other values mean for a RAG system?**  
These values will help determine where the current system is to help with trouble shooting.

0.85 – 1.00 (Excellent / Critical Risk)
0.70 – 0.84 (Good / Standard Production)
0.50 – 0.69 (Average / Room for Improvement)
Below 0.50 (Poor / Failing)
<!-- ─────────────────────────────────────────────────────────────────────────
     UNIT 2 — read this before you change anything above.

     If a criterion turns out to be BROKEN rather than merely unmet, you can
     revise it, and that earns credit. But never delete or edit the original
     line. Add the revision underneath it, like this:

         ## 1. Retrieved chunks contain the answer

         For at least 4 of my 5 test questions, the retrieved chunks include
         one that contains the answer.

         **Why this target:** ...

         > **Revised in unit 2:** For at least 4 of 5 questions, the top three
         > results contain the answer.
         >
         > **Why revised:** I couldn't judge "the chunks include one that
         > contains the answer" the same way twice — I scored two questions
         > differently on Monday than on Wednesday. The new version is
         > something I can actually check.

     That's a revision because the criterion couldn't be MEASURED.

     Lowering a target because you missed it is not a revision, and it costs
     you the point:

         ✗ "I said 4 of 5 but got 2 of 5, so 2 of 5 is more realistic."

     A number you missed stays where it is, gets diagnosed, and gets a fix
     attempted. That's where the points are.

     The whole reason the originals stay visible is so someone can see what you
     said before you knew the answer.
     ───────────────────────────────────────────────────────────────────────── -->
