// 媒体英文名 → 中文名映射（中文页面显示用）；未收录的英文名原样显示
export const outletZh: Record<string, string> = {
  'South China Morning Post': '南华早报',
  CGTN: 'CGTN',
  'CGTN Radio': 'CGTN 广播',
  Berlingske: '贝林时报',
  'China Review News': '中评社',
  'China News Service': '中国新闻网',
  'Institute for Peace & Diplomacy': '加拿大和平外交研究所（IPD）',
  'Phoenix TV': '凤凰卫视',
  'Hubei TV': '湖北卫视',
  'CISS China Forum': 'CISS 中国论坛',
  'China-US Focus': '中美聚焦',
};

export const outletSlug = (s: string) =>
  s.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-+|-+$/g, '');

export const outletLabel = (outlet: string, locale: 'en' | 'zh' | 'ar') =>
  locale === 'zh' ? (outletZh[outlet] ?? outlet) : outlet;
