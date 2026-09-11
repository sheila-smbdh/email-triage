# Handoff — Helen Email Digest, rebuilt on Composio and running in the cloud

| | |
|---|---|
| **Supersedes** | `2026-09-10 helen email digest gmail blocked.md` — the blocked-state handoff. That document is now historical, and two of its factual claims were wrong (see §6). |
| **Status** | Live. Access restored, scope narrowed, cloud Routine enabled and verified end-to-end on 2026-09-10. |
| **Last updated** | 2026-09-11 — Yobani's draft moved forward into this task and then rewritten to the day-1 rules; Helen's Ready Now and Price Wall drafts each gained a second variant; bonus claims added as the one non-lead the digest surfaces (§4). Sheet re-mapped to **A–V** — the Yobani draft is now column **N**; see the sheet-layout section. |

---

## 1. What this is

SMB Deal Hunter runs a daily task that reads new mail in Helen's inbox
(`helen@smbdealhunter.xyz`), picks out buyer leads, posts one digest to Slack
`#helen-email-digest`, and logs one row per lead to a Google Sheets tracker.

It produced no real digest between 2026-08-29 and 2026-09-10, posted the same misleading
failure notice 8 times, and was disabled on 2026-09-10. It has now been rebuilt.

Two things changed in the rebuild:

1. **Access moved to the Composio connector**, which resolves the outage.
2. **Scope narrowed to buyer leads only** — Buy Box, Ready Now, Price Wall.

The task definition lives at
[`skills/helen-email-digest/SKILL.md`](../skills/helen-email-digest/SKILL.md) in this
repository. That file is the single source of truth; the Routine reads it at run time
rather than carrying its own copy.

---

## 2. The outage, and what actually caused it

The old routine used the first-party Gmail connector, which authenticates as exactly one
mailbox — `sheila@smbdealhunter.xyz` — and whose `search_threads` tool exposes no
mailbox-selection or delegation parameter. It could not reach Helen's mail.

The previous handoff framed this as an open question between two causes (A1: Gmail
delegation lapsed; A2: the OAuth grant is scoped to Sheila's mailbox only). **A2 was
correct.** The first-party connector has no mechanism by which delegation could have helped
— web-UI delegation does not propagate to OAuth API scopes. The 8/29 run that worked did so
by a different route: the Gmail deep links in the 8/29 tracker rows carry a
`/mail/u/0/d/<delegation-token>/` path, i.e. that run read Helen's mail through Sheila's
delegated *browser* view, not through the API connector.

The fix was therefore not to repair delegation but to change connector. Composio holds a
direct OAuth grant against Helen's mailbox.

**The failure notice was the second problem.** The old task file hardcoded a specific
diagnosis — "Sheila needs to accept the pending delegated-access request from Helen" — and
posted it verbatim 8 times. That diagnosis was wrong, and it sent the team looking at Gmail
delegation settings for over a week. The new file posts the connection status it actually
observed and asserts no cause it has not verified. **Do not reintroduce a hardcoded
diagnosis into a failure path.**

---

## 3. Access, as verified on 2026-09-10

Every row below was confirmed with a live call, not inferred from configuration.

| Purpose | Route | Identifier | Verified by |
|---|---|---|---|
| Read Helen's mail | Composio `gmail` | `gmail_kath-tiou` → `helen@smbdealhunter.xyz` | `GMAIL_FETCH_EMAILS` on `in:inbox newer_than:1d` returned real mail |
| Post the digest | Slack connector | channel `C0BTCGZSF9R` (#helen-email-digest) | connector connected and enabled |
| Read/write tracker | Composio `googlesheets` | `googlesheets_gyte-urlar` (alias `helen-tracker`) | read `Tracker` and `Responsibility` tabs back |
| Verify booked calls | Close connector (`mcp__Close__*`), read-only | — | `lead_search` + `activity_search` confirmed live meetings for two leads |

Two Gmail accounts are connected to Composio — Helen's and Sheila's — so **account
selection is required on every Gmail call**. Helen's is currently the default, but that is
a flippable setting and the task file pins the account id explicitly. If someone ever sees
a digest full of Sheila's mail, this is the first thing to check.

The `googlesheets` connection was authorized as `sheila@smbdealhunter.xyz`. If Sheila's
edit access to the tracker changes, Step 4 breaks — the failure will surface in Slack.

---

## 4. Scope: buyer leads only

The routine tracks **three categories**, all of which were previously Tier 1:

- **Buy Box** — volunteers geography/industry/budget/financing criteria, asks for matching deals
- **Ready Now** — phone number, explicit call ask, enrollment language, or clear readiness on a specific deal
- **Price Wall** — asks pricing/cost directly without booking a call

Plus **Tracking Handover Progress**: threads *in those three categories* that Helen has
already handed off to a teammate.

Everything else is dropped — not digested, not logged, not counted. That means the
following are gone: Bleeding, Sellside, Investor, Operators, Pitches, Engaged Reader, and
the "Uncategorized / needs review" bucket.

The Slack digest therefore has exactly two sections: 🔴 Tier 1 and 🟢 Tracking Handover
Progress.

**Consequences accepted deliberately, recorded so nobody re-opens them by accident:**

- **A handed-off thread outside the three categories disappears.** Handover tracking
  follows the tracked categories rather than widening them. Kyle's Hunter Equity threads no
  longer appear anywhere in the digest.
- **There is no safety net for borderline mail.** With no Uncategorized bucket, anything
  that can't be confidently placed is dropped. The task file sets a ~70% confidence
  threshold. An occasional vaguely-worded buyer reply will be missed.
- **Complaints go unsurfaced.** Bleeding covered existing customers complaining about a
  setter, billing, or an unanswered reply. Nothing in this routine surfaces those now.

**What this would have done to the 8/29 run** — re-scoring the 26 existing tracker rows
against the new rules gives **10 rows instead of 26**: 8 Tier 1 (2 Buy Box, 5 Ready Now,
1 Price Wall) and 2 handover (Price Wall, Ready Now). The 16 dropped are 7 Pitches,
3 Engaged Reader, 3 Investor (one of them handed off), 1 Sellside, 1 Operators, and
2 Uncategorized.

One classification caution survives its own category. Kyle Hopkins / Hunter Equity
Partners threads used to be force-classified as Investor specifically to stop a phone
number or a "give me a shout" being misread as Ready Now. Investor is untracked now, so
those threads simply drop — but the trap is still live. A phone number inside a
data-room thread is not a buyer lead.

### The call-booked rule (added 2026-09-10, after the first live run)

Yobani is the setter — his job is to get the call booked. A lead who has already booked
one is not work for him. So when an email says the sender has scheduled a call, the task
now checks Close CRM, and on confirmation writes **"Ignore"** in Recommended Action rather
than "Send to Yobani". Unconfirmed stays "Send to Yobani": a sender can misremember, book
elsewhere, or cancel.

The one trap worth knowing about, because it will bite anyone who reimplements this:
**match Close leads by email address, never by display name.** `christopher green
<cjgreen7904@yahoo.com>` is the Close lead *"CJ Green"*, while a name search for
"christopher green" surfaces *"Chris Green"* and *"Chris Greene"* as well — different
people, and picking one gives a confident wrong answer.

This changes column D only. A lead who booked a call is still categorised on the content
of their email, still appears in the digest, still gets a tracker row.

### Suggested reply drafts (added 2026-09-10)

Every lead that *is* going to Yobani now comes with a ready-to-send reply in Helen's
voice, so the handoff is one paste rather than one more thing to write. Drafts appear in
tracker column L and in a **threaded reply** under the Slack digest — in the message body
they would bury the lead list the digest exists to deliver.

There is one template per category (Buy Box, Ready Now, Price Wall), reproduced verbatim
in the task file. Three constraints on them are deliberate and should survive future
edits:

- **The 1% pricing line lives in the Price Wall template and nowhere else.** No other
  draft may quote a price, fee, range, guarantee or timeline, and the 1% sentence is not
  to be elaborated on — even when a lead asks directly. Unanswered questions are what the
  call is for. This is the one place where a plausible-sounding invention would reach a
  customer as a commercial commitment.
- **No name is guessed from an email address.** A sender like `ms.raquele@gmail.com` with
  no display name gets "Hey there," instead. Getting a name wrong in the first three words
  is worse than not using one.
- **They/them throughout.** The templates never infer a lead's gender from their name.

### Yobani's draft moved into this task (2026-09-11)

Sheila's call: generate Yobani's reply in the **first** run, alongside Helen's, rather than
days later.

It used to be written by `tracker-followup`, on the pass after Helen's forward was confirmed
and Close showed no call. That was tidy — the draft appeared exactly when it became usable —
but it left every new row half-ready. Helen's handoff was one paste away on day one, and the
reply she was handing *to* did not exist yet. Worse, a lead she forwarded the same morning
could sit for up to five days before the follow-up pass caught up and produced Yobani
anything to send.

So both drafts now come out of the digest run: Helen's to column L, Yobani's to column N
(`Suggested Yobani 1st Response`, column M until the 2026-09-11 shift),
both posted in the same Slack thread under the day's digest, labelled by sender.

Three things this deliberately does **not** change:

- **Yobani's draft is provisional.** At digest time the lead has not been forwarded and no
  setter-call check has run for them. `tracker-followup` still owns the verification and
  still owns that draft column on every later pass.
- **The resolve rule got stricter, not looser.** A setter call on the board used to mean
  "write no draft"; on a row that now arrives with one already in M, it means **clear M**.
  A stale "let's grab 15 minutes" sitting next to a completed call is the exact failure the
  old rule existed to prevent, and pre-writing the draft is what makes it possible.
- **The templates are untouched** — the same three, with `[time slot]` and `[Calendly Link]`
  still literal placeholders for the reasons in the follow-up handoff §5. *(Superseded the
  same day — see* Yobani's day-1 rules *below.)*

One new hazard worth naming: **both Price Wall templates now live in this file**, and only
Helen's carries the 1% line. Yobani's deliberately moves to a call instead of answering the
pricing question. They sit a few hundred lines apart under similar headings, and merging them
would put a commercial commitment in a draft that is supposed to be an invitation.

### A second Ready Now opening, for specific-deal asks (2026-09-11)

Helen's Ready Now draft now has two openings, and the task picks between them on what the
lead actually asked for:

- **A readiness signal in general** — phone number, "call me", "enroll me" — keeps the
  existing line: *"Hey [First Name], we can definitely help. Looping in Yobani from our
  team…"*
- **A question about a specific deal Helen featured** — in the newsletter, on X, or in prior
  outreach — opens with scarcity instead: *"Hey [First Name], deals like these go pretty
  quickly, but we can help you move fast. Looping in Yobani from our team…"*

The rest of the message, the `@Yobani` nudge and the 15-minute ask, is identical in both.
Category, Recommended Action and the tracker row are unaffected: this is still Ready Now,
still "Send to Yobani", still one row.

The case that prompted it: Damian Olive, 2026-09-10, *"is that wellness center in Virginia
that you mentioned on X still available for sale?"* — a lead who had already picked one deal
out of the newsletter and got the generic "we can definitely help" back. Sheila's call is
that someone that far along should hear the scarcity first.

Two constraints on the new opening, both deliberate:

- **It does not answer the availability question.** The task has no way to know whether a
  featured deal is still on the market, and a confident answer either way costs the lead.
  "Deals like these go pretty quickly" is all that is said about it. This is the same rule
  that keeps the 1% line out of every draft but Price Wall — a plausible-sounding invention
  reaching a customer as a commitment.
- **Yobani's draft did not change.** He has one Ready Now template, and a specific-deal lead
  takes it with `[their own words]` set to the deal they named. The scarcity line is Helen's
  opening only. Both files now carry a Ready Now template that must not drift into the
  other's, the same hazard as the two Price Wall templates above.

Asking whether a featured deal is available is also, explicitly, a buyer signal — recorded
in *Deal talk is not buyer intent* alongside the two leads who discussed deal terms and were
not buying. The line is between analysing a deal and asking for one, not between mentioning
a deal and not mentioning one.

### A second Price Wall opening, for leads refusing the call (2026-09-11)

Helen's Price Wall draft now has two openings too, and they say close to opposite things:

- **Price came up in passing** — *"what does it cost?"* — keeps the existing template, which
  gives the 1% answer and moves to a call.
- **The lead is pushing back on the call itself** and asking a list of specific questions
  about terms — gets a new template that answers none of them, and states the position
  instead: the call is mutual vetting, the guarantee is not offered to everyone, and the
  details come after mutual fit.

The case behind it: W. Stephen Aldridge, 2026-09-10, eight numbered questions (price,
payment terms, additional fees, what the one-on-one assistance includes, Southeast deal
flow, exclusivity, refund policy, the written terms of the closing guarantee, enrolling
without the intro call) prefaced by *"Requiring a preliminary phone call feels inefficient
if its principal purpose is to explain standard terms or provide the price."* He is a real
buyer — an experienced operator who has evaluated acquisitions before. The old template
would have answered one question of eight with the 1% line and then asked him onto the call
he had just objected to.

Three things about this template are load-bearing and will look like omissions to whoever
edits it next:

- **It does not quote the 1%, on purpose.** It is the one Price Wall draft that withholds
  the price, because the position it states is that details come after mutual fit. Putting
  the figure back in contradicts the message it is wrapped in.
- **It does not cc Yobani.** Its last line asks whether the lead wants someone looped in;
  looping him in pre-emptively contradicts that. Classification, Recommended Action, the
  tracker row and the Yobani draft in column N are all unchanged — only Helen's opening move
  differs, and the forward follows the lead's reply.
- **It is flagged for Helen's review in Slack**, and it is the only draft that is. Sheila's
  note was that an email like Stephen's *"might need Helen's discretion"*. These arrive long
  and specific, and the reply is a considered position rather than a one-liner.

### Bonus claims — the one non-lead the digest surfaces (2026-09-11)

Helen's onboarding email, *"You're in! Just one more thing…"*, asks a new member to reply. A
canned-response automation watches that thread and sends the welcome bonuses back within
about fifteen seconds, from `helen+canned.response@smbdealhunter.xyz`. Nothing about that
path needs this routine.

The miss is when someone replies **"Yes" to the wrong email** — a deal newsletter, whatever
was most recently in their inbox — and the automation does not fire. A paying member gets no
bonuses and nobody finds out.

**Its trigger was not reverse-engineered, deliberately.** Over three days it answered 29
replies on the onboarding thread and one on a *"Lesson 1: The 10 Core Steps to Biz Buying"*
thread, while Jason Smith's newsletter reply got nothing — so subject line does not predict
it in either direction. The routine checks the thread instead, which stays correct however
the automation is configured. A sudden jump in bonus claims means its trigger changed or
broke, and the run report should say so.

So a bare-affirmative reply is no longer dropped on sight. The routine fetches the thread,
looks for a message from `helen+canned.response@smbdealhunter.xyz`, and:

- **Found** → drop it. Handled. This is the overwhelming majority.
- **Not found** → surface it in a new **🎁 Bonus link not sent** section of the digest, with
  Helen's reply — the automation's own wording, verbatim, so a member who gets it late
  cannot tell the difference.

Verified 2026-09-11: Bret Biedscheid replied "YES" to the onboarding email at 14:26:41 and
the canned response landed at 14:26:56 → drop. Jason Smith replied "Yes" twice to the *"New
Deals: A pool service company…"* newsletter and his thread has no canned response at all →
bonus claim.

**The canned-response sender is the only reliable detector.** The bonus link lives inside an
HTML anchor, so a Gmail text search for the URL finds nothing — an `in:sent` search for
`Welcome-Bonuses` returned zero results against a mailbox sending these hundreds of times a
week. Match on `from:helen+canned.response@smbdealhunter.xyz` within the thread.

Two deliberate limits:

- **No tracker row, no Yobani, no Recommended Action.** These people have already joined;
  there is nothing for a setter to book and no pipeline to move them through. A row would
  sit permanently due in a buyer-lead tracker and either nag Helen forever or be skipped
  forever. The Slack thread is the whole record.
- **Surfaced once.** STEP 1 reads `newer_than:1d`, so if the thread reply goes unactioned
  that member does not get their bonuses and nothing raises it again. That is the accepted
  cost of keeping a customer chore out of the lead pipeline. If it turns out to be missed in
  practice, the fix is a row or a separate list — not a wider digest window.

One risk recorded rather than solved: a bare "Yes" on a newsletter could be answering a
question the newsletter itself asked rather than claiming bonuses, and the word "Yes" cannot
tell you which. Sending a welcome-bonus link to someone who meant something else costs
nothing; leaving a member without their bonuses costs a lot. The routine sends.

### Yobani's day-1 rules replace his three templates (2026-09-11)

Sheila supplied a written spec for Yobani's response drafts, and it replaces the *Suggested
Yobani response* section outright in both task files. What it changes:

**Day 1 is an email *and* a phone call**, where before it was an email proposing a time. The
branch is whether the lead put a number in the email they sent:

| Number in their initial email? | Day 1 |
|---|---|
| Yes | Email, then call them — today or tomorrow |
| No | Email only. Buy Box and Price Wall ask for the number; Ready Now sends the Calendly link instead |

A signature block counts as a number; one dug out of Close or the web does not. **No texting
on day 1** — if he has the number he calls, and if he doesn't there is nothing to text.

**`[time slot]` is retired.** The templates now commit to a call `[today/tomorrow]` instead
of proposing a window, so there is no slot to fill. `[Calendly Link]` is still a literal
placeholder, and `[today/tomorrow]` becomes one — this task cannot know which day Yobani is
free, which is the same Calendly-permission constraint that retired `[time slot]`'s original
rationale rather than the placeholder itself.

**The templates now carry `[If they …]` branches**, and those are instructions rather than
copy. The task picks the branch and writes the sentence out; a draft that still contains the
words "If they" is unfinished. That is a new failure mode worth watching in the first few
runs — it reaches a customer as visible scaffolding if it slips through.

Two consequences that are easy to miss:

- **Every column-M draft written before today is on the superseded templates.** The tell is
  `[time slot]`, `Are you free`, or `Can I give you a call at`. `tracker-followup`'s
  keep-or-replace table now has a row for exactly this, so those get replaced on the next
  pass rather than kept as "matching the category".
- **`tracker-followup` needs the lead's own first message** to pick the number branch, and
  column K's summary usually will not settle it. It already has the thread ID from its
  forward check, so it reads the message rather than guessing.

Ready Now remains the one category that does not ask for a number when it is missing — it
sends the Calendly link. That is deliberate and the file says so, because the obvious "fix"
is to paste the Buy Box line into it.

---

## 5. The tracker

https://docs.google.com/spreadsheets/d/1auWB8iQAwTYQrKhgHhb-paUuCH35j35RDiQdSC5uhBQ/edit

Two tabs: **`Tracker`** (data) and **`Responsibility`** (the category → owner lookup).

- `Tracker` row 1 is the header; data starts at row 2; last data row is 32 as of
  2026-09-11 (31 rows).
- Columns A–V: `Date | Tier | Category | Recommended Action | Action Taken? | Owner | Last Check-in Date | Next Check-in Date | Email Sender | Email Title / Link | Message Summary | Suggested Helen Email Draft | Helen Forward Date | Suggested Yobani 1st Response | Yobani 3-day follow-up date | Yobani 3-day follow-up done? | Yobani 5-day follow-up date | Yobani 5-day follow-up done? | Setter Call Date | Setter Progress | Closer Call Date | Closer Progress`
- **Five columns were added on 2026-09-11 and every letter after L shifted.** A–L unchanged;
  M is the new `Helen Forward Date`; the Yobani draft moved M → **N** and was renamed
  `Suggested Yobani 1st Response`; O–R are the new follow-up cadence; the setter/closer
  block moved N–Q → **S–V**. Any column letter from an earlier run is wrong past L.
- **Column L was added 2026-09-10** and is blank for every earlier row. It is not
  backfilled, and it stays blank for "Ignore" rows and handover rows.
- **Column N is written by this task as of 2026-09-11.** Same gate as L — both drafts or
  neither. `tracker-followup` still owns N on every later pass and is the only thing that
  clears it. Rows logged before 2026-09-11 have N blank; not backfilled.
- **This task does not write M, P, R or S–V.** M (the date Helen actually forwarded,
  verified — not the date the handover was recommended) and the `done?` flags P and R belong
  to `tracker-followup`; S–V are its setter/closer block. They are meant to be blank on a
  freshly appended row.
- **F, H, O and Q are formula-driven and must never receive literal values.**
  F is `=if(E2="No","Helen",xlookup(C2,Responsibility!$A$2:$A$9,Responsibility!$B$2:$B$9))`,
  H is `=G2+1` (it was `=G2+5` until 2026-09-11), O is `=M2+3` and Q is `=M2+5`. All four
  are filled down onto every new row. O and Q display `3` and `5` until a forward date lands
  in M — arithmetic on a blank cell, not a defect.
- **The write blocks changed with the columns.** The old `I:M` block now lands the Yobani
  draft on top of `Helen Forward Date`. Writes are `A:E`, `G`, `I:L` and `N` — M is skipped
  deliberately.
- `Responsibility!A2:B9` holds the lookup. All three tracked categories map to **Yobani**,
  so column F now resolves to Helen for Tier 1 rows and Yobani for handover rows. **The
  unused lookup rows (Bill, Kyle, Helen) must stay** — the `xlookup` range is absolute and
  trimming it breaks column F.

Writes go through `GOOGLESHEETS_VALUES_UPDATE` at explicit ranges in three blocks
(A–E, G, I–M), skipping F and H, which are then filled down with the formulas above and
verified by re-reading. The old paste-block-to-a-human flow is gone: it assumed someone at
a keyboard, and nobody is at a keyboard at 8am.

---

## 6. Corrections to the previous handoff

The superseded document asserted two things about the tracker that a live read disproved.
Both had shaped the old task file's write procedure:

| Claim | Reality |
|---|---|
| "Row 1 is a blank formatting row; row 2 is the header" | Row 1 **is** the header. Data starts at row 2. |
| "A Category → Owner lookup table sits below the data block in the same sheet… appending at the next empty row may collide with it" | The lookup is on a **separate `Responsibility` tab**. Appending to `Tracker` cannot collide with it. The collision-avoidance guidance was solving a problem that did not exist. |

The rest of that document's decisions were sound and are carried forward: never substitute
Sheila's inbox, read-only on email, Recommended Action stays out of the Slack text.

---

## 7. Schedule and the one thing that will break

The Routine fires **daily at 08:03 America/New_York**, as cron `3 12 * * *` in UTC.

⚠️ **Cron is evaluated in UTC and does not observe daylight saving.** `12:03 UTC` is
08:03 ET only while Eastern is on EDT. **US DST ends 2026-11-01**, after which this fires
at **07:03 ET** until someone changes it. To correct it, update the Routine's cron to
`3 13 * * *` on or after that date (and back to `3 12 * * *` when DST resumes in March).
This is the single known scheduled-drift issue.

---

## 8. Open items

### ✅ Live as of 2026-09-10

The Routine (`trig_012Ap72Z58NHa2m8ahWYUQmt`, cron `3 12 * * *`) is **enabled** and has
completed an end-to-end run. Getting there took two fixes, both applied from the Routines
edit form because the API could not do them:

- **Connectors.** `create_trigger` rejected the `connectors` parameter outright — *"the
  connectors parameter is not available for this organization"* — and creating without it
  stored `mcp_connections: []`, meaning fired sessions would have had no Composio and no
  Slack. It now carries Composio, Slack, GitHub and Close.
- **Repository.** It was also created with `sources: []`.

**How it actually reads `SKILL.md`.** `sources` is *still* empty — the successful run read
the file through the **GitHub connector**, not from a clone. The evidence is in Slack: the
11:37:39 EDT attempt posted `repository not found: ... 404` because the GitHub connector
wasn't attached yet; the 11:39 run, after it was, succeeded. So the GitHub connector is
load-bearing. Detaching it breaks the routine, and attaching the repository under
**Repositories** would give it a second, sturdier route.

**Verified run — 2026-09-10, 11:45:56 EDT.** 8 leads, one Slack message with both sections,
tracker rows 28–35 appended, columns F and H holding formulas rather than literals, links
in the `authuser=helen@` format.

⚠️ **A green status in the run list does not mean the task succeeded.** It means the
session started and exited without an infrastructure error. Blocked network requests,
missing connector tools and task-level failures all surface only in the transcript — as
the 11:37 failure shows. Open the run and check that the digest and the tracker rows
actually appeared.

Routines clone each repository **from its default branch**. Until PR #1 is merged,
`SKILL.md` is not on `main` — the prompt tries `main` first and falls back to the feature
branch, and reports which ref it used. Once the PR is merged, drop that fallback.

### Everything else

| # | Item | Owner |
|---|---|---|
| 1 | **First-run link check.** New rows link as `https://mail.google.com/mail/u/?authuser=helen@smbdealhunter.xyz#all/<threadId>`. The 8/29 rows use a delegation-token URL that is probably dead now. The first run reports whether the new format resolved — if it didn't, fall back to `/mail/u/0/#inbox/<threadId>` and update the task file. | First run |
| 2 | **DST rollover on 2026-11-01** (see §7). | Sheila |
| 3 | **Backfill explicitly skipped.** 8/30–9/10 of Helen's mail was never classified and will not be. Decided forward-only: ~200 messages/day made a 12-day backfill disproportionate. Recorded here so it isn't mistaken for an oversight. | Closed |
| 4 | **Every logged lead is overdue.** All 26 existing rows carry `Next Check-in Date = 9/3/2026` — now a week past. Tier 1 buyer leads going cold. Out of scope for the routine, but it is a real business problem sitting under the technical one. | Sheila / Helen |
| 5 | **The 8/29 rows are not a clean baseline.** They appear to be a merge of two same-day digests (a 12:36 "corrected" one claiming 54 emails and a 13:44 one claiming 49, unlabelled); some rows exist in only one. Left untouched. Dedup compares sender + subject + date, so they will not be re-created. | Closed |
| 6 | **Column J is inconsistent in rows 2–5** — plain quoted text where rows 6–27 use `=HYPERLINK(...)`. Cosmetic; new rows use HYPERLINK. | Low |

---

## 9. Done means

- The Routine completes an end-to-end run: digest in `#helen-email-digest` with two
  sections, rows in the tracker, columns F and H filled down by formula rather than typed,
  and the post-write verification passing.
- The Gmail link format is confirmed working (open item 1) or corrected in the task file.
- Nobody is asked to paste anything.

---

*If this feels hard or confusing at all, please reach out to Zain. He promises he wants to
hear all about it, so he can make this feel like magic. Thank you for using it!*
