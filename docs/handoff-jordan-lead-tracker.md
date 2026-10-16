# Handoff — Jordan's Lead Tracker (live page)

| | |
|---|---|
| **Status** | Published 2026-10-13. Script syntax-checked; **not yet seen running with live data** (a page can only call connectors when it is open in Claude, so the first real load is Sheila's). Verify it on first open (§7). |
| **Page** | https://claude.ai/artifact/DMNUCPnJu5TJNCpimDB4ez ("Jordan's Lead Tracker"), private to Sheila. |
| **Source** | [`jordan-lead-tracker/jordan-lead-tracker.html`](../jordan-lead-tracker/jordan-lead-tracker.html): the whole page, logic included. No build step and no Routine. |
| **Asked for by** | Sheila, 2026-10-13: a dynamic summary tracker of every lead forwarded to Jordan, with the lead name linked to Close, a dated summary of what happened, the suggested next step, color groups by stage, and leads Jordan sent a breakup to moved to the bottom in grey. |
| **Related** | Same leads as the `Tracker (JordanK)` tab ([tracker follow-up handoff](handoff-tracker-followup.md)), the Close tasks made by the [lead intake Routine](routine-jordan-lead-intake.md), and the [daily scorecard](../jordan-scorecard/README.md). The page reads them and writes to none of them. |

---

## 1. What it is

One page that lists every lead Helen forwarded to Jordan Kempster and sorts them by stage. Each
row has three columns:

- **Lead**: the Close lead name, linked to `https://app.close.com/lead/<lead_id>/`, plus the
  tracker name when it differs, the Close status, phone and email.
- **What happened**: a dated list. Helen forwarded, Jordan responded (and how many days
  later), each follow-up day with its channels, the lead's first and latest reply, every
  setter and closer meeting (booked, held or cancelled), "Did not ascend to a closer", and the
  breakup. Late or bad events are shown in red.
- **Next step**: one action with a due tag (overdue, today, or the day).

It is **dynamic**: nothing is stored server-side. Every open (and the Refresh button) re-reads
the tracker and Close. Viewers without Close see the last saved snapshot (§1a).

**It is read-only.** It never writes to Close, the tracker, Gmail or Slack. Keep it that way:
the manifest declares only read tools.

## 1a. Saved version for viewers without Close (added 2026-10-13)

Jordan opens the page without a Close connector (he has no Claude account in Sheila's team
space), so he cannot load live data. The page therefore also carries a **saved snapshot**:

- Viewers with the Close connector (Sheila) see the saved version at once, and the page loads
  live data on its own when the saved one is over 10 minutes old (or on "Refresh from
  Close"). A **"Save for Jordan"** button then appears.
- "Save for Jordan" republishes the page with the new results built in (capability
  `artifact`; the page keeps its own source in `SELF`, `STYLE` and `SHELL` and writes the
  results into the `<script id="snap">` JSON). Every open view reloads to it.
- Everyone else, Jordan included, sees the last saved version and its time ("Saved · Oct 13,
  4:12 PM MDT"), with no buttons. If nothing was ever saved, the page says so.
- **The saved version only moves when someone with Close opens the page and clicks Save.**
  Make it part of the daily routine: open, wait for the live load, click "Save for Jordan".
- When republishing from Claude, pass the full capability set: `mcp` (the tools in §2) **and**
  `artifact: {}`. Leaving `artifact` out removes the Save button. A publish from Claude
  replaces the saved snapshot with an empty one until the next Save.

## 2. Where the data comes from

Runtime capability: `mcp`, with exactly these tools (the page's manifest):

| Connector | Tools | Used for |
|---|---|---|
| **Composio** | `COMPOSIO_MULTI_EXECUTE_TOOL` → `GOOGLESHEETS_BATCH_GET`, account `googlesheets_gyte-urlar`, spreadsheet `1auWB8iQAwTYQrKhgHhb-paUuCH35j35RDiQdSC5uhBQ` | The roster: `'Tracker (JordanK)'` columns D–F, I, M, W |
| **Close** | `fetch_lead`, `fetch_contact`, `activity_search`, `find_tasks`, `search`, `paginate_search` | Everything else |

**Roster rule** (same as the follow-up pass): a tracker row counts when E (`Forwarded to
Setter?`) is `Yes` and either F (Owner) is `Jordan` or D names `jkempster@`. Name = I,
forward date = M, Jordan's notes = W. Ranges are requested narrow on purpose: the full A–W read
is ~24k tokens, which Composio moves to its workbench instead of returning inline, and the page
cannot read the workbench.

**Fallback roster.** If the tracker read fails (the Composio connection is Sheila's private
one, so any other viewer fails here), the page uses `ROSTER`, the 54 rows embedded on
2026-10-13, and says so in the yellow notice. New forwards are then missed until the
tracker is readable again.

**Matching tracker names to Close.** `LEAD_IDS` in the page maps each lower-cased tracker name
to its Close lead id, resolved by hand on 2026-10-13 (mostly by email address, per the
name-matching trap in the follow-up handoff). A tracker name that is not in the map is matched
against the Close search "leads where custom field Setter is Jordan Kempster" (the intake
Routine sets that field) by exact name. No unique match → the row goes to **No Close record**.
Two names have `null` on purpose because no Close lead was found for them: `the beeee`
(hpohock@gmail.com) and `intuit111`. `Scott` (scottstuart1212@gmail.com) is in `DEPRIORITIZED`:
Sheila set him aside on 10/13 (not really interested per his latest email; no Close profile
needed). Add a lower-cased tracker name and a reason to `DEPRIORITIZED` to park any other lead
in the grey Deprioritized group at the bottom. Searching Close by
email misses a lead whose contact has no email on file, and searching by name misses a lead
whose lead name is blank: Dirk Welsh (`lead_QWat4nZQ…`) has both problems, and was wrongly
listed as no record until Sheila pointed it out. Before declaring "no record", also search the
phone number and the contact name. `Scott` is **not** Scott Boyette (`lead_FjbOspaw…`,
boyettecs@gmail.com), who is on the never-track list.

Non-obvious mappings: `butch gentry` → Walter Gentry, `B E` → Brent, `Amir B` → Amir
Behdani, `John Dusek` → John Dusek III, `Christopher Terry` → Dpcbuilds, `Kumar D` → Kumar
Dronamraju, `Md.Nasir Uddin` → Nasir Uddin, `Nick` → Nick Saucier, `Ben R` → Ben Rear,
`Mark Chappell` → the "Call in Progress" one of three Mark Chappells
(`lead_NekzBGAKe…`, the one with the Jose Rodriguez meeting).

**Per lead** (six leads at a time): `fetch_lead`, `activity_search` (lead id; calls, emails,
meetings, SMS, completed tasks; since 2026-09-01; up to 8 pages of 20), `find_tasks` (open
only), then `fetch_contact` on the primary contact for the phone and email. Calls are cached
for 2 minutes.

## 3. How Close is read (traps found while building it)

- **Activity details are in `preview`, a JSON string.** Parse it. `activity_search` results
  have no direction field.
- **Direction = `date_sent`.** An outbound email or SMS has `date_sent`; an inbound one does
  not. Calls carry neither, so every call by Jordan is treated as an outbound touch (inbound
  calls are not counted as replies).
- **Emails appear once per synced mailbox** (Helen's, Jay's, Jordan's). Dedupe on
  type + second + subject/text, and count an email as Jordan's only when `user_id` is Jordan's.
- **Forward time** = the lead's `Creation Date` custom field
  (`cf_RdUwNTlCpEBzzWDbmzUcPUwPMmQPmO6EZJLsH6olFhM`, Helen's reply time, set by the intake
  Routine). If empty, the tracker's M date from 00:00 Mountain; failing that, the lead's
  `created_at`. Anything before it is ignored, and an email within 60 s of it is Helen's
  forward itself.
- **Meetings before the forward are ignored** (Kumar Dronamraju has a 7/31 discovery call with
  Chris Cha that predates this handoff).
- **Setter vs closer**: the host is the name after the last ` and ` in the title. A host in
  Jordan Kempster, Jose Rodriguez, David Martin, Quinn Donelan or Yobani Mendoza, or a ≤15 min
  meeting that is not a discovery call, is the setter call. Anyone else is the closer call
  (Nick Saucier's 30-min call with Omar counts as a closer call). A title starting `Canceled:`
  or a `declined`/`canceled` status is cancelled; it never counts as held.
- **Held** = not cancelled and the start has passed. Close's preview has no no-show outcome, so
  a no-show that is still marked completed reads as held (Mick Petrucci's 9/28 call is
  the known case; see §7).
- **Jordan ticks off Day 1/2/5 tasks in bulk once a lead books.** Abdi Russi's "Day 5 breakup"
  task was completed on 10/2, the morning of his setter call. So a completed breakup task is
  **not** proof of a breakup by itself (§4).
- **Lead summaries carry email bodies.** `fetch_lead` returns `summaries`, which include the
  text of recent email threads. That is the only place the page can see what Jordan wrote in
  an email.

## 4. Stages, in page order

Colors are tokens `--s-*` at the top of the page, with light and dark values.

| Stage | Rule (first match wins) | Next step the page writes |
|---|---|---|
| Closer call booked | an upcoming closer meeting | Text the lead the day before to confirm (or a reminder that morning if it is today) |
| Setter call booked | an upcoming setter meeting | Confirm by text the day before; book the closer call live on the call |
| **Breakup sent** (grey, always last) | a breakup (below), not revived | Low priority; only re-engage if they reply (plus any open task's date) |
| Met with a closer | a held closer meeting | Closer stage: check the outcome with the closer |
| Closer call cancelled | a cancelled closer meeting | Rebook: call today, don't just email |
| Setter call held, not set | a held setter meeting and no live closer meeting | The date of Jordan's open follow-up task in Close, or "decide today and add a dated task"; Jordan's tracker note (W) underneath |
| Setter call cancelled | only cancelled setter meetings | Rebook: call today and resend the calendar link |
| Replied, no call booked | an inbound email or text after the forward | Call (or ask for a number) today if the lead wrote last, else next business day, and book the intro live |
| Chasing, no reply | Jordan has touched, no reply | Under 2 touch-days: Day 2 follow-up (forward + 1 business day). 2 or more: breakup email on forward + 5 days, then low priority. "Was due" shown when late |
| Not contacted yet | no touch from Jordan | First touch overdue: reply on Helen's thread and call today |
| No Close record | tracker row with no Close lead | Create the lead in Close |
| Could not load | a Close call failed for that lead | The error and its fix |

**Breakup** = Jordan's outbound text, or an email from him in the lead summary, matching
`stop following up | should I stop | close the loop / close out your file | last note/email/message from me`,
**or** his `Day 5 breakup` task completed while the lead had never replied and had no
non-cancelled meeting. **Revived** = an inbound reply or a non-cancelled meeting after the
breakup; the lead then drops back into its normal stage and the timeline says it came back.

Day 2 / Day 5 follow the intake Routine's cadence (Task 2 due D0+1, Task 3 due D0+5), in
America/Denver. Within a group, rows sort by due date, then name.

### Action required panel (added 2026-10-16)

Above the stage chips, "Action required for Jordan" lists every lead whose next step is due
today or earlier, oldest first, with the Close link, the due tag and the action. "Today" is
worked out when the page is opened (Mountain time), so Jordan's saved copy stays right from day
to day without a new save. Breakups, deprioritized leads and leads already with a closer are left
out. Overdue steps keep their real due date (Day 2 = forward + 1 business day, breakup = forward
+ 5 days, first touch = the forward date, a rebook = the cancelled call's date, a held call with
no follow-up task = the next business day after it), so they read as "overdue 10/3" rather than
"today". When nothing is due, the panel says so and names the next lead coming up.

## 5. Changing it

- **Edit** `jordan-lead-tracker/jordan-lead-tracker.html`, then publish the same file to the
  same URL: Artifact publish with `url: https://claude.ai/artifact/DMNUCPnJu5TJNCpimDB4ez`
  (read it first if this is a new conversation). Omit `icon` and omit `capabilities` unless
  the tool list changes. If it does, pass the **full** `mcp` manifest again: a non-empty
  capabilities object replaces the stored one.
- **Adding a lead id by hand**: add `"<tracker name, lower-case>": "<lead_id>"` to `LEAD_IDS`.
  Do this when a new tracker row lands in No Close record but the lead does exist in Close
  (the Setter field was not set, or the names differ).
- **Refreshing the fallback**: regenerate `ROSTER` from the tracker with the roster rule in §2.
- Check the script parses before publishing (extract the `<script>` body and `node --check`
  it). The stage and next-step logic is all in `analyse()`.
- No em dashes in anything the page writes (house rule for this repo).

## 6. Who can use it

Private to Sheila. Sharing works only if the viewer has the **Close** connector in claude.ai;
they are asked to allow it for the page on first load. **Composio** is Sheila's private
connection, so anyone else gets the fallback roster and the yellow notice. Error codes are
handled per connector (add / reconnect / allow for this page) rather than one generic banner.

## 7. Open items

1. **First live load not yet checked.** On Sheila's first open, compare a few rows against
   the tracker and Close: Graham Shaw (held, not set), Nick Saucier (closer call with Omar
   cancelled 10/9), Amit Jain (setter booked 10/14), James Wood (Day 5 task done 10/12, no
   reply: should be grey), Brent / `B E` (replied by text, no call), Abdi Russi (held 10/2,
   follow-up task 10/19; must **not** be grey).
2. **No-shows read as held.** Close's meeting outcome is not in the `activity_search`
   preview. If this matters, pull the outcome per meeting (or read the tracker's U column) and
   send no-shows to "Setter call cancelled".
3. **"Could have set" is not judged.** Sheila's example next step ("could have set but not
   set, follow up on x date") needs the call transcript. The page shows Jordan's own tracker
   note and his Close task date instead. The daily Slack coaching notes (tracker follow-up
   STEP 5) carry the verdicts; bringing them in would mean the follow-up pass writing them to
   a tracker column the page can read.
4. **Breakup emails are seen only through lead summaries**, which may not hold every old
   thread. A completed Day 5 task on a cold lead is the backstop.
5. **Inbound calls are not counted as replies** (calls have no direction in the preview).
6. **Load time** is about 250 Close calls for 54 leads (roughly a minute). If the list grows
   a lot, narrow `activity_at` to the forward date or skip leads in the grey group.
