+++
title = "Five frameworks for being understood"
description = "Five structures I use to make an idea land: PREP, BLUF, before-after-bridge, observation-impact-question and GROW, and what leading a team taught me about when each one helps."
date = "2026-09-03"
tags = ["communication", "career", "writing"]
+++

I lead a team, and the thing we come back to most often is not a technical problem. People know their work. What they usually do not know is how to communicate it: an idea that does not get bought, a question that does not get answered, a piece of work nobody realizes was hard, an opinion that never quite lands as an opinion.

English is a second language for most of us, and it would be easy to blame that. I do not think it is the main problem. Most of the time, the problem is knowing what to say first, what to leave out, and what you actually want the other person to do.

<!--more-->

Have you ever written a status update and noticed what was in it? Several items confirming that things are fine, one genuinely new decision, and a question that needs an answer, all in one block, with the question somewhere in the middle. That is the common one, but it is not the only one. It could be a proposal you want your team to buy. It could be a talk that never quite sounds confident. It could be a daily sync where you cannot get the point out.

At first I thought I was giving the same advice every time. Put the question at the top. Report only what actually changed. Start with the result. The more I used these frameworks, the more I realized the principle was the same, but the structure was not.

None of that advice is about English, and more of it gets written with AI every day, which is what convinces me that language was often not the main problem. AI can fix the sentences. It cannot tell you what the reader needs to know first.

Sometimes it makes it worse. You get back something longer and better polished, carrying the same buried question, and now it takes more of the reader's time to reach the same confusion. Everyone is already reading more than they can absorb. Being direct is what earns attention, and no tool will do that part for you.

This post is my study guide, and also a place to collect what I have picked up leading a team. It was prompted by Jordan Cutler's [Top 5 Communication Frameworks for Engineers](https://read.highgrowthengineer.com/p/top-5-communication-framework), which is where I found them gathered in one place.

## PREP: making the case

- **Point.** State your argument.
- **Reason.** Say why you believe it.
- **Example.** Back it with something concrete.
- **Point.** State the argument again.

The case I had to make recently was for the boring solution over the ambitious one. Building it properly meant about three months, a refactor of most of the project, and a real chance it would not work at the end of that. The unglamorous option put the same capability in production in a week. The version I want to avoid sounds like this: "the custom approach is one option, and it would probably give us more control, though the timeline is a concern, and of course there is the refactor to think about..." Every clause is true and none of it is a recommendation.

The trick is not the structure. It is being willing to have an opinion inside it. "We should ship the simple version first" is a sentence someone can disagree with. A suggestion is not, and that is what the softer version costs you: when your position is not clear, nobody feels they owe you an answer. They can nod and move on, because nothing was actually asked of them. Being clear gives the other person something concrete to agree with, reject, or challenge, and that is how a decision gets made instead of deferred.

I used to worry the closing restatement would sound repetitive. It does not. By the time you have given the reason and the example, the person has been thinking about the example, and saying the point again is what they leave with.

## BLUF: bottom line up front

Start with the point, the question, or the request. Add only the context that supports it. Do not build up to the ask.

This is the fix for the status update I opened with. Here is roughly what I suggested instead:

> I need a decision on the import batch size before Thursday.
>
> We process 5,000 rows per run today and the job times out roughly once a week. At 1,000 the run is reliable and takes about 40 minutes longer. My suggestion is 1,000.

Two things changed. The decision I need comes first, and the items reporting that things were fine are gone. Confirming something the reader never knew was in question does not inform them, it just costs them a paragraph. The rest of the context is still available if they want it, and the point of leading with the ask is that they get to decide. They can answer in one line, or they can ask why, which is a better conversation than one where they had to read everything first.

It also changes how you write for a specific person. Someone who reads fast and asks questions is badly served by a complete message; they do better with a short one they can interrogate. That is not a rule you can get from a framework, it is something you learn about the people you work with.

BLUF and PREP are the same instinct at different scales. Both flip the order most of us were taught, where you set up context, walk through the data, and arrive at the conclusion. BLUF is essentially the first P of PREP, applied to anything. The gain is largest in async communication, where the reader cannot interrupt you to ask where this is going.

This can feel abrupt in Portuguese, where opening with a bare request reads as brusque. It is adaptable, and it is worth adapting: with an international client, on a thread they are reading between two other meetings, the first line is often the only line that gets read.

## Before, after, bridge: presentations and demos

- **Before.** The situation without the work.
- **After.** The situation with it.
- **Bridge.** How you got there, including what was hard.

Engineers narrate in the order the work happened: problem, approach, challenges, outcome. The audience spends the whole middle not knowing whether any of it will matter. Lead with the result and the details have somewhere to land.

I worked on a dashboard that (**Before**) took over two minutes to load and usually timed out before it got there, so nobody could filter it down to their own data. We got it (**After**) to under two seconds! The (**Bridge**) was `EXPLAIN ANALYZE` on the real query, which is where guessing stops and a list starts: a few missing indexes, and a set of N+1 queries to refactor.

The bridge is the part that delivers the most value, and the part people actually want, but it only works if they already know it led somewhere.

This is the same reordering as BLUF, aimed at something different. BLUF comes out of military writing, where a buried point costs you a slow decision: it is risk avoidance. Before-after-bridge is a copywriting structure, and it wants the room to care how you did it. That is why one belongs in a Slack message and the other in a demo or a technical presentation.

## Observation, impact, question: feedback in the moment

Everything so far is something you can do alone, at your desk, before anyone else is involved. Another place we have to structure communication is feedback, and that one does not work unless the other person answers back.

This one comes from Lara Hogan's [feedback equation](https://larahogan.me/blog/feedback-equation/). Most feedback frameworks are built for performance reviews, so reaching for one on an ordinary Tuesday means visibly switching into feedback mode.

1. **Observation.** "I noticed that..."
2. **Impact.** "That leads to..."
3. **Question.** "What are your thoughts?" or "would you be open to...?"

Take the long messages from earlier. The version to avoid is "your messages are too confusing," which is a judgment about the person. The observation is "I noticed the questions in your updates usually come after the status items."

Impact is the part people find hardest, and the way through it is to say how it lands on you rather than to reach for something objective. "I have a hard time telling what input you need from me, which adds cognitive load, and I end up not being able to unblock you." That is checkable and it is not an accusation.

Then a question, and this is the step that is easiest to skip because we want to hand over the solution. A question opens a conversation, gives you context you did not have, and lets the other person find their own way to fix it. It also protects you: often enough the answer is unexpected and you discover the assumption underneath your feedback was wrong.

## GROW: from a conversation to a plan

- **Goal.** What the person or team wants to achieve.
- **Reality.** What is actually happening now, and what is in the way.
- **Options.** Possible actions, brainstormed rather than prescribed.
- **Will.** The specific steps and timelines they commit to.

Published in the 90s (*Coaching for Performance*), it predates most of the modern communication-framework language in this list. It is usually described as a coaching model. It works just as well for problem solving.

At first I did not think it belonged in a post about communication, because it does not shape a single message. Then I realized that is the point. GROW is the bridge between communication and action. It does not guide what you say, it conducts the process.

Look at what each step requires. To know the Reality you have to listen, pay attention, and observe. To reach Options you have to ask questions instead of telling, and provoke thought rather than supply conclusions. It is collaborative by construction. And the outcome it aims at is different from everything above: not mutual understanding, not a well-received piece of feedback, but a committed plan. An action engine.

It pairs directly with the previous section. You give feedback about a late delivery, and the person tells you they were overwhelmed by last-minute requests. That is where the feedback framework ends and this one starts:

- **Goal.** "What would a good version of the next sprint look like?"
- **Reality.** "What is actually happening when the requests arrive?"
- **Options.** "What could we try?"
- **Will.** "Which of those are you willing to commit to?"

Three of those four are questions I do not have the answer to, and that is the difference between this and everything above it. I use the same sequence in mentorship and in feedback cycles.

## Which one to reach for

| Situation | Framework |
| --- | --- |
| Arguing for a technical decision | PREP |
| Requests, decisions, status updates, async messages | BLUF |
| Demos, talks, explaining outcomes | Before, after, bridge |
| Feedback in the moment | Observation, impact, question |
| Mentorship, and turning a problem into a plan | GROW |

## Where I stop

Frameworks are scaffolding. They are useful because they stop you rambling, and the risk is that you get attached to the scaffolding and forget what it was holding up.

The thing I most want to teach is not any of these five. It is that the goal is to be understood, and being understood means taking the focus off yourself and what you want to say, and putting it on the person in front of you and what they need in order to know, act or decide. The same idea explained to a staff engineer, a product manager and a client is three different messages. Adapting between them is the actual skill, and you cannot adapt to a room you are not paying attention to.

I wrote in [Let's talk about communication]({{< relref "lets-talk-about-communication" >}}) that what changed my teaching was noticing the room rather than finding a better structure: asking "am I explaining this well?" instead of "did you understand?", and dropping the word "easy." That is the same skill GROW needs at Reality and the feedback equation needs at Question. A framework can make you more convincing while making you less attentive, and being convincing about the wrong thing is not an improvement.

So the order matters: listen first, then pick the structure that fits what you heard. Reaching for a framework before you know your audience is how you end up with a very well organized message that answers a question nobody asked.

## References

- [Feedback Equation](https://larahogan.me/blog/feedback-equation/) and [What are you optimizing for?](https://larahogan.me/blog/what-are-you-optimizing-for/), Lara Hogan, for observation, impact, question
- [GROW model](https://en.wikipedia.org/wiki/GROW_model), and John Whitmore, *Coaching for Performance*, 1992
- [BLUF](https://en.wikipedia.org/wiki/BLUF_(communication)), from US Army Regulation 25-50
- [Top 5 Communication Frameworks for Engineers You Must Remember](https://read.highgrowthengineer.com/p/top-5-communication-framework), Jordan Cutler, High Growth Engineer, 2025-11-16, which prompted this post
