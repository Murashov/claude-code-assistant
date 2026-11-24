"""Build linkedin.html: the full CV (cv.html) split into LinkedIn form fields,
each as plain text with a copy button.

    python3 work/cv/build_linkedin.py

Standard library only. Re-run after any change to cv.html, then republish
linkedin.html.
"""
import html
import re
import sys
import zlib
from pathlib import Path

HERE = Path(__file__).parent
SRC = HERE / "cv.html"
OUT = HERE / "linkedin.html"

# LinkedIn's limits for the free-text fields.
LIMITS = {"Headline": 220, "About": 2600, "Description": 2000}

NAV = {
    "ktool": "Ktool", "nashi": "Nashi.Global", "careem": "Careem",
    "gptbot": "AI bot", "talabat": "talabat", "vpn": "VPN app",
    "yandex": "Yandex", "mts": "MTS", "atom": "Atom", "samsung": "Samsung",
    "ispras": "ISPRAS",
}

# LinkedIn needs a month for every date; the CV shows only years for these.
DATES = {
    "mts": "Feb 2018 – Sep 2019",
}

LOGO_NOTE = ("Typing the company with the parent in parentheses drops the "
             "company logo. Picking the company page from LinkedIn's dropdown "
             "keeps the logo but not the parent name.")
NOTES = {
    "ktool": "The 8% conversion is left out here until you confirm the figure.",
    "careem": LOGO_NOTE,
    "talabat": LOGO_NOTE,
    "gptbot": "LinkedIn asks for start and end months. The CV has only the "
              "years, so pick the months yourself.",
    "mts": "The CV says 2018 – 2019. These months are the start of your first "
           "stint and the end of the second, merged into one entry.",
}

# The CV groups skills into prose lines; LinkedIn takes them one at a time.
SKILLS = [
    "Android", "Kotlin", "Java", "Flutter", "Dart", "Kotlin Multiplatform",
    "Python", "Django", "REST APIs", "Docker", "Vue.js",
    "Large Language Models (LLM)", "AI Agents", "Clean Architecture", "MVVM",
    "MVI", "Redux", "Data Pipelines", "Technical Leadership", "Scrum",
    "Mentoring", "Telegram Bots", "C++", "Security Research",
]

LANGUAGES = [
    ("Russian", "Native or bilingual proficiency"),
    ("English", "Full professional proficiency"),
    ("Portuguese", "Elementary proficiency"),
]


def text(fragment):
    fragment = re.sub(r'<span class="todo">.*?</span>', "", fragment, flags=re.S)
    fragment = re.sub(r"<[^>]+>", "", fragment)
    return re.sub(r"\s+", " ", html.unescape(fragment)).strip()


def body(fragment):
    """Paragraphs and bullets of a CV block as LinkedIn plain text."""
    out, prev = [], None
    for tag, inner in re.findall(r"<(p|li)>(.*?)</\1>", fragment, flags=re.S):
        if prev and (tag == "p" or prev == "p"):
            out.append("")
        out.append(("• " if tag == "li" else "") + text(inner))
        prev = tag
    return "\n".join(out)


def read():
    src = SRC.read_text()
    headline = text(re.search(r'<div class="headline">(.*?)</div>', src, re.S).group(1))
    location = text(re.search(r'<div class="contact">(.*?)</div>', src, re.S).group(1)).split(" · ")[0]
    about = body(re.search(r"<h2>Summary</h2>(.*?)<h2>", src, re.S).group(1))
    jobs = []
    for key, inner in re.findall(r'<section class="job" id="(\w+)">(.*?)</section>', src, re.S):
        role = text(re.search(r'<span class="role">(.*?)</span>', inner, re.S).group(1))
        meta = text(re.search(r'<span class="meta">(.*?)</span>', inner, re.S).group(1))
        title, company = role.split(" · ", 1)
        dates, place = meta.split(" · ", 1)
        desc = body(inner)
        if key == "ktool":
            cut = " and an 8% conversion to paid subscriptions"
            assert cut in desc, "Ktool intro changed; update the 8% handling"
            desc = desc.replace(cut, " and paid subscriptions")
        jobs.append(dict(key=key, title=title, company=company,
                         dates=DATES.get(key, dates),
                         place=None if place in ("Global", "Side project") else place,
                         desc=desc))
    assert set(NAV) == {j["key"] for j in jobs}, "positions changed; update NAV"
    return headline, location, about, jobs


def field(group, label, value, copy=True):
    esc = html.escape(value)
    if not copy:
        return (f'<div class="field"><div class="field-head"><span class="label">{label}</span>'
                f'<span class="hint">set in the form</span></div>'
                f'<div class="value plain">{esc}</div></div>')
    fid = f"{group}-{label.lower().replace(' ', '-')}-{zlib.crc32(value.encode()):08x}"
    count = ""
    if label in LIMITS:
        n, limit = len(value), LIMITS[label]
        if n > limit:
            sys.exit(f"{group} {label}: {n} characters, LinkedIn allows {limit}")
        count = f'<span class="count">{n:,} / {limit:,}</span>'
    return (f'<div class="field" data-id="{fid}"><div class="field-head">'
            f'<span class="label">{label}</span>{count}'
            f'<button type="button" class="copy" id="b-{fid}">Copy</button></div>'
            f'<div class="value" tabindex="0">{esc}</div></div>')


def section(key, name, fields, note=None):
    note = f'<p class="note">{html.escape(note)}</p>' if note else ""
    return (f'<section class="group" id="{key}"><h2>{html.escape(name)}</h2>{note}'
            + "".join(fields) + "</section>")


def build():
    headline, location, about, jobs = read()
    nav = [("intro", "Intro"), ("about", "About")]
    groups = [
        section("intro", "Intro", [field("intro", "Headline", headline),
                                   field("intro", "Location", location)]),
        section("about", "About", [field("about", "About", about)]),
    ]
    for j in jobs:
        k = j["key"]
        fields = [field(k, "Title", j["title"]), field(k, "Company", j["company"]),
                  field(k, "Dates", j["dates"], copy=False)]
        if j["place"]:
            fields.append(field(k, "Location", j["place"]))
        fields.append(field(k, "Description", j["desc"]))
        nav.append((k, NAV[k]))
        groups.append(section(k, f'{j["company"]}', fields, NOTES.get(k)))
    nav += [("education", "Education"), ("skills", "Skills"), ("languages", "Languages")]
    groups.append(section("education", "Education", [
        field("education", "School", "Higher School of Economics"),
        field("education", "Degree", "Bachelor's degree"),
        field("education", "Field of study", "Information Technology"),
        field("education", "Dates", "2012 – 2016", copy=False)]))
    chips = "".join(
        f'<button type="button" class="chip" id="s-{zlib.crc32(s.encode()):08x}" '
        f'data-id="skill-{zlib.crc32(s.encode()):08x}">{html.escape(s)}</button>' for s in SKILLS)
    groups.append('<section class="group" id="skills"><h2>Skills</h2>'
                  '<p class="note">LinkedIn takes skills one at a time. Tap a skill to copy it.</p>'
                  f'<div class="chips">{chips}</div></section>')
    langs = "".join(f"<li><b>{a}</b><span>{b}</span></li>" for a, b in LANGUAGES)
    groups.append('<section class="group" id="languages"><h2>Languages</h2>'
                  '<p class="note">Both parts are picked from lists in the form.</p>'
                  f'<ul class="langs">{langs}</ul></section>')
    links = "".join(f'<a href="#{k}">{html.escape(n)}</a>' for k, n in nav)
    page = TEMPLATE.replace("{{NAV}}", links).replace("{{GROUPS}}", "\n".join(groups))
    OUT.write_text(page)
    print(f"{OUT.name}: {len(jobs)} positions, {page.count('class=\"copy\"') + len(SKILLS)} copy buttons")


TEMPLATE = r"""<title>LinkedIn Paste Kit</title>
<meta name="claude:viewport-fit-sides" content="cover">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Source+Sans+3:wght@400;600;700&family=Source+Serif+4:wght@600&display=swap">
<style>
/* One narrow column of LinkedIn form sections; each field is a label row with
   its copy button, and the exact text to paste underneath. */
:root {
  --bg: #f3f5f8; --surface: #ffffff; --field: #f6f8fb;
  --ink: #1c2128; --muted: #5b6472; --line: #d5dbe3;
  --accent: #1f4e79; --on-accent: #ffffff; --done: #2c6e52; --done-bg: #e4f1ea;
  --body: "Source Sans 3", "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
  --display: "Source Serif 4", Georgia, "Times New Roman", serif;
}
@media (prefers-color-scheme: dark) {
  :root:not([data-theme="light"]) {
    color-scheme: dark;
    --bg: #11151b; --surface: #1a2029; --field: #141920;
    --ink: #e6eaf0; --muted: #9aa5b4; --line: #2d3644;
    --accent: #8ab8e6; --on-accent: #0e1620; --done: #7fcaa3; --done-bg: #1c3329;
  }
}
:root[data-theme="dark"] {
  color-scheme: dark;
  --bg: #11151b; --surface: #1a2029; --field: #141920;
  --ink: #e6eaf0; --muted: #9aa5b4; --line: #2d3644;
  --accent: #8ab8e6; --on-accent: #0e1620; --done: #7fcaa3; --done-bg: #1c3329;
}
body {
  background: var(--bg); color: var(--ink);
  font: 16px/1.5 var(--body);
  padding-block: 24px 64px;
  padding-left: max(16px, env(safe-area-inset-left, 0px));
  padding-right: max(16px, env(safe-area-inset-right, 0px));
}
.wrap { max-width: 720px; margin: 0 auto; display: flex; flex-direction: column; gap: 20px; }
h1 { font: 600 28px/1.2 var(--display); margin: 0; text-wrap: balance; }
.lede { margin: 6px 0 0; color: var(--muted); max-width: 60ch; }
.status { display: flex; flex-wrap: wrap; align-items: center; gap: 12px; color: var(--muted); font-variant-numeric: tabular-nums; }
.status b { color: var(--ink); }
nav { display: flex; flex-wrap: wrap; gap: 6px; }
nav a {
  color: var(--accent); text-decoration: none; font-size: 14px; font-weight: 600;
  padding: 4px 10px; border: 1px solid var(--line); border-radius: 999px; background: var(--surface);
}
.group {
  background: var(--surface); border: 1px solid var(--line); border-radius: 10px;
  padding: 16px; display: flex; flex-direction: column; gap: 14px;
  scroll-margin-top: calc(env(safe-area-inset-top, 0px) + 12px);
}
.group h2 { font: 600 19px/1.25 var(--display); margin: 0; text-wrap: balance; }
.note { margin: 0; color: var(--muted); font-size: 14px; }
.field { display: flex; flex-direction: column; gap: 6px; }
.field-head { display: flex; align-items: center; gap: 10px; min-height: 36px; }
.label { font-size: 12px; font-weight: 700; letter-spacing: .06em; text-transform: uppercase; color: var(--muted); margin-right: auto; }
.count, .hint { font-size: 13px; color: var(--muted); font-variant-numeric: tabular-nums; }
.value {
  background: var(--field); border: 1px solid var(--line); border-radius: 6px;
  padding: 10px 12px; white-space: pre-wrap; overflow-wrap: anywhere;
  -webkit-user-select: all; user-select: all;
}
.value.plain { background: none; border-style: dashed; -webkit-user-select: text; user-select: text; }
button { font: 600 14px/1 var(--body); cursor: pointer; }
.copy {
  background: var(--accent); color: var(--on-accent); border: 1px solid var(--accent);
  border-radius: 6px; padding: 10px 16px; min-width: 84px;
}
.done .copy, .chip.done { background: var(--done-bg); color: var(--done); border-color: var(--done); }
.done .value { border-color: var(--done); }
.chips { display: flex; flex-wrap: wrap; gap: 8px; }
.chip {
  background: var(--field); color: var(--ink); border: 1px solid var(--line);
  border-radius: 999px; padding: 10px 14px;
}
.reset { background: none; color: var(--accent); border: 1px solid var(--line); border-radius: 6px; padding: 8px 12px; }
.langs { list-style: none; margin: 0; padding: 0; display: flex; flex-direction: column; gap: 6px; }
.langs li { display: flex; flex-wrap: wrap; gap: 4px 12px; }
.langs span { color: var(--muted); }
:focus-visible { outline: 2px solid var(--accent); outline-offset: 2px; }
</style>

<div class="wrap">
  <header>
    <h1>LinkedIn Paste Kit</h1>
    <p class="lede">The full CV, split into LinkedIn's form fields. Copy a field, paste it into the matching box on LinkedIn. Copied fields turn green so you can stop and pick up later.</p>
  </header>
  <div class="status"><span><b id="n-done">0</b> of <b id="n-all">0</b> copied</span><button type="button" class="reset" id="reset">Clear marks</button></div>
  <nav aria-label="Sections">{{NAV}}</nav>
{{GROUPS}}
</div>

<script>
(function () {
  var KEY = 'linkedin-kit-copied';
  var done = {};
  try { done = JSON.parse(localStorage.getItem(KEY) || '{}') || {}; } catch (e) {}
  function save() { try { localStorage.setItem(KEY, JSON.stringify(done)); } catch (e) {} }

  var items = [].slice.call(document.querySelectorAll('[data-id]'));
  function label(el, on) {
    var b = el.classList.contains('chip') ? null : el.querySelector('.copy');
    if (b) b.textContent = on ? 'Copied' : 'Copy';
  }
  function paint() {
    var n = 0;
    items.forEach(function (el) {
      var on = !!done[el.dataset.id];
      el.classList.toggle('done', on);
      label(el, on);
      if (on) n++;
    });
    document.getElementById('n-done').textContent = n;
    document.getElementById('n-all').textContent = items.length;
  }

  function legacy(t) {
    return new Promise(function (ok, fail) {
      var ta = document.createElement('textarea');
      ta.value = t; ta.setAttribute('readonly', '');
      ta.style.cssText = 'position:fixed;top:0;left:0;opacity:0';
      document.body.appendChild(ta);
      ta.select(); ta.setSelectionRange(0, t.length);
      var good = false;
      try { good = document.execCommand('copy'); } catch (e) {}
      ta.remove();
      good ? ok() : fail();
    });
  }
  function copy(t) {
    if (navigator.clipboard && navigator.clipboard.writeText) {
      return navigator.clipboard.writeText(t).catch(function () { return legacy(t); });
    }
    return legacy(t);
  }
  // If the browser refuses both ways, select the text so one manual copy does it.
  function select(node) {
    var r = document.createRange(); r.selectNodeContents(node);
    var s = window.getSelection(); s.removeAllRanges(); s.addRange(r);
  }

  items.forEach(function (el) {
    var chip = el.classList.contains('chip');
    var btn = chip ? el : el.querySelector('.copy');
    var src = chip ? el : el.querySelector('.value');
    var t = src.textContent;
    btn.addEventListener('click', function () {
      copy(t).then(function () {
        done[el.dataset.id] = 1; save(); paint();
      }, function () {
        select(src);
        if (!chip) btn.textContent = 'Selected';
      });
    });
  });
  document.getElementById('reset').addEventListener('click', function () {
    done = {}; save(); paint();
  });
  paint();
})();
</script>
"""

if __name__ == "__main__":
    build()
