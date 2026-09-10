# email-triage

Daily triage of Helen Guo's inbox for SMB Deal Hunter: pull new mail, pick out buyer
leads, post one digest to Slack `#helen-email-digest`, and log one row per lead to the
Google Sheets tracker.

Two tasks make up the routine. The digest looks **forward** at new mail; the follow-up pass
looks **backward** at leads already logged.

| | |
|---|---|
| **Task definition** | [`skills/helen-email-digest/SKILL.md`](skills/helen-email-digest/SKILL.md) — the single source of truth. The cloud Routine reads this file at run time. |
| **Follow-up task** | [`skills/tracker-followup/SKILL.md`](skills/tracker-followup/SKILL.md) — walks due tracker rows: chases Helen's un-forwarded handoffs, checks Yobani's booking progress in Close, drafts his reply. Built and verified 2026-09-10, and running in the Routine alongside the digest. |
| **Handoff / context** | [`docs/handoff-helen-email-digest.md`](docs/handoff-helen-email-digest.md) and [`docs/handoff-tracker-followup.md`](docs/handoff-tracker-followup.md) — why it is built this way, what broke before, what is still open. |
| **Schedule** | Daily 08:03 America/New_York (cron `3 12 * * *` UTC — see the DST note in the handoff). |
| **Status** | ✅ Live — both tasks enabled and verified end-to-end on 2026-09-10. ⚠️ The Routine currently reads both specs from the branch `claude/sleepy-hamilton-bch8b6`, not `main`, because `main` holds a stale digest spec and no follow-up spec. Merge that branch, then repoint the Routine at `main`. |
| **Scope** | Buy Box, Ready Now, Price Wall, and handovers of those three. Everything else is dropped. |
| **Output** | One Slack message (Tier 1 + handovers), a threaded reply holding ready-to-send drafts for Helen, and one tracker row per lead. |

Email access runs through the **Composio** connector (account `gmail_kath-tiou` =
`helen@smbdealhunter.xyz`), not the first-party Gmail connector, which can only reach
`sheila@smbdealhunter.xyz`. **Close CRM** is read (never written) to confirm whether a
lead who says they booked a call actually did — if so the recommended action becomes
"Ignore" rather than sending them to the setter.

Changing the routine's behaviour means editing `SKILL.md` — the Routine picks up the
change on its next run, with no need to recreate it.

The routine is **read-only on email**: it never replies, labels, archives, or deletes.
