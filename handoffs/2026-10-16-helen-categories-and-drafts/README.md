# Handoff: Helen's lead categories, her email drafts, and how drafts land in her Gmail

**From:** Claude Code cloud session on `sheila-smbdh/email-triage`, 2026-10-16
**To:** any surface (Claude Code, Cowork, or a fresh chat). Sheila is in the chat.
**Mission:** give the next session a complete, current picture of three parts of the Helen
email digest (which categories Helen acts on, the exact drafts written for her, and the rules
for creating those drafts in her Gmail) so it can review, change, or explain them without
re-reading the 1,800-line task file.

Read this whole file first. It is self-contained: every template below is copied word for
word from the source of truth, so nothing here depends on reaching the repo. If you can reach
the repo (GitHub connector or a checkout), the source is
`skills/helen-email-digest/SKILL.md` on `main`, and it wins over this file if they differ.

---

## 1. What this is

SMB Deal Hunter runs a daily cloud Routine that reads Helen Guo's inbox
(`helen@smbdealhunter.xyz`), picks out buyer leads, writes Helen's reply as a **Gmail draft**
on each lead's thread (cc'ing whoever the lead is being forwarded to), logs one row per lead
to the Google Sheets tracker (`Tracker (JordanK)`), and posts one short to-do list to Slack
`#helen-email-digest`. Helen's whole job is: open the thread, read the draft, send.

The task definition is one file, `skills/helen-email-digest/SKILL.md`. The three parts this
handoff covers are: **STEP 2's categories** (what Helen pays attention to), **STEP 2's
"Suggested Helen email draft"** (the templates), and **STEP 3** (creating the drafts in Gmail).
The rest of the file (access preflight, Slack post, tracker write, Jordan's own drafts) is out
of scope here except where it touches these three.

Nothing is broken. This is a reference handoff, not a rescue.

## 2. Where everything lives

| Resource | What it is | Read in full? |
|---|---|---|
| This file | Self-contained summary plus every Helen template verbatim | Yes |
| `skills/helen-email-digest/SKILL.md` (repo `sheila-smbdh/email-triage`, `main`) | Source of truth. Categories: STEP 2, lines ~175-780. Helen templates: ~780-1140. Gmail drafts: STEP 3, ~1313-1478 | Only the section you are changing |
| `docs/handoff-helen-email-digest.md` (same repo) | Change log of every rule change with dates and real cases | No, look up a date when needed |
| `docs/routine-jordan-lead-intake.md` (same repo) | The hourly Routine that turns Helen's forward into Jordan's Close tasks | No |

The Routine reads `SKILL.md` at run time, so a merged change to that file is a live change the
next morning.

## 3. Part one: the categories Helen pays attention to

Every email that survives the inbox sweep ends in exactly one of these. There is no
"Uncategorized" bucket: below about 70% confidence, it is dropped.

### Tier 1: the three tracked lead categories (get a tracker row, a draft, a Slack bullet)

- **Buy Box**: volunteers geography, industry, budget or financing criteria, or asks if SMB
  Deal Hunter has matching deals ("anything in California?", "$50K down for a laundromat in NYC").
- **Ready Now**: gave a phone number, asked for a call, used enrollment language ("enroll me",
  "call me"), or replied with clear interest in a specific featured deal.
- **Price Wall**: asks what SMB Deal Hunter costs. Also covers "what does a business sell
  for", which gets a different draft (see Part two).

### Not leads, but still drafted for Helen

- **🎁 Bonus claim**: a bare "Yes" reply where the thread has **no** message from
  `helen+canned.response@smbdealhunter.xyz` (the welcome automation missed it). Draft, no cc,
  no tracker row, run report only (not Slack).
- **✋ Experienced operator asking for advice**: someone who says in their own words they have
  bought or run a business, asking Helen for advice or fit (not deals). Draft with a gap for
  Helen's advice, no cc, no row. The one ✋ case that appears in Slack, with a "Before you
  send" line. Real case: Kevin B.
- **✋ Listing link request**: a reader asks for a featured deal's link or says it is broken.
  Link is verified against Airtable `Business Sellers` (name, state, profit, revenue, start
  year all match, `Status` = Active) before drafting. Nothing verifies → no draft. No cc, no
  row, run report only. Real case: Jennifer Hill. A request for **more details** with no link
  problem is Ready Now, not this.

### 🟢 Tracking handover progress

A thread in one of the three categories that Helen has **already** forwarded (a teammate is
on it). Gets a tracker row, no draft, no Slack bullet. If the sender already has a row on the
tab, nothing new at all ("already tracked").

### Who the lead is forwarded to (tracker column D, and the draft's cc)

Looked up in Close by the lead's **email address** (never display name) on every Tier 1 and 🟢 lead:

| Close shows | Column D | Draft cc's |
|---|---|---|
| Client / Customer status, or any won opportunity | `Forward to Scott Moorhouse (scott@smbdealhunter.xyz)` | Scott |
| Had or has booked a meeting (non-cancelled), host still active and not Helen/Sheila | `Forward to <First Last> (<email>)` | that host |
| Host has left, or nothing found, or Close errors | `Send to Jordan` | Jordan (`jkempster@smbdealhunter.xyz`) |

### Dropped: no row, no draft, no Slack bullet (Helen does not reply)

Drop rules win over everything, including the Close routing:

1. Real estate plays (RV parks, mobile home parks, storage, land, rental property).
2. Business is outside the US (judge where the business is, not the person; watch for US towns with foreign names).
3. States under $50K to invest, whatever financing on top. Exactly $50K stays.
4. "Can't afford it" / "don't have the funds", even if they also ask the price.
5. Empty web form (Softr form with no `Message`).
6. Declined outright or obvious tyre-kicker.
7. Not wanting to buy a business (deal commentary, their own property). Deal vocabulary is not buyer intent; hydrate any numbers-heavy reply before judging.
8. Never-track list, checked first: **Hani Sammour, Ryan Hogan, Scott Boyette** (`boyettecs@gmail.com`).
9. A retort, not a request ("help me finance one then", "you don't help, scam").
10. Helen already replied (sent, not a draft) without cc'ing Jordan: her conversation now. Exception: the Price Wall call-pushback draft she sent to wait on the lead.
11. Not written in English.

Every dropped lead goes in the run report with its rule.

## 4. Part two: Helen's email drafts (verbatim)

### Rules that bind every draft

- **No em dashes or en dashes**, ever (and no spaced hyphen as a stand-in). Only exception: the bonus reply's `Hey -`.
- **Written out in full**: "definitely", "15 minutes", "with you". No shorthand.
- **Nothing beyond the template**: only the first name, plus Buy Box criteria/area, plus the forwarding name and `who you …` line. If a draft says something the template does not, take it out.
- **Never invent commercial terms.** The 1% line: plain Price Wall only. The guarantee (named, no terms): plain and call-pushback Price Wall only. "6 to 12 months": Buy Box only. "$175M": Buy Box and specific-deal Ready Now only, exact wording. Never answer whether a deal is still available.
- **First name**: sign-off name, else first word of Gmail display name, else (bare address) `Hey there,`. Never guess from the address. Address the lead as "you"; never infer gender.
- `@Jordan` / `@[Name]` is literal text in the email, read as a nudge because that person is cc'd.

### Which template

| Situation | Template | Cc |
|---|---|---|
| Buy Box, `Send to Jordan` | Buy Box | Jordan |
| Ready Now, general readiness | Ready Now | Jordan |
| Ready Now, asking about a specific featured deal | Ready Now, specific deal | Jordan |
| Price Wall, asks what we cost | Price Wall | Jordan |
| Price Wall, asks what a **business** sells for | Price Wall, business price | Jordan |
| Price Wall, pushing back on the call with a list of questions | Price Wall, call-pushback (flagged in Slack for Helen's review) | **none** |
| Any `Forward to …` row, any category | Forwarding | the column D person |
| 🎁 Bonus claim | Bonus reply | **none** |
| ✋ Operator | Operator reply | **none** |
| ✋ Listing link, verified | Listing link reply | **none** |

### Buy Box

```
Hey [First Name], finding custom deals like [their criteria] in [their area] is exactly what our Pro Program is built for. We help you source, finance, and acquire a business in 6 to 12 months, and in the past year alone we've helped our members close over $175M in deals. I've cc'd Jordan to give you a call or set up a time to chat if you'd like to learn more.
```

"Pro Program" is hyperlinked to `https://pro.smbdealhunter.xyz/` in Gmail. In plain text
(tracker column L): `is exactly what our Pro Program is built for (https://pro.smbdealhunter.xyz/).`
Criteria/area: drop whichever they did not give; neither → "finding custom deals like that".
Never add a criterion or place they did not mention.

### Ready Now

```
Hey [First Name], we can definitely help. Looping in Jordan from our team. @Jordan, do you mind finding 15 minutes to give [First Name] a call?
```

### Ready Now, asking about a specific deal

```
Hey [First Name], deals like this tend to go quickly. Our Pro Program helps buyers move fast and make competitive offers so they don't miss out. In the past 12 months, we've helped our members close over $175M in deals. I've looped in Jordan from our team in case you'd like to learn more. @Jordan, do you mind finding 15 minutes to chat with [First Name]?
```

"Pro Program" hyperlinked the same way. Plain text: `Our Pro Program (https://pro.smbdealhunter.xyz/) helps buyers move fast...`

### Price Wall

```
Hey [First Name], fair question. For our average member, the cost comes out to roughly 1% of the purchase price that is due upfront. We do have a success guarantee, which we can talk more about live. Let's get you on a quick call. @Jordan on our team can find a time that works for you.
```

### Price Wall, asking what a business sells for

```
Hey [First Name], great question. Let's get you on a quick call. @Jordan on our team can find a time that works for you.
```

Sort on whose price: our cost → plain Price Wall; a business's price (sale, asking, "go for",
valuation, a business type named next to "price") → this one.

### Price Wall, pushing back on the call itself (no cc)

```
Hey [First Name], fair questions, and I appreciate you being direct about it.

Here is why we start with a call. It is not a sales presentation to walk you through standard terms. The call is as much about us making sure you would be a good fit for our community as it is about you vetting us. We offer a guarantee to our members, and we cannot offer that to everyone, so we are selective about who we bring in. That is not something we can figure out over email.

So it is a two way thing, and that is why we do not get into the details until there is mutual fit on both sides.

Let me know if you're still interested and want me to loop someone from our team in.
```

Answers none of their questions, deliberately. Never add the 1% line. Real case: W. Stephen Aldridge.

### Forwarding (every `Forward to …` row)

```
Hey [First Name], great to hear from you. Looping in [Name], who you've worked with. @[Name], do you mind picking this up with [First Name]?
```

Swap the middle phrase: `who you've worked with` (client, to Scott), `who you spoke with
before` (past call), `who you have a call booked with` (upcoming call). `[Name]` is the
column D person's first name.

### Bonus reply (🎁, no cc)

```
Hey - thanks so much for joining! Here's the link to the bonuses: https://smbdealhunter.notion.site/SMB-Deal-Hunter-Welcome-Bonuses-18b3787936d0805eb0b4c1a88c7d2c40
```

No name, no personalisation.

### Operator reply (✋, no cc)

```
Hi [First Name],

Thanks for the context, and great background!

[HELEN: your take on where they should focus]

We're bringing on a couple CEOs in Residence/Operating Partners if that's of interest: https://www.linkedin.com/jobs/view/4445190173/

Helen
```

The bracketed line stays exactly as written; the routine never writes the advice. The CEO in
Residence line is always included; Helen deletes it if it does not fit.

### Listing link reply (✋, no cc)

```
[Listing Details URL]

Here you go!
```

Only the Airtable-verified `Listing Details URL`. Nothing else from the Airtable record
(it holds seller contact details) goes in the draft, report or Slack.

## 5. Part three: directions for drafting in Helen's Gmail (STEP 3)

**Connection.** Through Composio, Gmail account **`gmail_kath-tiou`** (Helen's mailbox), pinned
on **every** call. The default Composio Gmail account is Jordan's; an unpinned call would put
Helen's reply in Jordan's drafts. Never use the first-party Gmail connector (it is Sheila's mailbox).

**Which messages get a draft.** Exactly those that got a draft in Part two: Tier 1 (cc column
D), call-pushback (no cc), 🎁 bonus (no cc), ✋ operator (no cc), ✋ verified link (no cc).
No draft for 🟢 handovers, unverified link requests, or dropped leads.

**Step by step:**

1. **Check the thread first.** `GMAIL_FETCH_MESSAGE_BY_THREAD_ID` on the lead's `threadId`. If
   any message carries the `DRAFT` label, leave it exactly as it is, create nothing, and count
   it as "draft already present". Never a second draft on a thread.
2. **Create it:**
   ```
   GMAIL_CREATE_EMAIL_DRAFT
     account:          gmail_kath-tiou
     thread_id:        <the lead's threadId>
     recipient_email:  <the lead's own email address>
     cc:               ["<the address from column D>"]   # omit entirely for no-cc drafts
     body:             <the draft, verbatim, then three blank lines>
     is_html:          false
     subject:          (omit)
   ```
   - **Omit `subject`**: a subject with `thread_id` forks a new conversation.
   - **To is the lead only**: no `extra_recipients`, no `bcc`, never reply-all to a newsletter blast.
   - **Cc is one person**: Jordan on `Send to Jordan`, the address in parentheses on `Forward to …`. Omit the field for no-cc drafts.
   - **Body**: the draft character for character, then `\n\n\n\n` (Sheila's ask: space under the message). Tracker column L gets the same text without the trailing blank lines.
3. **Buy Box and specific-deal Ready Now are HTML** (`is_html: true`): "Pro Program" wrapped as
   `<a href="https://pro.smbdealhunter.xyz/">Pro Program</a>`, ending in `<br><br><br><br>`.
   Escape `&`, `<`, `>` in anything taken from the lead's email. Every other draft stays plain text.
4. On HTTP 429, back off and retry that draft.
5. **Verify every draft** with `GMAIL_GET_DRAFT` (`format: "full"`, using the **draft id**, not
   the message id): on the right thread; To is only the lead; Cc is exactly column D or absent
   for no-cc drafts; body matches, no `—` or `–`, ends with blank lines (trimmed blank lines are
   noted, not a failure); for HTML drafts, "Pro Program" is a live link and no raw `<a`, `<br>`
   or `&amp;` shows as text.
6. **Never send, update or delete.** Never `GMAIL_SEND_DRAFT`, `GMAIL_REPLY_TO_THREAD`,
   `GMAIL_UPDATE_DRAFT` or `GMAIL_DELETE_DRAFT`. No labelling, archiving or deleting mail.
7. **If a draft fails or does not verify**: still write the text to tracker column L, mark the
   lead's Slack bullet with the "No Gmail draft" line pointing Helen to column L, and report
   the tool's actual error in the run report. Do not fix it by creating a second draft. Never
   post draft text to Slack. The rest of the run carries on.

## 6. Decisions locked (do not re-litigate)

- Drafts only; the routine never sends email from Helen's mailbox.
- Three tracked categories only; no Tier 2/3, no Uncategorized, no "Ignore" rows (since 2026-09-24).
- Jordan Kempster is the setter (replaced Yobani 2026-09-23). Yobani still gets leads whose last call was with him.
- No em dashes in any draft (2026-09-24).
- Template wording is Sheila's and Helen's; do not restructure a template to suit an email.
- The $175M line: exact wording, only Buy Box and specific-deal Ready Now (2026-10-07).
- "Pro Program" links to `https://pro.smbdealhunter.xyz/` in those same two drafts (2026-10-07).
- Helen-already-answered-without-Jordan is dropped (2026-10-06); non-English is dropped (2026-10-07).
- Draft text never goes to Slack (2026-09-29).

## 7. Changed since

Nothing has changed in these three sections since 2026-10-07. The most recent repo commits
(through 2026-10-16) touched Jordan's scorecard and lead tracker, not the digest's categories
or drafts.

## 8. Blockers and unblock paths

None open. One dated item to watch:

- **The $175M figure is dated 2026-10-07.** Owned by Sheila. After 90 days (from 2027-01-05)
  every Slack post tags her until she gives a new figure; then it is changed in all four places
  in `SKILL.md` (two templates, two HTML bodies in STEP 3) in one edit, with the date updated.

## 9. First moves, in order

1. Read this file in full. Tell Sheila what you loaded and whether you can also reach
   `skills/helen-email-digest/SKILL.md` in `sheila-smbdh/email-triage` from this surface.
2. Ask Sheila, one question with tappable options, what she wants done with these sections:
   review them, change a category or template, explain them to someone (Helen, Jordan), or
   something else.
3. For any change: draft it as a redline against the verbatim text above, get Sheila's yes,
   then (only if this surface can write to the repo) edit `SKILL.md` in every place the rule
   appears (templates appear in STEP 2 and again as HTML in STEP 3; plain-text forms go to
   column L) and log it in `docs/handoff-helen-email-digest.md`.

## 10. Tone

Keep the machinery (branches, Composio account ids, tool names) out of Sheila's face unless
she asks; the conversation stays about Helen's leads and replies. When anything feels heavy:
"If this feels hard or confusing at all, please reach out to Zain. He promises he wants to
hear all about it, so he can make this feel like magic. Thank you for using it!"

## 11. Done means

- Sheila has what she asked for on these three sections (a review, a change, or an explainer).
- Any rule change is in `SKILL.md` everywhere it appears, and logged with today's date.
- Sheila is told in one plain sentence what changed and when it takes effect (the next morning's run).
