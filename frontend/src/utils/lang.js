// Simple heuristic language detection and domain routing for K-SASA

const SW_KEYWORDS = [
  'habari','nisaidie','jinsi','afya','elimu','serikali','tatizo','shule','mwili','ugonjwa','huduma','karibu','msaada','sawa','ndugu','rafiki'
];
const LUO_KEYWORDS = [
  'ani','odhi','ber','mondo','dhi','en ka','nadi','neno','nyathini','tho','rembo','puonj','wuon','dhako','nyathi','kite','bedo'
];
const GIKUYU_KEYWORDS = [
  'mũno','ũndũ','wendo','ũguo','ndirũ','thutha','mũthoni','rũgendo','ndũ','mũciĩ','thayu','kwigua','mũciarwa','ndire','mũgetho'
];

// Sheng cues (informal Swahili/English mix)
const SHENG_KEYWORDS = [
  'nairobi','msee','mrembo','mpangwingwi','mambo','poa','sasa','buda','nimechoka','mafuta','form','niko','sina','tumia','kupull','kuomoka'
];

export function detectLanguage(text) {
  const t = (text || '').toLowerCase();
  const score = (arr) => arr.reduce((s, k) => s + (t.includes(k) ? 1 : 0), 0);

  const sw = score(SW_KEYWORDS);
  const luo = score(LUO_KEYWORDS);
  const kik = score(GIKUYU_KEYWORDS);
  const sheng = score(SHENG_KEYWORDS);

  // Basic alphabet/word cues for English
  const englishLike = /\b(the|and|is|are|you|we|health|school|form|help)\b/i.test(text);

  const total = sw + luo + kik + (englishLike ? 2 : 0) + sheng;
  const pct = (v) => (total > 0 ? v / total : 0);

  if (pct(luo) > 0.6) return 'luo';
  if (pct(kik) > 0.6) return 'kik';
  if (pct(sw) > 0.6) return 'sw';
  if (pct(sheng) > 0.4) return 'sheng';
  if (englishLike) return 'en';

  // Fallback: pick max
  const byScore = [
    { code: 'sw', v: sw },
    { code: 'luo', v: luo },
    { code: 'kik', v: kik },
    { code: 'sheng', v: sheng },
    { code: 'en', v: englishLike ? 2 : 0 },
  ].sort((a, b) => b.v - a.v);
  return byScore[0].code || 'sw';
}

export function normalizeLanguageForReply(code) {
  switch (code) {
    case 'sw': return 'Swahili';
    case 'sheng': return 'Swahili'; // map Sheng to Swahili tone
    case 'luo': return 'Luo';
    case 'kik': return 'Gikuyu';
    default: return 'English';
  }
}

export function mapShengToReplyCode(code) {
  // Sheng leans to Swahili unless strongly English; our heuristic above already biases Swahili
  return code === 'sheng' ? 'sw' : code;
}

export function routeDomain(text) {
  const t = (text || '').toLowerCase();
  // Very simple keyword routing
  const edu = /(lesson|plan|class|teacher|student|exam|curriculum|school|mw\w*|shule|mwalimu|mtihani|puonj|chuo)/i.test(t);
  const health = /(pain|symptom|fever|cough|hospital|clinic|afya|ugonjwa|dalili|dawa|pregnan|mental|nutrition|first aid)/i.test(t);
  const gov = /(id|passport|birth|certificate|kra|ntsa|licen|huduma|serikali|county|permit|business|registration|form|e-citizen|ecitizen)/i.test(t);

  if (health) return 'health';
  if (gov) return 'governance';
  if (edu) return 'education';
  // Default to nearest: education as safe general
  return 'education';
}
