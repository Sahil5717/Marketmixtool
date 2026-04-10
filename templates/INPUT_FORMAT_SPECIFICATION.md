# Input Data Format Specification
## Yield Intelligence Platform
### Version 1.0 | Phase 1

---

## Overview

The platform requires **two CSV files** as input. Everything else is computed by the engines.

| File | Required? | Purpose | Expected Rows |
|------|-----------|---------|---------------|
| Campaign Performance | **Yes** | All KPIs, ROI, trends, diagnostics, optimization | 5K-500K (daily × channels × campaigns × regions) |
| User Journeys | **Yes for MTA** | Multi-touch attribution (linear, position-based) | 50K-5M (touchpoints across all user journeys) |

If User Journeys file is not provided, only Last-Touch attribution is available.

---

## File 1: Campaign Performance

**Filename convention:** `campaign_performance_YYYY.csv` or `campaign_data.csv`
**Encoding:** UTF-8
**Delimiter:** Comma
**Grain:** One row per Date × Channel × Campaign × Region (finest available)

### Required Columns

These 5 columns MUST be present. Analysis cannot proceed without them.

| Column | Type | Format | Rules | Used By |
|--------|------|--------|-------|---------|
| `date` | Date | YYYY-MM-DD | Valid date; no nulls; range within last 3 years | All engines — time axis for trends, seasonality, MoM |
| `channel` | String | Free text | Non-null; will be mapped to standard taxonomy | All engines — primary grouping dimension |
| `campaign` | String | Free text | Non-null; max 200 chars | Deep dive, diagnostics, campaign-level marginal ROI |
| `spend` | Numeric | Decimal, no currency symbols | ≥ 0; no nulls; in base currency units (e.g., USD) | ROI, ROAS, CAC, optimizer, leakage, avoidable cost |
| `revenue` | Numeric | Decimal, no currency symbols | ≥ 0; no nulls; attributed revenue | ROI, ROAS, response curves, optimizer |

### Recommended Columns

These unlock additional analyses. Missing columns disable specific features, not the whole tool.

| Column | Type | Format | Rules | Unlocks |
|--------|------|--------|-------|---------|
| `sub_channel` | String | Free text | e.g., "google", "meta", "bing" | Sub-channel drill-down within channels |
| `campaign_objective` | String | Enum-like | awareness, lead_generation, conversion, retargeting, nurture, brand_awareness, organic | Campaign objective analysis |
| `funnel_stage` | String | Enum | top, middle, bottom | Funnel stage mapping for spend allocation analysis |
| `region` | String | Free text | Will be mapped to taxonomy | Regional breakdown, regional leakage analysis |
| `product` | String | Free text | Product/BU name | Product attribution, product-level ROI |
| `audience_segment` | String | Free text | Target audience description | Audience-level performance analysis |
| `impressions` | Integer | Whole number | ≥ 0; set 0 for offline channels | CTR calculation, funnel top |
| `clicks` | Integer | Whole number | ≥ 0; ≤ impressions; set 0 for offline | CPC, CTR, CVR, funnel |
| `leads` | Integer | Whole number | ≥ 0 | CPL, lead-to-sale rate, funnel |
| `mqls` | Integer | Whole number | ≥ 0; ≤ leads | Funnel analysis, bottleneck detection |
| `sqls` | Integer | Whole number | ≥ 0; ≤ mqls | Funnel analysis, handoff analysis |
| `conversions` | Integer | Whole number | ≥ 0; ≤ sqls | CAC, CVR, payback period |
| `bounce_rate` | Decimal | 0.00 to 1.00 | 0 ≤ x ≤ 1; set 0 if unavailable | CX signals, conversion suppression |
| `avg_session_duration_sec` | Numeric | Seconds | ≥ 0; set 0 for offline | CX signals, experience analysis |
| `form_completion_rate` | Decimal | 0.00 to 1.00 | 0 ≤ x ≤ 1 | CX signals, conversion suppression |
| `pages_per_session` | Numeric | Decimal | ≥ 0 | Engagement depth |
| `nps_score` | Integer | -100 to 100 | Net Promoter Score | Retention risk signals |
| `unsubscribe_rate` | Decimal | 0.00 to 0.10 | Email channel only; set 0 for others | Retention risk |
| `confidence_tier` | String | Enum | High, Medium, Model-Estimated | Confidence badges on all metrics |

### Rules for Offline Channels

Offline channels (TV, radio, OOH, events, direct mail, partner) typically have:
- `impressions` = 0 (not directly tracked)
- `clicks` = 0
- `leads` may be available (event registrations, call-ins)
- `revenue` may be estimated via CRM matching or time-lag correlation
- `confidence_tier` = "Model-Estimated"
- `bounce_rate`, `session_duration`, `form_completion` = 0

**Do NOT leave these fields null** — use 0 for unavailable metrics. Nulls cause calculation errors.

### Example: What Different Channel Rows Look Like

**Paid Search (fully tracked):**
```
2025-01-15,paid_search,google,PS_Brand_Exact,brand,bottom,North,Product_A,existing,1250,15000,675,47,21,8,3,1140,0.35,155,0.14,3.2,38,0,High
```

**TV National (model-estimated):**
```
2025-01-15,tv_national,,TV_Brand_Q1,awareness,top,National,Product_A,,12000,0,0,0,0,0,0,0,0,0,0,0,0,0,Model-Estimated
```
Note: TV revenue attribution happens via MMM (Phase 2). In Phase 1, set revenue=0 and the tool will flag it as model-estimated.

**Events (partially tracked):**
```
2025-01-15,events,,CES_2025_Booth,lead_generation,middle,West,Product_B,,4500,0,0,85,38,14,5,5500,0.12,320,0.48,0,68,0,Model-Estimated
```

---

## File 2: User Journeys

**Filename convention:** `user_journeys_YYYY.csv` or `journey_data.csv`
**Encoding:** UTF-8
**Grain:** One row per Journey × Touchpoint

### Required Columns

| Column | Type | Format | Rules | Used By |
|--------|------|--------|-------|---------|
| `journey_id` | String | Unique ID | Consistent within a journey; e.g., "J00001" or user hash | All 3 attribution models |
| `touchpoint_order` | Integer | 1, 2, 3... | Sequential within journey; starts at 1 | Position-based attribution weights |
| `total_touchpoints` | Integer | ≥ 1 | Same value for all rows in a journey | Attribution weight calculation |
| `touchpoint_date` | Date | YYYY-MM-DD | Valid date | Time-based analysis |
| `channel` | String | Must match campaign file | Same channel names as File 1 | Attribution credit by channel |
| `campaign` | String | Must match campaign file | Same campaign names as File 1 | Campaign-level attribution |
| `converted` | Boolean | TRUE/FALSE | TRUE if journey resulted in conversion | Filters converting journeys |
| `conversion_revenue` | Numeric | Decimal | > 0 only on last touchpoint of converted journeys; 0 elsewhere | Revenue to distribute across touchpoints |

### Optional Columns

| Column | Type | Format | Unlocks |
|--------|------|--------|---------|
| `sub_channel` | String | Free text | Sub-channel attribution |
| `interaction_type` | String | ad_view, ad_click, organic_visit, email_click, phone_call, etc. | Interaction-type analysis |
| `device` | String | desktop, mobile, tablet, phone, tv, outdoor | Cross-device journey analysis |
| `conversion_date` | Date | YYYY-MM-DD | Time-to-conversion analysis |
| `conversion_product` | String | Product name | Product-level attribution |

### Journey Data Rules

1. **Every journey must have consecutive touchpoint_order** starting from 1
2. **total_touchpoints must be consistent** across all rows of the same journey_id
3. **conversion_revenue should only appear on the LAST touchpoint** of a converted journey
4. **Non-converted journeys** should have converted=FALSE and conversion_revenue=0 for all touchpoints
5. **Include non-converted journeys** — they provide volume context and path analysis
6. **Minimum data:** 1,000+ converted journeys recommended for reliable attribution
7. **Channel/campaign names must match** the Campaign Performance file for proper joining

### How Attribution Uses This Data

```
Last-Touch:     100% credit → last touchpoint before conversion
Linear:         Equal credit → each touchpoint gets revenue / total_touchpoints
Position-Based: 40% first + 40% last + 20% split among middle touchpoints
```

---

## Data Quality Requirements

### Minimum for Analysis

| Requirement | Minimum | Recommended |
|-------------|---------|-------------|
| Date range | 3 months | 12+ months |
| Rows (campaign file) | 500 | 5,000+ |
| Channels | 3 | 8+ |
| Campaigns | 10 | 30+ |
| Converted journeys | 500 | 3,000+ |

### Quality Gate Thresholds

| Check | Threshold | Result if Failed |
|-------|-----------|-----------------|
| Required columns present | All 5 present | ❌ Block all analysis |
| Data completeness | > 85% cells non-null | ⚠️ Warning banner |
| Date coverage | > 3 months | ⚠️ Response curves less reliable |
| Negative values in spend/revenue | 0 allowed | ❌ Block until fixed |
| Duplicate rows on key | 0 duplicates | ⚠️ Warning, deduplicate |
| Channel mapping | > 80% mapped | ⚠️ Block optimizer until mapped |

---

## What Happens If Columns Are Missing

| Missing Column(s) | Impact |
|-------------------|--------|
| impressions, clicks | No CTR, CPC; funnel starts at leads |
| leads, mqls, sqls | No funnel analysis; no bottleneck detection |
| conversions | No CAC, CVR, payback period; ROI uses revenue only |
| region | No regional breakdown or leakage heatmap |
| product | No product-level attribution |
| bounce_rate, session_duration, form_completion | No CX signals; no conversion suppression analysis |
| nps_score | No retention risk signals |
| confidence_tier | All metrics shown without confidence badges |
| User Journey file entirely | Only last-touch attribution; no linear or position-based |

---

## Preparing Your Data

### Step-by-Step

1. **Export daily campaign data** from each platform (Google Ads, Meta, LinkedIn, etc.)
2. **Combine into single CSV** with the schema above
3. **Add offline channels** — events, direct mail, TV as separate rows with spend + any tracked leads/conversions
4. **Set confidence_tier** — "High" for digital with tracking, "Medium" for partially tracked, "Model-Estimated" for offline
5. **Export journey data** from your CDP, analytics platform, or CRM
6. **Ensure channel/campaign names match** between both files
7. **Upload both files** into the platform

### Common Pitfalls

- **Don't mix currencies** — convert everything to one base currency before upload
- **Don't include header rows twice** — one header row at top only
- **Don't use commas in numbers** — 1250.50 not 1,250.50
- **Don't leave required fields blank** — use 0 for unavailable numeric fields
- **Don't use different channel names** between the two files — "Paid Search" in one and "paid_search" in the other will break joining
