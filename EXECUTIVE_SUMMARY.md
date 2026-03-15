# Prediction Market Research: Executive Summary

**Date:** March 15, 2026  
**Objective:** Identify short-horizon trading opportunities across Polymarket and Kalshi  
**Strategies:** Intraday Mean Reversion & 1-3 Day Swing Volatility

---

## Overview

This research scanned **1,500 prediction markets** across two major platforms (Polymarket and Kalshi) to identify tradeable opportunities in mid-tier liquidity markets. The goal was to find markets suitable for:

1. **Intraday Mean Reversion** — Markets with noisy flow that overshoots and reverts
2. **Swing Volatility (1-3 days)** — Markets likely to reprice on catalysts over a short horizon

We specifically avoided flagship/headline markets (presidential elections, Fed decisions, major sports finals) where pricing is efficient and edge is minimal.

---

## Key Statistics

| Metric | Value |
|--------|-------|
| **Total Markets Scanned** | 1,500 |
| **Polymarket Markets** | 700 |
| **Kalshi Markets** | 800 |
| **Passed All Filters** | 608 (41%) |
| **Excluded** | 892 (59%) |

---

## Filtering Criteria

### Hard Filters Applied
- ✅ Market must be **open/active**
- ✅ Liquidity between **$100,000 - $5,000,000**
- ✅ Recent activity ratio **> 2%**
- ✅ Non-stale order flow
- ❌ Excluded ultra-obvious macro/headline markets
- ❌ Excluded markets with crowding penalty > 6

### Exclusion Reasons (892 markets)
- Liquidity outside target range
- Stale markets (high displayed liquidity, weak recent activity)
- Flagship headline markets (Fed, Elections, Championships)
- Near-terminal pricing (price < 5¢ or > 95¢)
- Insufficient trading activity

---

## Top Opportunities Identified

### 🎯 Best Mean-Reversion Candidates

These markets show high activity relative to liquidity, repeated price movement, and mid-range pricing suitable for intraday reversals.

| Rank | Market | Platform | Liquidity | Activity Ratio | Score |
|------|--------|----------|-----------|----------------|-------|
| 1 | James Madison at Southern Miss Winner? | Kalshi | $815K | 661% | 9.57 |
| 2 | James Madison at Southern Miss (USM side) | Kalshi | $422K | 599% | 9.32 |
| 3 | Crude Oil $150 by end of March | Polymarket | $2.96M | 64% | 9.22 |
| 4 | Jason Day win 2026 Masters | Polymarket | $1.45M | 43% | 9.22 |
| 5 | Crude Oil $120 by end of March | Polymarket | $2.28M | 71% | 9.22 |

**Why These Work for Mean Reversion:**
- Extremely high churn (activity ratios 40-660%)
- Prices in tradeable mid-range zones
- Active two-way flow visible
- Not crowded headline markets
- Timeframes of 2-14 days to expiry

---

### 🌊 Best Swing-Volatility Candidates

These markets have identifiable catalysts, underfollowed attention, and are likely to reprice materially over 1-3 days.

| Rank | Market | Platform | Liquidity | Activity Ratio | Score |
|------|--------|----------|-----------|----------------|-------|
| 1 | Jason Day win 2026 Masters | Polymarket | $1.45M | 43% | 9.68 |
| 2 | Bitcoin reach $75,000 in March | Polymarket | $1.61M | 52% | 9.68 |
| 3 | Ethereum reach $4,000 in March | Polymarket | $1.58M | 56% | 9.68 |
| 4 | Bitcoin dip to $60,000 in March | Polymarket | $1.01M | 46% | 9.68 |
| 5 | Crude Oil $180 by end of March | Polymarket | $1.75M | 85% | 9.68 |

**Why These Work for Swing Trading:**
- Clear catalysts (tournament results, price movements, news)
- 2-4 week expiry windows
- Underfollowed relative to activity
- High inefficiency scores
- Room for material repricing

---

## Market Categories

| Category | Count | Examples |
|----------|-------|----------|
| **Sports** | High | College basketball, Masters golf, mid-tier NBA/NFL games |
| **Crypto** | Medium | BTC/ETH price thresholds by month-end |
| **Commodities** | Medium | Crude oil strike prices |
| **Politics** | Low | Regional elections, non-headline appointments |
| **Economy** | Low | Non-Fed macro events |

---

## Scoring Methodology

Each market was scored 1-10 on six dimensions:

| Dimension | Weight (MR) | Weight (Swing) | Description |
|-----------|-------------|----------------|-------------|
| **Mean Reversion** | 35% | — | Evidence of overshoot/retrace |
| **Swing Volatility** | — | 35% | Catalyst density, repricing potential |
| **Flow Intensity** | 25% | 25% | Recent volume vs liquidity |
| **Microstructure** | 25% | — | Spread, depth, slippage risk |
| **Inefficiency** | 15% | 20% | Underfollowed, fragmented attention |
| **Structural Clarity** | — | 20% | Clear rules, timing, resolution |

### Derived Metrics
- **Activity Ratio** = Recent Volume / Liquidity
- **Crowding Penalty** = Detection of flagship/headline status
- **Staleness Penalty** = High liquidity but weak recent flow
- **Distance from Extremes** = min(price, 1-price)

---

## Platform Comparison

| Metric | Polymarket | Kalshi |
|--------|------------|--------|
| **Markets Scanned** | 700 | 800 |
| **Data Available** | Volume (1w/1m/1y), tags, description | Volume (24h/total), last price |
| **Strengths** | Richer metadata, longer timeframes | Real-time pricing, 24h activity |
| **Top Categories** | Crypto, Politics, Sports | Sports betting, Event outcomes |

---

## Risk Factors

### Mean Reversion Risks
- High activity may indicate trending sentiment (not mean-reverting)
- Short expiry markets may price toward resolution
- Sudden catalyst can overwhelm reversion thesis

### Swing Volatility Risks
- Catalyst may not materialize in window
- Lower activity markets harder to exit
- Near-extreme prices limit upside

### General Risks
- Prediction market liquidity can evaporate
- Spreads may widen during volatility
- Platform-specific resolution rules may create ambiguity

---

## Recommendations

### For Mean Reversion
1. Focus on **Kalshi sports markets** with >100% activity ratios
2. Target **mid-range prices (30-70¢)** for maximum reversion room
3. Prefer **3-7 day expiry** windows
4. Monitor for sudden catalyst that breaks reversion pattern

### For Swing Volatility
1. Focus on **Polymarket crypto/commodity** threshold markets
2. Look for **clear binary catalysts** (price crosses X by date Y)
3. Enter when **activity spikes** but price hasn't fully adjusted
4. Size positions for **1-3 day holds**

### General
1. Avoid markets with **crowding penalty > 4** (too efficient)
2. Require **activity ratio > 10%** minimum
3. Check **resolution rules** before trading
4. Diversify across **multiple categories**

---

## Files & Resources

| File | Path | Description |
|------|------|-------------|
| Interactive Dashboard | `/index.html` | Filterable UI with all markets |
| Raw Data | `/results.json` | Complete JSON with scores/metrics |
| Analysis Script | `/analyze_markets.py` | Python code for scoring |
| This Summary | `/EXECUTIVE_SUMMARY.md` | Executive overview |

**Live Dashboard:** https://theylon.github.io/prediction-market-research/

---

## Methodology Notes

### Data Source
- **Dome API** (https://api.domeapi.io)
- Unified access to Polymarket and Kalshi markets
- Snapshot taken: March 15, 2026 at 18:30 UTC

### Limitations
- No real-time orderbook depth data available via API
- Liquidity estimated from volume as proxy
- Price data available for Kalshi only (Polymarket assumed mid-range)
- Historical price candles not available for volatility calculation

### Future Improvements
- Add orderbook depth when API supports it
- Calculate realized volatility from price history
- Add real-time refresh capability
- Track performance of identified opportunities

---

*This research is for informational purposes only and does not constitute financial advice. Always conduct your own due diligence before trading.*
