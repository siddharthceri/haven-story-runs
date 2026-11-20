// GET: every published story. POST (UPLOAD_KEY): add or replace one. DELETE ?id= (ADMIN_KEY): remove one and its video.
import { del, list, put } from '@vercel/blob';

const ID = /^[a-z0-9-]{3,80}$/;
const FIELDS = ['title', 'what', 'by', 'date', 'note'];

async function all() {
  const out = [];
  let cursor;
  do {
    const page = await list({ prefix: 'stories/', cursor, limit: 1000 });
    for (const b of page.blobs) {
      const r = await fetch(b.url, { cache: 'no-store' });
      if (r.ok) out.push(await r.json());
    }
    cursor = page.hasMore ? page.cursor : undefined;
  } while (cursor);
  return out.sort((a, b) => (b.createdAt || '').localeCompare(a.createdAt || '') || (a.order ?? 0) - (b.order ?? 0));
}

export default async function handler(req, res) {
  try {
    if (req.method === 'GET') {
      res.setHeader('Cache-Control', 'no-store');
      return res.status(200).json(await all());
    }
    const body = typeof req.body === 'string' ? JSON.parse(req.body || '{}') : req.body || {};
    if (req.method === 'POST') {
      if (body.key !== process.env.UPLOAD_KEY) return res.status(401).json({ error: 'bad upload key' });
      const s = body.story || {};
      if (!ID.test(s.id || '')) return res.status(400).json({ error: 'story.id must be a lowercase slug' });
      if (!/^https:\/\/[a-z0-9]+\.public\.blob\.vercel-storage\.com\/videos\/[a-z0-9-]+\.mp4$/.test(s.video || ''))
        return res.status(400).json({ error: 'story.video must be the blob URL from the upload' });
      for (const f of ['title', 'what', 'by']) if (!s[f]) return res.status(400).json({ error: `story.${f} is required` });
      const clean = { id: s.id, video: s.video, createdAt: new Date().toISOString(), order: Number(s.order) || 0 };
      for (const f of FIELDS) clean[f] = String(s[f] ?? '').slice(0, 600);
      clean.results = (Array.isArray(s.results) ? s.results : []).slice(0, 6)
        .map(([n, k]) => [Number(n) || 0, ['pass', 'fail', 'blocked', 'skipped'].includes(k) ? k : 'pass']);
      clean.chapters = (Array.isArray(s.chapters) ? s.chapters : []).slice(0, 60)
        .map((c) => ({ at: Number(c.at) || 0, caption: String(c.caption ?? '').slice(0, 200) }));
      await put(`stories/${s.id}.json`, JSON.stringify(clean), { access: 'public', contentType: 'application/json', addRandomSuffix: false, allowOverwrite: true });
      return res.status(200).json({ ok: true, id: s.id, url: `https://haven-story-runs.vercel.app/#${s.id}` });
    }
    if (req.method === 'DELETE') {
      if (body.key !== process.env.ADMIN_KEY) return res.status(401).json({ error: 'bad admin key' });
      const id = String(req.query.id || '');
      if (!ID.test(id)) return res.status(400).json({ error: 'id' });
      const s = (await all()).find((x) => x.id === id);
      if (!s) return res.status(404).json({ error: 'not found' });
      await del([s.video, (await list({ prefix: `stories/${id}.json` })).blobs[0]?.url].filter(Boolean));
      return res.status(200).json({ ok: true });
    }
    return res.status(405).end();
  } catch (e) {
    return res.status(500).json({ error: String(e.message || e) });
  }
}
