# Keys Motors — Google Ads Bulk Import Files

Ready-to-import CSVs for Google Ads Editor (or any campaign for Key Motors WPB).

**Total**: 5 campaigns · 12 ad groups · 61 keywords · 330 negatives · 12 RSAs (180 headlines) · $47.50/day ($1,425/mo)

## Files

| # | File | Rows | Purpose |
|---|---|---|---|
| 01 | `01_campaigns.csv` | 5 | Campaign settings (budget, geo, language, bid strategy) |
| 02 | `02_adgroups.csv` | 12 | Ad groups + Max CPC per ad group |
| 03 | `03_keywords.csv` | 61 | Positive keywords (Exact + Phrase) |
| 04 | `04_negative_keywords.csv` | 330 | Negative keywords (66 unique × 5 campaigns minus KBB-skip for trade-in) |
| 05 | `05_ads.csv` | 12 | Responsive Search Ads (RSAs) with full bilingual copy |
| 06 | `06_sitelinks.csv` | 6 | Sitelink extensions |
| 07 | `07_callouts.csv` | 10 | Callout extensions |
| 08 | `08_snippets.csv` | 2 | Structured snippet extensions |

## Campaign breakdown

| Campaign | Daily | Languages | Geo | Strategy |
|---|---|---|---|---|
| 01 - BHPH English Near Me | $20 | English | US + PB/Broward/Orange County | Maximize clicks |
| 02 - Local Florida Geo | $10 | English | Palm Beach County + WPB only | Maximize clicks |
| 03 - BHPH Spanish | $10 | Spanish | PB/Broward/Miami-Dade County | Maximize clicks |
| 04 - Trade-In | $5 | EN + ES | PB/Broward County | Maximize clicks |
| 05 - Branded Defensive | $2.50 | EN + ES | US-wide | Maximize clicks |

**Why Maximize Clicks first**: BHPH dealer with 0 historical conv data → can't use Smart Bidding yet. After 30+ conversions/mo per campaign, switch to **tCPA** target $40-50.

**All campaigns ship PAUSED** — Carlos reviews everything before activating.

## Import to Google Ads Editor (10 min)

### Prerequisites
1. Key Motors needs a Google Ads account (creates one at ads.google.com if not yet)
2. Account linked to Carlos's MCC (or Carlos becomes user of the account)
3. Conversion tracking set up (Web Pixel + Enhanced Conversions)
4. Landing page deployed and live (the `index.html` we built)

### Import steps
1. Open Google Ads Editor desktop app
2. Account → Open → select Keys Motors account
3. File → Import → from file
4. Import in this order (to satisfy parent-child dependencies):
   - 01_campaigns.csv (creates the 5 campaigns)
   - 02_adgroups.csv (creates ad groups)
   - 03_keywords.csv (adds positive keywords)
   - 04_negative_keywords.csv (adds negatives)
   - 05_ads.csv (creates RSAs)
   - 06/07/08 — extensions (sitelinks, callouts, snippets)
5. Review each campaign in Editor (status = Paused so nothing goes live)
6. **Update LANDING_URL placeholder** in 05_ads.csv before posting — currently `https://keys-motors-landing.example.com`
7. Post changes → Check Changes → Post

### Before activating
- [ ] Replace `LANDING_URL` placeholder with actual deployed URL
- [ ] Set up Conversion Actions in Google Ads → Tools → Conversions (Purchase / Lead form submit)
- [ ] Add the gtag conversion snippet to landing page success state
- [ ] Verify Enhanced Conversions enabled
- [ ] Set up Search Partners = OFF (lower quality traffic)
- [ ] Confirm geo targeting (Excluded locations if you don't ship out of state)
- [ ] Add ad schedule if business hours matter (Mon-Sat 9-7, Sun 11-5)
- [ ] Activate campaigns one-by-one, not all at once
- [ ] Watch for first 48h: spend pacing, click costs, search terms

## Keyword strategy summary

**Match type philosophy**:
- **Exact match** for top intent terms — control CPC, no surprises
- **Phrase match** for broader discovery — let Google expand within reason

**Negative strategy** (66 unique negatives per campaign):
- Vehicle out-of-scope: new, lease, luxury brands, salvage, parts
- Wrong intent: jobs, repair, reviews, how-to, wikipedia
- Competitor tools: kbb (except trade-in), edmunds, carfax, autotrader, carmax
- Geographic noise: colombia, venezuela, mexico (Spanish geo)
- Marketplaces: craigslist, facebook marketplace, offerup

**Note**: KBB negatives are SKIPPED for the Trade-In campaign — we WANT "kbb trade in value" traffic there (90K/mo high-intent qualified searches).

## Ad copy themes (verified patterns from BHPH research)

Every RSA includes at minimum:
- ✅ Credit-objection enumeration ("Bad Credit? No Credit? Bankruptcy?")
- ✅ Speed anchor ("Pre-Approved in 2 Minutes")
- ✅ Dollar anchor ("$1,500 Down")
- ✅ Trust signal ("9 Years · BBB A- · Family-Owned")
- ✅ Multi-CTA in headlines ("Drive Today" + "Apply Online" + "Call Now")
- ✅ "We Are The Bank" / In-house financing framing
- ✅ ITIN/No-SSN copy
- ✅ Spanish counterparts for Hispanic campaign

## Performance expectations (first 30 days)

Based on industry benchmarks (LocaliQ + DigitalApplied 2026):
- **Avg CPC**: $2.50 - $4.00 (target — BHPH range is $3-$11)
- **CTR**: 4-6% (good RSAs in BHPH often hit 5-8%)
- **Conversion rate**: 3-5% on lead form
- **CPL target**: $30-50 (sector avg $42.95)

**With $1,425/mo budget**:
- Expected clicks: 350-570
- Expected leads: 12-25
- Expected CPL: $57-119 (likely higher initially → drops as Quality Score builds)

## Next iteration (post-30-days)

1. Mine search terms → add more negatives to kill waste
2. Identify top-performing keywords → bump bids, add Exact match variants
3. Pause underperforming keywords (< 50 impressions or 0 conversions after 200 clicks)
4. Once 30+ conversions/mo: migrate to tCPA bidding
5. A/B test winning RSAs by pausing weakest headlines and adding new ones
6. Add Performance Max campaign with audience signals = "Used Car Shoppers" + "Hispanic Households FL"
