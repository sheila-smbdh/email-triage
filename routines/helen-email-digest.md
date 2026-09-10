# Routine: Helen email digest

Paste this as the Routine's prompt. The critical line is the pinned Composio
account ID — without it the run fails (see `docs/troubleshooting.md`).

---

Produce a digest of new mail in Helen's inbox (helen@smbdealhunter.xyz).

**Mailbox access — follow exactly:**

- Use the **Composio** connector. Do NOT use the built-in Gmail connector: it is
  bound to sheila@smbdealhunter.xyz and will silently return the wrong mailbox.
- On every Gmail tool call, pass the account field pinned to Helen:
  `account: "gmail_kath-tiou"`
- Never rely on the default account. Two Gmail accounts are connected to
  Composio, so an unpinned call fails with
  "Multiple gmail accounts connected. Specify which to use via the 'account' field."

**Steps:**

1. Call `GMAIL_GET_PROFILE` with `account: "gmail_kath-tiou"` and confirm the
   returned `emailAddress` is exactly `helen@smbdealhunter.xyz`.
   If it is not, stop and report the mismatch instead of producing a digest.
2. Call `GMAIL_FETCH_EMAILS` with:
   - `account: "gmail_kath-tiou"`
   - `label_ids: ["INBOX"]`
   - `query: "newer_than:1d"`
   - `max_results: 100`
   - `verbose: false`, `include_payload: false`
3. If `nextPageToken` is a non-empty string, paginate with `page_token` until it
   is empty or stops advancing. Dedupe on `messageId`.
4. Sort by `messageTimestamp` descending — results are NOT returned in order.
5. For any message that needs full text, hydrate it with
   `GMAIL_FETCH_MESSAGE_BY_MESSAGE_ID` (same pinned account).

**Digest output:**

Group into: Needs reply · FYI · Newsletters/Promotions · Automated.
For each item give sender, subject, timestamp, and a one-line summary.
Put anything unread and addressed directly to Helen at the top.
If there are zero new messages, say so plainly — an empty result is a valid
outcome, not an error.
