---
name: tracker-followup
description: Daily follow-up pass over leads already in the Google Sheets tracker — chase Helen's un-forwarded handoffs, check Yobani's booking progress in Close, and keep column N's Yobani draft current: write it where the digest did not, and never delete one
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
Tier 1, owner Helen  ──Helen forwards to Yobani──▶  In Progress, owner Yobani  ──setter call on the board──▶  resolved
        │                                                    │
        └── not forwarded → nag Helen in Slack               └── no setter call → Yobani's draft stands
```

This task's whole job is to work out where each due lead sits on that path, record it, and
keep the one artefact that unblocks the next step correct.

**The draft itself now arrives earlier than this pass.** `helen-email-digest` writes both
Helen's draft (column L) and Yobani's (column N) the morning a lead is logged, so a lead no
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
to leave column N alone. Every Yobani check fails to confirm, and an unconfirmed check is
**not** evidence either way. Write no new drafts for those rows and leave N exactly as you
found it. Note in column U (`Setter Progress`) that the check could not run, and say so in
Slack. Treating a Close outage as "no call booked" would put a fresh "let's grab 15 minutes"
draft against a lead who has already had their call.

---

## STEP 1 — Read the tracker and find the due rows

Tracker: https://docs.google.com/spreadsheets/d/1auWB8iQAwTYQrKhgHhb-paUuCH35j35RDiQdSC5uhBQ/edit
Spreadsheet ID: `1auWB8iQAwTYQrKhgHhb-paUuCH35j35RDiQdSC5uhBQ`

Read `Tracker!A1:W<n>` with **`valueRenderOption: "FORMULA"`**. This matters: column J
holds `=HYPERLINK(...)` and the formatted read gives you only the visible subject text,
throwing away the thread ID you need in Step 3.

Columns A–W:

`Date | Tier | Category | Recommended Action | Forwarded to Yobani? | Owner | Last Check-in Date | Next Check-in Date | Email Sender | Email Title / Link | Message Summary | Suggested Helen Email Draft | Helen Forward Date | Suggested Yobani 1st Response | Yobani 1st Response Done? | Yobani 3-day follow-up date | Yobani 3-day follow-up done? | Yobani 5-day follow-up date | Yobani 5-day follow-up done? | Setter Call Date | Setter Progress | Closer Call Date | Closer Progress`

Row 1 is the header; data starts at row 2.

**Six columns were added on 2026-09-11 and everything after L shifted right.** Any column
letter you remember from an earlier run is wrong past L. The sheet went A–Q → A–V → A–W in
two edits the same day; this is the final map:

| Was (A–Q) | Is now (A–W) | What changed |
|---|---|---|
| A–D | A–D | unchanged |
| E Action Taken? | **E** Forwarded to Yobani? | renamed |
| F–L | F–L | unchanged |
| — | **M** Helen Forward Date | new |
| M Suggested Yobani Response | **N** Suggested Yobani 1st Response | moved one right, renamed |
| — | **O** Yobani 1st Response Done? | new |
| — | **P–S** the 3-day and 5-day follow-up columns | new |
| N/O Setter Call Date, Setter Progress | **T/U** | moved six right |
| P/Q Closer Call Date, Closer Progress | **V/W** | moved six right |

**E was renamed, not repurposed.** `Action Taken?` → `Forwarded to Yobani?` names the
question it always answered: did Helen hand this lead over. Same `Yes`/`No`, same meaning,
and F still keys off `E="No"`. The rename matters because **O** is now a second "is it
done?" column asking a different question — E is Helen's action, O is Yobani's.

**M–S track the handover and the chase; T–W track the two stages of a lead's journey.**

- **M (Helen Forward Date)** is the date Helen *actually* forwarded the lead to Yobani,
  verified from the thread — not the date the handover was recommended. It is **this task's
  to write**, on the pass where STEP 2 confirms the forward — but that write is **not yet
  implemented** (see *Columns defined but not yet written* in STEP 6). Empty means the
  forward has not been confirmed yet, and the whole chase cadence below stays dormant.
- **O (Yobani 1st Response Done?)** is `Yes` once Yobani has **actually sent a reply to the
  prospect**, `No` until then. Those two values only — it does **not** take
  `Not Needed - Connected`. This task's to write, **not yet implemented**.
  **O is not a copy of E.** Helen can forward a lead (E = `Yes`) and Yobani not get to it
  for days (O = `No`); that gap is the whole reason the column exists. The values sitting in
  O today are a one-off backfill Sheila made on 2026-09-11, when Yobani reported he had
  cleared everything forwarded to him so far — which is why O matches E on all 31 existing
  rows. Do not read that as a rule, and never derive O from E.
- **P (`=M+3`) and R (`=M+5`)** are formulas giving the dates Yobani's 3-day and 5-day
  follow-ups come due. They read `3` and `5` while M is empty — arithmetic on a blank cell,
  not a literal to clean up. **Never write a literal date to P or R.**
- **Q and S** are the matching `done?` flags, also this task's to write and also **not yet
  implemented**. Allowed values, exactly: `Yes`, `No`, and `Not Needed - Connected` (the
  lead is already connected, so the touch is moot). No other text, no free-form notes.
- **N is the *first* of three touches.** There is no column for a 2nd or 3rd draft, and
  this task does not write one — O–S carry dates and status only.
- **T/U are the setter stage** — the short intro call that gets a lead onto the board,
  which is Yobani's job. **V/W are the closer stage** — the longer discovery/closing call
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
   checks, no draft, and **do not touch column G**. These leads were deliberately parked
   (they disqualified themselves, or their call was already verified in Close). They will
   read as perpetually due and that is fine — they are skipped every run at no cost.
2. **`Tier` (B) is `1` → run STEP 2** (the forward check).
3. **`Tier` (B) is `In Progress` → run STEP 3** (the Yobani check).
4. Any other tier value is historical. Leave it alone.

---

## STEP 2 — Tier 1: did Helen actually forward it?

For every due Tier 1 row, the question is whether Yobani has been looped in yet.

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

### Find Yobani's involvement in ONE query

Do **not** fetch each thread and scan its participants — that is one call per row for a
question a single search answers. Yobani is `yobani@smbdealhunter.xyz`. Run one
`GMAIL_FETCH_EMAILS` on `gmail_kath-tiou`:

```
query: {to:yobani@smbdealhunter.xyz cc:yobani@smbdealhunter.xyz bcc:yobani@smbdealhunter.xyz from:yobani@smbdealhunter.xyz} after:<YYYY/MM/DD>
max_results: 100
verbose: false
```

Braces are Gmail's OR syntax. Set `after:` a day before the oldest due row's Date so the
window covers every lead in play, and page through `nextPageToken` until it is absent or
empty-string.

That returns every message in Helen's mailbox that involves Yobani, each with its
`threadId`, `subject` and `preview.body`.

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
- **M** (`Helen Forward Date`) → the date of the forward you just confirmed. **Not yet
  implemented** — see *Columns defined but not yet written* below. Until that lands, M
  stays empty here and the O/Q cadence stays dormant.

Then **immediately run STEP 3 for this row in the same pass.** Column F is the formula
`=if(E="No","Helen",xlookup(C,...))`, so setting E to `Yes` flips the owner to Yobani the
moment it lands. The row is a Yobani row now and gets the Yobani check now — it does not
wait a week for the next cycle.

**Not forwarded** → nothing has happened. Write:

- **G** → today (the check ran, so the clock resets)
- B, E, M, N, T, U → unchanged

and flag it to Helen in Slack (STEP 5). This is the output that matters: a Tier 1 lead
still owned by Helen days after it arrived is a lead going cold because the handoff never
happened.

**One Price Wall row is expected to sit here for a while.** When a lead pushed back on the
call itself, `helen-email-digest` gives Helen a draft that asks whether they want someone
looped in rather than cc'ing Yobani, so the forward waits on their reply. Flag it the same
way — an unanswered lead is still worth surfacing — but say in Slack that the handoff is
waiting on the lead, not on Helen. Column N is unaffected: that row carries the ordinary
Price Wall draft and this step does not touch it.

---

## STEP 3 — Yobani rows: has the call been set up?

For every row now at `In Progress` / owner Yobani, ask Close whether a call exists.

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
   `activity_types: ["activity.meeting", "activity.call"]`. Batch the lead IDs into one
   call rather than one call per lead.
3. Read each result's `title`, `starts_at` / `activity_at`, and `note`.

### Sort each meeting into setter or closer

Close returns every meeting on the lead. Split them by **duration first, event name
second** — the two stages are different calls:

| | Setter call → T/U | Closer call → V/W |
|---|---|---|
| Duration | ~900s (15 min) | ~2700s (45 min) |
| Event name | `SMB Deal Hunter Intro with <name>`, `Intro Call With SMB Deal Hunter Pro` | `Discovery Call with SMB Deal Hunter Pro - S2C` |

**A setter call counts even if someone other than Yobani booked it.** The question is
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
Yobani's job is done and there is nothing further for him to draft. Resolving a row means
**writing no new draft** — it does not mean removing the one already there. That holds even
when the *closer* call then fell through: a cancelled discovery call needs re-booking by
whoever owns that stage, which is not a setter intro. Record it in V/W and mention it in
Slack.

---

## STEP 4 — Yobani's reply: keep or write

Only for a Yobani-owned row with **no call booked**. A row with a setter call on the board
skips this step entirely; whatever is already in N stays put.

**Check what is already in N before writing anything.** Since `helen-email-digest` began
writing the Yobani draft at log time, most rows reaching this step already have one:

| N as read in STEP 1 | Do |
|---|---|
| Holds a draft matching the row's category, in one of the current templates below, with every `[If they …]` branch already resolved | **Keep it, unchanged.** Write nothing to N. It is already in the Slack thread from the digest run and may already be pasted |
| Holds a draft on the **superseded** templates — the tell is `[time slot]`, `Are you free`, or `Can I give you a call at` | **Replace it** with the current template for that category, and say in Slack that you did. Every row logged before the day-1 rules landed is in this state |
| Empty — a row logged before this change, or a digest run that skipped it | **Write the draft**, exactly as below |
| Holds something that is not one of these templates, or the wrong category's template | **Replace it** with the right one, and say in Slack that you did and why |

Rewriting a draft that is already correct is not free: a lead in the Slack thread on Monday
and a different wording in the sheet on Friday reads as two different people replying, and
whoever pastes has to work out which is current. Byte-identical is the goal — if you would
produce the same text that is already there, leave it.

The draft is **a reply on the existing thread, keeping Helen on it** so the handoff stays
tracked. Not a fresh email. The lead has been talking to Helen, so the reply picks up from
her rather than introducing a stranger.

### What day 1 is

Every draft here is Yobani's **day-1 response** — the first contact he makes once Helen has
forwarded. It is an **email, and a phone call** if he has a number to call.

| Phone number in their initial email? | Day 1 |
|---|---|
| Yes | Email, then call them — today or tomorrow |
| No | Email only. Buy Box and Price Wall ask for the number; Ready Now sends the Calendly link instead |

**No texting on day 1.** If he has the number he calls; if he doesn't, there's nothing to
text. Either way the text is redundant.

"Number provided" means a number in the **initial email they sent** — a signature block
counts, a number dug out of the CRM or the web does not. Column K's summary usually will not
settle it, so read the lead's own first message in the thread before picking the branch. You
already have the thread ID from STEP 2.

### Reading the templates

The `[If they …]` blocks are instructions, not copy. Pick the branch that matches the row,
write out that sentence, and delete the marker and the brackets around it. The other branch
disappears. **A draft that still contains the words "If they" has not been finished** — and
that applies to a draft you are keeping, too: one carried over from the digest run with a
marker still in it is a draft to replace, not to keep.

`[today/tomorrow]` is pick-one, not literal text.

### The three templates

One per category, reproduced verbatim. Use the template for the row's category (column C).

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

### Filling them in

**`[Calendly Link]` and `[today/tomorrow]` stay as literal bracketed placeholders.** Yobani
fills them in himself. Do **not** substitute a real link or a real day:

- Sheila's Calendly token is role `user` and cannot read Yobani's event types or
  availability (`event_types-list_event_types` returns Permission Denied for another
  user), so any day you commit him to would be invented. A day he is not free on is worse
  than a blank he fills in five seconds.
- His scheduling page is `https://calendly.com/yobani-smbdealhunter` (from the Calendly
  API's `scheduling_url` on his org membership) if this is ever revisited — but leave the
  placeholder unless Sheila says otherwise.

**There is no `[time slot]` placeholder any more.** The templates commit to a call today or
tomorrow rather than proposing a window, so nothing needs slotting. A draft still carrying
`[time slot]` is an old one — replace it.

Say in the Slack thread that both brackets need filling before sending, so nobody pastes a
draft with a bracket still in it.

**First name.** The name the sender signs off with in the email body, else the first word
of their Gmail display name. If there is **no display name** — a bare address like
`ms.raquele@gmail.com` — open with `Hi there,` and drop the name. Getting a name wrong in
the first three words is worse than not using one.

**Pronouns.** The templates address the lead as "you" for this reason. Never infer a
lead's gender from their name; where a third-person reference is unavoidable, use
they/them unless the sender's own signature makes it explicit.

**`[buy box criteria]`** (Buy Box) — the concrete thing they asked for, in their own words,
phrased to follow "interested in": `hotels in California`, `deals in Central FL`,
`absentee businesses`. If the ask is too vague to name in a few words, write
`what we've got` rather than inflating it into a specific.

**`[their own words]`** (Ready Now) — a short quote or close paraphrase of their stated
readiness, from column K or the email: `buying a business`, `the Bethlehem PA deal`,
`the 50% seller financing terms`. Never invent a deal, a location or a number they did not
mention.

**Never invent commercial terms.** No draft here quotes a price, a fee, a range, a
guarantee or a timeline. Note that unlike Helen's Price Wall draft, **Yobani's Price Wall
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
- **🔴 Needs Helen** — Tier 1 rows never forwarded. Say how many days each has been
  waiting; that number is the point. Mention Helen as `<@U04ATRJKXPD>` once, in this
  section.
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
over unchanged from the digest run has already been posted in that run's thread; reposting
it on every pass turns the channel into an echo and makes it unclear which copy is live.
If the section would be empty because every due row's draft was already correct, say so in
one line in the parent message instead ("3 drafts already current, unchanged").

Format — one block per draft, each in a code block so it copies cleanly:

> ✍️ *Suggested replies for Yobani* — reply on the existing thread and keep Helen on it.
> **Fill in `[Calendly Link]` and `[today/tomorrow]` before sending** — and call them the
> same day if they gave a number.
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

- **F (Owner)** `=if(E<n>="No","Helen",xlookup(C<n>,Responsibility!$A$2:$A$9,Responsibility!$B$2:$B$9))`
- **H (Next Check-in Date)** `=G<n>+1`
- **P (Yobani 3-day follow-up date)** `=M<n>+3`
- **R (Yobani 5-day follow-up date)** `=M<n>+5`

They already hold these formulas on every existing row. Setting E and G is what moves F and
H — F recomputes the owner and H recomputes the due date on its own. P and R work the same
way off M: writing the forward date into M is what turns `3` and `5` into real dates.
Writing any of the four by hand converts a live formula to a dead literal and the row stops
tracking.

`Responsibility!A2:B9` holds the category → owner lookup. Its unused rows (Sellside → Bill,
Investor and Operators → Kyle, Pitches and Engaged Reader → Helen) **must stay** — the
`xlookup` range is absolute and trimming it breaks column F on every row.

### What to write per row

| Column | Value |
|---|---|
| **B** Tier | `In Progress` — only on a row whose forward you just confirmed |
| **E** Forwarded to Yobani? | `Yes` — same rows only. Match the existing casing exactly |
| **G** Last Check-in Date | today, on **every** row you checked (including not-forwarded rows) |
| **N** Suggested Yobani 1st Response | per STEP 4: **omit the cell from the write** when the existing draft stands; the new draft (plain text with real line breaks, not a formula, not quote-wrapped) when you wrote or replaced one. **Never an empty string** — drafts are not deleted, including on a resolved row. On a failed Close lookup, omit it: leave what is there |
| **T** Setter Call Date | the intro call's date. Empty when there is none |
| **U** Setter Progress | short factual context: who with, event name, any note the lead left |
| **V** Closer Call Date | the discovery/closing call's date. Empty when there is none |
| **W** Closer Progress | short factual context, including a cancellation and who it was with |

Do not touch A, C, D, I, J, K or L. **Do not touch P or R** — they are formulas. Do not
touch a row whose D is `Ignore`.

**Columns defined but not yet written.** M, O, Q and S are this task's by ownership, but
the steps above do not populate them yet — the routine change comes separately. Until it
lands:

| Column | Owner | Written today? | Allowed values |
|---|---|---|---|
| **M** Helen Forward Date | this task | **no** — STEP 2 confirms the forward but does not record its date | a real date, only once the forward is verified in the thread |
| **O** Yobani 1st Response Done? | this task | **no** | `Yes`, `No` — **two values only**, no `Not Needed - Connected` |
| **Q** Yobani 3-day follow-up done? | this task | **no** | `Yes`, `No`, `Not Needed - Connected` — nothing else |
| **S** Yobani 5-day follow-up done? | this task | **no** | same three values |

Leave all four exactly as found. Do not improvise a value into them, and do not treat a
blank as a bug. In particular **never copy E into O** — they answer different questions
(Helen forwarded vs. Yobani replied), and the fact that they happen to match on every
existing row is a one-off backfill, not a rule.

### How to write

Use `GOOGLESHEETS_VALUES_UPDATE` with `value_input_option: "USER_ENTERED"` so dates coerce
to real dates. Because the due rows are usually contiguous but the columns are not, write
in per-column blocks — `Tracker!B<a>:B<b>`, `Tracker!E<a>:E<b>`, `Tracker!G<a>:G<b>`,
`Tracker!N<a>:N<b>`, `Tracker!T<a>:W<b>` — which keeps F, H, P and R untouched by
construction.

**The old `M:Q` block is now wrong and destructive.** That rectangle covers Helen Forward
Date, the draft, the 1st-response flag and both follow-up formulas; writing it would blank M
and O and overwrite P and R with literals. The draft moved to N and the setter/closer pair
to T–W, and the two are no longer adjacent, so they take **two separate blocks** with M and
O–S left out entirely.

**The N block overwrites every cell in its range, including N on rows whose draft you
decided to keep.** A block write has no "leave this one alone". So for each row in the
block, put in the N slot the value that should end up there: the **exact string you read in
STEP 1** for a kept draft, or your new text for one you wrote or replaced. Round-tripping
the value you read is what "keep unchanged" means mechanically. **No row ever gets `""`** —
a resolved row keeps its draft like any other. If echoing a long draft back is awkward,
write the rewritten rows individually instead — but never send a block that blanks N on a
row you meant to leave alone. For scattered rows use
`GOOGLESHEETS_UPDATE_VALUES_BATCH` (note: it takes `valueInputOption` in camelCase, unlike
the singular tool's `value_input_option`) and check every entry in `data.responses[*]`.

Google Sheets rate-limits at 60 writes/minute. Batch; do not write cell by cell.

### Verify, and report honestly

Re-read `Tracker!A1:W<n>` with `valueRenderOption: "FORMULA"` and confirm:

- every G you wrote is today's serial, and H is still the formula `=G<n>+1`
- every F is still the `if(...xlookup(...))` formula, and none of them spilled `#N/A`
- **P and R are still the formulas `=M<n>+3` and `=M<n>+5`** — a literal date in either
  means a block write ran over them
- **M, O, Q and S are untouched** on every row
- B and E changed on exactly the rows you meant, and nowhere else
- N/T/U landed on the right rows
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
Yobani that Step 2 is checking for. If Helen has not forwarded a lead, this task says so;
it does not do it for her. Do not create, update or delete anything in Close.

## Failure reporting

If any step fails, post what actually happened to `C0BTCGZSF9R` — the failing step, the
tool that errored, and the error text. Never assert a cause you have not verified, and
never report a partial pass as a success.
