# Keys Motors — Bilingual Landing Page

Form-based landing for Google Ads campaigns. Pre-approval lead capture, EN/ES toggle, sends contacts to GHL via secure backend proxy.

## Files

| File | Purpose |
|---|---|
| `index.html` | Single-page landing (HTML + Tailwind via CDN + vanilla JS) |
| `worker.js` | Cloudflare Worker backend proxy (token never exposed to client) |
| `README.md` | This file |

## Architecture

```
[User]
  ↓ submits form
[Landing index.html on Keys Motors hosting]
  ↓ POST JSON to worker URL
[Cloudflare Worker (worker.js)]
  ↓ validates + sanitizes + adds PIT token
[GHL API services.leadconnectorhq.com/contacts/]
  ↓ creates contact
[GHL Location 1JkhDyRzZIktNwLCLPKD] → contact appears in Contacts
```

**Why the proxy** — the PIT token (`pit-11e60db1-...`) gives full API access to the GHL location. Exposing it in client-side JS is a security risk (any user could scrape it). The Worker keeps it server-side.

## Section breakdown (based on verified BHPH dealer patterns)

1. **Hero** — Credit-objection enumeration ("Bad credit? No credit? Bankruptcy? Repossession?") + speed anchor ("2 minutes") + dollar anchor ("$1,500 down")
2. **Trust strip** — 9 years · BBB A- · 70+ vehicles · 2-min pre-approval · Hablamos español
3. **Financing** — 8 credit-situation cards (bad credit, no credit, bankruptcy, repo, divorce, ITIN, self-employed, no co-signer) + 3-step process
4. **Inventory teaser** — 4 placeholder vehicle cards (replace with real inventory feed)
5. **Credit Builder Program** — 12-month graduation to traditional financing (verified pattern from OK Carz "Conquest Program")
6. **Trade-In** — "Any condition, any make" + free 30-min appraisal
7. **Address + Map** — West Palm Beach location with Google Maps embed
8. **Footer** — Links, locations, contact, BBB badge

## Bilingual implementation

- Toggle button top-right: 🇪🇸 Español ↔ 🇺🇸 English
- All copy wrapped in `<span class="lang-en">...</span><span class="lang-es">...</span>`
- Auto-detects browser locale on first visit (saves preference in localStorage)
- Placeholders use `data-placeholder-en` / `data-placeholder-es` attributes

## Form fields

| Field | Type | Notes |
|---|---|---|
| firstName | text | Required |
| lastName | text | Required |
| phone | tel | Auto-normalized to E.164 (+1XXXXXXXXXX) |
| email | email | Required, regex validated |
| vehicleType | select | sedan / suv / truck / van / any |
| monthlyIncome | select | BHPH classic question — income bracket |

Tags applied to contact: `google-ads-lead`, `landing-v1`, `vehicle:<type>`, `income:<bracket>`
Custom fields: `vehicle_type`, `monthly_income`

## Deploy

### Option A — Cloudflare Worker + static hosting (Recommended)

1. **Deploy worker**:
   - Cloudflare dashboard → Workers & Pages → Create Worker
   - Paste contents of `worker.js`
   - Settings → Variables & Secrets → add **encrypted** secrets:
     - `GHL_PIT_TOKEN` = `pit-11e60db1-6362-4627-884c-a27c91747861`
     - `GHL_LOCATION_ID` = `1JkhDyRzZIktNwLCLPKD`
   - Deploy → copy the URL (e.g. `https://keys-motors-form.YOURSUB.workers.dev`)

2. **Update landing**:
   - In `index.html`, line ~470 (in the form submit handler), replace:
     ```js
     const resp = await fetch('/api/lead', { ... })
     ```
     with:
     ```js
     const resp = await fetch('https://keys-motors-form.YOURSUB.workers.dev', { ... })
     ```
   - In `worker.js`, update `ALLOWED_ORIGINS` to include the production domain (e.g. `https://keysmotorswpb.com`)

3. **Host the landing**:
   - GHL AI Studio (vibe): paste HTML into the editor
   - OR Netlify drop: drag `index.html` to https://app.netlify.com/drop
   - OR Vercel: `vercel deploy`
   - OR any static host

### Option B — GHL Inbound Webhook (no Cloudflare needed)

If Carlos prefers no third-party infra:

1. In GHL location → Workflows → Create workflow
2. Trigger: **Inbound Webhook**
3. Get the webhook URL
4. Add action: **Create Contact** (map webhook fields to contact fields)
5. Add action: **Add Tag** with tags from payload
6. In landing `index.html`, change form action to that webhook URL
7. ⚠️ Note: GHL Inbound Webhooks don't enforce CORS, so the form might need to handle no-CORS responses

## Testing

### Local test (without deploy)

Open `index.html` in browser. The form submission will fail with `/api/lead` 404 (no backend yet) — that's expected. You can preview UI/UX freely.

### Worker test (via curl)

```bash
curl -X POST https://keys-motors-form.YOURSUB.workers.dev \
  -H "Content-Type: application/json" \
  -d '{
    "firstName": "Test",
    "lastName": "Lead",
    "email": "test@example.com",
    "phone": "5616531765",
    "source": "Test from curl",
    "tags": ["test"]
  }'
```

Expected response: `{"ok":true,"contactId":"...","message":"Lead saved successfully"}`

Check in GHL → Contacts that "Test Lead" appears with the source/tag set.

## Google Ads integration

To track conversions in Google Ads when form submits:

1. In Google Ads → Tools → Conversions → Create conversion action → Web
2. Get the Conversion ID + Label (`AW-XXXXXXXXXX/yyyyyyy`)
3. In `index.html`, find this line in the form submit handler:
   ```js
   if (window.gtag) window.gtag('event', 'conversion', { send_to: 'AW-XXXXXXXXXX/CONVERSION_LABEL' });
   ```
4. Replace `AW-XXXXXXXXXX/CONVERSION_LABEL` with the real ID
5. Also add the Google Tag (gtag.js) to `<head>` if not already there

## Customization checklist

Things to swap before going live:

- [ ] Brand colors (currently `keys-blue: #0c2c52`, `keys-red: #c91f1f`, `keys-gold: #f4a700` — adjust to match logo)
- [ ] Logo (currently text-only "KEYSMOTORS")
- [ ] Hero "$1,500 down" — confirm actual minimum down with cliente
- [ ] Inventory teaser — wire to real inventory feed (DealerCarSearch API?) or use static photos
- [ ] Hours (Mon-Sat 9-7, Sun 11-5 — confirm)
- [ ] Phone (561) 653-1765 — confirmed via BBB
- [ ] Add Facebook Pixel if running Meta Ads in parallel
- [ ] Add CAPTCHA (Cloudflare Turnstile free) if spam is a concern
- [ ] Add the actual Google Maps embed (currently uses generic coords)

## Decisions documented

Based on deep research of 6 verified BHPH dealers (OK Carz, ABC Autos, Crossroads Autoplex, Cassat Auto Sales, Midpoint Auto Group):

| Pattern | Where applied | Source confidence |
|---|---|---|
| Credit-objection enumeration in hero | Hero h1 + Financing section grid | 🟢 High (5 dealers) |
| Multi-CTA stack (4 parallel CTAs) | Hero CTAs | 🟢 High (3 dealers) |
| Low-friction primary CTA ("Start Here!") | Hero primary button | 🟡 Medium (2 dealers) |
| Speed anchor ("2 minutes") | Hero subheadline + form badge | 🟢 High |
| Dollar anchor ("$1,500 down") | Hero bullets | 🟢 High |
| 12-month credit graduation program | Dedicated section | 🟢 High |
| "We are the bank" framing | Financing section | 🟡 Medium |
| "Hablamos español" tag | Trust strip + lang toggle | 🔴 Low (only 1 dealer verified, but well-known convention) |

Patterns NOT used (couldn't verify in research):
- Full Spanish-mirror landing (we built bilingual toggle instead — simpler to maintain)
- ITIN-specific landing (mentioned but no verified example — included as bullet only)

## Known gaps

- No real Keys Motors inventory data (their sites timed out during research — kept getting ConnectTimeout)
- No real reviews/testimonials embedded (would pull from Google Business / Facebook in production)
- No SSL/security badges (could add Norton, McAfee, etc. — not critical for BHPH)
- No exit-intent popup (could add a "Wait! Get our financing calculator" modal)
