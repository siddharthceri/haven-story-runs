# Haven story runs

Source of https://haven-story-runs.vercel.app: a searchable list of narrated videos of Haven OS v2 user stories.

- `index.html` loads the list from `/api/stories`.
- Videos and story records live in the project's Vercel Blob store.
- `api/upload.js` hands out client-upload tokens for an `UPLOAD_KEY`.
- `api/stories.js` lists stories (GET), adds or replaces one (POST, `UPLOAD_KEY`), and deletes one (DELETE, `ADMIN_KEY`).
- `upload.mjs` is the one-command publisher the `record-user-stories` skill uses.

Teammates publish with the skill; nobody needs a pull request or a Vercel account.
