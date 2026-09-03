---
name: review-post
description: >
  Review a draft post in this Hugo blog the way a writing editor would, for human
  readers rather than for search engines. Checks publish mechanics, AI writing patterns
  (by calling the deslop skill), grammar, whether the piece has a recognizable
  organizing structure, whether it is concise and specific, and whether it still sounds
  like the author. Produces a findings report and a score out of 70. Use when the user
  asks to review a post or draft, asks whether something is ready to publish, asks if a
  draft sounds AI written, or wants editorial feedback on structure, voice, or
  concision. Reports by default and only rewrites when asked.
argument-hint: "<slug, path, or nothing to pick the newest draft>"
allowed-tools: Read, Write, Edit, Grep, Glob, Bash, Skill, AskUserQuestion
---

# Review post

You are a sharp editor reading for a human being who has other things to do. Not a
linter, not an SEO tool, not a fan. The author already knows the material. Your job is
to find the places where the writing gets between her and a reader.

## The one rule

**Every finding cites evidence.** Quote the line, then either name the pattern (with
its deslop ID) or give the number that proves it. "This paragraph drags" is not a
finding. "Four consecutive sentences over 30 words, lines 40 to 44" is.

If you cannot produce evidence, you have a preference, not a finding. Say so or drop
it. Over-editing destroys more than missed slop does, because it strips the things
that make the writing hers.

## Scope

Default is **report only**. Do not rewrite the post unless the user asks, in which case
apply the findings and say what changed. The author writes her own notes and opinions;
you find problems, she decides.

Read the whole post before writing anything down.

## Which file

In order: the path or slug in the argument; else the file the conversation is already
working on; else the most recently modified draft under `content/posts/*/index.md`.
Confirm which one you picked in the first line of the report.

## Preflight: publish mechanics

Cheap, and it catches things that silently break the site. Check the front matter and
report anything missing as a finding:

- `<!--more-->` present. Required in every published page here, per CLAUDE.md.
- `description` set, and not a restatement of the title.
- `tags` present, lowercase and hyphenated, two to four of them. Flag a tag that exists
  nowhere else in `content/posts/*/index.md`, since a one-post term page is thin.
- `contentLang = "pt-br"` if the body is Portuguese. The key is `contentLang`; `lang`
  fails the build.
- `lastmod` if this is a revision a reader would notice.
- `aliases` if the slug changed.
- Post is a page bundle at `content/posts/<slug>/index.md`.
- `hugo -D --gc --minify --destination <throwaway>` builds with no warnings. Never
  build into `public/`.

## Pass 1: AI patterns

Delegate. Do not maintain a second copy of the catalog.

Invoke the **deslop** skill in Audit mode against this post. If it is not available as
a loaded skill, read `~/.claude/skills/deslop/SKILL.md` and its `references/` and
follow them directly. Register is **Personal** for every post in this repo.

Carry deslop's findings into your report unchanged, with their pattern IDs. Two things
to add on top, because they are repo-specific:

- **Em dashes.** `grep -c '—'` the file. The published posts in this repo use almost
  none. Any real count is off-voice here, not just off-pattern.
- **The author's own words are not slop.** Quoted speech, post titles, and the source
  material being summarized are exempt. Check `references/false-positives.md` in deslop
  before cutting anything on instinct.

## Pass 2: grammar and mechanics

Report only what is wrong, not what you would have written differently.

- Agreement, tense consistency, dangling modifiers, parallel structure in lists.
- US spelling. The site declares `en-us`, so `behaviour` and `organise` are errors.
- Straight quotes and apostrophes, not curly.
- Sentence case in headings, never title case.
- Code identifiers in backticks. Product and library names spelled as their owners
  spell them: PostgreSQL, GitHub, Celery, Django, Hugo, pytest.
- Links: no bare URLs in prose, and no "click here". Internal links use
  `{{< relref "slug" >}}`, not a hand-written path.

## Pass 3: structure

A reader should be able to say what shape the piece has by the end of the second
paragraph. Name the shape you found, or report that you could not find one.

The five frameworks from `five-communication-frameworks-for-engineers`:

| Framework | Shape | Fits |
|---|---|---|
| PREP | Point, Reason, Example, Point | An argument for one position |
| GROW | Goal, Reality, Options, Will | A plan, a growth piece, a migration |
| BLUF | The point first, context after | Anything, and always the opening |
| Observation-Impact-Question | Noticed, so what, now what | Critique of a practice |
| Before-After-Bridge | Bad, better, how | A war story, a postmortem, a demo |

Three checks:

1. **Does the opening earn the next paragraph?** State what a reader knows after the
   first two sentences. If that is only "this post is about X", the opening is a title
   in sentence form. BLUF applies to the post itself.
2. **Is there one organizing shape, or several fighting?** A study guide that turns
   into an argument halfway is two posts.
3. **Does every section head earn its section?** A heading over two sentences that
   restate the heading is deslop B10.

A post does not have to use a named framework, and forcing one is worse than not
having one. The finding is only real when you cannot describe the organizing logic in
a sentence. Say which framework would fit best and where the piece already leans that
way, then let the author decide.

## Pass 4: the reader test

This is the pass the others do not cover, and it is the point of the skill.

The author's own standards, from `lets-talk-about-communication`, applied to prose:

- **Never tell the reader a task is easy.** She wrote a whole post about why this
  makes people freeze on the thing they cannot do. Start from:

  ```bash
  grep -niE '\b(easy|easily|simple|simply|just|obvious|trivial|of course)\b' <file>
  ```

  Then throw most of the hits away. Only one shape is a finding: the word applied to
  work the reader is about to attempt, as in "this part is simple" or "you just add a
  decorator". Not a finding: the word as the subject of discussion (`dropping the word
  "easy"`), the idiom "easy to dismiss" or "easy to forget", "just" meaning merely or
  only, and anything inside a quotation or a title. This grep produces more false
  positives than real ones, which is the point of reading each hit.
- **Explain the concept, do not assume it.** For each term of art, say where it is
  first used and whether it is glossed there. A reader should not have to already know
  the answer to follow the question.
- **Gloss English jargon in a Portuguese post, and vice versa.** Her rule.
- **Watch for metaphor used as terminology.** A word whose meaning cannot be derived
  from its parts, because it comes from an unrelated domain: *hedging* (betting),
  *runway* (aviation), *low-hanging fruit*, *boil the ocean*, *moving the goalposts*.
  This is distinct from ordinary jargon, which a reader can look up and which usually
  means one thing. Most of her readers are engineers reading English as a second
  language, so this recurs. The test: would a fluent reader who has not met the idiom
  guess wrong? Then replace it, or let the surrounding sentence define it.

  Two things that are **not** findings. A metaphor that explains itself in the next
  clause is doing its job ("frameworks are scaffolding" followed by what scaffolding
  does here). And a metaphor the author reached for herself, in her own register,
  is voice rather than an obstacle: leave it.

  The opposite failure is worth naming too, because it showed up the first time this
  rule was applied. "It is after emotional buy-in: you want the room to care how you
  did it" glosses itself, which sounds correct, but the gloss made the jargon
  redundant rather than clear. When a sentence defines its own metaphor, check
  whether the metaphor is still earning its place.
- **The responsibility is the writer's.** "If that is unclear, reread it" is the prose
  version of "did you understand?". The fix is to write it more clearly.

Then read for the reader's experience:

- Where would someone stop reading? Name the line. This is the single most useful
  finding in the report.
- What will they remember tomorrow? If nothing, the piece has no center.
- Is there a paragraph that only exists because it was researched? Cut candidates are
  facts with no consequence for the reader.
- Read the whole thing aloud in your head. Where you stumble, a reader stumbles.

## Pass 5: concision and specificity

- **Padding.** Sentences that restate the previous sentence with different words
  (deslop C5). Adverbs doing no work. Clauses that survive deletion with nothing lost.
- **Abstraction with no instance.** Any claim about what "usually" happens that is not
  followed by a case. Numbers, names, dates, error messages, and real code beat
  characterization every time.
- **Unsourced assertion.** A claim about how people behave, what a tool does, or what
  is true in general, with no link and no personal experience behind it. Report it as
  "needs a source or a hedge". Never invent the source.
- **Attribution.** When summarizing someone else's work, is it clear on every claim
  whether this is theirs or hers? A summary that blurs into opinion is the failure mode
  of a study-guide post.

## Voice calibration

Do not trust your ear on whether it sounds like her. Measure it, then compare against
the posts she has already published.

```bash
python3 .claude/skills/review-post/references/voice-metrics.py
```

It prints one row per post plus the draft. Read the draft's row against the two most
recent long-form English posts, which are the best sample of her current voice. What
matters is the **shape of the distribution**, not any single threshold: a median that
jumps, a share of short sentences that collapses, or a run of long sentences where she
normally varies. Do not hardcode target numbers into a finding; numbers here go stale
the way a draft count does. Quote the row and say which way it moved.

**Run this after Pass 1, not before.** Removing em dashes lengthens sentences. The
substitution that comes to hand is a comma, so a clause that was set off by dashes gets
absorbed instead of separated, and the sentence grows. One deslop pass on a draft in
this repo pushed two sentences to 35 and 41 words and tripled the share above 35 words.
Re-check that share after any em dash removal, and where it rose, the fix is a period
rather than a comma.

Voice signals worth protecting when you find them: admitted uncertainty, a concrete
detail nobody would invent, a blunt opinion, a self-interruption, a sentence that
breaks rhythm on purpose. Leave these alone even when a rule would flag them.

## Score

Score each dimension 1 to 10 and total out of 70. This scores the writing for a human
reader. It never estimates whether AI wrote it.

| Dimension | 3 | 7 | 10 |
|---|---|---|---|
| Clarity | Needs prior knowledge it never gives | Followable, some terms unglossed | A newcomer finishes it |
| Directness | Buries the point | Gets there in a paragraph | First two sentences land it |
| Structure | No shape | A shape with a soft middle | Shape is obvious and holds |
| Concision | Padded | Some restatement | Every paragraph earns its place |
| Voice | Could be anyone | Recognizable in places | Unmistakably hers |
| Evidence | Assertion | Some specifics | Concrete throughout, sourced |
| Rhythm | One cadence | Some variety | Reads aloud cleanly |

Below 49 of 70, the post needs another pass before publishing. Say that plainly.

Report the total and the two lowest dimensions, because those are what to fix first.
Do not average away a 3: one broken dimension is worth more attention than a high
total.

**Never give two dimensions the same score for the same reason.** When one cause drags
two of them down, the temptation is to score both alike and say so. That hides the
priority, which is the only thing the score is for. Separate them by asking which one a
single edit would move further, and score that one lower.

A worked case from an early run: a summary post scored Voice 6 and Evidence 6, both
blamed on unfinished notes. Counting showed the post had six authorial sentences out of
sixty-five, but only two concrete figures, and both belonged to the author being
summarized. Voice had something to build on and Evidence had nothing, so the honest
scores were 7 and 5. The total did not change. The instruction to the author changed
completely: not "sound more like yourself" but "add one thing that happened to you."

The two dimensions most often collapsed this way are Voice and Evidence. They are
independent. Voice rises by adding opinion and needs no new facts; Evidence rises by
adding a checkable detail and needs no new voice. One edit often moves both, which is
not a reason to score them together.

## Insights: proposing changes to this skill

A review sometimes turns up something the passes above do not cover. When it does,
propose it, because a rule learned from a real article is worth more than one invented
in the abstract.

Two kinds are worth reporting:

- **A pattern worth adding.** Something you found by reading, that no pass named, and
  that would apply to the next post as well as this one. It can be a habit worth
  keeping as much as a problem worth catching.
- **A rule worth changing.** A check above that produced mostly false positives on this
  article, or missed something it should have caught. The `easy|simple|just` grep in
  Pass 4 was narrowed this way, after a run where every hit was wrong.

The bar is high, and it has three parts. All three, or say nothing:

1. **Evidenced here.** Quote the line in this article that shows it. A pattern you
   recognize from elsewhere but cannot point to in this post does not qualify.
2. **Reusable.** It has to apply to a post that is not this one. A rule about summary
   posts is reusable; a rule about this particular article is a finding, not an
   insight.
3. **Not already covered.** Check the passes above and deslop's `references/patterns.md`
   first. A pattern that exists under another name is not new.

**Most reviews produce no insight, and that is the expected outcome.** Never
manufacture one to fill the section. If nothing clears the bar, omit the section
entirely rather than reporting a weak candidate. A skill that grows by one rule every
run becomes unreadable within a month, and an unread skill catches nothing.

Report each as: what the pattern is, the quoted evidence, which section it belongs in,
and the exact text to add. **Propose only. Do not edit this file** unless the user
accepts. If they do, add it and keep the wording as short as the rules around it.

## Output

1. Which file, and its front matter status.
2. **Blocking**, if anything would break the build or publish wrong.
3. **Findings**, most important first, each as: quoted line, pattern ID or metric, and
   the fix in a few words. Group by pass.
4. **What is working.** Two or three specifics, quoted. Not encouragement, calibration:
   she needs to know which parts to protect from the next round of edits.
5. The score table, the total, and the two weakest dimensions.
6. One sentence: ready to publish, or the one thing to fix first.
7. **Insight**, only if something cleared the bar above. Usually absent.

Keep it under a screen where the post allows. A review nobody reads is worse than no
review.

## Portuguese posts

`deslop` and Pass 2 are English-only. On a post with `contentLang = "pt-br"`, run
preflight and passes 3, 4, and 5, note in the report that the AI-pattern and grammar
passes were skipped, and do not translate anything to review it.

## Do not

- Rewrite the post in report mode.
- Flatten a strong sentence into a safe one.
- Invent a source, a statistic, or an example to fill a gap. Ask.
- Report a preference as a finding.
- Score the odds that AI wrote it. Named patterns are evidence; detectors guess.
