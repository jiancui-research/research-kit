---
description: Build and keep the writing-style file the writing commands read - distilled from papers you admire, the instructions you give, and the edits you make.
argument-hint: (none) to refresh and to harvest this conversation, or an instruction to record now (e.g. "stop opening sections with 'In this section'")
---

## User input

`$ARGUMENTS` holds an instruction to record now, or is empty to refresh from samples and harvest
what this conversation already taught you.

## What this phase is

Craft guides describe the genre. This describes **how this user wants their paper written**, and
it accumulates. Three sources feed one file at `./.research/writing/style.md`:

| Source | Section it feeds | Rebuilt on refresh? |
|---|---|---|
| Exemplars in `.research/writing/samples/` | the register, openings, outline shapes, habits, vocabulary | yes |
| Instructions the user gives in conversation | **Standing instructions** | never |
| Edits the user makes to prose written for them | **Learned from edits** | never |

It is optional: writing works without it, and better with it.

## Steps

1. Read `./.research/memory/constitution.md` if it exists; skip silently otherwise.
2. Read `./.research/writing/style.md` if it exists, so the two user-owned sections survive
   whatever follows. Create it from `.research/templates/style-template.md` if it does not.
3. **`$ARGUMENTS` non-empty:** append one dated entry to **Standing instructions** in the user's
   own words, plus what prompted it. Report it and stop - do not touch anything else.
4. **`$ARGUMENTS` empty:** do all three of these, then report each separately.
   - **Samples.** Read every file in `.research/writing/samples/` and rebuild the sample-derived
     sections. If the directory is missing, create it and say what to drop in (`.tex`, `.md`,
     `.txt`, `.pdf`; the user's own published work is the strongest signal; copyrighted PDFs
     belong in `.gitignore`). Fewer than two samples cannot separate a habit from a coincidence -
     say so and leave those sections alone.
   - **This conversation.** Re-read it for anything the user said about how the writing should
     go: a word they rejected, an opener they disliked, a structure they asked for. **Propose**
     them as Standing instructions and write only what they confirm.
   - **Their edits.** Where prose was written for them and then changed, diff it (`git diff`, or
     the version you wrote against what is on disk) and read the preference off the change.
     Propose each as a **Learned from edits** entry: what was written, what it became, and the
     rule that explains it. The rule is the part that generalizes; an entry without one is noise.
5. Never rewrite an existing entry in either user-owned section. A reversal is a new dated entry
   that says what it reverses.

## The rule that makes this safe

**Patterns and slots, never sentences.** A sentence copied out of a sample travels through this
file into the manuscript, and that is plagiarism with extra steps. Write
`[finding], which we believe is [scope hedge], will inspire [direction]` - never the sentence you
found it in. Quote at most a few words, and only where the phrase itself is the pattern. If a
pattern cannot be stated without reproducing someone's sentence, leave it out.

## Validate

- Standing instructions and Learned from edits survived untouched; only sample-derived sections
  were rebuilt.
- Nothing was inferred and written silently - conversation and edit harvests were proposed first.
- Every sample-derived claim appears in at least two samples; every edit entry states a rule.
- No sentence was copied from a sample, and nothing about the paper's findings leaked in - this
  file is about form, not content.

## Completion

Report the path, how many samples fed it, what was added to each of the three areas, and anything
proposed but declined. End with `Next: /research.write <section>`.
