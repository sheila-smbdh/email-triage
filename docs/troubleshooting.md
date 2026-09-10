# Helen email digest — why it was failing

Verified live on 2026-09-10 against the connected accounts.

## Connected Gmail paths in this workspace

| Path | Mailbox | Notes |
|---|---|---|
| Composio account `gmail_kath-tiou` | helen@smbdealhunter.xyz | Connected 2026-09-09. Composio default. 157,010 msgs / ~201 in inbox. |
| Composio account `gmail_uncast-hoop` | sheila@smbdealhunter.xyz | Connected 2026-09-01. 209 msgs. |
| Built-in Gmail connector | sheila@smbdealhunter.xyz | Cannot reach Helen's mail at all. |

## Failure mode A — hard error (most likely cause)

A Gmail call through Composio with no `account` field returns:

```
Multiple gmail accounts connected. Specify which to use via the 'account' field:
- "gmail_kath-tiou"
- "gmail_uncast-hoop"
```

Reproduced directly. Note the timeline: until 2026-09-09 only Sheila's account
was connected to Composio, so unpinned calls resolved automatically. Adding
Helen's account on 2026-09-09 made every unpinned call ambiguous and started
failing the Routine.

Being Composio's *default* account does not help — selection is still required
whenever more than one account is connected.

**Fix:** pass `account: "gmail_kath-tiou"` on every Gmail call.

## Failure mode B — silent wrong mailbox

If the Routine uses the built-in Gmail connector instead of Composio, it does
not error. It returns Sheila's inbox (14 threads) rather than Helen's (~201).
The digest comes out looking sparse or irrelevant rather than broken.

**Fix:** route Helen's mail through Composio only.

## Failure mode C — connector not granted to the Routine

Routines that spawn a fresh session per firing carry their own connector grant.
If Composio is not in that grant, the fired session has no Gmail tools at all
and fails before any of the above applies.

**Fix:** confirm the Routine lists Composio (and Gmail, if used) among its
allowed connectors. This must be checked in the Routine's own settings.

## Verifying a fix

A run is healthy when step 1 of the prompt returns
`emailAddress: helen@smbdealhunter.xyz` and the inbox count is in the hundreds,
not the low tens.
