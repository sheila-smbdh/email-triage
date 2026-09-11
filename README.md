# email-triage

Daily triage of Helen Guo's inbox for SMB Deal Hunter: pull new mail, pick out buyer
leads, write Helen's reply straight into her Gmail as a draft with the setter cc'd, post one
digest to Slack `#helen-email-digest`, and log one row per lead to the Google Sheets
tracker.

Two tasks make up the routine. The digest looks **forward** at new mail; the follow-up pass
looks **backward** at leads already logged.

| | |
|---|---|
| **Task definition** | [`skills/helen-email-digest/SKILL.md`](skills/helen-email-digest/SKILL.md) — the single source of truth. The cloud Routine reads this file at run time. |
| **Follow-up task** | [`skills/tracker-followup/SKILL.md`](skills/tracker-followup/SKILL.md) — walks due tracker rows: chases Helen's un-forwarded handoffs, checks Yobani's booking progress in Close, and keeps his draft in column N current (drafts are never cleared). Built and verified 2026-09-10, and running in the Routine alongside the digest. |
| **Handoff / context** | [`docs/handoff-helen-email-digest.md`](docs/handoff-helen-email-digest.md) and [`docs/handoff-tracker-followup.md`](docs/handoff-tracker-followup.md) — why it is built this way, what broke before, what is still open. |
| **Schedule** | Daily 08:03 America/New_York (cron `3 12 * * *` UTC — see the DST note in the handoff). |
| **Status** | ✅ Live — both tasks enabled and verified end-to-end on 2026-09-10. The Routine reads both specs from **`main`** (repointed 2026-09-10 once `claude/sleepy-hamilton-bch8b6` merged), so a spec change is live on the next run once it lands on `main`. |
| **Scope** | Buy Box, Ready Now, Price Wall, and handovers of those three. Everything else is dropped. |
| **Output** | A **Gmail draft on each lead's thread in Helen's mailbox, cc'ing Yobani** — she opens it, reviews, sends; one Slack message (Tier 1 + handovers, no draft thread); and one tracker row per lead carrying both drafts, Helen's and Yobani's, generated in the same first run (columns L and N). |

Email access runs through the **Composio** connector (account `gmail_kath-tiou` =
`helen@smbdealhunter.xyz`), not the first-party Gmail connector, which can only reach
`sheila@smbdealhunter.xyz`. **Close CRM** is read (never written) to confirm whether a
lead who says they booked a call actually did — if so the recommended action becomes
"Ignore" rather than sending them to the setter.

Changing the routine's behaviour means editing `SKILL.md` — the Routine picks up the
change on its next run, with no need to recreate it.

The routine **writes drafts and nothing else**. Since 2026-09-11 it creates Helen's reply as
a Gmail draft on the lead's own thread with Yobani cc'd, so she reviews and sends in place
instead of pasting out of Slack — and for that reason the Slack digest no longer carries a
thread of draft text. It never sends, replies, forwards, labels, archives, or deletes, and
never touches a draft it did not just create. Yobani's day-1 reply is **not** drafted in
Gmail; it stays in tracker column N, which is where he reads it.
