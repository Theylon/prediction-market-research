#!/usr/bin/env python3
"""
Prediction Market Research Agent
Analyzes Polymarket and Kalshi markets for short-horizon trading opportunities
"""

import json
import os
from datetime import datetime, timezone
from typing import Dict, List, Tuple
import math

# Load market data
def load_json_files(pattern: str) -> List[dict]:
    """Load all JSON files matching pattern"""
    markets = []
    for i in range(0, 900, 100):
        filepath = f"/tmp/{pattern}_{i}.json"
        if os.path.exists(filepath):
            try:
                with open(filepath, 'r') as f:
                    data = json.load(f)
                    if 'markets' in data:
                        markets.extend(data['markets'])
            except:
                pass
    return markets

# Flagship/headline market detection keywords
FLAGSHIP_KEYWORDS = [
    # Presidential/major elections
    'presidential election', 'president 2028', 'president 2024', 'trump win', 'biden win',
    'democratic nominee', 'republican nominee', 'electoral college',
    # Fed/Macro
    'fed interest rates', 'fomc', 'federal reserve', 'cpi', 'inflation rate',
    'nonfarm payroll', 'unemployment rate', 'gdp growth',
    # Major sports championships
    'super bowl', 'nba finals', 'world series', 'champions league final',
    'world cup final', 'stanley cup', 'championship game',
    # Other obvious headlines
    'recession in 2025', 'recession in 2026', 'government shutdown',
]

FLAGSHIP_TAGS = [
    'fed', 'cpi', 'nfp', 'fomc', 'presidential', 'superbowl', 'super bowl',
    'nba finals', 'world series', 'fed rates',
]

def is_flagship_market(market: dict) -> Tuple[bool, float]:
    """
    Detect if market is a flagship/headline market
    Returns (is_flagship, penalty_score)
    """
    title = market.get('title', '').lower()
    tags = [t.lower() for t in market.get('tags', [])]
    
    penalty = 0.0
    
    # Check title keywords
    for keyword in FLAGSHIP_KEYWORDS:
        if keyword in title:
            penalty += 3.0
    
    # Check tags
    for tag in FLAGSHIP_TAGS:
        if tag in tags:
            penalty += 1.5
    
    # High volume penalty (over $50M is likely flagship)
    volume = market.get('volume_total', market.get('volume', 0)) or 0
    if volume > 100_000_000:
        penalty += 4.0
    elif volume > 50_000_000:
        penalty += 2.0
    elif volume > 20_000_000:
        penalty += 1.0
    
    # Specific pattern detection
    if 'fed' in title and ('rate' in title or 'interest' in title):
        penalty += 5.0
    if 'presidential' in title and 'election' in title:
        penalty += 5.0
    if 'super bowl' in title or 'superbowl' in title:
        penalty += 4.0
    
    is_flagship = penalty >= 3.0
    return is_flagship, min(penalty, 10.0)

def calculate_hours_to_expiry(end_time: int) -> float:
    """Calculate hours until market expiry"""
    if not end_time:
        return float('inf')
    now = datetime.now(timezone.utc).timestamp()
    hours = (end_time - now) / 3600
    return max(0, hours)

def calculate_activity_ratio(market: dict, platform: str) -> float:
    """Calculate activity ratio (recent volume / total volume)"""
    if platform == 'polymarket':
        week_vol = market.get('volume_1_week', 0) or 0
        total_vol = market.get('volume_total', 0) or 1
        return week_vol / total_vol
    else:  # kalshi
        vol_24h = market.get('volume_24h', 0) or 0
        total_vol = market.get('volume', 0) or 1
        return (vol_24h * 7) / total_vol  # Annualize to weekly equivalent

def calculate_staleness_penalty(market: dict, platform: str) -> float:
    """Penalize markets with low recent activity relative to total volume"""
    activity_ratio = calculate_activity_ratio(market, platform)
    if activity_ratio < 0.01:
        return 5.0
    elif activity_ratio < 0.05:
        return 3.0
    elif activity_ratio < 0.1:
        return 1.5
    return 0.0

def estimate_liquidity(market: dict, platform: str) -> float:
    """
    Estimate liquidity from available data
    Using volume as proxy since orderbook data not available
    """
    if platform == 'polymarket':
        # Use weekly volume as liquidity proxy
        return market.get('volume_1_week', 0) or 0
    else:  # kalshi
        # Use 24h volume * 3 as liquidity estimate
        return (market.get('volume_24h', 0) or 0) * 3

def calculate_distance_from_extremes(price: float) -> float:
    """Calculate how far price is from 0 or 1"""
    if price is None:
        return 0.5  # Assume mid-range if unknown
    return min(price / 100, 1 - price / 100)

def score_mean_reversion(market: dict, platform: str, metrics: dict) -> float:
    """Score market for mean reversion suitability (1-10)"""
    score = 5.0  # Base score
    
    # Activity ratio boost - high churn good for mean reversion
    activity = metrics['activity_ratio']
    if activity > 0.3:
        score += 2.0
    elif activity > 0.15:
        score += 1.0
    
    # Distance from extremes - mid-range prices better
    dist = metrics['distance_from_extremes']
    if dist > 0.3:
        score += 1.5
    elif dist > 0.2:
        score += 0.5
    elif dist < 0.1:
        score -= 2.0
    
    # Time to expiry - not too close, not too far
    hours = metrics['hours_to_expiry']
    if 12 <= hours <= 168:  # 12 hours to 7 days
        score += 1.0
    elif hours < 6:
        score -= 1.5
    elif hours > 720:  # > 30 days
        score -= 0.5
    
    # Penalize flagships
    score -= metrics['crowding_penalty'] * 0.3
    
    # Penalize staleness
    score -= metrics['staleness_penalty'] * 0.5
    
    return max(1, min(10, score))

def score_swing_volatility(market: dict, platform: str, metrics: dict) -> float:
    """Score market for 1-3 day swing volatility (1-10)"""
    score = 5.0
    
    # Activity is key
    activity = metrics['activity_ratio']
    if activity > 0.25:
        score += 2.5
    elif activity > 0.1:
        score += 1.5
    elif activity < 0.05:
        score -= 1.5
    
    # Liquidity sweet spot
    liq = metrics['liquidity']
    if 200_000 <= liq <= 2_000_000:
        score += 1.5
    elif 100_000 <= liq <= 5_000_000:
        score += 0.5
    
    # Time to expiry - 1-14 days ideal for swing
    hours = metrics['hours_to_expiry']
    if 24 <= hours <= 336:
        score += 1.5
    elif hours < 12:
        score -= 1.0
    
    # Distance from extremes
    dist = metrics['distance_from_extremes']
    if dist > 0.25:
        score += 1.0
    elif dist < 0.15:
        score -= 1.0
    
    # Penalize flagships
    score -= metrics['crowding_penalty'] * 0.4
    
    return max(1, min(10, score))

def score_flow_intensity(market: dict, platform: str, metrics: dict) -> float:
    """Score market for flow intensity (1-10)"""
    score = 5.0
    
    activity = metrics['activity_ratio']
    if activity > 0.4:
        score += 3.0
    elif activity > 0.2:
        score += 2.0
    elif activity > 0.1:
        score += 1.0
    elif activity < 0.03:
        score -= 2.0
    
    # Recent volume absolute
    if platform == 'polymarket':
        week_vol = market.get('volume_1_week', 0) or 0
        if week_vol > 1_000_000:
            score += 1.5
        elif week_vol > 500_000:
            score += 1.0
    else:
        vol_24h = market.get('volume_24h', 0) or 0
        if vol_24h > 100_000:
            score += 1.5
        elif vol_24h > 50_000:
            score += 1.0
    
    return max(1, min(10, score))

def score_microstructure(market: dict, platform: str, metrics: dict) -> float:
    """Score market for microstructure quality (1-10)"""
    score = 5.0
    
    # Without orderbook data, estimate from activity
    activity = metrics['activity_ratio']
    if activity > 0.2:
        score += 2.0  # Active markets tend to have better books
    elif activity > 0.1:
        score += 1.0
    
    # Liquidity proxy
    liq = metrics['liquidity']
    if liq > 500_000:
        score += 1.5
    elif liq > 200_000:
        score += 0.5
    elif liq < 100_000:
        score -= 1.5
    
    # Distance from extremes affects spread
    dist = metrics['distance_from_extremes']
    if dist > 0.3:
        score += 1.0  # Mid-range prices usually tighter
    elif dist < 0.1:
        score -= 1.0  # Near extremes often wider
    
    return max(1, min(10, score))

def score_inefficiency(market: dict, platform: str, metrics: dict) -> float:
    """Score market for long-tail inefficiency (1-10)"""
    score = 5.0
    
    # Anti-flagship score
    if not metrics['is_flagship']:
        score += 2.5
    score -= metrics['crowding_penalty'] * 0.5
    
    # Medium liquidity sweet spot (not too big, not too small)
    liq = metrics['liquidity']
    if 150_000 <= liq <= 1_000_000:
        score += 2.0
    elif 100_000 <= liq <= 3_000_000:
        score += 1.0
    elif liq > 5_000_000:
        score -= 1.0
    
    # High activity relative to attention
    activity = metrics['activity_ratio']
    if activity > 0.2 and not metrics['is_flagship']:
        score += 1.5
    
    return max(1, min(10, score))

def score_structural_clarity(market: dict, platform: str, metrics: dict) -> float:
    """Score market for structural clarity (1-10)"""
    score = 6.0  # Base assumption of decent clarity
    
    # Has clear end time
    if metrics['hours_to_expiry'] < float('inf'):
        score += 1.0
    
    # Description length (longer = more detailed rules)
    desc = market.get('description', '') or ''
    if len(desc) > 500:
        score += 1.0
    elif len(desc) < 100:
        score -= 1.0
    
    # Has resolution source
    if market.get('resolution_source') or 'resolution' in desc.lower():
        score += 1.0
    
    return max(1, min(10, score))

def analyze_market(market: dict, platform: str) -> dict:
    """Full analysis of a single market"""
    
    # Calculate all metrics
    is_flag, crowd_pen = is_flagship_market(market)
    
    # Price handling
    if platform == 'kalshi':
        price = market.get('last_price', 50)
    else:
        price = 50  # Assume mid-range for Polymarket without price data
    
    metrics = {
        'hours_to_expiry': calculate_hours_to_expiry(market.get('end_time')),
        'activity_ratio': calculate_activity_ratio(market, platform),
        'liquidity': estimate_liquidity(market, platform),
        'distance_from_extremes': calculate_distance_from_extremes(price),
        'crowding_penalty': crowd_pen,
        'staleness_penalty': calculate_staleness_penalty(market, platform),
        'is_flagship': is_flag,
        'price': price,
    }
    
    # Score all dimensions
    scores = {
        'mean_reversion': score_mean_reversion(market, platform, metrics),
        'swing_volatility': score_swing_volatility(market, platform, metrics),
        'flow_intensity': score_flow_intensity(market, platform, metrics),
        'microstructure': score_microstructure(market, platform, metrics),
        'inefficiency': score_inefficiency(market, platform, metrics),
        'structural_clarity': score_structural_clarity(market, platform, metrics),
    }
    
    # Composite scores
    scores['mean_reversion_composite'] = (
        scores['mean_reversion'] * 0.35 +
        scores['flow_intensity'] * 0.25 +
        scores['microstructure'] * 0.25 +
        scores['inefficiency'] * 0.15
    )
    
    scores['swing_composite'] = (
        scores['swing_volatility'] * 0.35 +
        scores['flow_intensity'] * 0.25 +
        scores['inefficiency'] * 0.20 +
        scores['structural_clarity'] * 0.20
    )
    
    return {
        'market': market,
        'platform': platform,
        'metrics': metrics,
        'scores': scores,
    }

def passes_filters(analysis: dict) -> Tuple[bool, str]:
    """Check if market passes hard filters. Returns (passes, reason)"""
    m = analysis['metrics']
    market = analysis['market']
    
    # Status must be open
    if market.get('status') != 'open':
        return False, "Market not open"
    
    # Liquidity bounds
    liq = m['liquidity']
    if liq < 100_000:
        return False, f"Liquidity too low (${liq:,.0f})"
    if liq > 5_000_000:
        return False, f"Liquidity too high (${liq:,.0f})"
    
    # Activity filter
    if m['activity_ratio'] < 0.02:
        return False, f"Stale market (activity ratio: {m['activity_ratio']:.1%})"
    
    # Staleness penalty
    if m['staleness_penalty'] >= 4.0:
        return False, "High staleness penalty"
    
    return True, ""

def get_exclusion_reason(analysis: dict) -> str:
    """Get detailed exclusion reason"""
    m = analysis['metrics']
    market = analysis['market']
    
    reasons = []
    
    if m['activity_ratio'] < 0.05:
        reasons.append("Weak recent activity")
    
    if m['is_flagship'] and m['crowding_penalty'] > 4:
        reasons.append("Over-crowded headline market")
    
    if m['staleness_penalty'] > 2:
        reasons.append("Stale order book")
    
    if m['distance_from_extremes'] < 0.05:
        reasons.append("Near terminal pricing")
    
    hours = m['hours_to_expiry']
    if hours < 2:
        reasons.append("Too close to expiry")
    
    return "; ".join(reasons) if reasons else "Multiple factors"

def format_volume(v: float) -> str:
    """Format volume as human readable"""
    if v >= 1_000_000:
        return f"${v/1_000_000:.2f}M"
    elif v >= 1_000:
        return f"${v/1_000:.1f}K"
    else:
        return f"${v:.0f}"

def format_hours(h: float) -> str:
    """Format hours as human readable"""
    if h == float('inf'):
        return "N/A"
    elif h < 24:
        return f"{h:.1f}h"
    elif h < 168:
        return f"{h/24:.1f}d"
    else:
        return f"{h/168:.1f}w"

def main():
    print("Loading market data...")
    
    # Load all markets
    poly_markets = load_json_files('poly')
    kalshi_markets = load_json_files('kalshi')
    
    print(f"Loaded {len(poly_markets)} Polymarket markets")
    print(f"Loaded {len(kalshi_markets)} Kalshi markets")
    
    # Analyze all markets
    print("\nAnalyzing markets...")
    all_analyses = []
    
    for market in poly_markets:
        analysis = analyze_market(market, 'polymarket')
        all_analyses.append(analysis)
    
    for market in kalshi_markets:
        analysis = analyze_market(market, 'kalshi')
        all_analyses.append(analysis)
    
    # Filter and categorize
    passing = []
    excluded = []
    
    for analysis in all_analyses:
        passes, reason = passes_filters(analysis)
        if passes:
            # Additional flagship exclusion for top tier
            if analysis['metrics']['crowding_penalty'] > 6:
                excluded.append({
                    'analysis': analysis,
                    'reason': "Flagship/headline market"
                })
            else:
                passing.append(analysis)
        else:
            excluded.append({
                'analysis': analysis,
                'reason': reason
            })
    
    print(f"\nMarkets passing filters: {len(passing)}")
    print(f"Markets excluded: {len(excluded)}")
    
    # Sort by composite scores
    mean_reversion_ranked = sorted(passing, key=lambda x: x['scores']['mean_reversion_composite'], reverse=True)
    swing_ranked = sorted(passing, key=lambda x: x['scores']['swing_composite'], reverse=True)
    
    # Generate output
    results = {
        'generated_at': datetime.now(timezone.utc).isoformat(),
        'summary': {
            'total_polymarket': len(poly_markets),
            'total_kalshi': len(kalshi_markets),
            'passing_filters': len(passing),
            'excluded': len(excluded),
        },
        'mean_reversion_candidates': [],
        'swing_candidates': [],
        'excluded_markets': [],
    }
    
    # Top mean reversion candidates
    for i, analysis in enumerate(mean_reversion_ranked[:20]):
        m = analysis['market']
        metrics = analysis['metrics']
        scores = analysis['scores']
        platform = analysis['platform']
        
        if platform == 'polymarket':
            recent_vol = m.get('volume_1_week', 0)
            total_vol = m.get('volume_total', 0)
            identifier = m.get('market_slug', '')
        else:
            recent_vol = m.get('volume_24h', 0) * 7
            total_vol = m.get('volume', 0)
            identifier = m.get('market_ticker', '')
        
        entry = {
            'rank': i + 1,
            'title': m.get('title', 'Unknown'),
            'platform': platform.capitalize(),
            'identifier': identifier,
            'liquidity': format_volume(metrics['liquidity']),
            'liquidity_raw': metrics['liquidity'],
            'recent_volume': format_volume(recent_vol),
            'recent_volume_raw': recent_vol,
            'total_volume': format_volume(total_vol),
            'last_price': metrics['price'],
            'time_to_expiry': format_hours(metrics['hours_to_expiry']),
            'hours_to_expiry': metrics['hours_to_expiry'],
            'activity_ratio': f"{metrics['activity_ratio']:.1%}",
            'activity_ratio_raw': metrics['activity_ratio'],
            'why_suitable': generate_mean_reversion_rationale(analysis),
            'main_risk': generate_mean_reversion_risk(analysis),
            'scores': {k: round(v, 1) for k, v in scores.items()},
            'final_score': round(scores['mean_reversion_composite'], 2),
            'tags': m.get('tags', [])[:5],
            'description': (m.get('description', '') or '')[:300] + '...' if len(m.get('description', '') or '') > 300 else m.get('description', ''),
        }
        results['mean_reversion_candidates'].append(entry)
    
    # Top swing candidates
    for i, analysis in enumerate(swing_ranked[:20]):
        m = analysis['market']
        metrics = analysis['metrics']
        scores = analysis['scores']
        platform = analysis['platform']
        
        if platform == 'polymarket':
            recent_vol = m.get('volume_1_week', 0)
            total_vol = m.get('volume_total', 0)
            identifier = m.get('market_slug', '')
        else:
            recent_vol = m.get('volume_24h', 0) * 7
            total_vol = m.get('volume', 0)
            identifier = m.get('market_ticker', '')
        
        entry = {
            'rank': i + 1,
            'title': m.get('title', 'Unknown'),
            'platform': platform.capitalize(),
            'identifier': identifier,
            'liquidity': format_volume(metrics['liquidity']),
            'liquidity_raw': metrics['liquidity'],
            'recent_volume': format_volume(recent_vol),
            'recent_volume_raw': recent_vol,
            'total_volume': format_volume(total_vol),
            'last_price': metrics['price'],
            'time_to_expiry': format_hours(metrics['hours_to_expiry']),
            'hours_to_expiry': metrics['hours_to_expiry'],
            'activity_ratio': f"{metrics['activity_ratio']:.1%}",
            'activity_ratio_raw': metrics['activity_ratio'],
            'catalyst': generate_swing_catalyst(analysis),
            'why_suitable': generate_swing_rationale(analysis),
            'main_risk': generate_swing_risk(analysis),
            'scores': {k: round(v, 1) for k, v in scores.items()},
            'final_score': round(scores['swing_composite'], 2),
            'tags': m.get('tags', [])[:5],
            'description': (m.get('description', '') or '')[:300] + '...' if len(m.get('description', '') or '') > 300 else m.get('description', ''),
        }
        results['swing_candidates'].append(entry)
    
    # Excluded markets (sample)
    excluded_sorted = sorted(excluded, key=lambda x: x['analysis']['metrics']['liquidity'], reverse=True)
    for ex in excluded_sorted[:30]:
        analysis = ex['analysis']
        m = analysis['market']
        metrics = analysis['metrics']
        platform = analysis['platform']
        
        entry = {
            'title': m.get('title', 'Unknown'),
            'platform': platform.capitalize(),
            'liquidity': format_volume(metrics['liquidity']),
            'reason': ex['reason'],
            'details': get_exclusion_reason(analysis),
        }
        results['excluded_markets'].append(entry)
    
    # Save results
    with open('/Users/eylon/Claude/prediction-markets/results.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\nResults saved to results.json")
    return results

def generate_mean_reversion_rationale(analysis: dict) -> str:
    """Generate rationale for mean reversion suitability"""
    m = analysis['metrics']
    reasons = []
    
    if m['activity_ratio'] > 0.2:
        reasons.append("High trading activity relative to market size indicates active price discovery")
    elif m['activity_ratio'] > 0.1:
        reasons.append("Moderate activity suggests regular flow")
    
    if m['distance_from_extremes'] > 0.25:
        reasons.append("Price in mid-range zone allows room for reversals")
    
    if 24 <= m['hours_to_expiry'] <= 168:
        reasons.append("Timeframe suits intraday/multi-day mean reversion")
    
    if not m['is_flagship']:
        reasons.append("Not a crowded headline market - less efficient pricing")
    
    return "; ".join(reasons) if reasons else "Meets baseline criteria for mean reversion"

def generate_mean_reversion_risk(analysis: dict) -> str:
    """Generate main risk for mean reversion"""
    m = analysis['metrics']
    
    if m['hours_to_expiry'] < 24:
        return "Short time to expiry may cause price to trend toward resolution"
    if m['activity_ratio'] > 0.5:
        return "Very high activity could indicate trending sentiment"
    if m['distance_from_extremes'] < 0.15:
        return "Price near extreme may not revert"
    if m['crowding_penalty'] > 3:
        return "Moderate headline attention may reduce inefficiencies"
    
    return "Standard mean reversion risks apply"

def generate_swing_catalyst(analysis: dict) -> str:
    """Identify likely catalyst for swing"""
    m = analysis['market']
    tags = [t.lower() for t in m.get('tags', [])]
    title = m.get('title', '').lower()
    
    catalysts = []
    
    if any(t in tags for t in ['politics', 'elections', 'trump']):
        catalysts.append("Political news/statements")
    if any(t in tags for t in ['sports', 'nba', 'nfl', 'soccer', 'epl']):
        catalysts.append("Game results/injury news")
    if any(t in tags for t in ['economy', 'business', 'crypto']):
        catalysts.append("Economic data/market moves")
    if 'will' in title and ('win' in title or 'be' in title):
        catalysts.append("Event outcome uncertainty")
    
    if analysis['metrics']['hours_to_expiry'] < 72:
        catalysts.append("Near-term resolution approaching")
    
    return "; ".join(catalysts) if catalysts else "General news flow and sentiment shifts"

def generate_swing_rationale(analysis: dict) -> str:
    """Generate rationale for swing suitability"""
    m = analysis['metrics']
    reasons = []
    
    if m['activity_ratio'] > 0.15:
        reasons.append("Active trading suggests ongoing repricing")
    
    if 24 <= m['hours_to_expiry'] <= 336:
        reasons.append("1-14 day window ideal for swing positions")
    
    if not m['is_flagship']:
        reasons.append("Underfollowed market may misprice catalysts")
    
    if m['distance_from_extremes'] > 0.2:
        reasons.append("Price has room to move in either direction")
    
    return "; ".join(reasons) if reasons else "Suitable for multi-day swing trading"

def generate_swing_risk(analysis: dict) -> str:
    """Generate main risk for swing"""
    m = analysis['metrics']
    
    if m['hours_to_expiry'] > 720:
        return "Long time to expiry may result in slow price movement"
    if m['activity_ratio'] < 0.1:
        return "Lower activity may mean difficulty exiting"
    if m['distance_from_extremes'] < 0.15:
        return "Near-extreme price limits upside"
    
    return "Event-driven catalyst risk"

if __name__ == '__main__':
    main()
