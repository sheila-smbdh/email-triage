# Helen → Jordan lead intake (hourly)

You are running an automated, unattended job. No human is watching this session.
Follow these steps exactly, then stop. Never ask questions; when something is
ambiguous, **flag it** (step 6) and move on. Do not edit any repository or push code.

Hard rules:
- **Airtable is read-only.** Never create, update or delete Airtable records.
- **Never send email** from anyone's mailbox. Only read Gmail.
- **Helen's mailbox and the Google Sheets tracker are read-only** (step 5a). Never write,
  label, draft in or modify either.
- On an existing Close lead, the ONLY thing you may add is Jordan's three follow-up tasks (step 5).
  Never change its fields, status, owner, contacts or notes.
- Only create a lead when every duplicate check in step 3 is clean.

## Constants

| Thing | Value |
|---|---|
| Jordan's Gmail (Composio account) | `gmail_dah-ceyx` (jkempster@smbdealhunter.xyz) |
| Helen's Gmail (Composio account, read only, step 5a) | `gmail_kath-tiou` (helen@smbdealhunter.xyz) |
| Helen's sending address | `helen@smbdealhunter.xyz` |
| Tracker (Composio `googlesheets` account, read only) | `googlesheets_gyte-urlar`, spreadsheet `1auWB8iQAwTYQrKhgHhb-paUuCH35j35RDiQdSC5uhBQ`, tab `'Tracker (JordanK)'` |
| Airtable base / table | `appDBhzdZfjoIFh2J` / `tblqt9BdHcwm0TzX6` ("All Clients") |
| Slack channel | `#helen-email-digest` = `C0BTCGZSF9R` |
| Sheila's Slack user id (for @-mentions) | `U0BM6J8KM32` → write `<@U0BM6J8KM32>` |
| Jordan Kempster Close user id | `user_3IrYZLUcCBZrg2mb49wCybrxGBFTCxa5eqTHhE1ApuC` |
| Jordan's calendar link | https://calendly.com/jkempster-smbdealhunter/intro-call-with-smb-deal-hunter |
| Lead status "Potential" | `stat_v6aCXRI3yiAPBImnr8zJ1dyADO6m0mdPrhIvzK3Kdkj` |
| Timezone for dates | America/Denver (Jordan's) |

Close lead custom fields to set:

| Field | Id | Value |
|---|---|---|
| Lead Owner | `cf_iwYMbuKfpAL7hJicgF0ZwPDAan5eg3vdIh3WG4Bf7PL` | Jordan user id |
| Setter | `cf_GgXDBkiGJbOFFIOW43vcFWc0bXr706WQU5zxJMDIAAE` | Jordan user id |
| Initial Contact User | `cf_C6fOIXKxCBrG5PhlmEhcO6Rzu20G8XV6aA7wnADkH3P` | Jordan user id |
| Creation Date | `cf_RdUwNTlCpEBzzWDbmzUcPUwPMmQPmO6EZJLsH6olFhM` | Helen's reply timestamp (ISO 8601, UTC) |

Leave blank: Closer, SDR, Lead Source, Lead Quality, and every qualification
field unless the prospect's email states the answer outright (step 4e).

## Tools

- Gmail: Composio `GMAIL_FETCH_EMAILS`, `GMAIL_FETCH_MESSAGE_BY_THREAD_ID`, with `account: "gmail_dah-ceyx"`
  (Jordan) everywhere except step 5a, which reads Helen's mailbox with `account: "gmail_kath-tiou"`.
  (Call `COMPOSIO_SEARCH_TOOLS` first to get a session id, then `COMPOSIO_MULTI_EXECUTE_TOOL`.)
- Tracker: Composio `GOOGLESHEETS_BATCH_GET` with `account: "googlesheets_gyte-urlar"` (read only).
- Close search: Close connector `lead_search` (`full_text`, `name`) and `search` (natural language), or Composio `CLOSE_MCP_LEAD_SEARCH` / `CLOSE_MCP_SEARCH`.
- Close writes: Composio `CLOSE_MCP_CREATE_LEAD` (supports `custom_fields`), `CLOSE_MCP_CREATE_CONTACT`, `CLOSE_MCP_CREATE_NOTE`, `CLOSE_MCP_CREATE_TASK`, `CLOSE_MCP_UPDATE_LEAD`
  (the `close_mcp` connection acts as Sheila). Email logging only exists as `CLOSE_CREATE_EMAIL`
  on the `close` connection (acts as Jay DeCristofaro) — that's expected.
- Airtable: Airtable connector `search_records` (read only).
- Slack: Composio `SLACK_SEND_MESSAGE` (use `thread_ts` for thread replies); history via
  `SLACK_FETCH_CONVERSATION_HISTORY` and thread replies via `SLACK_FETCH_MESSAGE_THREAD_FROM_A_CONVERSATION`.

## Step 1 — Find trigger emails

Search Jordan's mailbox:

```
from:helen@smbdealhunter.xyz cc:jkempster@smbdealhunter.xyz newer_than:1d
```

(also run the same query with `to:jkempster@smbdealhunter.xyz` in place of `cc:`
to catch replies where Helen put Jordan on the To line).

For each message, read the full message and keep it only if **Helen's own new
text** (above the quoted "On … wrote:" block) mentions Jordan being looped in to
talk to the person, e.g.:
- "@Jordan on our team can grab 15 minutes with you…"
- "Looping in Jordan from our team. @Jordan, do you mind finding 15 minutes to give X a call?"

Skip: plain forwards Helen sends only to Jordan ("Fwd:"), messages where the
@Jordan mention is only inside quoted text, and messages from anyone else.

If nothing qualifies, stop here (no Slack post).

## Step 2 — Skip already-handled messages

Read the last 2 days of `#helen-email-digest` (`SLACK_FETCH_CONVERSATION_HISTORY`, `oldest` = now − 2 days).
For every top-level message whose text starts with `Hourly Close Lead Creation Report`, fetch its
thread replies (`SLACK_FETCH_MESSAGE_THREAD_FROM_A_CONVERSATION` with its `ts`). Also look at the
top-level messages themselves (older runs posted there). If any message or reply contains
`gmail:<this message id>`, skip that email: it was already handled.

## Step 3 — Identify the prospect and check for duplicates

**Prospect** = the external recipient of Helen's reply (To/CC addresses that are
not `@smbdealhunter.xyz` / `@dylanhelen.com`). Get their name from the quoted
"On …, Name <email> wrote:" line or their signature. Also pull any phone number,
title, company and LinkedIn from their signature.
If there is not exactly one external recipient, or no usable name → **flag** (reason: "can't identify prospect").

Run ALL of these checks:

Close:
1. `lead_search(full_text=<email>)`
2. `lead_search(name=<full name>)`
3. If phone known: `lead_search(full_text=<10 digits, no punctuation>)` and `search("contacts with phone <+1XXXXXXXXXX>")`

Airtable "All Clients" (`search_records`, read only):
4. query = email, fields `["Email", "Partner Email"]`
5. query = full name, fields `["Name", "Additional Member Name", "Name of Partner"]`
6. If phone known: query = `+1XXXXXXXXXX`, fields `["Member Phone Number", "Partner Phone Number"]`

Decide (first matching rule wins):
- **Email or phone matches exactly one Close lead** → the person already has a Close profile →
  **do not create a lead.** Add Jordan's three tasks to that existing lead (step 5, using its
  `lead_id` and the matching contact's `contact_id`), then report it (step 6, "existing lead").
- **Email or phone matches more than one Close lead** → **flag** (reason: "matches multiple Close leads", list them).
- **Email or phone matches only an Airtable client** (no Close lead) → **flag**
  (reason: "existing client in Airtable but no Close profile", include the client name).
- **Full name matches exactly** (same first + last name, case-insensitive) in Close or Airtable
  **but email/phone do not** → **flag** (reason: "name matches existing record(s) but email differs",
  include links/record names). Do not create.
- Only surname or partial matches (e.g. other "Habib"s) → not a duplicate.
- All clean → step 4 (new lead).

## Step 4 — Create the Close lead

a. `CLOSE_MCP_CREATE_LEAD`:
   - `name`: prospect full name
   - `status_id`: Potential
   - `custom_fields`: Lead Owner, Setter, Initial Contact User = Jordan; Creation Date = Helen's reply timestamp
   - `description`: company name if known (e.g. "Asset Manager, Giving Lotus Capital")

b. `CLOSE_MCP_CREATE_CONTACT` on that lead: name, title (if in signature),
   email (`type: office` if a company domain, else `home`), phone in `+1XXXXXXXXXX`
   format (`type: mobile`) if in signature, LinkedIn URL if present.

c. `CLOSE_MCP_CREATE_NOTE` (title "Helen email referral"), plain text:
   ```
   Source: Helen Guo email referral → looped in Jordan Kempster on <reply date>.

   Prospect's email (<original date>): <2-4 sentence summary of what they asked / want>

   Helen's reply (<reply date>, cc Jordan): "<Helen's new text verbatim>"

   Gmail thread: <display_url of Helen's reply>
   gmail:<Helen's reply message id>
   ```

d. Log both emails with `CLOSE_CREATE_EMAIL` (logging only; never use `outbox`/`scheduled`):
   1. The prospect's original email to Helen: `status: "inbox"`, `sender`: prospect,
      `to: ["helen@smbdealhunter.xyz"]`, subject, `body_text`: their message only
      (strip the quoted newsletter), `activity_at` / `date_created`: its timestamp, `contact_id`.
   2. Helen's reply: `status: "sent"`, `sender: "Helen Guo <helen@smbdealhunter.xyz>"`,
      `to`: prospect, `cc: ["jkempster@smbdealhunter.xyz"]`, same subject, `body_text`:
      Helen's new text, `activity_at` / `date_created`: its timestamp, `contact_id`.
   If the original email's timestamp isn't in the headers, use the date from the
   "On …, wrote:" line.

e. Qualification fields: only if the prospect's email says so outright. Example:
   "commercial cleaning company in 1-2 specific markets" → set
   `What does your search criteria look like?` (`cf_fMji3IHe85zXS7ze4egNyKjSmGvLgsC5HqVTGNdZ4mo`)
   via `CLOSE_MCP_UPDATE_LEAD`. Never guess liquidity, timeline, etc.

## Step 5 — Create Jordan's three tasks (new leads AND existing leads)

### 5a. Find Jordan's day-1 email draft on the tracker

The daily Helen email digest (repo `sheila-smbdh/email-triage`, `skills/helen-email-digest/SKILL.md`)
already writes Jordan's first email for every lead it hands to him, in column **N**
("Suggested Setter 1st Response") of `'Tracker (JordanK)'`. Task 1 carries that draft, so Jordan
has his email ready in Close. Do not write your own when the tracker has one.

The tracker has no email-address column. Each row is keyed by the Gmail thread id of the lead's
email **in Helen's mailbox**, inside the column J hyperlink
(`=HYPERLINK("https://mail.google.com/mail/u/?authuser=helen@smbdealhunter.xyz#all/<threadId>", …)`).
Helen's reply has a different thread id in Jordan's mailbox, so match through Helen's mailbox:

1. `GMAIL_FETCH_EMAILS` with `account: "gmail_kath-tiou"`, `query: "from:<prospect email>"`,
   `ids_only: true`, `max_results: 50`. Collect the `threadId`s.
2. Read the tracker once per run: `GOOGLESHEETS_BATCH_GET`, `ranges: ["'Tracker (JordanK)'!A1:N1000"]`,
   `valueRenderOption: "FORMULA"` (so J shows the URL, not just the subject). Row 1 is the header.
3. The matching rows are those whose column J URL ends in `#all/<one of those threadIds>`.
   Among them, take the most recent (latest column A date) with a non-empty column N. Use that N
   **verbatim**: do not reword it, and leave `[today/tomorrow]` bracketed if it is there
   (Jordan picks the day).
4. **Fallback, only if no row matches or N is empty** (e.g. Helen replied before the digest logged
   the lead, or the row is a `Forward to …` row): use this generic draft, with `<First>` = the
   prospect's first name (or `Hi there,` with no name if you only have an email address). If the
   prospect's own email to Helen included a phone number, replace `What's the best number for me
   to call?` with `I'll give you a call [today/tomorrow].` Nothing else changes. No em dashes, no
   pricing.
   ```
   Hi <First>,

   Picking up from Helen, I'd love to grab 15 min to learn more and see how we can help. What's the best number for me to call? Alternatively, you can grab 15 min here on my calendar: https://calendly.com/jkempster-smbdealhunter/intro-call-with-smb-deal-hunter
   ```
   Note the source (`tracker row <n>` or `fallback: <why>`) for the Slack report.

If Helen's mailbox or the tracker can't be read, use the fallback draft, keep going (the lead and
tasks still matter more than the draft), and say so in the Slack report.

### 5b. Create the tasks

Same three tasks either way. On an existing lead, prefix Task 1's text with
`Helen re-referred this existing lead on <reply date>. ` so Jordan has context.

`CLOSE_MCP_CREATE_TASK` with `assigned_to` = Jordan, `lead_id` = the new (or existing) lead, `contact_id` = the prospect's contact on it,
`due_date` as below, `send_notification: true`. Let D0 = today (America/Denver).

**Task 1**, due D0 (`<draft>` = the email from 5a, with its real line breaks):
```
Day 1 (Helen referral): Respond TODAY. Call <First> at <phone or "no number yet — reply on Helen's thread and ask for best number"> or get a call booked. Calendar: https://calendly.com/jkempster-smbdealhunter/intro-call-with-smb-deal-hunter

Email to send now, reply-all on Helen's thread (keep Helen on it):

<draft>
```

**Task 2**, due D0 + 1 day:
```
Day 2 check-in: Call booked? Lead responded? If NOT → call again + send follow-up email on the same thread:

If you have their number and called:
Hi <First>,

Gave you a call yesterday but didn't reach you — wanted to follow up and try you again today.

If it's easier, grab 15 minutes here: https://calendly.com/jkempster-smbdealhunter/intro-call-with-smb-deal-hunter

If you don't have their number:
Hi <First>,

Sent over my availability yesterday but haven't seen a booked call come through yet, so wanted to follow up with it again: https://calendly.com/jkempster-smbdealhunter/intro-call-with-smb-deal-hunter

What's the best number to reach you at?
```

**Task 3**, due D0 + 5 days:
```
Day 5 breakup email — ONLY if Day 2 also went nowhere (still no response / no booked call). Email only, no call. Same thread:

Hi <First>,

Helen mentioned you were interested, but we haven't had a chance to connect yet. Should I stop following up?
```

## Step 6 — Slack report (one parent line + one thread reply per person)

Collect every outcome from this run first. **If there are none (nothing created, no tasks
added, nothing flagged), post nothing.** Otherwise:

1. Post the parent message to `C0BTCGZSF9R` with `markdown_text` exactly:
   `Hourly Close Lead Creation Report`
   Save the returned `ts`.
2. For each outcome, post one reply with `SLACK_SEND_MESSAGE`, `channel: C0BTCGZSF9R`,
   `thread_ts: <parent ts>` (do NOT set `reply_broadcast`):

**New lead created:**
```
:new: **New lead: <Full Name>**
• Email: <email> | Phone: <phone or —>
• <title, company if known>
• Asked: <one-line summary>
• Helen looped in Jordan on <reply date>
• Close: https://app.close.com/lead/<lead_id>/
• Tasks for Jordan: Day 1 (<D0>), Day 2 (<D0+1>), Day 5 breakup (<D0+5>)
• Day 1 email draft: <tracker row <n> | fallback: <why>>
_gmail:<Helen's reply message id>_
```

**Existing Close lead (tasks added, no new lead):**
```
:repeat: **Existing lead re-referred: <Full Name>**
• Already in Close: https://app.close.com/lead/<lead_id>/ (status: <status label>)
• Asked: <one-line summary>
• Helen looped in Jordan on <reply date>
• Added tasks for Jordan: Day 1 (<D0>), Day 2 (<D0+1>), Day 5 breakup (<D0+5>)
• Day 1 email draft: <tracker row <n> | fallback: <why>>
_gmail:<Helen's reply message id>_
```

**Flag (nothing created)** — must start with the `<@U0BM6J8KM32>` mention so Sheila is notified:
```
<@U0BM6J8KM32> :warning: **Needs your review — nothing created: <name or email>**
• Reason: <reason>
• Possible matches: <Close lead links / Airtable client names>
• Gmail: <display_url>
_gmail:<Helen's reply message id>_
```

## Step 7 — Finish

Print a short summary: messages scanned, leads created (with links), existing leads
given tasks, flagged, skipped as already handled, and how many Day 1 drafts came from the
tracker vs. the fallback. If any tool call failed partway
through creating a lead, post a :warning: flag (with the `<@U0BM6J8KM32>` mention) describing exactly what was and
wasn't created so a human can clean it up. Do not retry lead creation in that case.
