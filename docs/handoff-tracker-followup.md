# Handoff — Tracker follow-up pass

| | |
|---|---|
| **Status** | Live. Built, run end-to-end, and wired into the cloud Routine on 2026-09-10 — but pinned to an unmerged branch, see open item 1. |
| **Task definition** | [`skills/tracker-followup/SKILL.md`](../skills/tracker-followup/SKILL.md) — the single source of truth. |
| **Companion** | [`handoff-helen-email-digest.md`](handoff-helen-email-digest.md) — the forward-looking half of the routine. |
| **Last updated** | 2026-09-11 — column M is now pre-written by the digest; this task keeps it current (§3). |

---

## 1. What this is and why it exists

`helen-email-digest` finds *new* buyer leads and logs them. Nothing looked at the leads
already in the tracker. Open item 4 of the digest handoff recorded the consequence
bluntly: *"Every logged lead is overdue. All 26 existing rows carry Next Check-in Date =
9/3/2026 — now a week past. Tier 1 buyer leads going cold."*

This task closes that gap. It walks rows that have come due and asks whether each one
actually moved:

- **Tier 1 / owner Helen** — has she forwarded it to Yobani yet? If yes, promote the row
  (`Tier` → `In Progress`, `Action Taken?` → `Yes`) and continue to the Yobani check in the
  same pass. If no, flag it to Helen in Slack.
- **In Progress / owner Yobani** — does Close show a setter call? If yes, the row is
  resolved and column M is **cleared**. If no, the draft already in M stands, and one is
  written if it is missing.

Every row that gets checked has `Last Check-in Date` (G) set to today, which rolls
`Next Check-in Date` (H) forward by formula.

---

## 2. Column F is a formula, not a field

This is the single most important thing to understand before editing this task.

```
F = if(E="No","Helen",xlookup(C,Responsibility!$A$2:$A$9,Responsibility!$B$2:$B$9))
H = G+5
```

**"Check column F to see who owns this" is the same test as reading column E.** F is
derived. Two consequences:

1. Setting `E` to `Yes` flips the owner to Yobani *immediately*. So confirming a forward
   and drafting Yobani's reply happen in one pass — the row does not wait a cycle.
2. Never write a literal to F or H. Writing either converts a live formula to a dead value
   and the row silently stops tracking. Set E and G; let F and H recompute.

The unused `Responsibility` rows (Sellside → Bill, Investor/Operators → Kyle,
Pitches/Engaged Reader → Helen) must stay — the `xlookup` range is absolute.

---

## 3. The tracker grew to A–Q

Columns M–Q were added across 2026-09-10 as the task was specified:

| Col | Header | Written by |
|---|---|---|
| M | Suggested Yobani Response | **`helen-email-digest` writes it first** (2026-09-11); this task keeps it current |
| N | Setter Call Date | this task |
| O | Setter Progress | this task |
| P | Closer Call Date | this task |
| Q | Closer Progress | this task |

### Column M changed hands on 2026-09-11

Sheila asked for Yobani's draft to be generated in the **first** digest run, next to Helen's,
instead of waiting for this pass. So the digest now writes M at log time, and what is left
here is the part only a later check can know — whether the call actually got booked.

This task's relationship to M is therefore mostly **subtractive** now:

| Close says | M |
|---|---|
| Setter call on the board | **clear it** — write `""` |
| No setter call, draft already present and correct | keep, byte for byte; write nothing |
| No setter call, M empty (pre-2026-09-11 row, or a gap) | write the draft, as before |
| Lookup failed | leave exactly as found — neither clear nor rewrite |

Two consequences worth carrying forward:

1. **"Resolved" now means deleting something.** The old rule was "a setter call on the board
   → write no draft", which was satisfied by doing nothing. Against a row that arrives with a
   draft already in it, doing nothing leaves a "let's grab 15 minutes" pointed at someone who
   has already had their call. Clearing M is now an action this task must actually take.
2. **The M–Q block write has no "skip this cell".** It overwrites its whole rectangle, so a
   row whose draft is being kept must have that exact string echoed back into the block —
   otherwise the keep silently blanks it. The task file spells this out; it is the most
   likely way to lose a draft here.

**N/O vs P/Q is a real distinction, not a rename.** N/O are the **setter** stage — the
~15-minute intro call that gets a lead onto the board, which is Yobani's job. P/Q are the
**closer** stage — the ~45-minute discovery/closing call that follows. Duration is the
reliable discriminator in Close; the event name confirms it.

A lead can have a completed setter call and a cancelled closer call. Collapsing those into
one column loses the only actionable fact on the row.

---

## 4. Traps found while building this

Each of these cost time on 2026-09-10 and will cost it again if forgotten.

**Read the sheet with `valueRenderOption: "FORMULA"`.** Column J holds
`=HYPERLINK(url, subject)`. A formatted read returns only the visible subject text and
throws away the thread ID the Gmail lookups need. The Google Drive connector's
`read_file_content` flattens formulas the same way — useful for a quick look at the data,
useless for getting thread IDs out.

**Three thread-link formats exist in column J, and one needs converting.** Rows logged on
8/29 by the very first run use `#inbox/%23thread-f%3A1874806018152371407` — a percent-encoded
`#thread-f:<decimal>` legacy ID. The Gmail API wants hex: `format(int(decimal),'x')` →
`1a04a623eebc94cf`. Pass the decimal and the fetch 404s. The other two formats
(delegation-token and current `authuser=`) already carry hex IDs. The delegation URLs no
longer open in a browser, but the ID inside them is still good.

**One Gmail query answers the forward question for every row.** Searching
`{to:yobani@… cc:yobani@… bcc:yobani@… from:yobani@…} after:<date>` in Helen's mailbox
returns every thread he has ever touched, with `threadId`, `subject` and a body preview
carrying the original sender's address. That is one call, not one per row. Match rows on
thread ID **and** on `Fwd: <subject>` — a forward usually stays in the original thread
(both real cases did) but Gmail sometimes threads it separately.

**Match Close leads by email address, never display name.** Carried over from the digest
task and still live: `christopher green <cjgreen7904@yahoo.com>` is the Close lead
*"CJ Green"*, while a name search for "christopher green" also returns *"Chris Green"* and
*"Chris Greene"* — different people. The tracker only stores a display name, so the address
has to come from Gmail.

**A Close outage must not produce drafts — and must not delete them either.** An unconfirmed
check is not evidence in either direction. Treating it as "no call booked" would send "let's
grab 15 minutes" to leads who have already had their call; treating it as "call booked" would
now quietly clear a draft the digest wrote and nobody has used yet. Leave M as found.

**Slack appends "Sent using Claude" itself.** Adding the footer by hand renders it twice —
visible in the channel on both 9/10 digests.

---

## 5. Sheila's rules, as given

Recorded verbatim in effect so they are not re-litigated:

- `Recommended Action = Ignore` → **out of scope**. Skipped entirely, and column G is *not*
  touched. These rows read as perpetually due; that is intended and costs nothing.
- Only `Tier` values `1` and `In Progress` exist now. The 8/29 batch's Tier 2/3 and
  Uncategorized rows were deleted from the sheet on 9/10.
- Every row whose E/F was checked gets **G = today**, whether or not anything changed.
- `[time slot]` and `[Calendly Link]` stay as **literal placeholders** for Yobani to fill
  in. Do not substitute a real time or link.
- Yobani replies **on the existing thread with Helen kept on it**, so the handoff stays
  tracked.
- A setter call already on the board **resolves** the row — no draft, even if the closer
  call then fell through.

### Why the Calendly placeholders are the right call, not just the instructed one

Sheila's Calendly token is role `user`. `event_types-list_event_types` returns
`Permission Denied` for any other member, so Yobani's event types and availability are
unreadable from this session — any proposed slot would be invented. His scheduling page is
`https://calendly.com/yobani-smbdealhunter` (from the Calendly API's `scheduling_url` on
his org membership) if this is ever revisited. Note `calendly.com` is blocked by the
session egress proxy, so it cannot be verified by fetching — the API record is the
authority.

---

## 6. The 2026-09-10 verification run

10 rows were due (`H = 9/3`, all from the 8/29 batch). Rows 12–20 sat at 9/15 and were
correctly untouched.

| Outcome | Rows | Detail |
|---|---|---|
| Skipped, `Ignore` | 1 | Mark Bunting — G deliberately left at 8/29 |
| **Never forwarded** | **5** | Zing Beam LLC, Christopher Terry, Daniel Spencer, Jeffrey Naegle, narinder Singh |
| Reclassified to `Ignore` | 2 | Jerome M Limage, J LaMacchia — see below |
| Setter call on the board | 2 | Michael j Wilson, Eric Rubinstein |

**The headline finding is the five.** Only three threads in Helen's entire mailbox have
ever involved Yobani, and two of them were already marked In Progress. So five Tier 1
buyer leads sat for **12 days** with no handoff at all — they were logged, and then nothing
happened. That is a process problem the tracker was not surfacing, and it is now the
digest's loudest section.

### Two of the original seven were not buyers at all

Sheila caught both, and the reason they were missed is worth more than the corrections.

- **Jerome M Limage** wanted seller financing on *"an investment property that I tend to
  hold"* — his own real estate, which he intends to keep.
- **J LaMacchia** appeared to make a live offer (*"50% down payment ($1,250,000)…"*) but his
  email ends *"…and I will remove from the market"* — he is reasoning from the **seller's**
  side about how offers should be handled, and never asks to speak to anyone.

Both replied to the same newsletter on the same day, and both were logged Tier 1 "Send to
Yobani" by the digest task. **Deal vocabulary is not buyer intent.** Replies to a
*"50% seller financed"* headline come back fluent in down payments, contingencies and terms
from readers who are commenting on the deal, discussing their own assets, or thinking from
the seller's side.

**The mechanical cause is worth fixing, not just the classification.** `verbose: false`
truncates `preview.body` at roughly 200 characters. J LaMacchia's snippet ended at *"Any
serious offer should be vi…"* — every word that revealed his position was past the cut, so
the snippet said the opposite of the email. The digest task now **requires hydrating any
reply containing deal terms** (dollar figures, down payments, financing structures,
contingencies, deadlines) before classifying it. Snippets remain fine for the short plain
asks that make up most real buyer mail; they are not safe for anyone doing arithmetic.

For contrast, the five genuine buyers all stated the ask in one line with no deal analysis:
*"I'm looking for local business in 94538 area code, ready to invest"*, *"Do you have a
company like this in Colorado"*, *"Helen I want to buy a business show me."* On this
newsletter, length and financial sophistication correlate **negatively** with buyer intent —
the real buyers ask for deals, the commentators explain deals.

After the second correction the **full text of every remaining un-forwarded lead was read**
rather than trusted from a snippet; all five are complete, unambiguous asks. Both reclassified
rows keep `Last Check-in Date` = 9/10 rather than reverting to 8/29: a check genuinely ran
that day, and `Ignore` rows are skipped on the column D test before H is consulted, so the
value has no behavioural effect.

The Slack digest had already gone out naming seven, so it was corrected twice in-thread with
a broadcast rather than left to mislead — forwarding non-buyers would have wasted the
setter's time and taught Yobani to distrust the digest.

The two that moved:

- **Michael j Wilson** (`michaeljwilson11@gmail.com`) — *"SMB Deal Hunter Intro with
  Yobani"*, 8/31 16:30 UTC, 15 min, held. Yobani did his job. → N/O.
- **Eric Rubinstein** (`ericrubinstein3@gmail.com`) — intro call 9/1 with **David Martin**
  (not Yobani, still counts), then a 9/8 discovery call with **Adam Larkins** that was
  **cancelled**. → N/O for the setter call, P/Q for the cancelled closer call.

**No drafts were produced.** Every Yobani-owned row already had a setter call, and the
seven cold leads have not reached him. So the STEP 4 drafting path is specified and
reviewed but **not yet exercised against live data** — the first real test of the templates
will be the first run where a forwarded lead has no call booked.

Writes verified by re-reading with `FORMULA`: G = 46275 on all nine checked rows, H still
`=G+5`, every F still the `if(...xlookup(...))` formula, no `#N/A`, no rows added or
removed, row 10 untouched.

---

## 7. Open items

| # | Item | Owner |
|---|---|---|
| **1** | ⚠️ **The Routine reads from an unmerged branch.** `trig_012Ap72Z58NHa2m8ahWYUQmt` is pinned to `claude/sleepy-hamilton-bch8b6`, because `main` holds an **older** `helen-email-digest/SKILL.md` (no hydration rule) and no `tracker-followup/SKILL.md` at all. A fallback-on-absence would not have caught the stale digest spec — the file exists on `main`, it is just wrong. **Merge that branch, then change the Routine's "Which ref to read" section to `main`.** Until then the branch must not be deleted, and anyone editing a spec on `main` will be silently ignored. | Sheila / Zain |
| 2 | **Both tasks now run in one Routine**, digest first, then follow-up, daily 08:03 ET. They are independent: if one spec cannot be read, the other still runs. Renamed to *"Helen email digest + tracker follow-up (daily 08:03 ET)"*. Connectors (GitHub, Composio, Slack, Close) unchanged. | Done 2026-09-10 |
| 3 | **Drafting path untested on live data** (see §6). Still true of *this* task's write path, and now narrower: since 2026-09-11 the digest writes the draft first, so this task's common case is keep-or-clear. The first real exercise of the templates is now the digest's first run with a "Send to Yobani" lead. | Accepted |
| 3a | **The clear-on-resolve path is new and untested** (2026-09-11). No row has yet arrived at this task with a pre-written draft *and* a setter call, because the digest only began writing M on 2026-09-11. The first run where one does is worth watching: confirm M actually comes out, and that no kept draft on a neighbouring row was blanked by the block write. | Watch |
| 4 | **Flagged leads go quiet for 5 days.** Setting G = today on a *not-forwarded* row pushes H forward, so Helen is nagged once every 5 days rather than daily. Reviewed and accepted as-is on 2026-09-10. | Accepted |
| 5 | **`H = G+5` is 5 days, not a week.** Sheila's phrasing was "so the next check-in date becomes next week"; the formula is +5 calendar days, so from a Monday check-in it lands on a Saturday. Reviewed and accepted as-is on 2026-09-10. | Accepted |
| 6 | **Re-review of the deleted 8/29 rows: explicitly declined.** Two of the ten surviving rows were misclassified from truncated snippets, so the ~16 rows deleted on 9/10 could hold the opposite error — a real buyer dropped as Tier 3. Sheila's call on 2026-09-10 was that recovering them from version history is not worth it. Recorded so it is not mistaken for an oversight. The hydration rule prevents the same error going forward. | Closed |
| 7 | **Loop-in detection is email-only.** If Helen hands a lead to Yobani in Slack, in Close, or verbally, this task will report it as never forwarded. | Accepted |
| 8 | **Yobani's mailbox is not connected.** If he replies to a lead without Helen on the thread, that reply is invisible here and the row could be drafted for again. Keeping Helen on the thread (§5) is the mitigation. | Accepted |
| 9 | **DST rollover on 2026-11-01.** Cron `3 12 * * *` is UTC and does not observe daylight saving, so this fires at 07:03 ET after that date until the cron is changed to `3 13 * * *`. Inherited from the digest Routine; now affects both tasks. | Sheila |

---

*If this feels hard or confusing at all, please reach out to Zain. He promises he wants to
hear all about it, so he can make this feel like magic. Thank you for using it!*
