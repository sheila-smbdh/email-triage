---
name: helen-email-digest
description: Daily Slack digest of new buyer leads in Helen Guo's inbox (Buy Box, Ready Now, Price Wall) plus bonus claims the welcome automation missed, and one row per lead in the Google Sheets tracker carrying both the Helen and Yobani reply drafts
---

You are running the daily "Helen email digest" task for SMB Deal Hunter.

This routine runs **unattended in the cloud**. There is no human at a keyboard when it
fires — every step must complete through connectors, or fail loudly to Slack. Never leave
work parked for a person to finish by hand.

**Scope: buyer leads only.** This routine tracks exactly three categories — **Buy Box**,
**Ready Now**, and **Price Wall** — plus threads in those three categories that Helen has
already handed off. Everything else in the inbox is dropped: not digested, not logged, not
counted. There is no Tier 2, no Tier 3, and no "Uncategorized / needs review" bucket.

**One non-lead exception: bonus claims.** A bare "Yes" reply from someone who has just
joined is normally answered by Helen's canned-response automation within seconds. When the
"Yes" lands on the wrong email the automation never fires and a new member silently gets no
bonuses. Those are surfaced in the digest with a ready-to-send reply. They are not buyer
leads: no tracker row, no Yobani, no Recommended Action. See *Bonus claims* in STEP 2.

---

## STEP 0 — Access preflight

All email and tracker access goes through the **Composio connector**. Do not use the
first-party Gmail connector for this routine: it authenticates as
`sheila@smbdealhunter.xyz` only and cannot reach Helen's mailbox.

Two Gmail accounts are connected to Composio, so **account selection is required on every
Gmail call**. Pin it explicitly:

| Purpose | Composio toolkit | Account id | Mailbox |
|---|---|---|---|
| Read Helen's mail | `gmail` | `gmail_kath-tiou` | `helen@smbdealhunter.xyz` |
| Tracker read/write | `googlesheets` | `googlesheets_gyte-urlar` (alias `helen-tracker`) | — |

Omitting `account` on a Gmail call lets it default to whichever account is marked default.
That is Helen's today, but it is a setting anyone can flip — never rely on it.

One lookup does **not** go through Composio: the call-booked check in STEP 2 reads Close
CRM through the **first-party Close connector** (`mcp__Close__*`). It is read-only. If the
Close connector is missing, that is not a reason to abort the run — the check simply fails
to confirm and every affected lead keeps the default "Send to Yobani" (see STEP 2). Say so
in the run report.

Before doing anything else, confirm both toolkits report an ACTIVE connection. If either is
not active, do NOT run a partial digest. Post this to Slack channel `C0BTCGZSF9R` and stop:

> ⚠️ Helen's email digest couldn't run — the Composio `<toolkit>` connection is not active
> (status: `<status>`). Sheila needs to reconnect it at https://dashboard.composio.dev,
> then this task can run again.

Substitute the real toolkit name and status. Do not assert a cause you have not verified —
the previous version of this file hardcoded a diagnosis ("Sheila needs to accept the
pending delegated-access request") that turned out to be wrong and misled the team for 8
consecutive days. Report the status you actually observed, nothing more.

**Never substitute Sheila's inbox for Helen's.** A digest built from the wrong mailbox is
worse than no digest.

---

## STEP 1 — Pull new emails

Call `GMAIL_FETCH_EMAILS` with `account: "gmail_kath-tiou"` and:

```
query:           in:inbox newer_than:1d
max_results:     500
verbose:         false
include_payload: false
```

Page through `nextPageToken` until it is absent. Do not stop at the first page —
`resultSizeEstimate` is approximate and must not be used as a stopping condition.

`verbose: false` returns sender, subject, `threadId`, `messageTimestamp` and a
`preview.body` snippet. That is enough to triage the large majority of mail. Only when a
snippet is genuinely ambiguous, hydrate that one message with
`GMAIL_FETCH_MESSAGE_BY_MESSAGE_ID` (`format: "metadata"`, or `"full"` if you need the
body). Do not hydrate the whole batch — it is slow and mostly wasted.

**One case always earns hydration: a reply containing deal terms** — dollar figures, down
payments, financing structures, contingencies, deposits, deadlines. `preview.body` is cut at
roughly 200 characters, and in a numbers-heavy reply the part past the cut routinely reverses
the part before it. Two leads were misclassified this way on 2026-08-29 (see *Deal talk is
not buyer intent* in STEP 2). Snippets are safe for the short, plain asks that make up most
real buyer mail; they are not safe for anyone doing arithmetic.

Results are not sorted by recency; sort by `messageTimestamp` / `internalDate` yourself.

**On volume.** Helen's inbox runs roughly 200 messages/day, the overwhelming majority of it
newsletters, promotions and vendor blasts. Because this routine now tracks only three
categories, expect to drop the large majority of each day's mail. That is the intended
behaviour, not a bug — a digest of five real buyer leads is the goal.

Discard, without logging: anything whose only Gmail category is `CATEGORY_PROMOTIONS` or
`CATEGORY_SOCIAL`; bulk newsletters; transactional receipts and automated notifications;
and — new in this version — everything that would previously have been Tier 2 or Tier 3
(Bleeding, Sellside, Investor, Operators, Pitches, Engaged Reader). Those categories are no
longer tracked anywhere.

**One thing not to discard on sight: a one-word "Yes" reply.** It looks like noise and is
usually already handled, but the cases where it is not are new members missing their
bonuses. Hold every bare-affirmative reply for the bonus check in STEP 2 before dropping
it.

**Gmail links.** Build thread links as:

```
https://mail.google.com/mail/u/?authuser=helen@smbdealhunter.xyz#all/<threadId>
```

The `display_url` Composio returns uses `/mail/u/0/`, which resolves to whichever account
happens to be first in the reader's browser — for anyone but Helen that opens the wrong
mailbox or a 404. The `authuser=` form pins it to Helen's mailbox for any reader who has
access to it.

Existing tracker rows from the 8/29 run use a third form,
`https://mail.google.com/mail/u/0/d/<delegation-token>/#inbox/<threadId>`. That token came
from Sheila's delegated view of Helen's mailbox — the same delegation that later lapsed, so
those links may now be dead. Do not reproduce that format for new rows.

**Verify one link by hand on the first run** and report in Slack whether it resolved. If
`authuser=` does not work for the people reading the channel, fall back to plain
`https://mail.google.com/mail/u/0/#inbox/<threadId>` and note the change here.

---

## STEP 2 — Classify

Every email that survives Step 1 is one of the three tracked categories, a handover of one
of them, a bonus claim, or dropped. There is no other outcome.

### TIER 1 — the only tracked tier

- **Buy Box** — volunteers geography/industry/budget/financing criteria, asks if SMB Deal
  Hunter has matching deals (e.g. "anything in California?", "$50K down for a laundromat in
  NYC")
- **Ready Now** — gave a phone number, explicitly asked for a call, used enrollment
  language ("enroll me", "call me"), OR replies with clear interest/readiness to a
  newsletter or prior outreach about a specific deal (even without a direct call ask or
  phone number). For this last case, set recommended action to "send to setter", and use the
  specific-deal variant of Helen's Ready Now draft — see *Which Ready Now template* below.
- **Price Wall** — asks for pricing/cost directly without booking a call ("what does it
  cost", "price before scheduling")

### BONUS CLAIMS (🎁) — bare "Yes" replies

Helen's onboarding email, subject **"You're in! Just one more thing…"**, asks a new member
to reply. A canned-response automation watches for that reply and sends the welcome bonuses
back within seconds, from `helen+canned.response@smbdealhunter.xyz`. That path needs nothing
from this routine.

What needs this routine is the miss: **people reply "Yes" to the wrong email** — a deal
newsletter, whatever was most recently in their inbox — and sometimes the automation does
not fire. The member gets no bonuses and nobody finds out.

**Do not try to predict when it fires.** Its exact trigger is not documented anywhere and
was not reverse-engineered: over three days it answered 29 replies on the onboarding thread
and one on a *"Lesson 1: The 10 Core Steps to Biz Buying"* thread, while Jason Smith's
newsletter reply got nothing. Subject line is not a reliable predictor either way. **Check
the thread, every time** — that is the whole method below, and it stays correct however the
automation is configured.

So, for every reply whose own text is a bare affirmative — `Yes`, `YES`, `yes`, `Yes please`
— with nothing else to it once the quoted email below and any signature block are set aside:

1. **Fetch the thread** with `GMAIL_FETCH_MESSAGE_BY_THREAD_ID`.
2. **Look for a message from `helen+canned.response@smbdealhunter.xyz`.** That address is
   the automation, and it is the only reliable tell — the bonus link sits inside an HTML
   anchor, so a Gmail text search for the URL does not find it.
3. **Automation already replied → drop the email.** Handled, nothing to surface. This is the
   common case and it is why bare "Yes" replies are not simply digested.
4. **No canned response in the thread → this is a bonus claim.** Surface it in the 🎁
   section of the digest with the bonus reply draft (see *The bonus reply* below).

The automation answers within about fifteen seconds, so on a 24-hour window its absence is
settled, not pending.

If the volume of bonus claims ever jumps, that is a signal the automation's trigger changed
or broke — say so in the run report rather than quietly drafting thirty replies.

Worked examples, both verified 2026-09-11:

| Sender | Replied "Yes" to | Canned response in thread | Outcome |
|---|---|---|---|
| Bret Biedscheid | "You're in! Just one more thing…" — the right email | Yes, 15 seconds later | Drop |
| Jason Smith | "New Deals: A pool service company with manager, pawn shop…" — a newsletter | None | 🎁 Bonus claim, draft the reply |

Jason replied "Yes" twice, eleven minutes apart, to a newsletter. Two "Yes" replies in one
thread is still one bonus claim — surface the thread once.

**Bonus claims are not buyer leads.** They are not Tier 1, they get no tracker row, no
Recommended Action, no Yobani draft, and Yobani is not cc'd. Someone replying to "You're
in!" has already joined; there is nothing for a setter to book. The only output is Helen's
one-line reply.

**The recorded trade-off.** A bare "Yes" on a newsletter could in principle be answering a
question the newsletter itself asked, rather than claiming bonuses. There is no way to tell
the two apart from the word "Yes". Sending the welcome-bonus link to someone who was
answering something else costs nothing; leaving a paying member without their bonuses costs
a lot. So the routine surfaces it. Do not build a cleverer test for this.

### TRACKING HANDOVER PROGRESS (🟢)

Threads **in one of the three categories above** where Helen has already made the intro and
handed off to someone else at SMB Deal Hunter. Signals: a teammate (e.g. Kyle Hopkins,
Yobani) is now an active participant replying in the thread, or Helen has explicitly
forwarded/looped a teammate in.

When this is the case the email goes here **instead of** Tier 1 — do not double-list it.
For each entry also record:

- **category** — which of Buy Box / Ready Now / Price Wall this lead was: classify as if
  Helen were still handling it directly, then note the handover
- **owner** — who at SMB Deal Hunter now owns the thread: "helen" if she's still following
  up herself post-intro, or the teammate's name if she's handed it off (e.g. "yobani" — a
  setter, so threads owned by yobani usually arrived there via "send to setter")

A handed-off thread whose original category is **not** one of the three (an Investor thread
Kyle is running, a Sellside thread with Bill) is **dropped**, same as any other untracked
category. Handover tracking follows the tracked categories; it does not widen them.

### Recommended action — and the call-booked check

Every Tier 1 lead gets a Recommended Action, written to tracker column D. There are two
values: **"Send to Yobani"** (the default — a real buyer worth the setter's time) and
**"Ignore"**.

Three things earn "Ignore":

1. **The lead has already disqualified themselves** — declined outright, an obvious
   tyre-kicker, or someone who says they cannot afford it.
2. **The lead has already booked a call, verified in Close CRM** — see below.
3. **The lead does not want to buy a business** — they are asking about something else
   entirely, even when the words look like a buyer's. See the next section.

#### Deal talk is not buyer intent

The deal newsletters go out with headlines like *"$280K/yr biz → 50% seller financed"*, and
replies come back talking fluently about seller financing, down payments, contingencies and
terms. **That vocabulary is not a buyer signal.** A reply full of deal language is often a
reader commenting on the deal, an owner talking about their own asset, or someone reasoning
from the seller's side of the table. The only question that matters is: **is this person
asking to buy a business through SMB Deal Hunter, or are they talking about something else?**

Both real cases below are from the *same newsletter thread on the same day*, and both were
first logged as Tier 1 "Send to Yobani". Both were wrong.

**Their own asset, not a business.** Jerome M Limage wrote *"I'd like knowing more of the
seller financing with 50% and would want an opted financing on an investment property that I
tend to hold."* That reads as a buyer discussing financing terms until you notice the asset:
his **own investment property, which he intends to keep**. He is not buying a business. →
**Ignore**.

**Commenting from the seller's side.** J LaMacchia wrote *"I would counter offer, to get the
conversation going, with a 50% down payment ($1,250,000) and 2 years funding the balance…
Any serious offer should be via written letter and a $100,000 deposit check with no more than
3 contingencies **and I will remove from the market**."* The first sentence looks like a live
offer. The last clause gives it away — he is talking as an owner about taking a listing off
the market, not asking to buy one. He is commenting on how the deal should be run, and never
asks to speak to anyone. → **Ignore**.

> ⚠️ **The truncated snippet inverted the meaning.** `verbose: false` returns
> `preview.body` cut at roughly 200 characters. J LaMacchia's preview ended at *"Any serious
> offer should be vi…"* — everything that revealed his actual position was past the cut.
> **So: whenever a reply contains deal terms — dollar figures, down payments, financing
> structures, contingencies, deadlines — hydrate the full message with
> `GMAIL_FETCH_MESSAGE_BY_MESSAGE_ID` before classifying it.** Do not classify a
> numbers-heavy reply from a snippet. This is the one category of email where the second
> sentence routinely reverses the first, and it is cheap to check: read the sender's own
> words up to the quoted newsletter and ignore the quoted text below it.

For contrast, a genuine buyer replying to the same kind of newsletter states the ask plainly
and briefly, with no deal analysis at all: *"I'm looking for local business in 94538 area
code, ready to invest"* (Zing Beam LLC), *"Do you have a company like this in Colorado,
preferred in Denver area"* (Christopher Terry), *"Helen I want to buy a business show me."*
(Daniel Spencer). **Length and financial sophistication correlate negatively with buyer
intent here.** The real buyers ask for deals; the commentators explain deals.

**Asking whether a featured deal is still available is buyer intent.** The line this section
draws is between analysing a deal and asking to buy one, not between mentioning a deal and
not mentioning one. *"Is that wellness center in Virginia that you mentioned on X still
available for sale?"* (Damian Olive, 2026-09-10) names a specific listing and asks for it →
**Ready Now**, and it takes its own opening line: see *Which Ready Now template* below.

The related judgement call, recorded because it recurs and has no clean answer: *"You do
great things i am interested to talk to you we own few businesses in albany ny area"*
(narinder Singh, same day). An explicit ask to talk, so Ready Now is defensible — but someone
who already owns businesses may be an operator or a future seller rather than a buyer.
Classify on the ask, flag it in the digest for a human eye, and do not drop it.

#### Price Wall: asking the price vs. not having the money

Both look like Price Wall, and they get opposite actions. Sort on **whether the lead has
told you they lack the funds**, not on whether price came up:

- *"What does it cost?"*, *"I have yet to see what the fees are"* — a live buyer with an
  unanswered question. **Send to Yobani**, with the Price Wall draft that answers it.
- *"I don't have the funds"*, *"that's out of my budget"*, *"I can't afford that right
  now"* — they have disqualified themselves. **Ignore**, no draft.

A statement of not having the money **wins over a pricing question in the same email**.
Real case from 2026-09-09: Andy Garcia wrote *"I am interested but I don't have the funds,
I don't know how much it is."* The second half is a pricing question, but the first half
already settles it → **Ignore**. Sending the 1% answer to someone who has just said they
have no money is the wrong reply.

#### The call-booked rule

Yobani is the setter; his job is to get the call booked. A lead who has already booked one
is not work for him, so passing them along is wasted effort. When an email says the sender
has scheduled a call — "I have a call scheduled", "I have booked a call", "we're speaking
Thursday" — check Close, and if it is confirmed there, write **"Ignore"** instead of "Send
to Yobani".

**Verify in Close before writing "Ignore". Never take the claim at face value** — a sender
can misremember, book with someone else, or have cancelled since writing.

Procedure (verified 2026-09-10):

1. `mcp__Close__lead_search` with `full_text: "<the sender's email address>"`.

   **Match on the email address, never the display name.** Gmail display names and Close
   lead names routinely disagree, and a fuzzy name match produces a confidently wrong
   answer. Real case from this inbox: `christopher green <cjgreen7904@yahoo.com>` is the
   Close lead **"CJ Green"** — but a name search for "christopher green" returns *"Chris
   Green"*, *"Chris Greene"* and *"CJ Green"* as three separate leads, and two of them are
   other people. The email search returns exactly one.

2. Take the `lead_id` from that result and call `mcp__Close__activity_search` with
   `lead_ids: ["<lead_id>"]` and `activity_types: ["activity.meeting"]`.

3. Read `activity_at` / `starts_at` on the returned meetings. Write **"Ignore"** only if a
   meeting is dated **today or later**. A meeting entirely in the past is a call that
   already happened, not the one the sender is describing — that is not a verification.

4. **If any of this fails to confirm** — the email address matches no lead, the lead has no
   meeting, the only meeting is in the past, or the Close lookup errors — leave the action
   as **"Send to Yobani"**. Unverified is not the same as false, and the safe default is to
   let the setter look.

In the final run report, list every lead that claimed a booked call and whether each one
verified. A lead claiming a call that Close doesn't show is worth a human's attention.

Worked examples, both verified 2026-09-10:

| Sender | Claim | Close lead | Meeting found | Action |
|---|---|---|---|---|
| Jim Jacobsen | "I have a call scheduled but I have yet to see what the fees are" | Jim Jacobsen | 2026-09-14 14:00 UTC — Discovery Call | Ignore |
| christopher green (`cjgreen7904@yahoo.com`) | "I am still interested and have booked a call" | **CJ Green** | 2026-09-11 16:00 UTC — Welcome Call | Ignore |

**This rule changes column D only.** It does not change classification: a lead who has
booked a call is still Buy Box / Ready Now / Price Wall on the content of their email,
still appears in the Slack digest under Tier 1, and still gets a tracker row. The
Recommended Action is not shown in Slack.

### Suggested Helen email draft

Every lead whose Recommended Action is **"Send to Yobani"** also gets a ready-to-send
reply draft, so Helen can paste it, cc Yobani, and send. Rows marked "Ignore" and Tracking
Handover Progress rows get **no draft** — leave the cell empty and omit them from the
Slack thread.

🎁 **Bonus claims also get a draft**, and they are the one kind that is not a lead: no
tracker row, no Recommended Action, no cc. Their template is *The bonus reply*, below.

The draft is a **reply in Helen's voice**, cc'ing Yobani Mendoza
(`yobani@smbdealhunter.xyz`, the setter). No subject line, no signature, no greeting
block — Helen is replying inside an existing thread.

**Two drafts do not cc Yobani**: the Price Wall call-pushback variant, which asks the lead's
permission to loop someone in rather than doing it, and the bonus reply, which has nothing
to do with him. Both say so where they are defined. Every other draft cc's him.

#### The templates

Use the template for the lead's category — and, for Ready Now and Price Wall, the variant
that matches what the lead asked for. Each one is a fully written-out message to the lead,
with Yobani mentioned inside it where he is being looped in — not a set of separate notes to
different people. The last template, the bonus reply, is the exception to all of this: it is
not a lead draft at all.

**Write it out in full.** No shorthand: "definitely", not "def"; "15 minutes", not
"15min"; "with you", not "w you". The register is warm and direct, the way Helen writes
when she has thirty seconds — but in whole words.

**Buy Box**

```
Hey [First Name], [their ask] is something we can help with. @Yobani on our team can grab 15 minutes with you to better understand what you're looking for.
```

**Ready Now**

```
Hey [First Name], we can definitely help. Looping in Yobani from our team. @Yobani, do you mind finding 15 minutes to give [First Name] a call?
```

**Ready Now — asking about a specific deal** (use this one instead when the lead is asking
about a deal Helen featured, rather than signalling readiness in general)

```
Hey [First Name], deals like these go pretty quickly, but we can help you move fast. Looping in Yobani from our team. @Yobani, do you mind finding 15 minutes to give [First Name] a call?
```

**Price Wall**

```
Hey [First Name], fair question. For our average member, the cost comes out to roughly 1% of the purchase price that is due upfront. We do have a success guarantee, which we can talk more about live. Let's get you on a quick call — @Yobani on our team can find a time that works for you.
```

**Price Wall — pushing back on the call itself** (use this one instead when the lead is
refusing or questioning the call and asking a list of specific questions about terms; see
*Which Price Wall template* below)

```
Hey [First Name], fair questions, and I appreciate you being direct about it.

Here is why we start with a call. It is not a sales presentation to walk you through standard terms. The call is as much about us making sure you would be a good fit for our community as it is about you vetting us. We offer a guarantee to our members, and we cannot offer that to everyone, so we are selective about who we bring in. That is not something we can figure out over email.

So it is a two way thing, and that is why we do not get into the details until there is mutual fit on both sides.

Let me know if you're still interested and want me to loop someone from our team in.
```

The `@Yobani` is literal text in the body of an email, not a Slack or Gmail mention. It
reads as a nudge to him because he is cc'd.

**The bonus reply** — for 🎁 bonus claims only, not for any lead category. Word for word
what Helen's automation sends, so a member who got it late cannot tell the difference:

```
Hey - thanks so much for joining! Here's the link to the bonuses: https://smbdealhunter.notion.site/SMB-Deal-Hunter-Welcome-Bonuses-18b3787936d0805eb0b4c1a88c7d2c40
```

The automation hyperlinks the word "link" rather than showing the URL; in a Slack code block
the URL has to be visible, and either form is fine to send as long as the link is there. No
first name, no personalisation, nothing added — it opens "Hey -" exactly as the automation
does. Yobani is not cc'd on this one.

#### Filling them in

**First name.** In order of preference: the name the sender signs off with in the email
body, then the first word of their Gmail display name. If the sender has **no display
name** — a bare address like `ms.raquele@gmail.com` — do not guess a name out of the
address. Drop the name and open with `Hey there,` instead. Getting someone's name wrong in
the first three words is worse than not using it.

**Pronouns.** The templates address the lead directly as "you" for exactly this reason.
Never infer a lead's gender from their name; where a third-person reference is
unavoidable, use they/them unless the sender's own signature makes it explicit.

**Their ask (Buy Box).** `[their ask]` is the concrete thing they asked for, phrased as a
gerund and in their own words: "finding deals in Central FL", "finding hotels in
California", "finding absentee businesses". If their ask is too vague to name in three or
four words, use "that" — *"Hey Scott, that is something we can help with."* Never inflate
a vague ask into a specific one.

Ready Now and Price Wall take no personalisation beyond the first name. Do not restructure
a template to suit the email.

**Which Ready Now template.** Ready Now covers two different asks, and they open
differently:

- **A readiness signal in general** — a phone number, "call me", "enroll me", "I want to buy
  a business", a reply that says they are ready without naming anything. → the plain
  **Ready Now** template.
- **A question about a specific deal Helen featured** — in the newsletter, on X, or in prior
  outreach: *"is that wellness center in Virginia still available?"*, *"is the laundromat
  still for sale?"*, *"tell me more about the $280K/yr biz"*. → the **specific deal**
  template.

Real case, 2026-09-10. Damian Olive wrote *"I'm a business owner based in Arlington,
Virginia. Question: is that wellness center in Virginia that you mentioned on X still
available for sale?"* Helen's reply went out on the plain Ready Now template the next
morning. Sheila's call is that a lead asking about one specific listing should hear the
scarcity first — it is true, and it is what moves someone who has already picked a deal out
of the newsletter.

**Do not answer the availability question.** The template says nothing about whether the
deal is still on the market, and neither should you: this task does not know, and a wrong
answer in either direction costs the lead. *"Deals like these go pretty quickly"* is the
whole of what gets said about it, and the call handles the rest — the same bar as every
other draft, no price, no deal specific, no timeline the template does not carry.

Damian also opened with *"I'm a business owner"*. That does not move him out of Ready Now —
classify on the ask, the same judgement as narinder Singh in STEP 2.

**Which Price Wall template.** Price Wall also covers two different asks, and the answers
are close to opposite:

- **Price came up, in passing** — *"what does it cost?"*, *"I have yet to see what the fees
  are"*. They have not objected to a call; they just want the number. → the plain **Price
  Wall** template, which gives them the 1% answer and moves to a call.
- **They are pushing back on the call itself** — questioning why a call is needed before
  they can see terms, and asking a list of specific questions about price, fees, contract
  terms, refunds, or what exactly is included. → the **call-pushback** template, which does
  not answer any of them.

Real case, 2026-09-10. W. Stephen Aldridge wrote eight numbered questions — total membership
price and payment terms, additional fees, what the one-on-one assistance includes, deal flow
in the Southeast, exclusivity, the cancellation and refund policy, the written terms of the
closing guarantee, and whether an experienced buyer can enrol without the introductory call
— and framed the whole thing as *"Requiring a preliminary phone call feels inefficient if
its principal purpose is to explain standard terms or provide the price."* He is a real
buyer: an experienced operator who has evaluated acquisitions before and says he is
seriously interested. The plain Price Wall template would have answered one of his eight
questions with the 1% line and then asked him onto the call he had just objected to.

**The call-pushback template deliberately answers none of the questions**, including the
price. That is the whole point of it: the position it states is that the call comes before
the details, so quoting the 1% figure in the same message contradicts the message. **Do not
import the 1% line into this template**, and do not append answers to any of the numbered
questions, however well you think you know them.

**It does not cc Yobani either.** Its last line asks whether the lead wants someone looped
in, so looping him in pre-emptively contradicts that too. The forward follows their reply.

⚠️ **Flag this one for Helen's eye.** The emails that earn this template are long, specific
and often from sophisticated buyers, and the reply is a considered position rather than a
one-liner — she may want to adjust it for the particular person. Mark it in the Slack thread
as needing her review before sending. Every other draft is paste-and-send; this one is a
starting point.

The lead is still **Price Wall**, still **Send to Yobani**, and still gets a tracker row and
a Yobani draft in column N. Only Helen's opening move changes.

**Never invent commercial terms.** The 1% figure appears in the plain Price Wall template
and nowhere else — not even in the call-pushback variant, which is a Price Wall draft that
deliberately withholds it. The guarantee is named, without terms, in both Price Wall
templates. Do not quote a price, a fee, a range, a guarantee, a timeline, or a deal specific
in any other draft, do not elaborate on the 1% beyond the sentence given, and do not state
what the guarantee actually promises — even if the lead asked a direct question about either.
If a lead asks something the template does not answer, send the template as-is and let the
call handle it.

**Nothing else goes in.** A finished lead draft should be the template plus a first name
and, for Buy Box, their ask — and nothing more. The bonus reply takes no substitutions at
all. If a draft says something the template does not, take that back out.

### Suggested Yobani response

Produced in the **same run as Helen's draft, for the same leads**, and written to tracker
column N (`Suggested Yobani 1st Response`).

Everything here is Yobani's **day-1 response**: the first contact he makes after Helen
forwards her reply. Later touches are not covered here — `tracker-followup` owns those.

This draft used to be written days later, by the `tracker-followup` pass, once Helen's
forward had been confirmed and Close showed no call. That left every new row half-ready:
Helen's handoff was one paste away on day one, and Yobani's reply did not exist until a
later pass picked the row up. Both drafts now come out of this run, so a lead's whole path
is written the morning it arrives.

**Same gate as Helen's draft.** Every lead whose Recommended Action is `Send to Yobani`
gets one. `Ignore` rows and Tracking Handover Progress rows get none — leave M empty, and
omit them from the Slack thread. 🎁 Bonus claims are not leads and have no row, so there is
nothing to write: they get no Yobani draft at all.

**The draft is provisional, and writing it resolves nothing.** At digest time the lead has
not been forwarded yet and no setter-call check has run for them. `tracker-followup` still
runs that check on a later pass and remains the authority: when Close shows a setter call,
it **clears** M rather than leave a stale "let's grab 15 minutes" pointed at someone who has
already had their call. Writing M here does not mark the row handled and does not exempt it
from the follow-up pass.

#### When it goes out

As soon as Helen forwards. Yobani replies on the **same thread**, with Helen kept on it — so
the handoff stays tracked. Not a fresh email: the lead has been talking to Helen, so the
reply picks up from her rather than introducing a stranger.

#### What day 1 is

An **email, and a phone call** if he has a number to call.

| Phone number in their initial email? | Day 1 |
|---|---|
| Yes | Email, then call them — today or tomorrow |
| No | Email only. Buy Box and Price Wall ask for the number; Ready Now sends the Calendly link instead |

**No texting on day 1.** If he has the number he calls; if he doesn't, there's nothing to
text. Either way the text is redundant.

"Number provided" means a number in the **initial email they sent** — a signature block
counts, a number dug out of the CRM or the web does not. This task is reading that email
already, so settle the branch while writing the draft rather than leaving the choice to
whoever pastes it.

#### Reading the templates

The `[If they …]` blocks are instructions, not copy. Pick the branch that matches the row,
write out that sentence, and delete the marker and the brackets around it. The other branch
disappears. **A draft that still contains the words "If they" has not been finished.**

`[today/tomorrow]` is pick-one, not literal text.

#### The three templates

One per category. Use the template for the row's category — the same category that chose
Helen's draft.

**There are no variants here.** Helen's Ready Now and Price Wall drafts each have two
openings; Yobani's have one apiece.

- A lead who asked about a deal Helen featured takes the plain Ready Now template below,
  with `[their own words]` set to the deal they named — *the wellness center in Virginia*.
  The scarcity line is Helen's opening only.
- A lead who pushed back on the call takes the plain Price Wall template below, unchanged.
  Helen's reply to them asks whether they want someone looped in, so Yobani's draft may sit
  unused for longer than most — that is expected, and `tracker-followup` still owns column N
  from there.

**Buy Box**

```
Hi [First Name],

Sounds like you're interested in [buy box criteria], and I'd love to hop on a call to get precise on your box and figure out how SMB Deal Hunter can help kickstart your business buying journey.

[If they didn't provide a number: What's the best number to reach you at?] I will give you a call [today/tomorrow]. Alternatively, find a time slot that works for you here [Calendly Link].
```

**Ready Now**

```
Hi [First Name],

Picking up from Helen, sounds like you're ready to move on [their own words], so let's not waste time. [If they provided a number: I will give you a call [today/tomorrow].] [If they didn't provide a number: Grab 15 minutes here: [Calendly Link].]

I want to get sharper on where things stand and figure out the fastest next step.
```

Ready Now is the one category that **doesn't ask for a number** when it's missing — it sends
the link. That's deliberate; don't borrow the Buy Box line to "fix" it.

**Price Wall**

```
Hi [First Name],

Let's grab 15 minutes so I can get a better sense of your situation and make sure SMB Deal Hunter is the right fit for what you're looking to do. [If they didn't provide a number: What's the best number to reach you at?] I can give you a call [today/tomorrow]. Alternatively, book a time with me here [Calendly link].
```

#### Placeholders

- `[First Name]`, `[buy box criteria]`, `[their own words]` — filled in when the draft is
  written, per the rules below.
- `[Calendly Link]` — stays a literal bracketed placeholder; Yobani fills it in before
  sending.
- `[today/tomorrow]` — stays bracketed too, and Yobani picks one before sending. This task
  has no way to know which day he is free.

**There is no `[time slot]` placeholder any more.** The templates commit to a call today or
tomorrow rather than proposing a window, so nothing needs slotting. This also retires the
old reason for leaving it blank: Sheila's Calendly token is role `user` and cannot read
Yobani's event types or availability (`event_types-list_event_types` returns Permission
Denied for another user), so any time proposed here would have been invented. That constraint
still applies to `[Calendly Link]` — do not substitute a real link. His scheduling page is
`https://calendly.com/yobani-smbdealhunter` if this is ever revisited, but leave the
placeholder unless Sheila says otherwise.

Say in the Slack thread that `[Calendly Link]` and `[today/tomorrow]` both need filling
before sending, so nobody pastes a draft with a bracket still in it.

**First name.** Resolved exactly as for Helen's draft: the name the sender signs off with,
else the first word of their Gmail display name, else — for a bare address like
`ms.raquele@gmail.com` — open with `Hi there,` and drop the name.

**Pronouns.** The templates address the lead as "you" for this reason. Never infer a lead's
gender from their name; where a third-person reference is unavoidable, use they/them unless
the sender's own signature makes it explicit.

**`[buy box criteria]`** (Buy Box) — the concrete thing they asked for, in their own words,
phrased to follow "interested in": `hotels in California`, `deals in Central FL`, `absentee
businesses`. Note this reads differently from Helen's `[their ask]`, which is a gerund
("finding deals in Central FL"); do not paste one into the other. If the ask is too vague to
name in a few words, write `what we've got` rather than inflating it into a specific.

**`[their own words]`** (Ready Now) — a short quote or close paraphrase of their stated
readiness, from the email or the message summary: `buying a business`, `the Bethlehem PA
deal`, `the 50% seller financing terms`. Never invent a deal, a location or a number they
did not mention.

#### What day 1 never does

No price, fee, range, guarantee or timeline — including in Price Wall, which moves to a call
and nothing else. **The 1% line is Helen's and hers only**; it sits a few hundred lines above
in this same file, and importing it here would put a commercial commitment in a message that
is supposed to be an invitation. If a lead asked a direct pricing question, Helen's reply
answers it and the call handles the rest.

**Nothing else goes in.** A finished draft is the template plus the substitutions above, with
every `[If they …]` branch resolved. If it says something the template does not, take that
back out.


### On borderline mail

If you cannot confidently place an email in one of the three categories, **drop it**. There
is no Uncategorized bucket to park it in. The bonus check above is the one thing this does
not override: run it on a bare "Yes" before dropping, since a bare "Yes" is by definition not
placeable in a category and would otherwise never survive this rule. This is a deliberate trade: the digest stays
short and unambiguous, and the cost is that an occasional vaguely-worded buyer reply gets
missed. Lean toward including a genuine buyer signal you're 70% sure of; drop anything
below that rather than inventing a category for it.

Note the historical exception that no longer applies: Kyle Hopkins / Hunter Equity Partners
threads used to be force-classified as Investor to stop them being misread as Ready Now.
Investor is no longer tracked, so these threads are simply dropped — but keep the
underlying caution in mind. A phone number or "give me a shout" inside a Hunter Equity /
data-room thread is **not** a Ready Now buyer lead, and must not be pulled into Tier 1 on
the strength of that phrasing.

---

## STEP 3 — Post ONE Slack digest

Post to channel ID `C0BTCGZSF9R` (#helen-email-digest):

- **Header:** date + total count of leads found (the post-drop count, not raw inbox volume)
- **🔴 Tier 1** — bold header, categories as sub-bullets in this exact format:
  `*Category* — Sender: "subject line" — snippet`
  with the subject line as the Gmail thread link. Do NOT include the recommended-action
  field in the visible digest text, even when it's set internally.
- **🟢 Tracking Handover Progress** — same bullet format, with owner inserted right after
  the category:
  `*Category* — Owner: Name — Sender: "subject line" — snippet`
- **🎁 Bonus link not sent** — bare "Yes" replies whose thread has no canned response, one
  bullet each: `Sender — replied "Yes" to "subject line"`, the subject as the Gmail thread
  link. Keep it last and keep it short: it is a chore list, not a lead list. Say in the
  header line that the automation missed these because the reply landed on the wrong email.
- These are the only three sections. Skip any of them entirely if it has zero entries.
- If there were zero tracked leads and zero bonus claims in the last 24h, post a short "No
  new buyer leads in Helen's inbox today" message instead.
- Use Slack mrkdwn formatting (bold, bullets). Do NOT use `@channel` or `@here`.

### The drafts go in a thread under that message

Post the reply drafts as **one threaded reply** to the digest message, not in the message
body. Five or six full drafts inline would bury the lead list the digest exists to
deliver; in the thread they are one click away and still copy-pasteable.

Capture the parent message's `ts` when you post it and reply with that as `thread_ts`.

Thread reply format — one block per lead whose action is "Send to Yobani", in the same
order as the Tier 1 list, then one block per 🎁 bonus claim. **Each lead now carries both
drafts**: Helen's reply, and the reply Yobani sends once she has forwarded it. Put each draft
in its own Slack code block so it copies cleanly, and label whose it is — the two are sent by
different people at different times, and an unlabelled pair invites Helen to paste the wrong
one. A bonus claim carries one draft and no Yobani block.

Two drafts need a word of warning next to them, because pasting them blind is the failure
mode:

- A **Price Wall call-pushback** draft → prefix it with `⚠️ Needs Helen's review — long,
  specific email; this reply deliberately answers none of it.` It is also the one lead draft
  with no cc, so say `Do not cc Yobani on this one.`
- A **bonus claim** draft → say the automation missed this one and Yobani is not involved.

> ✍️ *Suggested replies* — Helen's to send now, cc yobani@smbdealhunter.xyz. Yobani's is
> for after the forward, as a reply on the same thread with Helen kept on it.
> **Fill in `[Calendly Link]` and `[today/tomorrow]` before sending Yobani's** — and call
> them the same day if they gave a number.
>
> *Buy Box — Dean Julia*
> Helen:
> ```
> Hey Dean, finding deals in Central FL is something we can help with. @Yobani on our team can grab 15 minutes with you to better understand what you're looking for.
> ```
> Yobani:
> ```
> Hi Dean,
>
> Sounds like you're interested in deals in Central FL, and I'd love to hop on a call to get precise on your box and figure out how SMB Deal Hunter can help kickstart your business buying journey.
>
> What's the best number to reach you at? I will give you a call [today/tomorrow]. Alternatively, find a time slot that works for you here [Calendly Link].
> ```
> *(Dean gave no number, so the Buy Box "best number" branch is written out. Had he given
> one, that sentence would be gone and the line would open at "I will give you a call".)*
>
> 🎁 *Bonus link — Jason Smith* — replied "Yes" to a newsletter, so the automation never
> fired. Helen's to send; Yobani is not involved.
> ```
> Hey - thanks so much for joining! Here's the link to the bonuses: https://smbdealhunter.notion.site/SMB-Deal-Hunter-Welcome-Bonuses-18b3787936d0805eb0b4c1a88c7d2c40
> ```

If no lead has action "Send to Yobani" and there are no bonus claims, post no thread reply
at all — not an empty one.

Yobani's draft is posted here as a preview of what is waiting in column N, not as something
to send today — the lead has not been forwarded yet. Do not tag or DM him from this task;
the `tracker-followup` pass is what surfaces a row once it is actually his.

---

## STEP 4 — Log to the Google Sheets tracker

Tracker: https://docs.google.com/spreadsheets/d/1auWB8iQAwTYQrKhgHhb-paUuCH35j35RDiQdSC5uhBQ/edit
Spreadsheet ID: `1auWB8iQAwTYQrKhgHhb-paUuCH35j35RDiQdSC5uhBQ`

Add ONE new row per email that appeared in the Slack digest — Tier 1 rows and Tracking
Handover Progress rows. Nothing else gets a row. What was dropped in Steps 1–2 is not
logged.

**🎁 Bonus claims get no row**, even though they appear in the digest. They are the one thing
this task surfaces that is not a lead: nothing to chase, no stages to move through, no owner
to flip. A row for one would sit permanently due and would either nag Helen forever or be
skipped forever. The Slack thread is the whole record.

**The cost of that, stated plainly:** STEP 1 reads `newer_than:1d`, so a bonus claim is
surfaced on the day it arrives and never again. If nobody acts on that thread reply, that
member does not get their bonuses and nothing will raise it a second time. This is the
accepted trade for keeping a customer chore out of a buyer-lead pipeline. If it turns out to
be missed in practice, the fix is a tracker row or a separate list — not a wider digest
window.

### Sheet layout — verified 2026-09-10

The spreadsheet has **two tabs**: `Tracker` (the data) and `Responsibility` (the lookup).

**`Tracker` tab.** Row 1 is the header. Data starts at **row 2**. As of 2026-09-11 the last
data row is **row 32** (31 rows). **The sheet runs to column W** — the layout was changed
twice on 2026-09-11, so any column letter you remember from before that date is wrong.
Columns A–W:

`Date | Tier | Category | Recommended Action | Forwarded to Yobani? | Owner | Last Check-in Date | Next Check-in Date | Email Sender | Email Title / Link | Message Summary | Suggested Helen Email Draft | Helen Forward Date | Suggested Yobani 1st Response | Yobani 1st Response Done? | Yobani 3-day follow-up date | Yobani 3-day follow-up done? | Yobani 5-day follow-up date | Yobani 5-day follow-up done? | Setter Call Date | Setter Progress | Closer Call Date | Closer Progress`

What moved on 2026-09-11, stated as a map so nothing is written to the wrong cell. The
sheet went A–Q → A–V → A–W in two edits the same day; only the final column is the one to
write to.

| Was (A–Q) | Is now (A–W) | What changed |
|---|---|---|
| A–D | A–D | unchanged |
| E Action Taken? | **E** Forwarded to Yobani? | renamed |
| F–L | F–L | unchanged |
| — | **M** Helen Forward Date | new |
| M Suggested Yobani Response | **N** Suggested Yobani 1st Response | moved one right, renamed |
| — | **O** Yobani 1st Response Done? | new |
| — | **P–S** the 3-day and 5-day follow-up columns | new |
| N–Q Setter/Closer | **T–W** Setter/Closer | moved six right |

**Column E was renamed, not repurposed.** `Action Taken?` → `Forwarded to Yobani?` names
the question it was always answering: has Helen handed this lead to Yobani. Same `Yes`/`No`
values, same rule for this task (`No` on Tier 1 rows, `Yes` on Tracking Handover Progress
rows), and column F still keys off `E="No"`. The rename matters because there is now a
second, easily confused "is it done?" column — **O**, which asks whether *Yobani* replied.
E is Helen's action; O is Yobani's.

Column **L — "Suggested Helen Email Draft"** was added 2026-09-10 and is empty for every
row before then. That is expected; do not backfill it.

**Column N — "Suggested Yobani 1st Response" — is written by this task too**, as of the
change that moved Yobani's draft forward into the digest run. It used to be filled in days
later by `tracker-followup`. That task still owns N on every later pass — it revises the
draft when one is missing — but on a row this task creates, N arrives populated. Like L, it
is empty on every row logged before the change and is not backfilled. It was called
"Suggested Yobani Response" and sat in column M until 2026-09-11; the rename to **1st**
marks it as the opening message in a three-touch sequence, not a new field.

**Drafts in L and N are never deleted.** Confirmed with Sheila on 2026-09-11: once a draft
is written it stays, whatever happens to the lead afterwards. `tracker-followup` used to
clear N when a setter call showed up in Close; **that rule is gone.** A draft sitting next
to a completed call is not a bug — the `done?` columns are what say whether it was acted
on, and the draft is kept as a record of what was offered.

**Column M — "Helen Forward Date" — is not this task's to write.** It records the date
Helen *actually* forwarded the lead to Yobani, verified from the thread — not the date the
handover was recommended. `tracker-followup` writes it on the pass where it confirms the
forward and flips Forwarded to Yobani? to `Yes`. On a row this task appends, M is **empty**,
which is correct: at logging time the forward has not happened yet.

**Column O — "Yobani 1st Response Done?" — is not this task's either.** It is `Yes` once
Yobani has **actually sent a reply to the prospect**, `No` until then — those two values
only, no third state and no free text. It is not a copy of E: Helen can forward a lead
(E = `Yes`) and Yobani not get to it for days (O = `No`). On a row this task appends, O is
**empty**.

> **The O values in the sheet today are a one-off backfill, not observed data.** Sheila set
> O = `Yes` on every forwarded row on 2026-09-11 because Yobani reported he had cleared
> everything Helen had sent him at that point. That is why O currently matches E exactly on
> all 31 rows. It will not stay true, and nothing should infer "forwarded ⇒ responded" from
> it.

**Columns P–S are the Yobani follow-up cadence**, and they hang off M. P (`=M+3`) and R
(`=M+5`) are **formulas**, filled down like F and H — see below. Q and S are the matching
`done?` flags, owned by `tracker-followup`. This task never writes Q or S.

**T–W** (`Setter Call Date`, `Setter Progress`, `Closer Call Date`, `Closer Progress`)
belong to `tracker-followup`, which fills them in on later passes. This task writes
**A–L and N**, fills down the four formula columns (F, H, P, R), and leaves M, O, Q, S and
T–W empty on the rows it appends. Do not widen this task's writes into them, and do not
"fix" them when they are blank on a new row — they are meant to be.

**`Responsibility` tab.** The `Category → Owner` lookup lives here, in `A2:B9`. Buy Box,
Ready Now and Price Wall all map to **Yobani**; the other rows (Sellside → Bill, Investor
and Operators → Kyle, Pitches and Engaged Reader → Helen) are now unused by this routine
but must be left in place — the `xlookup` range is absolute and shrinking it would break
column F. It is **not** below the data block on `Tracker`, so appending to `Tracker` cannot
collide with it. (An earlier handoff doc claimed row 1 was blank with the header on row 2,
and that the lookup sat below the data — both are wrong. Trust this section.)

**Columns F, H, P and R are formula-driven. Never write literal values to them.** The
formulas, read verbatim from row 2:

- **F (Owner):** `=if(E2="No","Helen",xlookup(C2,Responsibility!$A$2:$A$9,Responsibility!$B$2:$B$9))`
  — rows where Forwarded to Yobani? is "No" resolve to Helen regardless of category; only
  handed-over rows get the category's owner. Since all three tracked categories map to
  Yobani, in practice column F now reads Helen for Tier 1 rows and Yobani for handover
  rows.
- **H (Next Check-in Date):** `=G2+1` — the day after the last check-in, so an open lead
  comes due on every follow-up pass. (This was `=G2+5` until 2026-09-11.)
- **P (Yobani 3-day follow-up date):** `=M2+3` — three days after Helen's forward.
- **R (Yobani 5-day follow-up date):** `=M2+5` — five days after Helen's forward.

P and R read `3` and `5` on every row where M is still empty. That is the formula doing
arithmetic on a blank cell, not a stray literal — leave it. Both light up as real dates the
moment `tracker-followup` writes the forward date into M.

Dates in A and G are stored as Google serial numbers and displayed as dates; writing a
plain `9/11/2026` string with `valueInputOption: "USER_ENTERED"` is coerced correctly.

Column J is inconsistent in the existing data: rows 2–5 hold plain quoted subject text,
rows 6–27 hold `=HYPERLINK(...)`. Write new rows as `=HYPERLINK(...)`, matching the
majority and the documented format.

### How to write

1. `GOOGLESHEETS_GET_SHEET_NAMES` to confirm the tab is still called `Tracker`.
2. `GOOGLESHEETS_VALUES_GET` on `Tracker!A:W` to read existing rows and find the true last
   data row. Compute your target range explicitly rather than relying on the append API's
   table detection.
3. **Dedup.** Before writing a row, check it isn't already in the sheet (same sender + same
   subject + same date, e.g. a recurring broker broadcast logged earlier the same day).
   Skip duplicates rather than creating a second row.
4. Write with `GOOGLESHEETS_VALUES_UPDATE` at explicit ranges, in three blocks, so F and H
   are never overwritten with literals:
   - `Tracker!A<first>:E<last>` — Date, Tier, Category, Recommended Action, Forwarded to Yobani?
   - `Tracker!G<first>:G<last>` — Last Check-in Date
   - `Tracker!I<first>:L<last>` — Email Sender, Email Title / Link, Message Summary,
     Suggested Helen Email Draft
   - `Tracker!N<first>:N<last>` — Suggested Yobani 1st Response

   **Skip column M.** The Helen Forward Date belongs to `tracker-followup` and must stay
   empty on a new row, so it gets its own gap in the write rather than being swept up in a
   range ending at N. The old single block `I:M` now lands the Yobani draft in the wrong
   column — do not use it.

   Use `valueInputOption: "USER_ENTERED"` so dates coerce and `=HYPERLINK(...)` renders.
5. **Fill down F, H, P and R** by writing the same four formulas into the new rows with
   their row references incremented — for a new row `<n>`:
   - F: `=if(E<n>="No","Helen",xlookup(C<n>,Responsibility!$A$2:$A$9,Responsibility!$B$2:$B$9))`
   - H: `=G<n>+1`
   - P: `=M<n>+3`
   - R: `=M<n>+5`

   The lookup ranges are absolute (`$A$2:$A$9`) and must stay exactly as written; only the
   `E<n>`, `C<n>`, `G<n>` and `M<n>` references change. Never invent a different formula.
   P and R go in as formulas even though M is empty — they are meant to sit dormant until
   the forward date arrives.
6. **Verify.** Re-read `Tracker!A:W` and confirm: row count increased by exactly the number
   of rows you wrote, F and H are populated and did not spill `#N/A`, P and R hold their
   formulas, L and N landed on exactly the "Send to Yobani" rows and are empty on the
   others, M/O/Q/S and T–W are empty on every new row, and no row was duplicated. If
   verification fails, say so explicitly in Slack — do not report success.

### Column contents

- **Date** — today's digest date
- **Tier** — `1` for Tier 1 rows, `In Progress` for Tracking Handover Progress rows. These
  are the only two values this routine writes. (Historical rows also contain `2`, `3` and
  `Uncategorized`; leave them alone.)
- **Category** — `Buy Box`, `Ready Now`, or `Price Wall`. No other value.
- **Recommended Action** — `Send to Yobani` or `Ignore`, decided in STEP 2. Not a fixed
  lookup from the category: read the actual email. "Ignore" covers a lead who has
  disqualified themselves *and* a lead whose booked call you verified in Close — the
  call-booked rule in STEP 2 governs, including its requirement to match Close leads by
  email address rather than name.
- **Forwarded to Yobani? (E)** — "Yes" for Tracking Handover Progress ("In Progress") rows,
  "No" for Tier 1 rows. Called `Action Taken?` before 2026-09-11; the values and the rule
  are unchanged. It answers whether **Helen** forwarded — not whether Yobani replied, which
  is column O.
- **Owner (F)** and **Next Check-in Date (H)** — formula-driven, see fill-down above
- **Last Check-in Date** — the last date anyone at SMB Deal Hunter actually replied to this
  sender. If there's no reply yet (true for most brand-new Tier 1 leads), use today's
  digest date.
- **Email Sender** — same sender name used in the Slack digest
- **Email Title / Link** — `=HYPERLINK("<gmail thread link>","<subject>")` so it renders as
  a clickable link like the existing rows
- **Message Summary** — same quoted snippet used in the Slack digest
- **Suggested Helen Email Draft (L)** — the draft from STEP 2, byte-identical to the one
  posted in the Slack thread. Write it as plain text with real line breaks, not a formula
  and not wrapped in quotes. Leave the cell **empty** for "Ignore" rows and for Tracking
  Handover Progress rows.
- **Helen Forward Date (M)** — **leave empty.** Owned by `tracker-followup`, which writes
  the date Helen actually forwarded the lead once it has confirmed the forward. The
  follow-up cadence in O–R keys off this cell, so a guessed or optimistic date here starts
  a chase clock for a handover that never happened.
- **Suggested Yobani 1st Response (N)** — the Yobani draft from STEP 2, byte-identical to
  the one posted in the Slack thread, with `[Calendly Link]` and `[today/tomorrow]` still as
  literal placeholders and every `[If they …]` branch already resolved. Same format rule as
  L: plain text with real line breaks, no formula, no surrounding quotes. Same gate as L too
  — **empty** for "Ignore" rows and for Tracking Handover Progress rows. A row gets both
  drafts or neither; L populated with N blank on a "Send to Yobani" row is a bug worth
  reporting in Slack. This is the *first* of three touches; the 3-day and 5-day follow-ups
  are tracked as dates and status only, and **no draft is written for them** — there is no
  column for one and this task does not generate one.
- **Yobani 1st Response Done? (O)** — **leave empty.** Owned by `tracker-followup`. `Yes`
  only once Yobani has actually sent a reply to the prospect, `No` until then — those two
  values, nothing else. Never mirror E into it.
- **Yobani 3-day / 5-day follow-up dates (P, R)** — formula-driven, see fill-down above
- **Yobani 3-day / 5-day follow-up done? (Q, S)** — **leave empty.** Owned by
  `tracker-followup`. The allowed values are `Yes`, `No`, and `Not Needed - Connected`
  (used when the lead is already connected and the touch is moot) — no other text, and no
  free-form notes. Note these take a third value that O does not.
- **Setter/Closer columns (T–W)** — **leave empty.** Owned by `tracker-followup`.

Match the formatting of the existing rows exactly — do not reformat the sheet, resize
columns, or change header styling.

---

## Scope limits

Do not take any action beyond reading emails, reading Close CRM, posting the Slack digest,
and logging rows to this tracker. Specifically: do **not** reply to, label, archive, or
delete any email, and do **not** create, update, or delete anything in Close — the
call-booked check in STEP 2 is a read, and Close access stays read-only. The routine is
read-only on email.

## Failure reporting

If any step fails, post what actually happened to `C0BTCGZSF9R` — the failing step, the
tool that errored, and the error text. Never post a success digest for a run that only
partly completed, and never assert a cause you have not verified.
