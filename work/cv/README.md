# CV

- `linkedin-profile-2026-11-24.pdf`: original LinkedIn export (source).
- `cv.html`: working version. Started as the LinkedIn content with only
  English headings, dates and obvious typos fixed. Positions are rewritten
  one at a time, newest first, starting with Ktool. Used later to update
  LinkedIn. Target: 2 A4 pages.
- `cv-2page.html`: the condensed 2-page CV, cut down from `cv.html`. It is
  the source of the PDF.
- `Artyom-Murashov-CV.pdf`: the 2-page A4 PDF, built by `build_pdf.py` from
  `cv-2page.html` (needs reportlab in a venv; the script's docstring has the
  commands). Fonts are in `fonts/` (Source Sans 3, Source Serif 4, OFL).
  The script exits with an error if the result is not exactly 2 pages.
- `linkedin.html`: the full CV split into LinkedIn form fields, plain text
  with a copy button per field, for pasting into LinkedIn by hand (no
  LinkedIn connector exists here). Built from `cv.html` by
  `build_linkedin.py` (standard library only). Re-run it after any change to
  `cv.html` and republish. It leaves out the red todo notes and the
  unconfirmed 8%, and holds the LinkedIn-only data: months for MTS and the
  list of individual skills.
- Published as a private artifact: https://claude.ai/artifact/L9hPBUsXXsajFXFrU7ME7g (republish the same file path).

## Keep out of the CV (Art, 2026-11-24)

- Company-private data: total registrations, subscription counts. The
  conversion rate (8%) stays only after Art confirms the figure.
- Company secrets and over-detailed tech: the AI model and hosting
  (Claude, AWS Bedrock), storage tech (Parquet, S3). Describe in generic terms.
- Hardware plans are not public: no mention of the company's own tracking
  hardware. Say "ecosystem" instead.
- Be gentle about the original prototype (no "buggy").
- Call the physicist co-founder "algorithm engineer".

## Plan (Art, 2026-11-24)

- Add all positions and projects first, going backwards in time, then trim
  to 2 pages. Older positions get trimmed harder.

## Two outputs (Art, 2026-11-24)

- Write the whole CV in full first and do not cut yet. The full version is
  what goes to LinkedIn, where more text is fine.
- After that, condense it into the 2-page CV, which will need heavy cuts.

## Positioning (Art, 2026-11-24)

- Target roles: lead engineer or engineering manager, not executive roles.
  A CTO title is fine only at a really small startup that needs the same
  hands-on competencies.
- Problem to fix: recruiters message him asking to hire people for him,
  not to hire him. The profile should not read as an executive's.
- Headline: drop "CTO at Nashi.Global"; "Founding Engineer at Ktool" is
  better than VP of Engineering there; add Founder and/or Android Expert;
  keep Security Researcher.
- Location in the contact line: Dubai. He will be looking for work in Dubai
  (he lives in Curitiba).
- Languages: Russian native, English C2, Portuguese A2 (hopes for B1 soon).
- Security research stays in the summary only. It is a hobby, not work.
  The bounties (Xiaomi, Whoop and others) were for medium-severity bugs in
  IoT devices; severity is not stated in the CV.
- Telegram Android contest: he won a money prize, "third place or
  something like that", in an animation contest. His animation runs
  directly on the GPU with a shader. Telegram later shipped this animation
  in the app with its own, slightly better optimized implementation. The CV
  says "prize winner" until the place and year are confirmed.
- Skills: rebuilt from the rewritten roles. Telethon (on LinkedIn) is
  dropped under the no-library-names rule; ask Art if it should return.

## Decisions (Art, 2026-11-24, evening)

- Ktool job title is "Founding Engineer", not "Vice President of
  Engineering".
- "10+ years of commercial Android development" stays: he still builds a
  mobile app that runs on Android at Ktool. "A bit of a stretch, but not a
  lie."

## What the 2-page version leaves out (2026-11-24)

- Ktool: the 8% conversion (unconfirmed), "stored once and never changes",
  the token-efficient data artifact detail, Clean Architecture on the app.
- Nashi.Global: the product-decisions bullet (monetization, ambassadors);
  mini-app and bot merged into the launch bullet; status cut to one line.
- Careem: integration documentation, features in the customer and driver
  apps, Scrum practices.
- AI bot: links, media and image understanding; message splitting.
- talabat: the Grocery Home Page reference, null safety migration, the
  effects of the two Flutter initiatives.
- VPN app: architecture names, analytics and animated UI, the two lessons.
- Yandex: feature descriptions (only names stay), the Uber merger story.
- MTS: Stream and MTS background, the statistics and education track
  screens.
- Atom: details of both apps, product decisions.
- Samsung and ISPRAS: one line each.
- Summary: the Scale bullet. Locations of the Russian roles shortened to
  "Russia".

## Parent companies (Art, 2026-11-24)

- Show the better-known parent in parentheses in the role heading:
  "Careem (Uber)" and "talabat (Delivery Hero)". Both are subsidiaries, so
  it is accurate, and it draws the eye.
