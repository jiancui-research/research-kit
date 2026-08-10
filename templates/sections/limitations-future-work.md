> Loaded by `/research.write` or explicit `/research.implement paper limitations` or `paper future-work` mode.
> Craft for limitations and future work, which in most empirical security and systems venues
> are one passage rather than two sections.

# Limitations and future work

**TL;DR:** Future work signals roadmap maturity and artifact longevity - it is not a place to
apologise. Frame every item as an extension you chose not to take yet, in future tense, never as
a gap you failed to close. The defensive test: **every sentence should be safely quotable in a
rebuttal.**

---

## What it is for

It shows you see the wider landscape, signals the artifact is a platform others can build on,
and pre-empts "did you consider X?" before a reviewer asks. It is not for surfacing limitations
you did not already discuss, and not for performing modesty.

## Where it lives

Three conventions, all common:

- Folded into a **Limitations and Future Work** paragraph at the end of the discussion.
- A run-in paragraph closing a discussion subsection, with bolded sub-topics.
- **Conclusion and Future Work**, with enumerated directions.

**If recent papers at your target venue have no standalone Future Work header, do not invent
one.** A standalone section invites "you should have done that".

## The verb ladder

Match the commitment to what you can actually deliver. Weakest to strongest:

```
can be extended   <   is a natural extension   <   we plan to   <   we will
```

Use `we will` only for things you control. For anything depending on others, or that you may
never do, prefer *an interesting question is whether ...* - it signals optionality rather than
obligation.

## Patterns that work

- **Scope extension.** Extend a scope you already justified; do not fix a gap you just
  revealed. "Future work can expand coverage to [adjacent classes], [more languages],
  [other settings]."
- **The optional item.** "An interesting future work item is to extend [system] to [setting]."
  Signals awareness without committing.
- **Minimum commitment.** "We leave this to future work." Effective precisely because it is
  terse - use it sparingly, or it reads as a list of things you skipped.
- **Enumerated roadmap.** For papers with public artifacts and a continuing team: *First ...
  Second ... Third ... Finally ...* Mix the verbs - `we will` for the ones you own, `an
  interesting question is whether` for the ones you do not.
- **Limitation with mitigation.** Name the limitation, then neutralise it in the next sentence:
  "Our framework currently [limitation]. However, this can be addressed through [concrete
  mitigation]." This is the single most useful move here - it converts a weakness a reviewer
  would raise into evidence that you understand the system.
- **Stakeholder-driven directions.** Common for measurement work: anchor each item to a
  stakeholder concern rather than to a technical axis.

## Pitfalls

1. **Apologetic verbs.** Replace *unfortunately*, *we did not*, *we were unable* with *expand,
   extend, explore, incorporate, evaluate, generalize*.
2. **Listing capabilities the reviewer already expects.** Either justify the scope cut earlier
   and frame the extension as roadmap, or actually add the capability.
3. **Naming a competitor's preferred method as future work.** It reads as appeasement and
   invites the reviewer to require it.
4. **Promising what you cannot deliver.** See the verb ladder.
5. **Contradicting your own contribution.** If the paper claims comprehensive coverage, do not
   promise to make it more comprehensive later.
6. **Introducing new limitations here.** Forward-reference the ones already discussed; a
   limitation that appears for the first time in future work reads as a confession.
7. **Ending the paper on future work.** Follow it with a short conclusion, or end the passage
   itself on a contribution-anchored sentence.

## Skeleton

```
**Limitations and future work.** [One sentence restating an already-justified scope cut.]
[One sentence on orthogonal axes a future iteration could cover - extend / expand /
incorporate.] [One sentence on the obvious methodological axis, as an interesting future
work item.] [One sentence on artifact longevity, only if you intend to maintain it.]
```

For a longer passage, graduate to the enumerated form with a deliberate mix of commitment
verbs.

## Checklist

- [ ] No apologetic verbs.
- [ ] Every item is an extension, not a confession.
- [ ] Commitment verbs match what you can actually deliver.
- [ ] Limitations named here were already discussed, not introduced here.
- [ ] Nothing contradicts a contribution claim.
- [ ] The paper does not end on this passage.
- [ ] Every sentence would be safe to quote back in a rebuttal.
