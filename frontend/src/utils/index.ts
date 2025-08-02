/**
 * 工具函数统一导出
 *
 * @author 古月
 * @version 1.0.0
 */

// 导出所有工具函数模块
export * from './storage'
export * from './date'
export * from './validation'

import { SYSTEM_CONSTANTS } from '@/constants/system'

/**
 * 防抖函数
 * @param func 要防抖的函数
 * @param delay 延迟时间（毫秒）
 */
export function debounce<T extends (...args: any[]) => any>(
  func: T,
  delay: number
): (...args: Parameters<T>) => void {
  let timeoutId: NodeJS.Timeout | null = null

  return function (...args: Parameters<T>) {
    if (timeoutId) {
      clearTimeout(timeoutId)
    }

    timeoutId = setTimeout(() => func(...args), delay)
  }
}

/**
 * 节流函数
 * @param func 要节流的函数
 * @param delay 延迟时间（毫秒）
 */
export function throttle<T extends (...args: any[]) => any>(
  func: T,
  delay: number
): (...args: Parameters<T>) => void {
  let lastCall = 0

  return function (...args: Parameters<T>) {
    const now = Date.now()
    if (now - lastCall >= delay) {
      lastCall = now
      func(...args)
    }
  }
}

/**
 * 深拷贝
 * @param obj 要拷贝的对象
 */
export function deepClone<T>(obj: T): T {
  if (obj === null || typeof obj !== 'object') {
    return obj
  }

  if (obj instanceof Date) {
    return new Date(obj.getTime()) as T
  }

  if (obj instanceof Array) {
    return obj.map(item => deepClone(item)) as T
  }

  if (typeof obj === 'object') {
    const clonedObj = {} as T
    for (const key in obj) {
      if (obj.hasOwnProperty(key)) {
        clonedObj[key] = deepClone(obj[key])
      }
    }
    return clonedObj
  }

  return obj
}

/**
 * 生成唯一ID
 * @param prefix 前缀
 */
export function generateId(prefix: string = 'id'): string {
  return `${prefix}_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
}

/**
 * 格式化文件大小
 * @param bytes 字节数
 * @param decimals 小数位数
 */
export function formatFileSize(bytes: number, decimals: number = 2): string {
  if (bytes === 0) return '0 Bytes'

  const k = 1024
  const dm = decimals < 0 ? 0 : decimals
  const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB']

  const i = Math.floor(Math.log(bytes) / Math.log(k))

  return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + ' ' + sizes[i]
}

/**
 * 获取文件扩展名
 * @param filename 文件名
 */
export function getFileExtension(filename: string): string {
  return filename.slice(((filename.lastIndexOf('.') - 1) >>> 0) + 2)
}

/**
 * 判断是否为图片文件
 * @param filename 文件名或MIME类型
 */
export function isImageFile(filename: string): boolean {
  const imageExtensions = ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp', 'svg']
  const imageMimeTypes = [
    'image/jpeg',
    'image/png',
    'image/gif',
    'image/bmp',
    'image/webp',
    'image/svg+xml'
  ]

  const ext = getFileExtension(filename).toLowerCase()
  return imageExtensions.includes(ext) || imageMimeTypes.includes(filename.toLowerCase())
}

/**
 * 判断是否为视频文件
 * @param filename 文件名或MIME类型
 */
export function isVideoFile(filename: string): boolean {
  const videoExtensions = ['mp4', 'avi', 'mov', 'wmv', 'flv', 'webm', 'mkv']
  const videoMimeTypes = [
    'video/mp4',
    'video/avi',
    'video/quicktime',
    'video/x-ms-wmv',
    'video/x-flv',
    'video/webm',
    'video/x-matroska'
  ]

  const ext = getFileExtension(filename).toLowerCase()
  return videoExtensions.includes(ext) || videoMimeTypes.includes(filename.toLowerCase())
}

/**
 * 判断是否为音频文件
 * @param filename 文件名或MIME类型
 */
export function isAudioFile(filename: string): boolean {
  const audioExtensions = ['mp3', 'wav', 'flac', 'aac', 'ogg', 'wma']
  const audioMimeTypes = [
    'audio/mpeg',
    'audio/wav',
    'audio/flac',
    'audio/aac',
    'audio/ogg',
    'audio/x-ms-wma'
  ]

  const ext = getFileExtension(filename).toLowerCase()
  return audioExtensions.includes(ext) || audioMimeTypes.includes(filename.toLowerCase())
}

/**
 * 判断是否为文档文件
 * @param filename 文件名或MIME类型
 */
export function isDocumentFile(filename: string): boolean {
  const documentExtensions = ['pdf', 'doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx', 'txt']
  const documentMimeTypes = [
    'application/pdf',
    'application/msword',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    'application/vnd.ms-excel',
    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    'application/vnd.ms-powerpoint',
    'application/vnd.openxmlformats-officedocument.presentationml.presentation',
    'text/plain'
  ]

  const ext = getFileExtension(filename).toLowerCase()
  return documentExtensions.includes(ext) || documentMimeTypes.includes(filename.toLowerCase())
}

/**
 * 对象转查询字符串
 * @param obj 对象
 */
export function objectToQueryString(obj: Record<string, any>): string {
  const params = new URLSearchParams()

  for (const [key, value] of Object.entries(obj)) {
    if (value !== null && value !== undefined && value !== '') {
      if (Array.isArray(value)) {
        value.forEach(item => params.append(key, String(item)))
      } else {
        params.append(key, String(value))
      }
    }
  }

  return params.toString()
}

/**
 * 查询字符串转对象
 * @param queryString 查询字符串
 */
export function queryStringToObject(queryString: string): Record<string, any> {
  const params = new URLSearchParams(queryString)
  const obj: Record<string, any> = {}

  for (const [key, value] of params.entries()) {
    if (obj[key]) {
      if (Array.isArray(obj[key])) {
        obj[key].push(value)
      } else {
        obj[key] = [obj[key], value]
      }
    } else {
      obj[key] = value
    }
  }

  return obj
}

/**
 * 检查值是否为空
 * @param value 值
 */
export function isEmpty(value: any): boolean {
  if (value === null || value === undefined) return true
  if (typeof value === 'string') return value.trim() === ''
  if (Array.isArray(value)) return value.length === 0
  if (typeof value === 'object') return Object.keys(value).length === 0
  return false
}

/**
 * 首字母大写
 * @param str 字符串
 */
export function capitalize(str: string): string {
  if (!str) return ''
  return str.charAt(0).toUpperCase() + str.slice(1).toLowerCase()
}

/**
 * 驼峰转下划线
 * @param str 字符串
 */
export function camelToSnake(str: string): string {
  return str.replace(/[A-Z]/g, letter => `_${letter.toLowerCase()}`)
}

/**
 * 下划线转驼峰
 * @param str 字符串
 */
export function snakeToCamel(str: string): string {
  return str.replace(/_([a-z])/g, (_, letter) => letter.toUpperCase())
}

/**
 * 生成随机颜色
 */
export function generateRandomColor(): string {
  return (
    '#' +
    Math.floor(Math.random() * 16777215)
      .toString(16)
      .padStart(6, '0')
  )
}

/**
 * 计算年龄（保留兼容性）
 * @param birthDate 出生日期
 * @deprecated 请使用 date.ts 中的 calculateAge 函数
 */
export function calculateAge(birthDate: string | Date): number {
  const birth = new Date(birthDate)
  const today = new Date()
  let age = today.getFullYear() - birth.getFullYear()
  const monthDiff = today.getMonth() - birth.getMonth()

  if (monthDiff < 0 || (monthDiff === 0 && today.getDate() < birth.getDate())) {
    age--
  }

  return age
}

/**
 * 验证邮箱格式（保留兼容性）
 * @param email 邮箱地址
 * @deprecated 请使用 validation.ts 中的 validateEmail 函数
 */
export function isValidEmail(email: string): boolean {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  return emailRegex.test(email)
}

/**
 * 验证手机号格式（保留兼容性）
 * @param phone 手机号
 * @deprecated 请使用 validation.ts 中的 validatePhone 函数
 */
export function isValidPhone(phone: string): boolean {
  const phoneRegex = /^1[3-9]\d{9}$/
  return phoneRegex.test(phone)
}

/**
 * 验证密码强度（保留兼容性）
 * @param password 密码
 * @deprecated 请使用 validation.ts 中的 getPasswordStrength 函数
 */
export function validatePasswordStrength(password: string): {
  score: number
  level: 'weak' | 'medium' | 'strong'
  feedback: string[]
} {
  let score = 0
  const feedback: string[] = []

  if (password.length >= 8) score++
  else feedback.push('密码长度至少8位')

  if (/[a-z]/.test(password)) score++
  else feedback.push('包含小写字母')

  if (/[A-Z]/.test(password)) score++
  else feedback.push('包含大写字母')

  if (/\d/.test(password)) score++
  else feedback.push('包含数字')

  if (/[!@#$%^&*(),.?":{}|<>]/.test(password)) score++
  else feedback.push('包含特殊字符')

  let level: 'weak' | 'medium' | 'strong'
  if (score <= 2) level = 'weak'
  else if (score <= 3) level = 'medium'
  else level = 'strong'

  return { score, level, feedback }
}
