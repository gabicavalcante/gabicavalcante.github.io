+++
title = "Communication frameworks for being understood"
description = "The three communication frameworks I actually use: PREP, BLUF and before-after-bridge, and what leading a team taught me about when each one helps."
date = "2026-09-03"
lastmod = "2026-09-04"
tags = ["communication", "career", "writing"]
+++

I lead a team, and the thing we come back to most often is not a technical problem. People know their work. What they usually do not know is how to communicate it: an idea nobody buys into, a question that does not get answered, a piece of work nobody realizes was hard, an opinion that never quite lands as an opinion, and feedback that was never given.


<!--more-->

Have you ever written a report message and noticed that something was off? Several items confirming that things are fine, and a question that needs an answer, all in one block, with the question somewhere in the middle. And surprisingly, no one replied with the answer you wanted. That is the common one, but the more I worked leading teams, the more I realized the challenge was the same, but the structure was not.

You might think AI would have solved this by now, right? Sometimes it makes it worse. You get back something longer and better polished, carrying the same buried question, and now it takes more of the reader's time to reach the same confusion. Everyone is already reading more than they can absorb. Being direct is what earns attention, and no tool will do that part for you.


<!-- Have you ever written a status update and noticed that something was off? Several items confirming that things are fine, one genuinely new decision, and a question that needs an answer, all in one block, with the question somewhere in the middle. That is the common one, but it is not the only one. It could be a proposal you want your team to buy, a talk that never quite sounds confident, a daily sync where you cannot get the point out, a simple feedback that you couldn't structured in a way that sounds natural. 

At first I thought I was giving the same advice every time. Put the question at the top. Report only what actually changed. Start with the result. The more I used these frameworks, the more I realized the principle was the same, but the structure was not.

None of that advice is about English, and more of it gets written with AI every day, which is what convinces me that language was often not the main problem. AI can fix the sentences. It cannot tell you what the reader needs to know first. -->


This post is my study guide, and also a place to collect what I have picked up leading a team. I thought about writing up my experience after reading Jordan Cutler's [Top 5 Communication Frameworks for Engineers](https://read.highgrowthengineer.com/p/top-5-communication-framework), which is where I found them gathered in one place.

## PREP: making the case

- **Point.** State your argument.
- **Reason.** Say why you believe it.
- **Example.** Back it with something concrete.
- **Point.** State the argument again.

The case I had to make recently was for the boring solution over the ambitious one. Building it properly meant about six months, a refactor of most of the project, and a real chance it would not work at the end of that. The unglamorous option put the same capability in production in a week. The version I want to avoid sounds like this: *"the custom approach is one option, and it would probably give us more control, though the timeline is a concern, and of course there is the refactor to think about..."* Every clause is true and none of it is a recommendation.

Now, what do you feel about this other way to start: *"We should ship the simple version first"*. This sentence someone can disagree with. A suggestion is not, and that is what the softer version costs you: when your position is not clear, nobody feels they owe you an answer. They can nod and move on, because nothing was actually asked of them. Being clear gives the other person something concrete to agree with, reject, or challenge, and that is how a decision gets made instead of deferred.

I used to worry the closing restatement would sound repetitive. It does not. By the time you have given the reason and the example, the person has been thinking about the example, and saying the point again is what they leave with.

## BLUF: bottom line up front

Start with the point, the question, or the request. Add only the context that supports it. Do not build up to the ask.

This is the fix for the confusing report message I opened with. 
<!--
[Gabi's comment]: can you add a example of cofusing msg to show before X after?
-->
Here is roughly what I suggested instead:

{{< quote channel="#slack-channel" >}}
I need a decision on the import batch size before Thursday.

We process 5,000 rows per run today and the job times out roughly once a week. At 1,000 the run is reliable and takes about 40 minutes longer. My suggestion is 1,000.
{{< /quote >}}

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

## Which one to reach for

| Situation | Framework |
| --- | --- |
| Arguing for a technical decision | PREP |
| Requests, decisions, status updates, async messages | BLUF |
| Demos, talks, explaining outcomes | Before, after, bridge |

Everything here is something you can do alone, at your desk, before anyone else is involved. You draft it, you fix the order, you send it. Structuring a conversation, where the other person answers back and you have to change course, is a different problem, and I wrote about that separately.

## Where I stop

Frameworks are scaffolding. They are useful because they stop you rambling, and the risk is that you get attached to the scaffolding and forget what it was holding up.

The thing I most want to teach is not any of these three. It is that the goal is to be understood, and being understood means taking the focus off yourself and what you want to say, and putting it on the person in front of you and what they need in order to know, act or decide. The same idea explained to a staff engineer, a product manager and a client is three different messages. Adapting between them is the actual skill, and you cannot adapt to a room you are not paying attention to.

I wrote in [Let's talk about communication]({{< relref "lets-talk-about-communication" >}}) that what changed my teaching was noticing the room rather than finding a better structure: asking "am I explaining this well?" instead of "did you understand?", and dropping the word "easy." That is the skill none of these three can give you. A framework can make you more convincing while making you less attentive, and being convincing about the wrong thing is not an improvement.

So the order matters: listen first, then pick the structure that fits what you heard. Reaching for a framework before you know your audience is how you end up with a very well organized message that answers a question nobody asked.

## References

- [BLUF](https://en.wikipedia.org/wiki/BLUF_(communication)), from US Army Regulation 25-50
- [Top 5 Communication Frameworks for Engineers You Must Remember](https://read.highgrowthengineer.com/p/top-5-communication-framework), Jordan Cutler, High Growth Engineer, 2025-11-16, which prompted this post
