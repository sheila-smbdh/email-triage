# Handoff — Helen Email Digest, rebuilt on Composio and running in the cloud

| | |
|---|---|
| **Supersedes** | `2026-09-10 helen email digest gmail blocked.md` — the blocked-state handoff. That document is now historical, and two of its factual claims were wrong (see §6). |
| **Status** | Live. Access restored, scope narrowed, cloud Routine enabled and verified end-to-end on 2026-09-10. |
| **Last updated** | 2026-09-11 — Yobani's draft moved forward into this task (§4). |

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

So both drafts now come out of the digest run: Helen's to column L, Yobani's to column M,
both posted in the same Slack thread under the day's digest, labelled by sender.

Three things this deliberately does **not** change:

- **Yobani's draft is provisional.** At digest time the lead has not been forwarded and no
  setter-call check has run for them. `tracker-followup` still owns the verification and
  still owns column M on every later pass.
- **The resolve rule got stricter, not looser.** A setter call on the board used to mean
  "write no draft"; on a row that now arrives with one already in M, it means **clear M**.
  A stale "let's grab 15 minutes" sitting next to a completed call is the exact failure the
  old rule existed to prevent, and pre-writing the draft is what makes it possible.
- **The templates are untouched** — the same three, with `[time slot]` and `[Calendly Link]`
  still literal placeholders for the reasons in the follow-up handoff §5.

One new hazard worth naming: **both Price Wall templates now live in this file**, and only
Helen's carries the 1% line. Yobani's deliberately moves to a call instead of answering the
pricing question. They sit a few hundred lines apart under similar headings, and merging them
would put a commercial commitment in a draft that is supposed to be an invitation.

---

## 5. The tracker

https://docs.google.com/spreadsheets/d/1auWB8iQAwTYQrKhgHhb-paUuCH35j35RDiQdSC5uhBQ/edit

Two tabs: **`Tracker`** (data) and **`Responsibility`** (the category → owner lookup).

- `Tracker` row 1 is the header; data starts at row 2; last data row is 27 as of
  2026-09-10 (26 rows, all dated 8/29/2026).
- Columns A–M: `Date | Tier | Category | Recommended Action | Action Taken? | Owner | Last Check-in Date | Next Check-in Date | Email Sender | Email Title / Link | Message Summary | Suggested Helen Email Draft | Suggested Yobani Response`
- **Column L was added 2026-09-10** and is blank for every earlier row. It is not
  backfilled, and it stays blank for "Ignore" rows and handover rows.
- **Column M is written by this task as of 2026-09-11.** Same gate as L — both drafts or
  neither. `tracker-followup` still owns M on every later pass and is the only thing that
  clears it. Rows logged before 2026-09-11 have M blank; not backfilled.
- **F and H are formula-driven and must never receive literal values.**
  F is `=if(E2="No","Helen",xlookup(C2,Responsibility!$A$2:$A$9,Responsibility!$B$2:$B$9))`,
  H is `=G2+5`.
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
