---
description: Distill the papers you admire into one living voice profile the writing commands read, and keep it current as you work.
argument-hint: (none) to build or refresh from samples, or a correction to record (e.g. "stop opening sections with 'In this section'")
---

## User input

`$ARGUMENTS` is empty to build or refresh the voice profile from the samples on disk, or holds a
correction to record - something you told the agent about your writing that should outlive this
conversation.

## What this phase is

Craft guides describe the genre. This describes **your** register, learned from papers you chose.
It is optional: writing works without it, and better with it. `voice.md` is a living file, built
from samples and extended every time you correct the prose.

## Steps

1. Read `./.research/memory/constitution.md` if it exists; skip silently otherwise.
2. Resolve `./.research/style/samples/`. If it does not exist, create it, tell the user to drop
   in papers whose writing they want to sound like (`.tex`, `.md`, `.txt`, or `.pdf`; their own
   published work counts and is the strongest signal), note that copyrighted PDFs belong in
   `.gitignore`, and stop. Fewer than two samples is not enough to tell a habit from a
   coincidence - say so and stop.
3. **With `$ARGUMENTS` empty:** read every sample in full and distill it into
   `./.research/style/voice.md`, using `.research/templates/voice-template.md`. Record
   how sections open, the paragraph-level shape of each section, how findings land, which words
   recur and which never appear. Attribute each pattern to the number of samples showing it, and
   drop anything that appears in only one.
4. **With `$ARGUMENTS` non-empty:** do not re-read the samples. Append one dated entry to the
   profile's **Learned while writing** section: the correction in the user's own words, and what
   prompted it. Never rewrite an earlier entry - a reversal is a new entry that says so.
5. Refreshing preserves the **Learned while writing** section verbatim; only the
   sample-derived sections are rebuilt. Report what changed.

## The rule that makes this safe

**Patterns and slots, never sentences.** A sentence copied out of a sample travels through the
profile into the manuscript, and that is plagiarism with extra steps. Write
`[finding], which we believe is [scope hedge], will inspire [direction]` - never the sentence you
found it in. Quote at most a few words, and only where the phrase itself is the pattern
(`we are surprised to find`). If a pattern cannot be stated without reproducing someone's
sentence, leave it out.

## Validate

- Every entry is a pattern with slots; no sentence was copied from a sample.
- Every sample-derived claim appears in at least two samples.
- `Learned while writing` survived the refresh untouched.
- Nothing about the current paper's content leaked in - this file is about form, not findings.

## Completion

Report the profile path, how many samples fed it, which patterns were added or dropped, and any
sample that could not be read. End with `Next: /research.write <section>`.
