// 社媒平台数据：无 url 且无 qr 的平台在 Social Media 页先隐藏，拿到链接后填入 url 即显示。
// 阿语简介为 AI 翻译，待用户校对（见 AGENTS.md §7）。
export interface SocialPlatform {
  id: string;
  icon: 'wechat' | 'channels' | 'bilibili' | 'youtube' | 'x' | 'linkedin' | 'weibo';
  name: string;
  handle?: string;
  url?: string;
  qr?: string;
  descEn: string;
  descZh: string;
  descAr: string;
}

export const socials: SocialPlatform[] = [
  {
    id: 'wechat',
    icon: 'wechat',
    name: 'WeChat 微信公众号',
    handle: '文晶Talk',
    qr: '/images/wenjing-talk-qr.jpg',
    descEn: 'Flagship column: long-form analysis on Middle East politics and international communication.',
    descZh: '主阵地：中东政治与国际传播深度长文。',
    descAr: 'المنصة الرئيسية: تحليلات معمّقة حول سياسات الشرق الأوسط والتواصل الدولي.',
  },
  {
    id: 'channels',
    icon: 'channels',
    name: 'WeChat Channels 视频号',
    handle: '文晶Talk',
    descEn: 'Short video commentary and event highlights.',
    descZh: '短视频评论与活动集锦。',
    descAr: 'تعليقات مرئية قصيرة ومقتطفات من الفعاليات.',
  },
  {
    id: 'bilibili',
    icon: 'bilibili',
    name: 'Bilibili 哔哩哔哩',
    handle: '文晶Talk',
    descEn: 'Lectures, forum talks and interview replays in Chinese.',
    descZh: '讲座、论坛发言与采访回放（中文）。',
    descAr: 'محاضرات وكلمات في منتديات وإعادات مقابلات بالصينية.',
  },
  {
    id: 'youtube',
    icon: 'youtube',
    name: 'YouTube',
    descEn: 'English-language interviews and international forum videos.',
    descZh: '英文采访与国际论坛视频。',
    descAr: 'مقابلات بالإنجليزية وفيديوهات المنتديات الدولية.',
  },
  {
    id: 'weibo',
    icon: 'weibo',
    name: 'Weibo 微博',
    handle: '文晶Talk',
    url: 'https://weibo.com/u/1969913095',
    descEn: 'Commentary and updates for a Chinese-speaking audience.',
    descZh: '面向中文读者的评论与动态。',
    descAr: 'تعليقات ومستجدات للجمهور الناطق بالصينية.',
  },
  {
    id: 'x',
    icon: 'x',
    name: 'X (Twitter)',
    handle: '@JingWenOxford',
    url: 'https://x.com/JingWenOxford',
    descEn: 'Real-time commentary on breaking Middle East news.',
    descZh: '中东突发新闻的即时评论。',
    descAr: 'تعليقات فورية على أخبار الشرق الأوسط العاجلة.',
  },
  {
    id: 'linkedin',
    icon: 'linkedin',
    name: 'LinkedIn',
    handle: 'Jodie Wen 文晶',
    url: 'https://www.linkedin.com/in/jodie-wen-文晶-1a2606387',
    descEn: 'Professional updates, publications and speaking engagements.',
    descZh: '职业动态、发表与演讲信息。',
    descAr: 'مستجدات مهنية ومنشورات ومشاركات في فعاليات.',
  },
];
