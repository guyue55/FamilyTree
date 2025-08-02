/**
 * 日期时间工具函数
 * 提供统一的日期时间处理功能
 *
 * @author 古月
 * @version 1.0.0
 */

/**
 * 日期格式常量
 */
export const DATE_FORMATS = {
  DATE: 'YYYY-MM-DD',
  TIME: 'HH:mm:ss',
  DATETIME: 'YYYY-MM-DD HH:mm:ss',
  DATETIME_SHORT: 'YYYY-MM-DD HH:mm',
  MONTH: 'YYYY-MM',
  YEAR: 'YYYY',
  CHINESE_DATE: 'YYYY年MM月DD日',
  CHINESE_DATETIME: 'YYYY年MM月DD日 HH:mm:ss',
  ISO: 'YYYY-MM-DDTHH:mm:ss.sssZ'
} as const

/**
 * 时间单位常量（毫秒）
 */
export const TIME_UNITS = {
  SECOND: 1000,
  MINUTE: 60 * 1000,
  HOUR: 60 * 60 * 1000,
  DAY: 24 * 60 * 60 * 1000,
  WEEK: 7 * 24 * 60 * 60 * 1000,
  MONTH: 30 * 24 * 60 * 60 * 1000,
  YEAR: 365 * 24 * 60 * 60 * 1000
} as const

/**
 * 日期类型
 */
export type DateInput = string | number | Date

/**
 * 格式化日期
 * @param date 日期
 * @param format 格式
 */
export function formatDate(date: DateInput, format: string = DATE_FORMATS.DATETIME): string {
  if (!date) return ''

  const d = new Date(date)
  if (isNaN(d.getTime())) return ''

  const year = d.getFullYear()
  const month = String(d.getMonth() + 1).padStart(2, '0')
  const day = String(d.getDate()).padStart(2, '0')
  const hour = String(d.getHours()).padStart(2, '0')
  const minute = String(d.getMinutes()).padStart(2, '0')
  const second = String(d.getSeconds()).padStart(2, '0')
  const millisecond = String(d.getMilliseconds()).padStart(3, '0')

  return format
    .replace(/YYYY/g, String(year))
    .replace(/MM/g, month)
    .replace(/DD/g, day)
    .replace(/HH/g, hour)
    .replace(/mm/g, minute)
    .replace(/ss/g, second)
    .replace(/sss/g, millisecond)
}

/**
 * 解析日期字符串
 * @param dateStr 日期字符串
 */
export function parseDate(dateStr: string): Date | null {
  if (!dateStr) return null

  const date = new Date(dateStr)
  return isNaN(date.getTime()) ? null : date
}

/**
 * 获取相对时间描述
 * @param date 日期
 * @param baseDate 基准日期，默认为当前时间
 */
export function getRelativeTime(date: DateInput, baseDate: DateInput = new Date()): string {
  const targetDate = new Date(date)
  const base = new Date(baseDate)

  if (isNaN(targetDate.getTime()) || isNaN(base.getTime())) {
    return ''
  }

  const diff = base.getTime() - targetDate.getTime()
  const absDiff = Math.abs(diff)
  const isPast = diff > 0

  if (absDiff < TIME_UNITS.MINUTE) {
    return '刚刚'
  } else if (absDiff < TIME_UNITS.HOUR) {
    const minutes = Math.floor(absDiff / TIME_UNITS.MINUTE)
    return isPast ? `${minutes}分钟前` : `${minutes}分钟后`
  } else if (absDiff < TIME_UNITS.DAY) {
    const hours = Math.floor(absDiff / TIME_UNITS.HOUR)
    return isPast ? `${hours}小时前` : `${hours}小时后`
  } else if (absDiff < TIME_UNITS.WEEK) {
    const days = Math.floor(absDiff / TIME_UNITS.DAY)
    return isPast ? `${days}天前` : `${days}天后`
  } else if (absDiff < TIME_UNITS.MONTH) {
    const weeks = Math.floor(absDiff / TIME_UNITS.WEEK)
    return isPast ? `${weeks}周前` : `${weeks}周后`
  } else if (absDiff < TIME_UNITS.YEAR) {
    const months = Math.floor(absDiff / TIME_UNITS.MONTH)
    return isPast ? `${months}个月前` : `${months}个月后`
  } else {
    const years = Math.floor(absDiff / TIME_UNITS.YEAR)
    return isPast ? `${years}年前` : `${years}年后`
  }
}

/**
 * 计算年龄
 * @param birthDate 出生日期
 * @param referenceDate 参考日期，默认为当前日期
 */
export function calculateAge(birthDate: DateInput, referenceDate: DateInput = new Date()): number {
  const birth = new Date(birthDate)
  const reference = new Date(referenceDate)

  if (isNaN(birth.getTime()) || isNaN(reference.getTime())) {
    return 0
  }

  let age = reference.getFullYear() - birth.getFullYear()
  const monthDiff = reference.getMonth() - birth.getMonth()

  if (monthDiff < 0 || (monthDiff === 0 && reference.getDate() < birth.getDate())) {
    age--
  }

  return Math.max(0, age)
}

/**
 * 获取年龄描述
 * @param birthDate 出生日期
 * @param referenceDate 参考日期，默认为当前日期
 */
export function getAgeDescription(
  birthDate: DateInput,
  referenceDate: DateInput = new Date()
): string {
  const age = calculateAge(birthDate, referenceDate)

  if (age === 0) {
    const birth = new Date(birthDate)
    const reference = new Date(referenceDate)
    const monthDiff =
      (reference.getFullYear() - birth.getFullYear()) * 12 + reference.getMonth() - birth.getMonth()

    if (monthDiff < 1) {
      const dayDiff = Math.floor((reference.getTime() - birth.getTime()) / TIME_UNITS.DAY)
      return dayDiff <= 0 ? '新生儿' : `${dayDiff}天`
    } else {
      return `${monthDiff}个月`
    }
  }

  return `${age}岁`
}

/**
 * 判断是否为同一天
 * @param date1 日期1
 * @param date2 日期2
 */
export function isSameDay(date1: DateInput, date2: DateInput): boolean {
  const d1 = new Date(date1)
  const d2 = new Date(date2)

  return (
    d1.getFullYear() === d2.getFullYear() &&
    d1.getMonth() === d2.getMonth() &&
    d1.getDate() === d2.getDate()
  )
}

/**
 * 判断是否为今天
 * @param date 日期
 */
export function isToday(date: DateInput): boolean {
  return isSameDay(date, new Date())
}

/**
 * 判断是否为昨天
 * @param date 日期
 */
export function isYesterday(date: DateInput): boolean {
  const yesterday = new Date()
  yesterday.setDate(yesterday.getDate() - 1)
  return isSameDay(date, yesterday)
}

/**
 * 判断是否为明天
 * @param date 日期
 */
export function isTomorrow(date: DateInput): boolean {
  const tomorrow = new Date()
  tomorrow.setDate(tomorrow.getDate() + 1)
  return isSameDay(date, tomorrow)
}

/**
 * 获取日期范围
 * @param startDate 开始日期
 * @param endDate 结束日期
 */
export function getDateRange(startDate: DateInput, endDate: DateInput): Date[] {
  const start = new Date(startDate)
  const end = new Date(endDate)
  const dates: Date[] = []

  if (start > end) return dates

  const current = new Date(start)
  while (current <= end) {
    dates.push(new Date(current))
    current.setDate(current.getDate() + 1)
  }

  return dates
}

/**
 * 获取月份的天数
 * @param year 年份
 * @param month 月份（0-11）
 */
export function getDaysInMonth(year: number, month: number): number {
  return new Date(year, month + 1, 0).getDate()
}

/**
 * 获取月份的第一天是星期几
 * @param year 年份
 * @param month 月份（0-11）
 */
export function getFirstDayOfMonth(year: number, month: number): number {
  return new Date(year, month, 1).getDay()
}

/**
 * 获取季度
 * @param date 日期
 */
export function getQuarter(date: DateInput): number {
  const d = new Date(date)
  return Math.floor(d.getMonth() / 3) + 1
}

/**
 * 获取周数（一年中的第几周）
 * @param date 日期
 */
export function getWeekOfYear(date: DateInput): number {
  const d = new Date(date)
  const firstDay = new Date(d.getFullYear(), 0, 1)
  const days = Math.floor((d.getTime() - firstDay.getTime()) / TIME_UNITS.DAY)
  return Math.ceil((days + firstDay.getDay() + 1) / 7)
}

/**
 * 添加时间
 * @param date 日期
 * @param amount 数量
 * @param unit 单位
 */
export function addTime(date: DateInput, amount: number, unit: keyof typeof TIME_UNITS): Date {
  const d = new Date(date)
  d.setTime(d.getTime() + amount * TIME_UNITS[unit])
  return d
}

/**
 * 减去时间
 * @param date 日期
 * @param amount 数量
 * @param unit 单位
 */
export function subtractTime(date: DateInput, amount: number, unit: keyof typeof TIME_UNITS): Date {
  return addTime(date, -amount, unit)
}

/**
 * 获取时间戳
 * @param date 日期，默认为当前时间
 */
export function getTimestamp(date: DateInput = new Date()): number {
  return new Date(date).getTime()
}

/**
 * 从时间戳创建日期
 * @param timestamp 时间戳
 */
export function fromTimestamp(timestamp: number): Date {
  return new Date(timestamp)
}

/**
 * 验证日期格式
 * @param dateStr 日期字符串
 * @param format 期望格式
 */
export function isValidDateFormat(dateStr: string, format: string): boolean {
  if (!dateStr) return false

  // 简单的格式验证
  const formatRegex = format
    .replace(/YYYY/g, '\\d{4}')
    .replace(/MM/g, '\\d{2}')
    .replace(/DD/g, '\\d{2}')
    .replace(/HH/g, '\\d{2}')
    .replace(/mm/g, '\\d{2}')
    .replace(/ss/g, '\\d{2}')

  const regex = new RegExp(`^${formatRegex}$`)
  if (!regex.test(dateStr)) return false

  // 验证日期是否有效
  const date = parseDate(dateStr)
  return date !== null && !isNaN(date.getTime())
}

/**
 * 获取生肖
 * @param year 年份
 */
export function getChineseZodiac(year: number): string {
  const zodiacs = ['鼠', '牛', '虎', '兔', '龙', '蛇', '马', '羊', '猴', '鸡', '狗', '猪']
  return zodiacs[(year - 4) % 12]
}

/**
 * 获取星座
 * @param month 月份（1-12）
 * @param day 日期
 */
export function getConstellation(month: number, day: number): string {
  const constellations = [
    '摩羯座',
    '水瓶座',
    '双鱼座',
    '白羊座',
    '金牛座',
    '双子座',
    '巨蟹座',
    '狮子座',
    '处女座',
    '天秤座',
    '天蝎座',
    '射手座'
  ]

  const dates = [20, 19, 21, 20, 21, 22, 23, 23, 23, 24, 23, 22]

  if (day < dates[month - 1]) {
    return constellations[month - 1]
  } else {
    return constellations[month % 12]
  }
}

/**
 * 格式化持续时间
 * @param milliseconds 毫秒数
 */
export function formatDuration(milliseconds: number): string {
  if (milliseconds < 0) return '0秒'

  const seconds = Math.floor(milliseconds / 1000)
  const minutes = Math.floor(seconds / 60)
  const hours = Math.floor(minutes / 60)
  const days = Math.floor(hours / 24)

  if (days > 0) {
    return `${days}天${hours % 24}小时${minutes % 60}分钟`
  } else if (hours > 0) {
    return `${hours}小时${minutes % 60}分钟`
  } else if (minutes > 0) {
    return `${minutes}分钟${seconds % 60}秒`
  } else {
    return `${seconds}秒`
  }
}
