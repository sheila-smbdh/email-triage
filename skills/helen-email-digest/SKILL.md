---
name: helen-email-digest
description: Daily Slack digest of new buyer leads in Helen Guo's inbox (Buy Box, Ready Now, Price Wall), plus one row per lead in the Google Sheets tracker
---

You are running the daily "Helen email digest" task for SMB Deal Hunter.

This routine runs **unattended in the cloud**. There is no human at a keyboard when it
fires — every step must complete through connectors, or fail loudly to Slack. Never leave
work parked for a person to finish by hand.

**Scope: buyer leads only.** This routine tracks exactly three categories — **Buy Box**,
**Ready Now**, and **Price Wall** — plus threads in those three categories that Helen has
already handed off. Everything else in the inbox is dropped: not digested, not logged, not
counted. There is no Tier 2, no Tier 3, and no "Uncategorized / needs review" bucket.

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

Every email that survives Step 1 is either one of the three tracked categories, a handover
of one of them, or dropped. There is no other outcome.

### TIER 1 — the only tracked tier

- **Buy Box** — volunteers geography/industry/budget/financing criteria, asks if SMB Deal
  Hunter has matching deals (e.g. "anything in California?", "$50K down for a laundromat in
  NYC")
- **Ready Now** — gave a phone number, explicitly asked for a call, used enrollment
  language ("enroll me", "call me"), OR replies with clear interest/readiness to a
  newsletter or prior outreach about a specific deal (even without a direct call ask or
  phone number). For this last case, set recommended action to "send to setter".
- **Price Wall** — asks for pricing/cost directly without booking a call ("what does it
  cost", "price before scheduling")

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

Two things earn "Ignore":

1. **The lead has already disqualified themselves** — declined outright, an obvious
   tyre-kicker, someone reacting to price and walking away.
2. **The lead has already booked a call, verified in Close CRM** — see below.

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

The draft is a **reply in Helen's voice**, cc'ing Yobani Mendoza
(`yobani@smbdealhunter.xyz`, the setter). No subject line, no signature, no greeting
block — Helen is replying inside an existing thread.

#### The three templates

Use the template for the lead's category. Each one is a short, fully written-out message
to the lead, with Yobani mentioned inside it — not a set of separate notes to different
people.

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

**Price Wall**

```
Hey [First Name], fair question. For our average member, the cost comes out to roughly 1% of the purchase price that is due upfront. We do have a success guarantee, which we can talk more about live. Let's get you on a quick call — @Yobani on our team can find a time that works for you.
```

The `@Yobani` is literal text in the body of an email, not a Slack or Gmail mention. It
reads as a nudge to him because he is cc'd.

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

**Never invent commercial terms.** The 1% figure and the success guarantee appear in the
Price Wall template and nowhere else. Do not quote a price, a fee, a range, a guarantee, a
timeline, or a deal specific in any other draft, and do not elaborate on the 1% beyond the
sentence given — even if the lead asked a direct question about it. If a lead asks
something the template does not answer, send the template as-is and let the call handle it.

**Nothing else goes in.** A finished draft should be the template plus a first name and,
for Buy Box, their ask — and nothing more. If it says something the template does not,
take that back out.

### On borderline mail

If you cannot confidently place an email in one of the three categories, **drop it**. There
is no Uncategorized bucket to park it in. This is a deliberate trade: the digest stays
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
- These are the only two sections. Skip either one entirely if it has zero entries.
- If there were zero tracked leads in the last 24h, post a short "No new buyer leads in
  Helen's inbox today" message instead.
- Use Slack mrkdwn formatting (bold, bullets). Do NOT use `@channel` or `@here`.

### The drafts go in a thread under that message

Post the reply drafts as **one threaded reply** to the digest message, not in the message
body. Five or six full drafts inline would bury the lead list the digest exists to
deliver; in the thread they are one click away and still copy-pasteable.

Capture the parent message's `ts` when you post it and reply with that as `thread_ts`.

Thread reply format — one block per lead whose action is "Send to Yobani", in the same
order as the Tier 1 list, each draft in a Slack code block so it copies cleanly:

> ✍️ *Suggested replies* — paste and send from Helen's inbox, cc yobani@smbdealhunter.xyz
>
> *Buy Box — Dean Julia*
> ```
> Hey Dean, finding deals in Central FL is something we can help with. @Yobani on our team can grab 15 minutes with you to better understand what you're looking for.
> ```

If no lead has action "Send to Yobani", post no thread reply at all — not an empty one.

---

## STEP 4 — Log to the Google Sheets tracker

Tracker: https://docs.google.com/spreadsheets/d/1auWB8iQAwTYQrKhgHhb-paUuCH35j35RDiQdSC5uhBQ/edit
Spreadsheet ID: `1auWB8iQAwTYQrKhgHhb-paUuCH35j35RDiQdSC5uhBQ`

Add ONE new row per email that appeared in the Slack digest — Tier 1 rows and Tracking
Handover Progress rows. Nothing else gets a row. What was dropped in Steps 1–2 is not
logged.

### Sheet layout — verified 2026-09-10

The spreadsheet has **two tabs**: `Tracker` (the data) and `Responsibility` (the lookup).

**`Tracker` tab.** Row 1 is the header. Data starts at **row 2**. As of 2026-09-10 the last
data row is **row 27** (26 rows, all dated 8/29/2026). Columns A–K:

`Date | Tier | Category | Recommended Action | Action Taken? | Owner | Last Check-in Date | Next Check-in Date | Email Sender | Email Title / Link | Message Summary | Suggested Helen Email Draft`

Column **L — "Suggested Helen Email Draft"** was added 2026-09-10 and is empty for every
row before then. That is expected; do not backfill it.

**`Responsibility` tab.** The `Category → Owner` lookup lives here, in `A2:B9`. Buy Box,
Ready Now and Price Wall all map to **Yobani**; the other rows (Sellside → Bill, Investor
and Operators → Kyle, Pitches and Engaged Reader → Helen) are now unused by this routine
but must be left in place — the `xlookup` range is absolute and shrinking it would break
column F. It is **not** below the data block on `Tracker`, so appending to `Tracker` cannot
collide with it. (An earlier handoff doc claimed row 1 was blank with the header on row 2,
and that the lookup sat below the data — both are wrong. Trust this section.)

**Columns F and H are formula-driven. Never write literal values to them.** The formulas,
read verbatim from row 2:

- **F (Owner):** `=if(E2="No","Helen",xlookup(C2,Responsibility!$A$2:$A$9,Responsibility!$B$2:$B$9))`
  — rows where Action Taken? is "No" resolve to Helen regardless of category; only
  handed-over rows get the category's owner. Since all three tracked categories map to
  Yobani, in practice column F now reads Helen for Tier 1 rows and Yobani for handover
  rows.
- **H (Next Check-in Date):** `=G2+5` — five days after the last check-in.

Dates in A and G are stored as Google serial numbers and displayed as dates; writing a
plain `9/11/2026` string with `valueInputOption: "USER_ENTERED"` is coerced correctly.

Column J is inconsistent in the existing data: rows 2–5 hold plain quoted subject text,
rows 6–27 hold `=HYPERLINK(...)`. Write new rows as `=HYPERLINK(...)`, matching the
majority and the documented format.

### How to write

1. `GOOGLESHEETS_GET_SHEET_NAMES` to confirm the tab is still called `Tracker`.
2. `GOOGLESHEETS_VALUES_GET` on `Tracker!A:L` to read existing rows and find the true last
   data row. Compute your target range explicitly rather than relying on the append API's
   table detection.
3. **Dedup.** Before writing a row, check it isn't already in the sheet (same sender + same
   subject + same date, e.g. a recurring broker broadcast logged earlier the same day).
   Skip duplicates rather than creating a second row.
4. Write with `GOOGLESHEETS_VALUES_UPDATE` at explicit ranges, in three blocks, so F and H
   are never overwritten with literals:
   - `Tracker!A<first>:E<last>` — Date, Tier, Category, Recommended Action, Action Taken?
   - `Tracker!G<first>:G<last>` — Last Check-in Date
   - `Tracker!I<first>:L<last>` — Email Sender, Email Title / Link, Message Summary,
     Suggested Helen Email Draft

   Use `valueInputOption: "USER_ENTERED"` so dates coerce and `=HYPERLINK(...)` renders.
5. **Fill down F and H** by writing the same two formulas into the new rows with their row
   references incremented — for a new row `N`, F is
   `=if(E<N>="No","Helen",xlookup(C<N>,Responsibility!$A$2:$A$9,Responsibility!$B$2:$B$9))`
   and H is `=G<N>+5`. The lookup ranges are absolute (`$A$2:$A$9`) and must stay exactly
   as written; only the `E<N>`, `C<N>` and `G<N>` references change. Never invent a
   different formula.
6. **Verify.** Re-read `Tracker!A:L` and confirm: row count increased by exactly the number
   of rows you wrote, F and H are populated and did not spill `#N/A`, and no row was
   duplicated. If verification fails, say so explicitly in Slack — do not report success.

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
- **Action Taken?** — "Yes" for Tracking Handover Progress ("In Progress") rows, "No" for
  Tier 1 rows
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
