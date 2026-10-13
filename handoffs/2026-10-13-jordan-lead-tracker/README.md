# Handoff: Jordan's Lead Tracker

**From:** Sheila Xu's Claude Code session, 2026-10-13
**To:** a teammate's own Claude chat (claude.ai or Cowork), with the teammate in the chat
**Mission:** Get your own copy of Jordan's Lead Tracker running from your claude.ai account, and use it every weekday to see where each of Jordan's leads stands and what he should do next.

Read this whole file first. Everything you need is in this folder; nothing points to Sheila's GitHub.

---

## 1. What this is

Helen Guo forwards buyer leads from her inbox to Jordan Kempster, our setter. Jordan then has to
reply, follow up, book a 15-minute intro (setter) call, and set good leads up with a closer. This
tracker is one live web page (a claude.ai artifact) listing **every lead Helen forwarded to
Jordan**. Each row shows the lead's name linked to their Close profile, a dated timeline of what
happened (Helen forwarded, Jordan responded, Jordan followed up, lead replied, setter call booked
or held, closer call booked, held or cancelled, breakup sent), and one suggested next step with a
due date. Leads are grouped and colored by stage. Leads Jordan has sent a breakup to sit at the
bottom in grey.

The page is **dynamic**: it stores no data of its own. Every time it opens, or you press
"Refresh from Close", it reads Helen's tracker sheet and every lead's history in Close through
the viewer's claude.ai connectors, then rebuilds the list. Jordan has no Close connector, so he sees
the last **saved** version instead: whoever has Close opens the page, waits about a minute for
the live load, and clicks **"Save for Jordan"**. "Doing it daily" means exactly that, once each
morning; no copy-pasting, no rebuilding. It is **read-only**: it never writes to
Close, the sheet, Gmail or Slack.

Sheila built and published it on 2026-10-13 at a link only she can open
(https://claude.ai/artifact/DMNUCPnJu5TJNCpimDB4ez). It is moving to you so you can run it from
your own account without her repo. You will publish **your own copy** from the HTML file in this
folder, after one small edit for your Google Sheets connection (§5).

## 2. Where everything lives

| Resource | What it is | Read in full? |
|---|---|---|
| `README.md` (this file) | The brief | Yes |
| `jordan-lead-tracker.html` | The whole page: layout, the lead list, and all the logic. Publish this as the artifact | Skim; the settings are near the top of the `<script>` |
| `reference.md` | Technical reference: data sources, how Close is read, the stage rules, traps, open items | Yes, before changing any logic |
| Helen's tracker, tab `Tracker (JordanK)` | Google Sheet `1auWB8iQAwTYQrKhgHhb-paUuCH35j35RDiQdSC5uhBQ`. The page reads columns D–F, I, M and W | Not needed; the page reads it |
| Close CRM | Leads, emails, texts, calls, meetings, tasks. Read through the **Close** connector | Not needed |

## 3. Decisions locked (do not re-litigate)

- **Live page, not a sheet or a daily report.** Sheila asked for it to be dynamic. It recomputes on every open, so nobody maintains it by hand.
- **Read-only.** It only uses read tools. Never add a tool that writes.
- **Who counts as Jordan's lead:** a tracker row where "Forwarded to Setter?" (E) is `Yes` and Owner (F) is `Jordan`, or the action (D) names `jkempster@`.
- **Close is matched by lead id, never by name alone.** The ids for the 54 leads as of 10/13 are written into the page; name searches in Close return the wrong person.
- **Stage order:** closer call booked, setter call booked, met with a closer, closer call cancelled, setter call held but not set, setter call cancelled, replied with no call, chasing with no reply, not contacted, no Close record, could not load, and **breakup sent last, in grey**.
- **What counts as a breakup:** Jordan texted or emailed a stop-following-up message, or marked his Day 5 breakup task done while the lead had never replied or booked. Jordan often ticks all his tasks once a lead books, so a ticked task on a warm lead is not a breakup. A reply or booking afterwards moves the lead back up.
- **Follow-up cadence:** Day 2 follow-up = forward + 1 business day; breakup email = forward + 5 days, both in Jordan's time zone (Mountain). It matches the tasks the intake Routine already creates.
- **No em dashes** in anything the page writes.

## 4. Changed since this work paused

1. The page has been published but **has not yet been seen loading live data.** Your first open is the first real test (§6, move 5).
2. The page's Google Sheets setting points at **Sheila's** Composio connection (`googlesheets_gyte-urlar`). That id will not work for you; change it first (§5).

## 5. Blockers and unblock paths

- **You need the Close connector.** Owned by: you. Unblock: claude.ai Settings, Connectors, add Close and sign in with your Close login. Then the page can read leads.
- **You need Composio with a Google Sheets account that can open Helen's tracker.** Owned by: you, plus Sheila or Helen to share the sheet with your Google account (view access is enough). Unblock: add the Composio connector in claude.ai, connect Google Sheets inside Composio, then have your Claude find your Sheets account id and put it in the page (move 3). Without this the page still works from its saved list of 54 leads, but it won't see new forwards.
- **The original artifact is Sheila's.** Owned by: Sheila, only if she wants you editing her copy. Otherwise publish your own copy (move 4); nothing else is needed.

## 6. First moves, in order

1. Read `README.md` and `reference.md` in full, skim `jordan-lead-tracker.html`, and tell the teammate what you loaded and which connectors this chat can reach (Close? Composio?).
2. Check the two connectors from §5 with the teammate. If either is missing, walk them through adding it before anything else.
3. In `jordan-lead-tracker.html`, set `SHEET_ACCOUNT` (near the top of the `<script>`) to the teammate's own Composio Google Sheets account id. Find it by asking Composio which Google Sheets accounts are connected; use the one whose email can open the sheet. Change nothing else.
4. Publish the edited file as a new artifact with the title "Jordan's Lead Tracker". Give it the `artifact` capability (for the Save button) and the `mcp` capability with exactly these read tools: **Close**: `fetch_lead`, `fetch_contact`, `activity_search`, `find_tasks`, `search`, `paginate_search`; **Composio**: `COMPOSIO_MULTI_EXECUTE_TOOL`. If the Composio connector has a different display name in this account, use that name in both the manifest and the page's `call("Composio", …)` line.
5. Have the teammate open the page, allow Close and Composio when asked, and wait about a minute for the first load. Then spot-check these against Close:
   - Graham Shaw: setter call held 9/30, not set to a closer
   - Nick Saucier (tracker name "Nick"): closer call with Omar on 10/9, cancelled
   - Amit Jain: setter call booked 10/14
   - James Wood: Day 5 breakup task done 10/12, no reply, so **grey**
   - Brent (tracker name "B E"): replied by text, no call booked
   - Abdi Russi: setter call held 10/2, follow-up task 10/19, so **not** grey

   Note that some of these will have moved on by the time you read this.
6. If the yellow notice at the top says the tracker was not read live, go back to move 3; the error text says which connector and what to do.
7. Click "Save for Jordan", then share the page with Jordan from its Share menu (he does not need Claude connectors).
8. Daily: open the page each weekday morning, let it load live (or press Refresh), click "Save for Jordan". Read top to bottom: overdue tags (red) first, then today (amber).

## 7. Tone

Keep the machinery (capability manifests, connector ids, code) out of the teammate's face; the
conversation stays about Jordan's leads and what he should do next. When anything feels heavy:
"If this feels hard or confusing at all, please reach out to Zain. He promises he wants to hear
all about it, so he can make this feel like magic. Thank you for using it!"

## 8. Done means

- The teammate has their own published copy of the page, and it loads all of Jordan's leads with "tracker: live" in the top-right status line.
- The six spot-checks above match Close, or any mismatch has been written down with what Close showed.
- Jordan can open the teammate's copy and sees a "Saved" time from today.
- The teammate knows the daily routine: open the page, click Save for Jordan, work the overdue and today items.
- Tell Sheila in one plain sentence that the teammate's copy is live, and send her any mismatches.
