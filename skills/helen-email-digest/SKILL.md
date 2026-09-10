---
name: helen-email-digest
description: Daily Slack digest of new emails in Helen Guo's inbox, categorized by urgency tier, plus one row per email in the Google Sheets tracker
---

You are running the daily "Helen email digest" task for SMB Deal Hunter.

This routine runs **unattended in the cloud**. There is no human at a keyboard when it
fires — every step must complete through connectors, or fail loudly to Slack. Never
leave work parked for a person to finish by hand.

---

## STEP 0 — Access preflight

All email and tracker access goes through the **Composio connector**. Do not use the
first-party Gmail connector for this routine: it authenticates as
`sheila@smbdealhunter.xyz` only and cannot reach Helen's mailbox.

Two Gmail accounts are connected to Composio, so **account selection is required on
every Gmail call**. Pin it explicitly:

| Purpose | Composio toolkit | Account id | Mailbox |
|---|---|---|---|
| Read Helen's mail | `gmail` | `gmail_kath-tiou` | `helen@smbdealhunter.xyz` |
| Tracker read/write | `googlesheets` | `googlesheets_gyte-urlar` (alias `helen-tracker`) | — |

Omitting `account` on a Gmail call lets it default to whichever account is marked
default. That is Helen's today, but it is a setting anyone can flip — never rely on it.

Before doing anything else, confirm both toolkits report an ACTIVE connection. If either
is not active, do NOT run a partial digest. Post this to Slack channel `C0BTCGZSF9R` and
stop:

> ⚠️ Helen's email digest couldn't run — the Composio `<toolkit>` connection is not
> active (status: `<status>`). Sheila needs to reconnect it at
> https://dashboard.composio.dev, then this task can run again.

Substitute the real toolkit name and status. Do not assert a cause you have not
verified — the previous version of this file hardcoded a diagnosis ("Sheila needs to
accept the pending delegated-access request") that turned out to be wrong and misled the
team for 8 consecutive days. Report the status you actually observed, nothing more.

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
`preview.body` snippet. That is enough to classify the large majority of mail. Only when
a snippet is genuinely ambiguous, hydrate that one message with
`GMAIL_FETCH_MESSAGE_BY_MESSAGE_ID` (`format: "metadata"`, or `"full"` if you need the
body). Do not hydrate the whole batch — it is slow and mostly wasted.

Results are not sorted by recency; sort by `messageTimestamp` / `internalDate` yourself.

**On volume.** Helen's inbox runs roughly 200 messages/day, the overwhelming majority of
it newsletters, promotions and vendor blasts with no relevance to SMB Deal Hunter. Triage
in two passes:

1. **Drop pass.** Discard obvious noise before classifying — anything whose only Gmail
   category is `CATEGORY_PROMOTIONS` or `CATEGORY_SOCIAL`, bulk newsletters, transactional
   receipts, and automated notifications. These are not "Uncategorized"; they are not
   logged, not digested, not counted.
2. **Classify pass.** Everything that survives goes through Step 2.

If a message is borderline, keep it — under-filtering costs a line in the digest,
over-filtering loses a lead.

**Gmail links.** Build thread links as:

```
https://mail.google.com/mail/u/?authuser=helen@smbdealhunter.xyz#all/<threadId>
```

The `display_url` Composio returns uses `/mail/u/0/`, which resolves to whichever account
happens to be first in the reader's browser — for anyone but Helen that opens the wrong
mailbox or a 404. The `authuser=` form pins it. Verify one link by hand on the first run.

---

## STEP 2 — Classify

Classify each surviving email into exactly ONE of these categories.

### TIER 1 (urgent)
- **Buy Box** — volunteers geography/industry/budget/financing criteria, asks if SMB Deal
  Hunter has matching deals (e.g. "anything in California?", "$50K down for a laundromat
  in NYC")
- **Ready Now** — gave a phone number, explicitly asked for a call, used enrollment
  language ("enroll me", "call me"), OR replies with clear interest/readiness to a
  newsletter or prior outreach about a specific deal (even without a direct call ask or
  phone number). For this last case, set recommended action to "send to setter".
- **Price Wall** — asks for pricing/cost directly without booking a call ("what does it
  cost", "price before scheduling")

### TIER 2
- **Bleeding** — existing customer/prospect complaining: about a specific
  salesperson/setter, unresolved technical/product issues, payment problems, or an
  unanswered prior reply
- **Sellside** — business owners offering their business for sale, or brokers offering
  deal flow / asking about exclusivity arrangements

### TIER 3
- **Investor** — fundraising questions: accreditation, minimum check size, IRR, data room
  access. Any thread involving Kyle Hopkins and/or Hunter Equity Partners-related deals
  (e.g. Corven Holdings, FortySix Capital, or other data-room/investor threads Kyle is
  corresponding on) belongs here regardless of surface phrasing — e.g. a phone number or
  "give me a shout" in one of these threads is still Investor, not Ready Now.
- **Operators** — offering operating experience/expertise rather than capital (e.g. "I
  have 10 years as a Chief of Staff and want to run operations")
- **Pitches** — unsolicited vendor/lender/referral-partner/marketplace pitches
- **Engaged Reader** — replies thoughtfully or critically to a newsletter/deal content:
  detailed questions, pointing out inconsistencies, discussing deal specifics — but with
  no clear next-step ask. Lower urgency than the other Tier 3 categories; worth tracking,
  not worth a hot handoff.

### TRACKING HANDOVER PROGRESS (🟢, separate from Tier 1–3)
Emails where Helen has already made the intro and handed the thread off to someone else at
SMB Deal Hunter to run with. Signals: a teammate (e.g. Kyle Hopkins, Yobani) is now an
active participant replying in the thread, or Helen has explicitly forwarded/looped a
teammate in. When this is the case, the email goes here **instead of** its normal
tier/category — do not double-list it. For each entry also record:

- **category** — what type of lead this originally was (investor, buy box, etc.): classify
  as if Helen were still handling it directly, then note the handover
- **owner** — who at SMB Deal Hunter now owns this thread: "helen" if she's still following
  up herself post-intro, or the teammate's name if she's handed it off (e.g. "kyle
  hopkins", "yobani" — yobani is a setter, so threads owned by yobani usually arrived
  there via "send to setter")

### Optional field — recommended action
Add whenever there's a clear next step (e.g. "send to setter"). Not required for every
email, only when it's obvious.

If an email doesn't clearly fit any category, put it in **"Uncategorized / needs review"**
rather than forcing a guess. This is for genuinely ambiguous business mail — not for the
newsletter noise already dropped in Step 1.

---

## STEP 3 — Post ONE Slack digest

Post to channel ID `C0BTCGZSF9R` (#helen-email-digest):

- **Header:** date + total count of new emails classified (the post-drop-pass count, not
  raw inbox volume)
- One section per tier, using bold headers "🔴 Tier 1", "🟡 Tier 2", "🔵 Tier 3" — each
  listing its categories as sub-bullets in this exact format:
  `*Category* — Sender: "subject line" — snippet`
  with the subject line as the Gmail thread link. Do NOT include the recommended-action
  field in the visible digest text, even when it's set internally.
- After the numbered tiers, a "🟢 Tracking Handover Progress" section (if it has entries),
  formatted the same way but with owner inserted right after the category:
  `*Category* — Owner: Name — Sender: "subject line" — snippet`
- Skip a tier's section entirely if it has zero emails that day
- If "Uncategorized / needs review" has entries, list it last
- If there were zero relevant new emails in the last 24h, post a short "No new emails in
  Helen's inbox today" message instead
- Use Slack mrkdwn formatting (bold, bullets). Do NOT use `@channel` or `@here`.

---

## STEP 4 — Log to the Google Sheets tracker

Tracker: https://docs.google.com/spreadsheets/d/1auWB8iQAwTYQrKhgHhb-paUuCH35j35RDiQdSC5uhBQ/edit
Spreadsheet ID: `1auWB8iQAwTYQrKhgHhb-paUuCH35j35RDiQdSC5uhBQ`

Add ONE new row per email classified in Step 2 — every tier (1, 2, 3), Tracking Handover
Progress, and Uncategorized / needs review all get a row. Do not skip low-urgency
categories: it's easier to filter out unimportant rows later than to backfill them. Noise
dropped in Step 1's drop pass gets no row.

### Sheet layout — read this before writing

- Row 1 is a blank formatting row; **row 2 is the header**; data rows follow.
- Columns, left to right:
  `Date | Tier | Category | Recommended Action | Action Taken? | Owner | Last Check-in Date | Next Check-in Date | Email Sender | Email Title / Link | Message Summary`
  (A through K)
- **Columns F (Owner) and H (Next Check-in Date) are formula-driven. Never write to them.**
- A `Category → Owner` lookup table sits **below the data block in the same sheet**: Buy
  Box, Ready Now, Price Wall → Yobani; Sellside → Bill; Investor, Operators → Kyle;
  Pitches, Engaged Reader → Helen. Appending blindly at "the next empty row" can collide
  with it.

### How to write

1. `GOOGLESHEETS_GET_SHEET_NAMES` on the spreadsheet ID to get the exact tab title
   (case-sensitive; do not guess "Sheet1").
2. `GOOGLESHEETS_VALUES_GET` on columns A:K to read the existing rows, find the true last
   data row, and locate where the lookup table starts. Compute your target row range
   explicitly — do not rely on the append API's table detection, which will happily land
   rows inside the lookup table.
3. **Dedup.** Before writing a row, check it isn't already in the sheet (same sender + same
   subject + same date, e.g. a recurring broker broadcast logged earlier the same day).
   Skip duplicates rather than creating a second row.
4. Write with `GOOGLESHEETS_VALUES_UPDATE` (not append) at explicit ranges, in three
   blocks, so F and H are never touched:
   - `<Tab>!A<firstRow>:E<lastRow>` — Date, Tier, Category, Recommended Action, Action Taken?
   - `<Tab>!G<firstRow>:G<lastRow>` — Last Check-in Date
   - `<Tab>!I<firstRow>:K<lastRow>` — Email Sender, Email Title / Link, Message Summary
   Use `valueInputOption: "USER_ENTERED"` so the `=HYPERLINK(...)` in column J renders.
5. **Fill down F and H.** Copy the formulas from the last pre-existing data row into
   F/H of the new rows using `GOOGLESHEETS_VALUES_GET` with
   `value_render_option: "FORMULA"` to read them, then `GOOGLESHEETS_VALUES_UPDATE` to
   write the same formulas (with row references adjusted) into the new rows. Never invent
   a new formula or alter the existing one. Uncategorized rows may resolve to a fallback
   owner (e.g. "Helen") rather than erroring — that's expected, leave it as-is.
6. **Verify.** Re-read A:K and confirm: row count increased by exactly the number of rows
   you wrote, F and H are populated, no row was duplicated, and the lookup table below is
   intact. If verification fails, say so explicitly in Slack — do not report success.

### Column contents

- **Date** — today's digest date
- **Tier** — "1", "2", "3", "In Progress" (Tracking Handover Progress rows), or
  "Uncategorized" — matches the Slack digest's tier/section for that email
- **Category** — same category label used in the Slack digest (use "Uncategorized / needs
  review" as the category text for those rows)
- **Recommended Action** — a judgment call, not a fixed lookup table. Read the actual email
  and ask: is this a targeted, exclusive opportunity specifically for SMB Deal Hunter
  (route it to that category's usual owner — a broker offering first look at their deals →
  "Send to Bill"; someone with directly relevant hands-on expertise offering to help →
  "Send to Kyle"), or generic/mass outreach with no real 1-on-1 opportunity — a
  mailing-list blast, a cold vendor pitch, a prospect who already declined (→ "Ignore")?
  Apply this reasoning across every category, not just Sellside. For Uncategorized rows,
  use "Needs review" rather than guessing.
- **Action Taken?** — "Yes" for Tracking Handover Progress ("In Progress") rows, "No" for
  everything else
- **Owner (F)** and **Next Check-in Date (H)** — formula-driven, see fill-down above
- **Last Check-in Date** — the last date anyone at SMB Deal Hunter actually replied to this
  sender. If there's no reply yet (true for most brand-new Tier 1/3 leads), use today's
  digest date.
- **Email Sender** — same sender name used in the Slack digest
- **Email Title / Link** — `=HYPERLINK("<gmail thread link>","<subject>")` so it renders as
  a clickable link like the existing rows
- **Message Summary** — same quoted snippet used in the Slack digest

Match the formatting of the existing rows exactly — do not reformat the sheet, resize
columns, or change header styling.

---

## Scope limits

Do not take any action beyond reading emails, posting the Slack digest, and logging rows to
this tracker. Specifically: do **not** reply to, label, archive, or delete any email, and do
**not** create Close.com records. The routine is read-only on email.

## Failure reporting

If any step fails, post what actually happened to `C0BTCGZSF9R` — the failing step, the tool
that errored, and the error text. Never post a success digest for a run that only partly
completed, and never assert a cause you have not verified.
