class WatchlistConstants {
  static const Set<String> starStocks = {
    "JBMA", "APOLLO", "DIXON", "LLOYDSME", "PREMIERENE", "GRANULES", "BSE", "GVT&D",
    "GRSE", "M&M", "LLOYDSENGG", "GRAVITA", "EMVEE", "TRANSRAIL", "ASHOKLEY",
    "CONCORDBIO", "OBEROIRLTY", "LICI", "NATIONALUM", "TITAGARH", "ETERNAL",
    "UNOMINDA", "JKPAPER"
  };

  static const Set<String> master35 = {
    "EMVEE", "GENUSPOWER", "DIXON", "OBEROIRLTY", "PREMIERENE", "NATIONALUM", "BSE",
    "LLOYDSME", "TRANSRAIL", "SAGILITY", "GRANULES", "ANANTRAJ", "BELRISE", "MAZDOCK",
    "M&M", "GRSE", "MCX", "KALYANKJIL", "NETWEB", "PVRINOX", "BRIGADE", "ASHOKLEY",
    "ETERNAL", "TITAGARH", "GVT&D", "LICI", "CONCORDBIO", "GRAVITA", "HINDALCO",
    "APOLLO", "JBMA", "JKPAPER", "CDSL", "UNOMINDA", "LLOYDSENGG"
  };

  static const Set<String> activeCore = {
    "EMVEE", "GENUSPOWER", "DIXON", "OBEROIRLTY", "PREMIERENE", "NATIONALUM", "BSE",
    "LLOYDSME", "TRANSRAIL", "SAGILITY", "GRANULES", "ANANTRAJ", "BELRISE", "MAZDOCK",
    "M&M", "GRSE"
  };

  static const Set<String> readyToBuy = {
    "EMVEE", "GENUSPOWER", "DIXON", "OBEROIRLTY", "NATIONALUM", "BSE", "LLOYDSME",
    "GRANULES", "ANANTRAJ", "MAZDOCK"
  };

  static const Set<String> waitAlert = {
    "PREMIERENE", "TRANSRAIL", "SAGILITY", "BELRISE", "M&M", "GRSE"
  };

  static const Set<String> favorites = {
    "MCX", "KALYANKJIL", "NETWEB", "PVRINOX", "BRIGADE"
  };

  static const Set<String> quarantine = {
    "ASHOKLEY", "ETERNAL", "TITAGARH", "GVT&D", "LICI", "CONCORDBIO", "GRAVITA", "HINDALCO"
  };

  static const Set<String> eliminated = {
    "APOLLO", "JBMA", "JKPAPER", "CDSL", "UNOMINDA", "LLOYDSENGG"
  };

  static const List<String> allSectors = [
    "All Sectors",
    "Automobiles & Auto Components",
    "Banking & Financial Services (BFSI)",
    "Capital Markets & Exchanges",
    "Cement & Building Materials",
    "Chemicals, Petrochemicals & Specialty Chem",
    "Consumer Electronics & EMS",
    "Consumer Internet & E-Commerce Platforms",
    "Defence, Aerospace & Strategic Tech",
    "Diversified Industrial Manufacturing",
    "FMCG, Food & Quick-Service Restaurants",
    "IT, Software & Cloud Technologies",
    "Infrastructure, EPC & Ports",
    "Media & Entertainment",
    "Metals, Mining & Steel",
    "Oil, Gas & Petrochemicals",
    "Pharmaceuticals & Healthcare",
    "Power & Electrical Equipment",
    "Railways & Mass Transit",
    "Real Estate & Urban Development",
    "Renewable Energy & Green Power",
    "Retail, Apparel & Consumer Brands",
    "Telecommunications, 5G & Media"
  ];
}

class StrategyPreset {
  final String key;
  final String label;
  final String icon;
  final String tooltip;

  const StrategyPreset({
    required this.key,
    required this.label,
    required this.icon,
    required this.tooltip,
  });
}

const List<StrategyPreset> kStrategyPresets = [
  StrategyPreset(key: 'ALL', label: 'All Strategies', icon: '🌐', tooltip: 'No preset filter'),
  StrategyPreset(key: '1D_GAINERS', label: '1D Gainers (≥ +1.5%)', icon: '🚀', tooltip: 'Strong intraday positive price action'),
  StrategyPreset(key: '1D_DIPS', label: '1D Dips (≤ -1.0%)', icon: '🔻', tooltip: 'Intraday pullbacks & potential dip-buy levels'),
  StrategyPreset(key: '1W_LEADERS', label: '1W Leaders (≥ +4.0%)', icon: '⚡', tooltip: 'Strong multi-session weekly momentum'),
  StrategyPreset(key: 'MASTER_ALPHA', label: 'Master Alpha (≥ 88)', icon: '🌟', tooltip: 'Top tier overall institutional composite score'),
  StrategyPreset(key: 'TRIPLE_CROWN', label: 'Triple-Crown (≥ 88)', icon: '👑', tooltip: 'Elite Fundamental + Technical + Sentiment alignment'),
  StrategyPreset(key: 'HIGH_FORECAST', label: 'High Forecast (≥ +20%)', icon: '🚀', tooltip: 'Over 20% consensus upside to 1-year target'),
  StrategyPreset(key: 'MOD_FORECAST', label: 'Mod Forecast (+10% to +20%)', icon: '🎯', tooltip: 'Balanced 10-20% analyst price target upside'),
  StrategyPreset(key: 'STRONG_BUY', label: 'Strong Buy (≥ 80%)', icon: '⭐', tooltip: '80%+ analyst consensus Buy/Outperform ratings'),
  StrategyPreset(key: 'EUPHORIC_MOOD', label: 'Euphoric Mood (≥ 90)', icon: '🔥', tooltip: 'Extreme institutional accumulation & sentiment'),
  StrategyPreset(key: 'POSITIVE_MOOD', label: 'Positive Mood (75-89)', icon: '🟢', tooltip: 'Solid institutional optimism & sentiment'),
  StrategyPreset(key: 'DIP_BUYS', label: 'Dip Buy at Support', icon: '💎', tooltip: 'High fundamental quality pulling back into support'),
  StrategyPreset(key: 'DEEP_VALUE', label: 'Deep Value (Disc ≥ 20%)', icon: '🌟', tooltip: '20%+ discount to 8-quarter median P/E multiple'),
  StrategyPreset(key: 'FAIR_VALUE', label: 'Fair Accumulate (5%-20%)', icon: '⚖️', tooltip: '5-20% margin of safety to historical valuation'),
  StrategyPreset(key: 'STAGE2_TREND', label: 'Stage 2 Strong Uptrend', icon: '🚀', tooltip: 'Minervini Stage 2 structural uptrend above 50 & 200 DMA'),
  StrategyPreset(key: 'RSI_BULL', label: 'Bullish RSI (50-65)', icon: '☑️', tooltip: 'Sweet spot RSI momentum accumulation range'),
  StrategyPreset(key: 'RSI_OVERSOLD', label: 'Oversold (RSI < 40)', icon: '❄️', tooltip: 'Oversold oscillator levels due for mean reversion'),
  StrategyPreset(key: 'BREAKOUT_52W', label: '52W High Breakout (< -10%)', icon: '⛰️', tooltip: 'Within 10% of all-time / 52-week high'),
  StrategyPreset(key: 'HYPER_GROWTH', label: 'YoY PAT Hyper-Growth (> 50%)', icon: '⚡', tooltip: 'Over 50% year-over-year net profit growth'),
  StrategyPreset(key: 'PROFIT_STREAKS', label: 'Growth Streaks (≥ 3 Qtrs)', icon: '🏆', tooltip: 'At least 3 consecutive quarters of profit compounding'),
  StrategyPreset(key: 'VOL_SURGE', label: 'Vol Surge (> 1.5x)', icon: '🔥', tooltip: 'Over 1.5x 20-day average trading volume'),
  StrategyPreset(key: 'HIGH_RR', label: 'High R:R (≥ 1:2.5)', icon: '🎯', tooltip: 'Favorable Risk-to-Reward ratio of 1:2.5 or better'),
  StrategyPreset(key: 'LARGE_QUALITY', label: 'Large-Cap Quality', icon: '🏢', tooltip: 'Established large-cap blue-chip equities'),
  StrategyPreset(key: 'MID_COMPOUNDERS', label: 'Mid-Cap Compounders', icon: '🚀', tooltip: 'High-growth mid-cap market leaders'),
  StrategyPreset(key: 'SMALL_MICRO', label: 'Small & Micro Cap Alpha', icon: '💎', tooltip: 'Emerging micro and small-cap alpha opportunities'),
  StrategyPreset(key: 'INTRADAY_RADAR', label: 'Intraday Radar Setup', icon: '⚡', tooltip: 'High tech score with volume surge for day trading'),
  StrategyPreset(key: 'SWING_RADAR', label: 'Swing Radar Setup', icon: '🚀', tooltip: 'High tech score with minimum 2.0x R:R ratio'),
  StrategyPreset(key: 'PERFECT_RADAR', label: 'Perfect Radar Setup', icon: '🎯', tooltip: 'Elite 85+ tech score, 80%+ win-rate, 2.5x R:R'),
];
