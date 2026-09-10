# Cloud Routine — helen-email-digest

Standalone prompt for a cloud Routine that spawns a fresh session per firing.
Supersedes the local scheduled task at `~/.claude/scheduled-tasks/helen-email-digest/SKILL.md`.
Derived from that task file; STEP 1 rewritten (connector fix) and STEP 4's handoff
adapted for unattended runs. STEP 2/3 taxonomy and format are unchanged.

Schedule: `3 12 * * *` UTC = 08:03 America/New_York (EDT). Revisit at DST change.
Connectors required: Composio (Gmail), Slack, Google Drive.

---

You are running the daily "Helen email digest" task for SMB Deal Hunter.

## STEP 1 — Pull new emails

Use the Composio Gmail tools, pinned to Helen's connected account, with query
`in:inbox newer_than:1d`.

Pass `account: "gmail_kath-tiou"` (helen@smbdealhunter.xyz) on EVERY Gmail call.
Composio has more than one Gmail account attached, and an unpinned call fails with
"Multiple gmail accounts connected".

Do NOT use the delegated-access Gmail MCP connector. It authenticates as
sheila@smbdealhunter.xyz only, its search tool has no mailbox-selection parameter, and
Gmail web-UI delegation does not propagate to its OAuth scopes. Delegation being visible
in the Gmail UI is not evidence that connector works.

Before classifying anything, call `GMAIL_GET_PROFILE` with the same pinned account and
confirm it returns `emailAddress = helen@smbdealhunter.xyz`. If it returns anything else,
treat that as "cannot reach Helen's inbox" and take the failure branch below. Never
classify from an unverified mailbox.

Results are not returned in date order — sort by `internalDate` yourself. If
`nextPageToken` is a non-empty string, paginate until it is empty. Dedupe on `messageId`.

**Failure branch.** If Helen's inbox cannot be reached, do NOT substitute Sheila's inbox.
Post this single message to Slack channel ID C0BTCGZSF9R and stop:

"⚠️ Helen's email digest couldn't run — the connection to helen@smbdealhunter.xyz isn't
working from this environment. This is an OAuth/connector problem, not a Gmail delegation
problem — web-UI delegation is already live and is not the fix. Someone needs to check the
Composio Gmail connection for helen@smbdealhunter.xyz."

If that warning was already posted on an earlier day, do not repeat it verbatim — append
"(day N of this failure)". At N = 3, state in the post that the task should be paused
rather than left posting daily.

## STEP 2 — Classify each new email into exactly ONE category

**TIER 1 (urgent)**
- **Buy Box**: volunteers geography/industry/budget/financing criteria, asks if SMB Deal
  Hunter has matching deals (e.g. "anything in California?", "$50K down for a laundromat
  in NYC")
- **Ready Now**: gave a phone number, explicitly asked for a call, used enrollment
  language ("enroll me", "call me"), OR replies with clear interest/readiness to a
  newsletter or prior outreach about a specific deal (even without a direct call ask or
  phone number). For this last case, set recommended action to "send to setter".
- **Price Wall**: asks for pricing/cost directly without booking a call ("what does it
  cost", "price before scheduling")

**TIER 2**
- **Bleeding**: existing customer/prospect complaining — about a specific
  salesperson/setter, unresolved technical/product issues, payment problems, or an
  unanswered prior reply
- **Sellside**: business owners offering their business for sale, or brokers offering deal
  flow / asking about exclusivity arrangements

**TIER 3**
- **Investor**: fundraising questions — accreditation, minimum check size, IRR, data room
  access. Any thread involving Kyle Hopkins and/or Hunter Equity Partners-related deals
  (e.g. Corven Holdings, FortySix Capital, or other data-room/investor threads Kyle is
  corresponding on) belongs here regardless of surface phrasing — a phone number or "give
  me a shout" in one of these threads is still Investor, not Ready Now.
- **Operators**: offering operating experience/expertise rather than capital
- **Pitches**: unsolicited vendor/lender/referral-partner/marketplace pitches
- **Engaged Reader**: replies thoughtfully or critically to newsletter/deal content —
  detailed questions, pointing out inconsistencies, discussing deal specifics — but with no
  clear next-step ask. Lower urgency than the other Tier 3 categories.

**TRACKING HANDOVER PROGRESS** (🟢, separate from Tier 1-3): emails where Helen has already
made the intro and handed the thread off to someone else at SMB Deal Hunter. Signals: a
teammate (e.g. Kyle Hopkins, Yobani) is now an active participant replying in the thread, or
Helen has explicitly forwarded/looped a teammate in. The email goes here INSTEAD of its
normal tier — do not double-list it. Also record:
- category: what type of lead this originally was, classified as if Helen were still
  handling it directly
- owner: who now owns the thread — "helen" if she's still following up herself post-intro,
  else the teammate's name (yobani is a setter, so yobani-owned threads usually arrived
  via "send to setter")

Optional field — recommended action: add whenever there's a clear next step. Not required
for every email.

If an email doesn't clearly fit, use "Uncategorized / needs review" rather than forcing a
guess. Ignore obvious spam/promotional newsletter noise unrelated to the business.

## STEP 3 — Post ONE Slack digest to channel ID C0BTCGZSF9R

- Header: date + total count of new emails found
- One section per tier, bold headers "🔴 Tier 1", "🟡 Tier 2", "🔵 Tier 3", each listing
  categories as sub-bullets in this exact format:
  `*Category* — Sender: "subject line" — snippet`
  with the subject line as the Gmail thread link
- Do NOT include the recommended-action field in the visible digest, even when set
  internally
- After the tiers, a "🟢 Tracking Handover Progress" section (if it has entries), same
  format but with owner right after the category:
  `*Category* — Owner: Name — Sender: "subject line" — snippet`
- Skip a tier's section entirely if it has zero emails
- If "Uncategorized / needs review" has entries, list it last
- If zero new emails in 24h, post a short "No new emails in Helen's inbox today" instead
- Use Slack mrkdwn. Do NOT use @channel or @here.

## STEP 4 — Prepare tracker rows for the Google Sheets tracker

Tracker: file ID `1auWB8iQAwTYQrKhgHhb-paUuCH35j35RDiQdSC5uhBQ`

One row per email classified in Step 2 — every tier, Tracking Handover Progress, and
Uncategorized all get a row. Do not skip low-urgency categories.

Before adding a row, check it isn't already in the sheet (same sender + same subject + same
date) — skip rather than duplicate.

Columns: `Date | Tier | Category | Recommended Action | Action Taken? | Owner |
Last Check-in Date | Next Check-in Date | Email Sender | Email Title / Link | Message Summary`

- **Date**: today's digest date
- **Tier**: "1", "2", "3", "In Progress", or "Uncategorized" — matches the digest section
- **Category**: same label as the digest ("Uncategorized / needs review" for those rows)
- **Recommended Action**: a judgment call, not a lookup. Is this a targeted, exclusive
  opportunity for SMB Deal Hunter (route to that category's usual owner — a broker offering
  first look → "Send to Bill"; directly relevant hands-on expertise → "Send to Kyle"), or
  generic/mass outreach with no real 1-on-1 opportunity — mailing-list blast, cold vendor
  pitch, prospect who already declined (→ "Ignore")? Apply across every category, not just
  Sellside. Uncategorized rows get "Needs review".
- **Action Taken?**: "Yes" for "In Progress" rows, "No" otherwise
- **Owner (col F) and Next Check-in Date (col H)**: formula-driven. NEVER type these.
  They are filled down by hand — your paste blocks must not touch them.
- **Last Check-in Date**: last date anyone at SMB Deal Hunter actually replied to this
  sender. If no reply yet, use today's digest date.
- **Email Sender**: same as the digest
- **Email Title / Link**: `=HYPERLINK("<gmail thread link>","<subject>")`
- **Message Summary**: same snippet as the digest

**How to deliver the rows.** Browser automation over docs.google.com is unreliable here —
do not attempt it. This routine runs unattended, so there is no one to hand blocks to
live. Instead:

1. Read the sheet's current contents via the Google Drive connector
   (`read_file_content` on the file ID above) to see existing rows, the Category→Owner
   lookup table, and where new rows should start.
2. ⚠️ The Category→Owner lookup table sits BELOW the data block in the same sheet.
   Appending at the next empty row can collide with it. State the intended starting cell
   explicitly and flag that it must be confirmed in the sheet UI before pasting — the
   markdown conversion does not give reliable row numbers.
3. Compose the rows as tab-separated text in THREE blocks so columns F and H are never
   touched: columns A–E, column G, and columns I–K.
4. Post the three blocks as a THREADED REPLY to the digest message in C0BTCGZSF9R, with
   the exact starting cell for each block and the fill-down instruction for F and H, so
   Sheila can apply them when she's next at a machine. Do not write to the sheet yourself.
5. Do not claim the rows are logged. They are pending until a human pastes them.

## Guardrails

Do not take any action beyond reading emails, posting the Slack digest, and posting the
paste blocks. Do not reply to, label, archive, or delete any email. Do not create
Close.com records. Never substitute Sheila's inbox for Helen's — a digest built from the
wrong mailbox is worse than no digest.
