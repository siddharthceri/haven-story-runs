// Issues short-lived client-upload tokens so a recorder can put a video straight into the Blob store.
// The caller proves it may publish by sending UPLOAD_KEY in clientPayload.
import { handleUpload } from '@vercel/blob/client';

export default async function handler(req, res) {
  if (req.method !== 'POST') return res.status(405).end();
  try {
    const result = await handleUpload({
      body: req.body,
      request: req,
      onBeforeGenerateToken: async (pathname, clientPayload) => {
        const { key } = JSON.parse(clientPayload || '{}');
        if (!key || key !== process.env.UPLOAD_KEY) throw new Error('bad upload key');
        if (!/^videos\/[a-z0-9-]+\.mp4$/.test(pathname)) throw new Error('pathname must be videos/<lowercase-slug>.mp4');
        return { allowedContentTypes: ['video/mp4'], maximumSizeInBytes: 200 * 1024 * 1024, addRandomSuffix: false, allowOverwrite: true };
      },
      onUploadCompleted: async () => {},
    });
    return res.status(200).json(result);
  } catch (e) {
    return res.status(400).json({ error: String(e.message || e) });
  }
}
