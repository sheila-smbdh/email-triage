# Jordan's setter scorecard (daily)

A one-card scorecard of Jordan Kempster's setter KPIs on Helen's email leads, sent to
Sheila as a PNG every weekday at about 8am ET by the Routine "Jordan daily scorecard".

| | |
|---|---|
| Artifact | https://claude.ai/artifact/PUAKxnBAqzo5xeBxtUm4oq ("Jordan's Setter Scorecard") |
| Build | `python3 build.py metrics.json OUT_DIR` writes `jordan-scorecard.html` and `jordan-scorecard-<date>.png` |
| Example input | `sample-metrics.json` (the Oct 7 numbers from the setter deep dive) |
| Layout and targets | `build.py` and `style.css`. A daily run never changes them. |

The scorecard is for Sheila only. Never message Jordan, never post to Slack, and never write
to Close, the tracker or anyone's mailbox.

## Daily run

0. **Start the screenshot tool first.** At the very start of the run, start
   `pip install -q playwright` in the background (it can take over 2 minutes). The browser is
   already at `/opt/pw-browsers/chromium`; never run `playwright install`. At build time, use
   whichever of `python3` or `/usr/bin/python3` can `import playwright`.
1. **Dates.** `today` = the run date in America/New_York. `D` = the previous weekday
   (Monday uses Friday). The window is leads whose Helen Forward Date is between `D - 13 days`
   and `D`, inclusive. `measured_on` = today, `window_start` / `window_end` = the window.
2. **Leads.** Read the `Tracker (JordanK)` tab with Composio `GOOGLESHEETS_BATCH_GET`
   (account `googlesheets_gyte-urlar`, spreadsheet `1auWB8iQAwTYQrKhgHhb-paUuCH35j35RDiQdSC5uhBQ`,
   range `'Tracker (JordanK)'!A1:Z300`, `dateTimeRenderOption: FORMATTED_STRING`).
   Keep rows where column F (Owner) contains "Jordan" and column M (Helen Forward Date) is in
   the window. One lead per person: dedupe on column I (Email Sender), keeping the earliest
   forward. Columns: I sender, J subject/link, K summary, M forward date, T setter call date,
   U setter progress, V closer call date, W closer progress.
3. **Close.** For each lead, find the Close lead (`lead_search` by name, then by email if the
   name is ambiguous) and pull its activity with `activity_search` (`lead_ids`, all types).
   Jordan's Close user id is `user_3IrYZLUcCBZrg2mb49wCybrxGBFTCxa5eqTHhE1ApuC`. Use
   `fetch_call` for call duration and direction. A lead with no Close record keeps its tracker
   data and counts as "no reply" and "no call" unless the tracker says otherwise.
4. **Count the KPIs** (definitions below) into the metrics JSON.
5. **Build.** `<python> build.py metrics.json out`, with the python from step 0.
6. **Publish.** Artifact `read` on the artifact URL above, then publish
   `out/jordan-scorecard.html` with `url` set to that link. Do not pass `icon`.
7. **Check and send.** Read the PNG once to check it rendered (6 tiles, wins and fixes filled).
   Send it with `SendUserFile` (status `proactive`, display `attach`) and the caption
   `Jordan scorecard for <today, e.g. Friday, Oct 9>: reply in 2h <X>%, same-day call <Y>%, held <Z>%, booked before hanging up <W>%. Fix: <top fix, short>.`

If a step fails, send Sheila one or two lines saying which step and what you saw. If Composio
returns an auth or "API key revoked" error, say the Composio connector needs reconnecting in
Claude's settings, and stop. No em dashes in anything you write.

## Metrics JSON

```json
{
  "measured_on": "YYYY-MM-DD", "window_start": "YYYY-MM-DD", "window_end": "YYYY-MM-DD",
  "kpis": {
    "reply2h":      {"num": 0, "den": 0, "median_hours": 0},
    "sameday_call": {"num": 0, "den": 0},
    "held":         {"num": 0, "den": 0},
    "booked_live":  {"num": 0, "den": 0, "excluded_not_fit": 0},
    "set_closer":   {"num": 0, "den": 0, "names": ["First names"]},
    "closer_show":  {"num": 0, "den": 0, "upcoming": "Name with Closer, Mon DD"}
  },
  "wins": ["2 or 3 short lines"],
  "fixes": ["2 or 3 short lines"],
  "notes": ["optional footnotes, e.g. a source that could not be read"]
}
```

## How each number is counted

Business hours are 9am to 5pm, Monday to Friday, America/Denver (Jordan's time).

- **Tracker dates.** The tracker's forward date (column M) is sometimes the lead's own email
  date, not Helen's forward. Always use the Close forward time below; the tracker only decides
  which leads are in the window.
- **Forward time.** The Close lead's `Creation Date` custom field
  (`cf_RdUwNTlCpEBzzWDbmzUcPUwPMmQPmO6EZJLsH6olFhM`, set by the lead intake Routine to Helen's
  reply time). If it is empty, use the earliest email on the lead from helen@smbdealhunter.xyz
  that includes jkempster@smbdealhunter.xyz; failing that, 9am MT on the tracker's forward date.
- **reply2h (target 80%).** Jordan's first outbound email, call or SMS on the lead after the
  forward time. Hit if it came within 2 business hours. A lead with no reply counts as a miss
  once 2 business hours have passed; leads still inside their first 2 business hours are left
  out. `median_hours` = median business hours to first touch over leads that got one, rounded
  to the nearest 0.5.
- **sameday_call (target 80%).** Leads that had a phone number by the end of the forward's
  business day: on the Close contact, in the lead's email or signature, or in the tracker
  summary. Hit if Jordan placed an outbound call (any outcome) the same business day. A forward
  after 5pm MT or on a weekend uses the next business day. Leave out leads whose day has not
  ended.
- **held (target 30%).** Leads with a held setter call: a Jordan meeting marked completed whose
  Close outcome is not No Show or Reschedule and that has some proof it happened (a connected
  Jordan call of 5+ minutes that day, a call note, or his info package email after), or a
  connected Jordan call of 5+ minutes. Denominator = all leads in the window.
- **booked_live (target 80%).** Of held setter calls, the share where a meeting on the lead
  (with a closer, or a callback with Jordan) was created in Close between the call's start and
  30 minutes after it ended. The Close connector does not show when a meeting was created, so
  use the time of the Calendly "New Event" notification email on the lead as the creation time. Leave out calls that ended in a clear "not a fit" (Close outcome
  Disqualified or Not a Fit, or Jordan's note says so) and report how many in
  `excluded_not_fit`.
- **set_closer (tracked, no target).** Held setter calls followed by a meeting with a closer
  (any user other than Jordan and the setters Jose Rodriguez, David Martin and Quinn Donelan),
  created after the setter call. `names` = the leads' first names. This is deliberately not a
  target, so setters are not pushed to set weak leads.
- **closer_show (tracked guardrail).** Of the closer meetings counted in set_closer whose start
  time has passed, the share that were held (status completed and not a no-show). `upcoming` =
  the next one not yet due.
- **Wins and fixes.** 2 or 3 short lines each, written to Jordan, naming leads by first name.
  Fixes go to the red tiles first, e.g. "Book the closer before hanging up. Call Rhett and PK
  to book theirs." Wins name a real set or a tile that hit its target.
