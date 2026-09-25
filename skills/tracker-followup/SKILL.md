---
name: tracker-followup
description: Daily follow-up pass over leads already in the Google Sheets tracker — chase Helen's un-forwarded handoffs (to Jordan, Scott, or a lead's previous closer/setter), check Jordan's booking progress in Close, record the forward date and Jordan's 1st/3-day/5-day touches (M, O, Q, S), and keep column N's Jordan draft current: write it where the digest did not, and never delete one
---

You are running the daily **tracker follow-up** pass for SMB Deal Hunter.

This is the second half of the daily routine. The `helen-email-digest` task looks
*forward* — it finds new buyer leads in Helen's inbox and logs them. This task looks
*backward* — it walks leads already in the tracker and asks, for each one that has come
due, whether it actually moved.

It runs **unattended in the cloud**. There is no human at a keyboard when it fires. Every
step completes through connectors or fails loudly to Slack.

**It is read-only on email and on Close CRM.** It never replies, forwards, labels,
archives or deletes an email, and never writes to Close. Its only writes are to the
tracker and to Slack. Drafts are written for a human to paste — nothing is sent.

---

## The shape of the thing

Each tracked lead moves along one path:

```
Tier 1, owner Helen  ──Helen forwards to Jordan──▶  In Progress, owner Jordan  ──setter call on the board──▶  resolved
        │                                                    │
        └── not forwarded → nag Helen in Slack               └── no setter call → Jordan's draft stands
```

This task's whole job is to work out where each due lead sits on that path, record it, and
keep the one artefact that unblocks the next step correct.

**Forward rows take a shorter path.** Since 2026-09-24 the digest also logs leads that go to
someone who already knows them: column D reads `Forward to <First Last> (<email>)` (Scott
for an existing client, or the closer/setter who held the lead's most recent call). For those
rows the only question is whether Helen forwarded to **that person**. Once she has, the row is
done: that person owns the relationship, there is no Jordan draft, and this task checks
nothing further.

```
Tier 1, owner Helen, D = Forward to X  ──Helen forwards to X──▶  In Progress, owner X  (done)
        │
        └── not forwarded → nag Helen in Slack
```

**The draft itself now arrives earlier than this pass.** `helen-email-digest` writes both
Helen's draft (column L) and Jordan's (column N) the morning a lead is logged, so a lead no
longer waits for this pass to have a reply ready. What is left here is the part only a later
check can know: whether the call actually got booked. So what is left for column N here is
narrow — **write a draft only where the digest left a gap, and never remove one.**

---

## STEP 0 — Access preflight

Identical to `helen-email-digest`. All email and tracker access goes through the
**Composio connector**; the first-party Gmail connector authenticates as
`sheila@smbdealhunter.xyz` only and cannot reach Helen's mailbox.

| Purpose | Composio toolkit | Account id | Mailbox |
|---|---|---|---|
| Read Helen's mail | `gmail` | `gmail_kath-tiou` | `helen@smbdealhunter.xyz` |
| Tracker read/write | `googlesheets` | `googlesheets_gyte-urlar` (alias `helen-tracker`) | — |

**Account selection is required on every Gmail call** — two mailboxes are connected and
the default is a flippable setting. Pin `gmail_kath-tiou` explicitly every time.

Close CRM is read through the **first-party Close connector** (`mcp__Close__*`),
read-only.

If either Composio toolkit is not ACTIVE, do not run a partial pass. Post to Slack
`C0BTCGZSF9R` and stop:

> ⚠️ The tracker follow-up pass couldn't run — the Composio `<toolkit>` connection is not
> active (status: `<status>`). Sheila needs to reconnect it at
> https://dashboard.composio.dev, then this task can run again.

Report the status you actually observed. **Never assert a cause you have not verified** —
an earlier version of the digest task hardcoded a wrong diagnosis and sent the team
looking in the wrong place for eight days.

If the **Close** connector is missing, that is not a reason to abort — but it is a reason
to leave column N alone. Every Jordan check fails to confirm, and an unconfirmed check is
**not** evidence either way. Write no new drafts for those rows and leave N exactly as you
found it. Note in column U (`Setter Progress`) that the check could not run, and say so in
Slack. Treating a Close outage as "no call booked" would put a fresh "let's grab 15 minutes"
draft against a lead who has already had their call.

---

## STEP 1 — Read the tracker and find the due rows

Tracker: https://docs.google.com/spreadsheets/d/1auWB8iQAwTYQrKhgHhb-paUuCH35j35RDiQdSC5uhBQ/edit?gid=1722038405#gid=1722038405
Spreadsheet ID: `1auWB8iQAwTYQrKhgHhb-paUuCH35j35RDiQdSC5uhBQ`
Tab: **`Tracker (JordanK)`** (sheet id `1722038405`)

**The tracker moved to a new tab on 2026-09-23**, when Jordan Kempster
(`jkempster@smbdealhunter.xyz`) took over from Yobani as the setter Helen cc's and forwards
to. Every read and write in this task goes to **`Tracker (JordanK)`** and only that tab.

- The old tab is now called **`Tracker (Yobani)`** (sheet id `0`). It is history. **Do not
  read it for due rows, do not write to it, and do not chase anything in it** — its open
  leads are frozen as they were on 2026-09-22, by Sheila's decision. A range written as
  bare `Tracker!…` no longer resolves to either tab; always use the quoted name.
- The tab name contains a space and parentheses, so it must be quoted in A1 notation:
  `'Tracker (JordanK)'!A1:W<n>`. Unquoted, the range fails to parse.
- The new tab started empty (header only). On the first passes there may be no due rows at
  all — that is expected, not a failed read. Say so in the run report and post nothing to
  Slack (STEP 5).

Read `'Tracker (JordanK)'!A1:W<n>` with **`valueRenderOption: "FORMULA"`**. This matters: column J
holds `=HYPERLINK(...)` and the formatted read gives you only the visible subject text,
throwing away the thread ID you need in Step 3.

Columns A–W:

`Date | Tier | Category | Recommended Action | Forwarded to Setter? | Owner | Last Check-in Date | Next Check-in Date | Email Sender | Email Title / Link | Message Summary | Suggested Helen Email Draft | Helen Forward Date | Suggested Setter 1st Response | Setter 1st Response Done? | Setter 3-day follow-up date | Setter 3-day follow-up done? | Setter 5-day follow-up date | Setter 5-day follow-up done? | Setter Call Date | Setter Progress | Closer Call Date | Closer Progress`

Row 1 is the header; data starts at row 2. Column X (`Note`) is a free-text column for
people; this task neither reads nor writes it.

**Same column letters as the old tab; only the headers changed.** The layout is identical
to `Tracker (Yobani)` column for column. The headers that named Yobani now say **Setter**
instead (`Forwarded to Yobani?` → `Forwarded to Setter?`, `Suggested Yobani 1st Response` →
`Suggested Setter 1st Response`, and so on through S). In this file "the setter" is Jordan.

**E asks whether Helen handed this lead over** (`Yes`/`No`), and F keys off `E="No"`. **O**
is a second "is it done?" column asking a different question — E is Helen's action, O is
Jordan's.

**M–S track the handover and the chase; T–W track the two stages of a lead's journey.**

- **M (Helen Forward Date)** is the date Helen *actually* forwarded the lead to Jordan,
  verified from the thread — not the date the handover was recommended. **This task writes
  it** on the pass where STEP 2 confirms the forward, and backfills it on any forwarded row
  where it is still empty (STEP 3A). Empty means the forward has not been confirmed yet, and
  the whole chase cadence below stays dormant.
- **O (Setter 1st Response Done?)** is `Yes` once Jordan has **actually sent a reply to the
  prospect**, `No` until then. Those two values only — it does **not** take
  `Not Needed - Connected`. **This task writes it** (STEP 3A).
  **O is not a copy of E.** Helen can forward a lead (E = `Yes`) and Jordan not get to it
  for days (O = `No`); that gap is the whole reason the column exists. Never derive O from
  E. (On the old `Tracker (Yobani)` tab, O matched E on every row only because of a one-off
  backfill on 2026-09-11 — that was never a rule, and it does not carry over.)
- **P (`=M+2`) and R (`=M+5`)** are formulas giving the dates Jordan's next-day and 5-day
  follow-ups come due (the column header still says "3-day"; P moved from `=M+3` to `=M+2`
  on 2026-09-24). They read `2` and `5` while M is empty — arithmetic on a blank cell,
  not a literal to clean up. **Never write a literal date to P or R.**
- **Q and S** are the matching `done?` flags, also this task's to write (STEP 3A). Allowed
  values, exactly: `Yes`, `No`, and `Not Needed - Connected` (the lead is already connected,
  so the touch is moot). No other text, no free-form notes. Each stays **blank until its
  date in P or R arrives**.
- **N is the *first* of three touches.** There is no column for a 2nd or 3rd draft, and
  this task does not write one — O–S carry dates and status only.
- **T/U are the setter stage** — the short intro call that gets a lead onto the board,
  which is Jordan's job. **V/W are the closer stage** — the longer discovery/closing call
  that follows. Read the pair separately: a lead can have a completed setter call and a
  failed closer call, and conflating them loses the only fact worth acting on.

**Dates come back as Google serial numbers** under a FORMULA or UNFORMATTED read. Serial
`46275` = 2026-09-10. Convert with `date = 1899-12-30 + serial days`. Compute today's
serial the same way and compare numerically — do not string-compare formatted dates.

**A row is due when `H <= today`.** H is the formula `=G+1` (it was `=G+5` until
2026-09-11), so read G and add 1 rather than trusting a cached H. With a one-day gap an
open lead comes due on effectively every pass.

### Scope filter — apply in this order

1. **`Recommended Action` (D) is `Ignore` → out of scope.** Skip the row entirely: no
   checks, no draft, and **do not touch column G**. The digest stopped writing `Ignore` on
   2026-09-24 (those leads are now dropped with no row), so only older rows carry it. They
   will read as perpetually due and that is fine — they are skipped every run at no cost.
2. **`Tier` (B) is `1` → run STEP 2** (the forward check), whatever D says.
3. **`Tier` (B) is `In Progress` and D starts `Forward to ` → out of scope.** Helen has
   forwarded it to the person who already knows the lead, and that is the end of this
   task's involvement. Skip it like an `Ignore` row, and do not touch G.
4. **`Tier` (B) is `In Progress` and D is `Send to Jordan` → run STEP 3** (the Jordan check).
5. Any other tier value is historical. Leave it alone.

---

## STEP 2 — Tier 1: did Helen actually forward it?

For every due Tier 1 row, the question is whether the person in column D has been looped in
yet: Jordan on a `Send to Jordan` row, or the address inside the parentheses on a
`Forward to <First Last> (<email>)` row (e.g. `scott@smbdealhunter.xyz`).

### Get the thread ID out of column J

Column J is `=HYPERLINK("<url>","<subject>")`. Pull the URL and take the thread ID from
its fragment. **Three URL formats exist in the sheet** and the first is a trap:

| Format | Example fragment | Thread ID |
|---|---|---|
| Legacy, URL-encoded decimal | `#inbox/%23thread-f%3A1874806018152371407` | **decimal — convert to hex**: `1a04a623eebc94cf` |
| Delegation-token URL, hex | `/d/<token>/#inbox/1a04e6390ccde4d0` | `1a04e6390ccde4d0` as-is |
| Current `authuser=` form, hex | `?authuser=helen@...#all/1a08bf287ff6e1ef` | `1a08bf287ff6e1ef` as-is |

The Gmail API takes the **hex** thread ID. A `%23thread-f%3A` fragment is
`#thread-f:<decimal>` percent-encoded; `format(int(decimal), 'x')` gives the API ID. Pass a
raw decimal and the fetch 404s.

The delegation-token URLs no longer open in a browser — that delegation lapsed — but the
thread ID inside them is still valid. Extract it and ignore the dead prefix.

### Find each forward target's involvement in ONE query per person

Do **not** fetch each thread and scan its participants — that is one call per row for a
question a single search answers. Jordan is `jkempster@smbdealhunter.xyz`. Run one
`GMAIL_FETCH_EMAILS` on `gmail_kath-tiou` for Jordan, and one more, the same shape with the
address swapped, for each other distinct address in a due row's `Forward to …` action:

```
query: {to:jkempster@smbdealhunter.xyz cc:jkempster@smbdealhunter.xyz bcc:jkempster@smbdealhunter.xyz from:jkempster@smbdealhunter.xyz} after:<YYYY/MM/DD>
max_results: 100
verbose: false
```

Braces are Gmail's OR syntax. Set `after:` a day before the oldest due row's Date so the
window covers every lead in play, and page through `nextPageToken` until it is absent or
empty-string.

That returns every message in Helen's mailbox that involves that person, each with its
`threadId`, `subject`, `messageTimestamp` and `preview.body`.

**Run the Jordan query once per pass, over every due row — not just the Tier 1 ones.** STEP 3A
reads the same result set to see what Jordan has sent on the `In Progress` rows, so set its
`after:` from the oldest due row of either kind. One query answers both questions; do not run
it twice.

**Only the person in column D counts.** Match each due row only against the results for its
own forward target. A `Send to Jordan` row forwarded to someone else (the old setter,
`yobani@smbdealhunter.xyz`, say) is **not forwarded**: say in its 🔴 bullet who it went to
instead of Jordan. The same holds the other way: a `Forward to Scott …` row that Helen sent to
Jordan is not forwarded, and its bullet says so. Yobani is a valid target only on a row whose
D reads `Forward to Yobani Mendoza (yobani@smbdealhunter.xyz)`.

### Match a due row to that set

A row counts as forwarded if **either** holds:

- **Same thread** — the row's thread ID appears in the result set. A forward often stays
  in the original thread, so this is the common case.
- **Separate thread** — a result's subject is `Fwd: <the row's subject>` (compare with
  `Re:`/`Fwd:` prefixes stripped), or its `preview.body` contains the lead's email
  address. Gmail sometimes threads a forward separately, and matching only on thread ID
  would miss it.

Match on thread ID and subject/address. **Never conclude "forwarded" from the sender's
display name alone** — several leads in this sheet share first names.

### Then

**Forwarded** → Helen did her part. Write, in this run:

- **B** → `In Progress` (literal text)
- **E** → `Yes`
- **G** → today
- **M** (`Helen Forward Date`) → the date of the forward you just confirmed: the
  `messageTimestamp` of the **earliest** matching message (the first message in the row's
  thread that involves the forward target, or the `Fwd:` message), taken as a calendar date
  the same way you compute today. Write it as a date (`YYYY-MM-DD`, which `USER_ENTERED`
  coerces), never as text. Writing M is what turns P and R into real dates. If M already
  holds a date, leave it: the first forward is the one that counts.

On a `Send to Jordan` row, then **immediately run STEP 3 for this row in the same pass.**
Column F is a formula keyed off E, so setting E to `Yes` flips the owner to Jordan the
moment it lands. The row is a Jordan row now and gets the Jordan check now — it does not
wait a week for the next cycle.

On a `Forward to …` row, **stop there.** F flips the owner to that person's first name, and
the row is done; it drops out of scope from the next pass (STEP 1, rule 3). No STEP 3, no
STEP 3A, no draft. M is still written (it records when Helen handed the lead over), but O,
Q and S stay blank: they track Jordan's chase, and Jordan is not on this lead.

**Not forwarded** → nothing has happened. Write:

- **G** → today (the check ran, so the clock resets)
- B, E, M, N, O, Q, S, T–W → unchanged

and flag it to Helen in Slack (STEP 5), naming who it should go to. This is the output that matters: a Tier 1 lead
still owned by Helen days after it arrived is a lead going cold because the handoff never
happened.

**One Price Wall row is expected to sit here for a while.** When a lead pushed back on the
call itself, `helen-email-digest` gives Helen a draft that asks whether they want someone
looped in rather than cc'ing Jordan, so the forward waits on their reply. Flag it the same
way — an unanswered lead is still worth surfacing — but say in Slack that the handoff is
waiting on the lead, not on Helen. Column N is unaffected: that row carries the ordinary
Price Wall draft and this step does not touch it.

---

## STEP 3 — Jordan rows: has the call been set up?

For every row now at `In Progress` / owner Jordan, ask Close whether a call exists.

### You need the lead's email address, and the tracker does not have it

Column I holds a display name (`Michael`, `narinder Singh`, sometimes a bare address).
Close must be matched **by email address, never by display name** — see the trap below. Get
the address from Gmail: the thread's sender, or the `From:` line quoted inside Helen's
forward (`preview.body` of the Step 2 results carries it, e.g.
`From: Michael Wilson <michaeljwilson11@gmail.com>`).

If you cannot resolve an address, do not guess. Treat it as "no call booked", say so in
column U (`Setter Progress`), and flag it in Slack.

> **The name-matching trap.** `christopher green <cjgreen7904@yahoo.com>` is the Close lead
> **"CJ Green"**, while a name search for "christopher green" also returns *"Chris Green"*
> and *"Chris Greene"* — different people. A name match produces a confidently wrong
> answer. The email search returns exactly one.

### Query Close

1. `mcp__Close__lead_search` with `full_text: "<the lead's email address>"`.
2. `mcp__Close__activity_search` with `lead_ids: ["<lead_id>"]` and
   `activity_types: ["activity.meeting", "activity.call", "activity.email"]`. Batch the lead
   IDs into one call rather than one call per lead.
3. Read each result's `title`, `starts_at` / `activity_at`, and `note`. The emails are for
   STEP 3A: keep each one's direction, sender, recipients and date.

### Sort each meeting into setter or closer

Close returns every meeting on the lead. Split them by **duration first, event name
second** — the two stages are different calls:

| | Setter call → T/U | Closer call → V/W |
|---|---|---|
| Duration | ~900s (15 min) | ~2700s (45 min) |
| Event name | `SMB Deal Hunter Intro with <name>`, `Intro Call With SMB Deal Hunter Pro` | `Discovery Call with SMB Deal Hunter Pro - S2C` |

**A setter call counts even if someone other than Jordan booked it.** The question is
whether this lead got onto the board, not who gets credit. Real case: Eric Rubinstein's
intro call was held by **David Martin**, and it still resolves the row. The meeting title
names the host (`Eric Rubinstein and David Martin`), so record who it was with.

**A cancelled call is not a held call.** Close prefixes the title `Canceled:`. Never read
one as progress.

### Then

| What Close shows | T/U (setter) | V/W (closer) | N (draft) |
|---|---|---|---|
| A setter call, upcoming or already held | its date + who with, event name, any lead note | closer call if one exists | **leave it** — resolved |
| A setter call held **and** a cancelled closer call | the setter call | the cancelled call's date + that it was cancelled and by whom | **leave it** — resolved. Surface in Slack |
| No setter call, or the only one was cancelled | empty, or `No call booked` | — | **keep or write the draft** (STEP 4) |
| No Close record for the address | `No Close record for <address>` | — | **keep or write the draft** |
| Close lookup failed | that the check could not run | — | **leave exactly as found** — say so in Slack |

> **Drafts are never deleted — confirmed with Sheila, 2026-09-11.** Neither L nor N is ever
> cleared, by this task or any other. An earlier version of this spec told you to write an
> empty string to N once a setter call appeared in Close ("clear it — resolved"); **that
> rule is gone.** A draft sitting beside a completed call is not a defect to tidy up: the
> `done?` columns (O, Q, S) record whether anything was actually sent, and the draft stays
> as the record of what was offered. If you find yourself about to blank a draft cell, stop
> — that is the old rule.

**On a failed Close lookup, change nothing in N** — do not write a new draft over the one
that is there. An unconfirmed check is not evidence either way, and a draft the digest
already wrote is not made wrong by this task failing to reach Close.

Always write **G → today** for a row you checked.

**A setter call on the board resolves the row.** Once a lead has had their intro call,
Jordan's job is done and there is nothing further for him to draft. Resolving a row means
**writing no new draft** — it does not mean removing the one already there. That holds even
when the *closer* call then fell through: a cancelled discovery call needs re-booking by
whoever owns that stage, which is not a setter intro. Record it in V/W and mention it in
Slack.

---

## STEP 3A — Jordan's chase: M, O, Q, S

For every `Send to Jordan` row now at `In Progress` (forwarded this pass or earlier), record
the handover date and whether each of Jordan's three touches happened. `Forward to …` rows
never reach this step. Everything here comes from data you already have: the Jordan result
set from STEP 2 and the Close activities from STEP 3. No new queries.

### M — backfill it if it is empty

If M already holds a date, leave it. If it is empty (the forward was confirmed before this
column was written), find the forward in the Jordan result set exactly as STEP 2 does and
write its date by the same rule. If the forward cannot be found (it fell outside the
`after:` window, say), leave M empty, say so in column U, and do not write O, Q or S for
the row: without M there is no cadence to measure against.

### Jordan's touches

A **touch** is a message **from Jordan** (`jkempster@smbdealhunter.xyz`) **to the lead**,
dated on or after M. Collect them from two sources and merge them:

- **Gmail** — Jordan result set messages that are `from:` Jordan and are either in the row's
  thread or addressed to the lead's email address. Jordan replies keeping Helen on the thread,
  so these land in her mailbox.
- **Close** — outgoing `activity.email` from Jordan to the lead's address. This catches a
  reply that left Helen off.

The same message found in both counts once (match on date and subject). Sort the touches by
date. A message to Helen or anyone else, or a forward between staff, is not a touch.
Never count a message by display name alone.

**Connected** means the lead has a setter call on the board (upcoming or held, not
`Canceled:`, per STEP 3), or has replied to Jordan: a message from the lead's address dated
after Jordan's first touch.

### What to write

| Column | When to write it | Value |
|---|---|---|
| **O** 1st Response Done? | once M is set | `Yes` if there is at least one touch, else `No`. **Two values only**, never `Not Needed - Connected` |
| **Q** 3-day follow-up done? | once today ≥ the date in P | `Yes` if there is a second touch; else `Not Needed - Connected` if connected; else `No` |
| **S** 5-day follow-up done? | once today ≥ the date in R | `Yes` if there is a third touch; else `Not Needed - Connected` if connected; else `No` |

- **Before its date, Q or S stays blank.** A follow-up that is not due yet is not "not
  done". Read P and R as the serials they compute to (the sheet does the `M+2`/`M+3`/`M+5`
  arithmetic; do not recompute with your own offsets).
- **Never downgrade.** `Yes` and `Not Needed - Connected` are final: once written, leave
  them. A `No` moves to `Yes` or `Not Needed - Connected` on a later pass when the evidence
  appears.
- **Never derive O from E**, and never set O to `Yes` because a setter call exists. A lead
  can book off Helen's email without Jordan ever writing; O asks whether Jordan did.
- **On a failed Close lookup**, you cannot see Close emails or whether the lead is
  connected. Write `Yes` where Gmail alone shows the touch; otherwise leave O, Q and S
  exactly as found, and say in Slack that the chase check was partial.
- **Jordan can be missed.** A reply that neither cc'd Helen nor synced to Close is
  invisible to this task, so a `No` means "no touch found", not proof. When O, Q or S is
  `No`, say in column U what was checked (`No reply from Jordan found in Helen's mailbox or
  Close`) so a reader can tell.

---

## STEP 4 — Jordan's reply: keep or write

Only for a Jordan-owned (`Send to Jordan`) row with **no call booked**. `Forward to …` rows
never reach this step and never get a Jordan draft. A row with a setter call on the board
skips this step entirely; whatever is already in N stays put.

**Check what is already in N before writing anything.** Since `helen-email-digest` began
writing the Jordan draft at log time, most rows reaching this step already have one:

| N as read in STEP 1 | Do |
|---|---|
| Holds a draft matching the row's category, in one of the current templates below (opens `Picking up from Helen, …` and carries Jordan's real calendar link) | **Keep it, unchanged.** Write nothing to N. It has been sitting in the sheet since the digest run and may already have been used |
| Holds a draft on a **superseded** template. The tells: `[Calendly Link]` or `[Calendly link]`, `If they`, `[time slot]`, `Are you free`, `Can I give you a call at`, `Sounds like you're interested in … and I'd love to hop on a call`, `ready to move on`, `Let's grab 15 minutes so I can`, or any `—` | **Replace it** with the current template for that category, and say in Slack that you did. Every row logged before 2026-09-24 is in this state |
| Empty — a row logged before this change, or a digest run that skipped it | **Write the draft**, exactly as below |
| Holds something that is not one of these templates, or the wrong category's template | **Replace it** with the right one, and say in Slack that you did and why |

Rewriting a draft that is already correct is not free: one wording in the sheet on Monday
and a different one on Friday reads as two different people replying, and whoever pastes has
to work out which is current. Byte-identical is the goal — if you would produce the same text
that is already there, leave it.

The draft is **a reply on the existing thread, keeping Helen on it** so the handoff stays
tracked. Not a fresh email. The lead has been talking to Helen, so the reply picks up from
her rather than introducing a stranger.

### What day 1 is

Every draft here is Jordan's **day-1 response** — the first contact he makes once Helen has
forwarded. It is an **email, and a phone call** if he has a number to call.

| Phone number in their initial email? | Day 1 |
|---|---|
| Yes | Email, then call them, today or tomorrow |
| No | Email only. It asks for their number and offers his calendar link |

**No texting on day 1.** If he has the number he calls; if he doesn't, there's nothing to
text. Either way the text is redundant.

"Number provided" means a number in the **initial email they sent** — a signature block
counts, a number dug out of the CRM or the web does not. Column K's summary usually will not
settle it, so read the lead's own first message in the thread before writing the draft. You
already have the thread ID from STEP 2.

### The three templates

One per category, word for word as Sheila wrote them on 2026-09-24, identical to the ones
in `helen-email-digest`. Use the template for the row's category (column C). There are no
variants.

**Buy Box**

```
Hi [First Name],

Picking up from Helen, sounds like you're interested in [buy box criteria]. I'd love to grab 15 min to better understand your buy box and see how we can help. What's the best number for me to call? Alternatively, you can grab 15 min here on my calendar: https://calendly.com/jkempster-smbdealhunter/intro-call-with-smb-deal-hunter
```

**Ready Now**

```
Hi [First Name],

Picking up from Helen, I'd love to grab 15 min to learn more and see how we can help. What's the best number for me to call? Alternatively, you can grab 15 min here on my calendar: https://calendly.com/jkempster-smbdealhunter/intro-call-with-smb-deal-hunter
```

**Price Wall**

```
Hi [First Name],

Picking up from Helen, I'd love to grab 15 min to get a better sense of your situation and make sure we're the right fit for what you're looking to do. What's the best number for me to call? Alternatively, you can grab 15 min here on my calendar: https://calendly.com/jkempster-smbdealhunter/intro-call-with-smb-deal-hunter
```

This template doesn't answer the pricing question. It moves the conversation to a call.

**When they already gave a number**, replace `What's the best number for me to call?` with
`I'll give you a call [today/tomorrow].` and leave the rest of the template unchanged. With
no number, the template goes out exactly as written.

### Filling them in

**`[today/tomorrow]` stays a literal bracketed placeholder** (it only appears when the lead
gave a number). Jordan picks the day himself: Sheila's Calendly token is role `user` and
cannot read another user's availability (`event_types-list_event_types` returns Permission
Denied), so any day you commit him to would be invented.

**The calendar link is real**: `https://calendly.com/jkempster-smbdealhunter/intro-call-with-smb-deal-hunter`,
Jordan's own intro-call page, supplied by Sheila on 2026-09-24. Copy it exactly, and never
use the old setter's link (`https://calendly.com/yobani-smbdealhunter`).

**No em dashes.** None in the templates, and none added when filling them in. Do not use an
en dash or a spaced hyphen as a stand-in either; a comma or a period does the job.

**First name.** The name the sender signs off with in the email body, else the first word
of their Gmail display name. If there is **no display name** — a bare address like
`ms.raquele@gmail.com` — open with `Hi there,` and drop the name. Getting a name wrong in
the first three words is worse than not using one.

**Pronouns.** The templates address the lead as "you" for this reason. Never infer a
lead's gender from their name; where a third-person reference is unavoidable, use
they/them unless the sender's own signature makes it explicit.

**`[buy box criteria]`** (Buy Box) is what they asked for, in their own words, phrased to
follow "interested in": `hotels in California`, `businesses in Central FL`, `absentee
businesses`. **Never inflate a vague ask into a specific one.** If the ask is too vague to
name in a few words, write `what we've got`.

**Never invent commercial terms.** No draft here quotes a price, a fee, a range, a
guarantee or a timeline. Note that unlike Helen's Price Wall draft, **Jordan's Price Wall
template deliberately does not answer the pricing question** — it moves to a call. Do not
import the 1% line from the digest task's templates into it. If a lead asked a direct
pricing question, the call is where it gets answered.

**Nothing else goes in.** A finished draft is the template plus the substitutions above.
If it says something the template does not, take that back out.

---

## STEP 5 — Post the follow-up digest to Slack

Post to channel `C0BTCGZSF9R` (#helen-email-digest) as its **own message**, separate from
the morning lead digest — the two answer different questions and merging them buries both.

Use the channel's established format: a bold header, emoji section headers, and
`_Category_ — Sender: "<link|subject>" — detail` bullets.

Sections, each skipped entirely when empty:

- **Header** — `**Tracker Follow-up — <Month D, YYYY>**` and the count of due rows checked.
- **🔴 Needs Helen** — Tier 1 rows never forwarded. One bullet each, subject linked
  straight into the thread in Helen's mailbox:

  `_Category_ — Sender: "[subject](<gmail thread link>)" — waiting N days`

  On a `Forward to …` row, add who it goes to: `— forward to Scott (existing client)` or
  `— forward to Jabali (previous call)`, so Helen does not send it to Jordan by habit.

  Two things carry this section. **The link**: Helen clicks the subject, lands on the
  thread, and forwards it to Jordan — no hunting through the inbox or the tracker for a
  lead that has already gone cold. **The number of days**: say how long each has been
  waiting, because that is what makes the bullet urgent rather than informational. Mention
  Helen as `<@U04ATRJKXPD>` once, in this section.

  **Build the link yourself from the thread ID — do not paste column J's URL into Slack.**
  Two of the three formats in the sheet (see STEP 2) do not open in a browser: the legacy
  `%23thread-f%3A<decimal>` fragment, and the delegation-token URL whose delegation lapsed.
  You already extracted the hex thread ID in STEP 2; rebuild the link from it in the current
  form, the same one `helen-email-digest` writes:

  ```
  https://mail.google.com/mail/u/?authuser=helen@smbdealhunter.xyz#all/<hex threadId>
  ```

  `authuser=` pins the link to Helen's mailbox. The `/mail/u/0/` form opens whichever
  account happens to be first in the reader's browser, which for anyone but Helen is the
  wrong mailbox or a 404.

  If a row's thread ID cannot be recovered at all, still list the row with the subject
  unlinked and say the link is missing. A lead going cold is worth flagging without a link;
  dropping it because the link failed is not a trade worth making.
- **🟡 Needs a decision** — rows Step 3 could not resolve: an address that would not
  resolve to a Close lead, a failed Close lookup.
- **🟢 Moving** — rows with a setter call on the board. One line each: who with, and when.
  Where the closer call was cancelled, say so on the same line — it is the one actionable
  fact on an otherwise resolved row. Their drafts stay in the sheet untouched; there is
  nothing to report about them.
- **✍️ Drafts** — *not in the message body.* See below.

Write the message in standard markdown (`**bold**`, `_italic_`, `[text](url)`); the Slack
tool converts it to Slack mrkdwn on send. **Do not add a "Sent using Claude" footer** —
the platform appends one automatically, and including your own produces it twice.

If no row was due at all, post nothing. A daily "nothing to do" message in a channel that
also carries the lead digest is noise. Say it in the run report instead.

### Drafts go in a threaded reply

Capture the parent message's `ts` and post the drafts as **one threaded reply** with
`thread_ts`. Full drafts inline would bury the flags the message exists to deliver.

Include a lead here only when **this pass** wrote or replaced its draft. A draft carried
over unchanged from the digest run is already sitting in column N, where Jordan reads it;
reposting it on every pass turns the channel into an echo and makes it unclear which copy is
live. (The digest run stopped posting drafts to Slack on 2026-09-11, when Helen's reply moved
into her Gmail as a draft — Jordan's has always lived in the sheet, and now that is the only
place it appears until a pass here changes it.)
If the section would be empty because every due row's draft was already correct, say so in
one line in the parent message instead ("3 drafts already current, unchanged").

Format — one block per draft, each in a code block so it copies cleanly:

> ✍️ *Suggested replies for Jordan* — reply on the existing thread and keep Helen on it.
> **Fill in `[today/tomorrow]` before sending** where it appears, and call them that day.
>
> *Ready Now — Jerome M Limage*
> ```
> Hi Jerome,
> …
> ```

If this pass wrote or replaced no draft, **post no thread reply at all** — not an empty one.
A pass where every draft was already current is the normal case, not a failure.

Do not use `@channel` or `@here`.

---

## STEP 6 — Write the tracker back

All writes go to the rows you already identified. Never append a row: this task updates
existing leads, it never creates them.

**Columns F and H are formula-driven. Never write a literal to either.**

- **F (Owner)** `=if(E<n>="No","Helen",if(left(D<n>,11)="Forward to ",regexextract(D<n>,"^Forward to (\S+)"),"Jordan"))` on rows the digest wrote from 2026-09-24; older rows hold
  `=if(E<n>="No","Helen","Jordan")`. Either is correct for its row; leave whichever is there
- **H (Next Check-in Date)** `=G<n>+1`
- **P (Setter 3-day follow-up date)** `=M<n>+2` on rows the digest wrote from 2026-09-24;
  older rows hold `=M<n>+3`. Either is correct for its row; leave whichever is there
- **R (Setter 5-day follow-up date)** `=M<n>+5`

They already hold these formulas on every existing row. Setting E and G is what moves F and
H — F recomputes the owner and H recomputes the due date on its own. P and R work the same
way off M: writing the forward date into M is what turns `3` and `5` into real dates.
Writing any of the four by hand converts a live formula to a dead literal and the row stops
tracking.

**F is updated through E, then checked.** This task is responsible for F reading the right
owner on every row it touches, but it gets there by writing E, not by writing a name into F.
After the write, the verify step re-reads F. If a row's F is no longer a formula (someone
typed or pasted a name over it) or reads `#N/A`, `#VALUE!` or `#ERROR!`, **restore the
formula** in that one cell with the 2026-09-24 form above, which gives the same answer as the
older form on a `Send to Jordan` row. Say in Slack which rows you repaired. Never write a
plain name into F.

**F on this tab does not use the `Responsibility` lookup.** `Responsibility!A2:B9` still maps
Buy Box, Ready Now and Price Wall to *Yobani*, and it stays that way so the old tab's owner
column keeps reading correctly as history. The new tab names Jordan directly instead. Do not
edit `Responsibility`, and do not "restore" an `xlookup` formula into F on this tab — it
would show Yobani as the owner of Jordan's leads.

### What to write per row

The pass writes **B, E, F, G, M, N, O, Q, S, T, U, V and W**, each only as the steps above
decide. F is the exception to "write": it is kept correct through E and repaired if broken
(see above), never given a literal.

| Column | Value |
|---|---|
| **B** Tier | `In Progress` — only on a row whose forward you just confirmed |
| **E** Forwarded to Setter? | `Yes` — same rows only. Match the existing casing exactly |
| **F** Owner | nothing written directly. It follows E; the verify step restores the formula if it is broken |
| **G** Last Check-in Date | today, on **every** row you checked (including not-forwarded rows) |
| **M** Helen Forward Date | the forward's date (STEP 2), or a backfill on a forwarded row where it is empty (STEP 3A). Never overwrite a date already there |
| **N** Suggested Setter 1st Response | per STEP 4: **omit the cell from the write** when the existing draft stands; the new draft (plain text with real line breaks, not a formula, not quote-wrapped) when you wrote or replaced one. **Never an empty string** — drafts are not deleted, including on a resolved row. On a failed Close lookup, omit it: leave what is there |
| **O** Setter 1st Response Done? | `Yes` or `No` per STEP 3A, once M is set |
| **Q** Setter 3-day follow-up done? | `Yes`, `No` or `Not Needed - Connected` per STEP 3A, once P's date has arrived. Blank before then |
| **S** Setter 5-day follow-up done? | same three values, once R's date has arrived. Blank before then |
| **T** Setter Call Date | the intro call's date. Empty when there is none |
| **U** Setter Progress | short factual context: who with, event name, any note the lead left, and what the chase check found when O, Q or S is `No` |
| **V** Closer Call Date | the discovery/closing call's date. Empty when there is none |
| **W** Closer Progress | short factual context, including a cancellation and who it was with |

Do not touch A, C, D, H, I, J, K or L. **Do not touch P or R** — they are formulas. Do not
touch a row whose D is `Ignore`. On a `Forward to …` row, write only B, E, G and M (STEP 2),
never N, O, Q, S or T–W.

**Never copy E into O**, and never fill O, Q or S with a guess. They answer different
questions (Helen forwarded vs. Jordan replied), and they matched on every row of the old tab
only because of a one-off backfill, which was never a rule. A value in O, Q or S comes from
the touches STEP 3A counted, or it is not written.

### How to write

Use `GOOGLESHEETS_VALUES_UPDATE` with `value_input_option: "USER_ENTERED"` so dates coerce
to real dates. Because the due rows are usually contiguous but the columns are not, write
in per-column blocks — `'Tracker (JordanK)'!B<a>:B<b>`, `'Tracker (JordanK)'!E<a>:E<b>`,
`'Tracker (JordanK)'!G<a>:G<b>`, `'Tracker (JordanK)'!M<a>:M<b>`,
`'Tracker (JordanK)'!N<a>:N<b>`, `'Tracker (JordanK)'!O<a>:O<b>`,
`'Tracker (JordanK)'!Q<a>:Q<b>`, `'Tracker (JordanK)'!S<a>:S<b>`,
`'Tracker (JordanK)'!T<a>:W<b>` — which keeps F, H, P and R untouched by construction.
Send them together in one `GOOGLESHEETS_UPDATE_VALUES_BATCH` (note: it takes
`valueInputOption` in camelCase, unlike the singular tool's `value_input_option`) and check
every entry in `data.responses[*]`.

**Never write a rectangle that spans M to S.** `M:S` covers the date formulas in P and R;
writing it would overwrite them with literals. M, O, Q and S each take their own
single-column block, with P and R left out.

**Every block overwrites every cell in its range**, including rows you meant to leave alone.
A block write has no "leave this one alone". So for each row in a block, put in the value
that should end up there: the **exact value you read in STEP 1** for a cell you are keeping,
or the new value for one you are changing. Round-tripping the value you read is what "keep
unchanged" means mechanically. This matters most in three places:

- **N** — a kept draft goes back byte for byte. **No row ever gets `""`**; a resolved row
  keeps its draft like any other.
- **M** — an existing date goes back as the same date, never blanked or moved.
- **O, Q, S** — a `Yes` or `Not Needed - Connected` goes back as is, and a blank that is not
  due yet goes back blank.

If echoing a long draft back is awkward, write the changed rows individually as separate
ranges in the batch instead — but never send a block that blanks a cell you meant to leave
alone.

Google Sheets rate-limits at 60 writes/minute. Batch; do not write cell by cell.

### Verify, and report honestly

Re-read `'Tracker (JordanK)'!A1:W<n>` with `valueRenderOption: "FORMULA"` and confirm:

- every G you wrote is today's serial, and H is still the formula `=G<n>+1`
- every F is a formula (either form above) and none reads `#N/A`, `#VALUE!` or `#ERROR!`.
  Where one is a literal or an error, restore the formula in that cell (see *F is updated
  through E, then checked*) and re-read it. Then confirm, with a formatted read of F, that
  each row you moved shows the owner you expected: `Jordan` on a forwarded `Send to Jordan`
  row, the forward target's first name on a forwarded `Forward to …` row, `Helen` otherwise
- **P and R are still the formulas `=M<n>+2` (or `=M<n>+3` on older rows) and `=M<n>+5`** —
  a literal date in either
  means a block write ran over them
- every M you wrote is a date serial, not text, and no M that held a date before has changed
- **O, Q and S hold only their allowed values** (`Yes`/`No` in O; `Yes`/`No`/`Not Needed -
  Connected` in Q and S) or blank; Q and S are blank on every row whose P or R date is still
  in the future; no `Yes` or `Not Needed - Connected` you read in STEP 1 has changed
- B and E changed on exactly the rows you meant, and nowhere else
- N and T–W landed on the right rows
- **no draft cell is empty that was not empty before.** Every L and N you read in STEP 1 is
  still there, byte for byte, unless this pass deliberately rewrote it. A draft that came
  back blank means the block write clobbered it; restore it from what you read in STEP 1 and
  say so in Slack
- no row was added or removed

If verification fails, **say so explicitly in Slack**. Never post a success digest for a
pass that only partly completed.

---

## Scope limits

Read email, read Close, write the tracker, post to Slack. Nothing else. Specifically: do
**not** reply to, forward, label, archive or delete any email — including the forward to
Jordan that Step 2 is checking for. If Helen has not forwarded a lead, this task says so;
it does not do it for her. Do not create, update or delete anything in Close.

## Failure reporting

If any step fails, post what actually happened to `C0BTCGZSF9R` — the failing step, the
tool that errored, and the error text. Never assert a cause you have not verified, and
never report a partial pass as a success.
