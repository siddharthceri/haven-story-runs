# Haven story runs

The site behind https://haven-story-runs.vercel.app: narrated videos of Haven OS v2 user stories, recorded end to end.
Vercel deploys `main` automatically.

## Add your stories (open a pull request)

1. Record with the `record-user-stories` skill. It gives you `<file>.mp4` and `<file>.marks.json` per story.
2. Copy both files into the root of this repo. Use a file name that starts with your story and is unique, e.g. `story-6-financing-alex.mp4`.
3. Append one entry per story to `stories.json`:
   `file`, `title`, `what` (one line on what it records), `by` (your name), `date`, `results` (e.g. `[[10,"pass"],[1,"fail"]]`), `note`.
4. Rebuild the page: `STORY_WORK=. STORY_SITE=. python3 build_site.py`
5. Open a pull request. Sid merges; the site updates a minute later.

Keep each video under about 20 MB (the skill's compose.py output is 4 to 8 MB). Never commit keys or logins.
