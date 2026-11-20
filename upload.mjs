#!/usr/bin/env node
// Publish one story to https://haven-story-runs.vercel.app.
// usage: STORY_UPLOAD_KEY=… node upload.mjs <story.mp4> <story.marks.json> <story.meta.json>
// meta.json: {"id":"story-6-financing-alex","title":"…","what":"…","by":"Alex","date":"21 Nov 2026","results":[[9,"pass"],[1,"fail"]],"note":"…"}
// Needs @vercel/blob installed next to it (npm i @vercel/blob@2.8.2).
import fs from 'node:fs';
import { upload } from '@vercel/blob/client';

const SITE = process.env.STORY_SITE_URL ?? 'https://haven-story-runs.vercel.app';
const key = process.env.STORY_UPLOAD_KEY;
const [videoPath, marksPath, metaPath] = process.argv.slice(2);
if (!key || !videoPath || !marksPath || !metaPath) {
  console.error('usage: STORY_UPLOAD_KEY=… node upload.mjs <story.mp4> <story.marks.json> <story.meta.json>');
  process.exit(2);
}
const meta = JSON.parse(fs.readFileSync(metaPath, 'utf8'));
if (!/^[a-z0-9-]{3,80}$/.test(meta.id ?? '')) throw new Error('meta.id must be a lowercase slug, e.g. story-6-financing-alex');
const marks = JSON.parse(fs.readFileSync(marksPath, 'utf8'));

const blob = await upload(`videos/${meta.id}.mp4`, new Blob([fs.readFileSync(videoPath)], { type: 'video/mp4' }), {
  access: 'public',
  contentType: 'video/mp4',
  handleUploadUrl: `${SITE}/api/upload`,
  clientPayload: JSON.stringify({ key }),
  multipart: true,
});
const chapters = marks.map((m) => ({ at: m.at, caption: m.caption }));
const r = await fetch(`${SITE}/api/stories`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ key, story: { ...meta, video: blob.url, chapters } }),
});
const out = await r.json();
if (!r.ok) throw new Error(`publish failed: ${r.status} ${JSON.stringify(out)}`);
console.log('published', out.url);
