# email-triage

Daily triage of Helen Guo's inbox for SMB Deal Hunter: pull new mail, pick out buyer
leads, post one digest to Slack `#helen-email-digest`, and log one row per lead to the
Google Sheets tracker.

| | |
|---|---|
| **Task definition** | [`skills/helen-email-digest/SKILL.md`](skills/helen-email-digest/SKILL.md) — the single source of truth. The cloud Routine reads this file at run time. |
| **Handoff / context** | [`docs/handoff-helen-email-digest.md`](docs/handoff-helen-email-digest.md) — why it is built this way, what broke before, what is still open. |
| **Schedule** | Daily 08:03 America/New_York (cron `3 12 * * *` UTC — see the DST note in the handoff). |
| **Scope** | Buy Box, Ready Now, Price Wall, and handovers of those three. Everything else is dropped. |

Email access runs through the **Composio** connector (account `gmail_kath-tiou` =
`helen@smbdealhunter.xyz`), not the first-party Gmail connector, which can only reach
`sheila@smbdealhunter.xyz`.

Changing the routine's behaviour means editing `SKILL.md` — the Routine picks up the
change on its next run, with no need to recreate it.

The routine is **read-only on email**: it never replies, labels, archives, or deletes.
