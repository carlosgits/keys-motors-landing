/**
 * Keys Motors — Form-to-GHL Cloudflare Worker
 *
 * Deploy this on Cloudflare Workers (free tier: 100K requests/day).
 * The PIT token lives in Cloudflare's secret env vars — never exposed to client.
 *
 * Deploy steps:
 *   1. Go to https://dash.cloudflare.com → Workers & Pages → Create Worker
 *   2. Paste this code into the editor
 *   3. Settings → Variables → Add secret:
 *        GHL_PIT_TOKEN = pit-11e60db1-6362-4627-884c-a27c91747861
 *        GHL_LOCATION_ID = 1JkhDyRzZIktNwLCLPKD
 *   4. Save & deploy. Get the URL (e.g. https://keys-motors-form.YOUR-SUBDOMAIN.workers.dev)
 *   5. Update landing index.html — change `/api/lead` to that worker URL
 */

const ALLOWED_ORIGINS = [
  'https://keysmotorswpb.com',
  'https://www.keysmotorswpb.com',
  'http://localhost:8080',  // for local testing
  'http://127.0.0.1:5500',  // VSCode Live Server
];

function corsHeaders(origin) {
  const allowed = ALLOWED_ORIGINS.includes(origin) ? origin : ALLOWED_ORIGINS[0];
  return {
    'Access-Control-Allow-Origin': allowed,
    'Access-Control-Allow-Methods': 'POST, OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type',
    'Access-Control-Max-Age': '86400',
  };
}

export default {
  async fetch(request, env, ctx) {
    const origin = request.headers.get('Origin') || '';

    // Preflight
    if (request.method === 'OPTIONS') {
      return new Response(null, { status: 204, headers: corsHeaders(origin) });
    }

    if (request.method !== 'POST') {
      return new Response('Method not allowed', { status: 405, headers: corsHeaders(origin) });
    }

    let payload;
    try {
      payload = await request.json();
    } catch {
      return jsonResp({ error: 'Invalid JSON' }, 400, origin);
    }

    // Sanitize + validate
    const required = ['firstName', 'lastName', 'email', 'phone'];
    for (const f of required) {
      if (!payload[f] || typeof payload[f] !== 'string' || payload[f].length > 200) {
        return jsonResp({ error: `Invalid field: ${f}` }, 400, origin);
      }
    }
    if (!/^\S+@\S+\.\S+$/.test(payload.email)) {
      return jsonResp({ error: 'Invalid email' }, 400, origin);
    }
    // Normalize phone to E.164
    let phone = payload.phone.replace(/[^\d+]/g, '');
    if (!phone.startsWith('+')) {
      phone = '+1' + phone.replace(/\D/g, '');
    }
    if (phone.replace(/\D/g, '').length < 10) {
      return jsonResp({ error: 'Invalid phone' }, 400, origin);
    }

    // Spam guard: simple rate limit per IP using KV (optional, requires KV binding)
    // const ip = request.headers.get('CF-Connecting-IP');
    // ... rate limit check ...

    // Build GHL contact payload
    const ghlPayload = {
      locationId: env.GHL_LOCATION_ID,
      firstName: payload.firstName.slice(0, 100),
      lastName: payload.lastName.slice(0, 100),
      email: payload.email.toLowerCase().slice(0, 200),
      phone: phone,
      source: payload.source || 'Keys Motors Landing',
      tags: Array.isArray(payload.tags) ? payload.tags.slice(0, 10) : [],
      customFields: Array.isArray(payload.customFields) ? payload.customFields.slice(0, 20) : [],
    };

    // Call GHL API
    try {
      const ghlResp = await fetch('https://services.leadconnectorhq.com/contacts/', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${env.GHL_PIT_TOKEN}`,
          'Version': '2021-07-28',
          'Content-Type': 'application/json',
          'Accept': 'application/json',
        },
        body: JSON.stringify(ghlPayload),
      });

      const ghlData = await ghlResp.json();

      if (!ghlResp.ok) {
        console.error('GHL API error:', ghlResp.status, ghlData);
        return jsonResp({ error: 'Lead saved failed', detail: ghlData }, 502, origin);
      }

      return jsonResp({
        ok: true,
        contactId: ghlData.contact?.id,
        message: 'Lead saved successfully',
      }, 200, origin);

    } catch (err) {
      console.error('GHL fetch error:', err.message);
      return jsonResp({ error: 'Upstream error' }, 502, origin);
    }
  },
};

function jsonResp(body, status, origin) {
  return new Response(JSON.stringify(body), {
    status,
    headers: {
      'Content-Type': 'application/json',
      ...corsHeaders(origin),
    },
  });
}
