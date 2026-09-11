# Helen's reply drafts — the short version

How the daily digest writes the "Suggested Helen Email Draft" (tracker column L, and the
Slack thread under each digest). Condensed from
[`skills/helen-email-digest/SKILL.md`](../skills/helen-email-digest/SKILL.md), which is the
source of truth if the two ever disagree.

## Who gets one

Only leads whose Recommended Action is **"Send to Yobani"**.

No draft for **"Ignore"** rows (the lead already booked a call, confirmed in Close) or for
**Tracking Handover Progress** rows. Those cells stay empty and the leads are left out of
the Slack thread.

## What it is

A **reply in Helen's voice**, inside the existing thread, cc'ing Yobani Mendoza
(`yobani@smbdealhunter.xyz`, the setter). No subject line, no greeting block, no signature.

Warm and direct — how Helen writes when she has thirty seconds — but **in whole words**:
"definitely" not "def", "15 minutes" not "15min", "with you" not "w you".

## The three templates

One per category. Use the lead's category; don't restructure a template to suit the email.

**Buy Box**
```
Hey [First Name], [their ask] is something we can help with. @Yobani on our team can grab 15 minutes with you to better understand what you're looking for.
```

**Ready Now**
```
Hey [First Name], we can definitely help. Looping in Yobani from our team. @Yobani, do you mind finding 15 minutes to give [First Name] a call?
```

**Price Wall**
```
Hey [First Name], fair question. For our average member, the cost comes out to roughly 1% of the purchase price that is due upfront. We do have a success guarantee, which we can talk more about live. Let's get you on a quick call — @Yobani on our team can find a time that works for you.
```

`@Yobani` is literal text in the email body — not a Slack or Gmail mention. It reads as a
nudge to him because he's cc'd.

## Filling them in

**First name** — in order: the name they sign off with in the email body, then the first
word of their Gmail display name. If there's no display name (a bare address like
`ms.raquele@gmail.com`), **don't guess a name from the address** — open with `Hey there,`
instead. Getting a name wrong in the first three words is worse than not using one.

**`[their ask]`** (Buy Box only) — the concrete thing they asked for, as a gerund, in their
own words: "finding deals in Central FL", "finding hotels in California", "finding absentee
businesses". Too vague to name in three or four words? Use "that" — *"Hey Scott, that is
something we can help with."* Never inflate a vague ask into a specific one.

Ready Now and Price Wall take no personalisation beyond the first name.

**Pronouns** — the templates say "you" for a reason. Never infer gender from a name; if a
third-person reference is unavoidable, use they/them unless their own signature makes it
explicit.

## Three hard rules

1. **The 1% line lives in the Price Wall template and nowhere else.** No other draft quotes
   a price, fee, range, guarantee, timeline or deal specific.
2. **Don't elaborate on the 1%** — not even when a lead asks a direct pricing question.
   Send the template as-is; unanswered questions are what the call is for. This is the one
   place where a plausible-sounding invention reaches a customer as a commercial commitment.
3. **Nothing else goes in.** A finished draft is the template, plus a first name, plus
   (Buy Box) their ask. If it says anything the template doesn't, take it back out.

## Where the draft ends up

- **Tracker column L** — plain text with real line breaks, not a formula, not wrapped in
  quotes.
- **Slack** — in a threaded reply under the day's digest, in its own code block so it copies
  cleanly, labelled "Helen:". Never in the digest body; full drafts inline would bury the
  lead list.

Both copies must be byte-identical.

## The other draft

Each of these leads also gets a **Yobani** draft in column M, written in the same run and
posted in the same thread labelled "Yobani:" — his reply for after Helen forwards, sent on
the same thread with her kept on it. Two things to know:

- Its `[time slot]` and `[Calendly Link]` stay as literal placeholders; Yobani fills them
  in before sending.
- **Yobani's Price Wall template does not answer the pricing question** — it moves to a
  call. Helen's is the only one carrying the 1% line. The two sit near each other in the
  task file; never merge them.

A row gets both drafts or neither.
