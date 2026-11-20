#!/usr/bin/env python3
"""Builds $STORY_WORK/site/index.html: a plain searchable list of recorded user stories.
Reads $STORY_WORK/stories.json (file, title, what, by, date, results, note) and the <file>.mp4 + <file>.marks.json
pairs from compose.py, copied into $STORY_WORK/site/."""
import html
import json
import os

WORK = os.environ.get('STORY_WORK', os.path.expanduser('~/story-runs'))
D = os.environ.get('STORY_SITE', os.path.join(WORK, 'site'))
STORIES = json.load(open(os.path.join(WORK, 'stories.json')))

CSS = """:root{--bg:#FAFAF9;--surface:#FFFFFF;--hover:#F4F3F1;--line:#E8E6E1;--line-strong:#D4D1CA;--fg:#0A0A0A;--fg-2:#52504B;
--fg-3:#8F8B83;--accent:#D8C7A3;--accent-ink:#7A6440;--accent-wash:#F5EFE3;--ok:#2F7A4F;--bad:#C0392B;
--sans:"Geist",ui-sans-serif,system-ui,sans-serif;--mono:"Geist Mono",ui-monospace,Menlo,monospace}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--fg-2);font:15px/1.55 var(--sans)}
main{max-width:1040px;margin:0 auto;padding:56px 24px 72px}
.lab{font:500 11px/1 var(--mono);text-transform:uppercase;letter-spacing:.06em;color:var(--fg-3)}
h1{font-size:40px;font-weight:600;letter-spacing:-.04em;line-height:1.05;color:var(--fg);margin:12px 0 12px}h1 span{color:var(--fg-3)}
.lead{max-width:640px;margin:0 0 28px}
.bar{display:flex;align-items:center;border:1px solid var(--line);background:var(--surface);margin-bottom:-1px}
.bar input{flex:1;height:44px;border:0;padding:0 16px;font:15px var(--sans);background:none;outline:none;color:var(--fg)}
.bar .sum{font:12px var(--mono);color:var(--fg-3);padding:0 16px;white-space:nowrap;border-left:1px solid var(--line);line-height:44px}
.bar .sum b{color:var(--accent-ink);font-weight:500}
table{width:100%;border-collapse:collapse;border:1px solid var(--line);background:var(--surface)}
th{text-align:left;font:500 11px var(--mono);text-transform:uppercase;letter-spacing:.06em;color:var(--fg-3);padding:10px 16px;border-bottom:1px solid var(--line)}
td{padding:16px;border-bottom:1px solid var(--line);vertical-align:top}tr.row{transition:background .15s ease}tr.row:hover{background:var(--hover)}
.t{color:var(--fg);font-weight:600;font-size:16px;letter-spacing:-.01em}.w{font-size:13px;color:var(--fg-3);margin-top:2px;max-width:560px}
.m{font:12px/1.7 var(--mono);white-space:nowrap}
.st i{display:inline-block;width:6px;height:6px;margin-right:8px;background:var(--fg-3)}.st.pass i{background:var(--ok)}.st.fail i{background:var(--bad)}
button.watch{height:30px;padding:0 14px;border-radius:999px;border:1px solid var(--fg);background:var(--fg);color:#fff;font:500 12px var(--sans);
cursor:pointer;transition:background .15s ease,color .15s ease}button.watch.on{background:var(--surface);color:var(--fg);border-color:var(--line-strong)}
tr.player td{padding:0 16px 20px;background:var(--surface)}video{width:100%;display:block;background:#000}
.chs{display:grid;grid-template-columns:1fr 1fr;border:1px solid var(--line);border-top:0}
.ch{text-align:left;border:0;border-bottom:1px solid var(--line);background:none;padding:8px 12px;font:13px var(--sans);color:var(--fg-2);cursor:pointer;transition:background .15s ease}
.ch:nth-child(odd){border-right:1px solid var(--line)}.ch:hover{background:var(--hover)}.ch span{font:12px var(--mono);color:var(--fg-3);margin-right:10px}
.note{font-size:13px;margin:12px 0 0;padding:10px 12px;background:var(--accent-wash);color:var(--accent-ink)}
.empty{padding:16px;color:var(--fg-3);border:1px solid var(--line);border-top:0;background:var(--surface);margin:0}
footer{margin-top:24px;font-size:13px;color:var(--fg-3)}
@media(max-width:720px){main{padding:32px 16px 48px}h1{font-size:30px}th:nth-child(2),td:nth-child(2){display:none}.chs{grid-template-columns:1fr}.ch:nth-child(odd){border-right:0}}"""

JS = """const q=document.getElementById('q');q.oninput=()=>{const v=q.value.toLowerCase();let n=0;
document.querySelectorAll('tr.row').forEach(r=>{const hit=r.dataset.s.includes(v);r.hidden=!hit;if(!hit)r.nextElementSibling.hidden=true;n+=hit});
document.getElementById('empty').hidden=n>0};
document.querySelectorAll('button.watch').forEach(b=>b.onclick=()=>{const p=b.closest('tr').nextElementSibling,v=p.querySelector('video');
p.hidden=!p.hidden;b.textContent=p.hidden?'Watch':'Hide';b.classList.toggle('on',!p.hidden);if(p.hidden)v.pause()});
document.querySelectorAll('.ch').forEach(c=>c.onclick=()=>{const v=c.closest('td').querySelector('video');v.currentTime=+c.dataset.t;v.play()})"""


def row(s):
    marks = json.load(open(os.path.join(D, f"{s['file']}.marks.json")))
    ch = ''.join(f'<button class="ch" data-t="{m["at"]}"><span>{int(m["at"] // 60)}:{int(m["at"] % 60):02d}</span>{html.escape(m["caption"])}</button>' for m in marks)
    res = '<br>'.join(f'<span class="st {k}"><i></i>{n} {k}</span>' for n, k in s['results'])
    note = f'<p class="note">{html.escape(s["note"])}</p>' if s.get('note') else ''
    search = html.escape(' '.join([s['title'], s['what'], s['by'], s['date'], s.get('note', ''), ' '.join(m['caption'] for m in marks)]).lower())
    return (f'<tr class="row" data-s="{search}"><td><div class="t">{html.escape(s["title"])}</div><div class="w">{html.escape(s["what"])}</div></td>'
            f'<td class="m">{html.escape(s["by"])}<br>{html.escape(s["date"])}</td><td class="m">{res}</td>'
            f'<td><button class="watch">Watch</button></td></tr>'
            f'<tr class="player" hidden><td colspan="4"><video src="{s["file"]}.mp4" controls preload="none" playsinline></video><div class="chs">{ch}</div>{note}</td></tr>')


page = f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Haven story runs</title><link href="https://fonts.googleapis.com/css2?family=Geist:wght@400;500;600&family=Geist+Mono:wght@400;500&display=swap" rel="stylesheet">
<style>{CSS}</style></head><body><main><div class="lab">Haven OS v2 · user stories on video</div>
<h1>Haven story runs. <span>Real customer journeys, recorded end to end.</span></h1>
<p class="lead">Each story runs through the real product on a test company, narrated step by step. Useful while QAing, and for understanding how a flow works.</p>
<div class="bar"><input id="q" type="search" placeholder="Search stories, steps, people…" aria-label="Search stories"><div class="sum">{len(STORIES)} stories · <b>{sum(n for x in STORIES for n,k in x['results'] if k=='pass')}</b> steps pass</div></div>
<table><thead><tr><th>Story</th><th>Recorded by</th><th>Result</th><th></th></tr></thead><tbody>
{''.join(row(s) for s in STORIES)}</tbody></table><p id="empty" class="empty" hidden>No story matches.</p>
<footer>Recorded with Playwright and narrated with ElevenLabs. Add yours with the record-user-stories skill.</footer></main><script>{JS}</script></body></html>"""

open(os.path.join(D, 'index.html'), 'w').write(page)
print('wrote', os.path.join(D, 'index.html'), len(STORIES), 'stories')
