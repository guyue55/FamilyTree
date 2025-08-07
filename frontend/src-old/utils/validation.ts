/**
 * 验证工具函数
 * 提供统一的数据验证功能
 *
 * @author 古月
 * @version 1.0.0
 */

/**
 * 验证规则接口
 */
export interface ValidationRule {
  required?: boolean
  min?: number
  max?: number
  minLength?: number
  maxLength?: number
  pattern?: RegExp
  validator?: (value: any) => boolean | string
  message?: string
}

/**
 * 验证结果接口
 */
export interface ValidationResult {
  valid: boolean
  message?: string
}

/**
 * 常用正则表达式
 */
export const REGEX_PATTERNS = {
  // 邮箱
  EMAIL: /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/,
  // 手机号（中国）
  PHONE: /^1[3-9]\d{9}$/,
  // 身份证号（中国）
  ID_CARD: /^[1-9]\d{5}(18|19|20)\d{2}((0[1-9])|(1[0-2]))(([0-2][1-9])|10|20|30|31)\d{3}[0-9Xx]$/,
  // 密码（8-20位，包含字母和数字）
  PASSWORD: /^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d@$!%*#?&]{8,20}$/,
  // 强密码（8-20位，包含大小写字母、数字和特殊字符）
  STRONG_PASSWORD: /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,20}$/,
  // 用户名（3-20位，字母、数字、下划线）
  USERNAME: /^[a-zA-Z0-9_]{3,20}$/,
  // 中文姓名
  CHINESE_NAME: /^[\u4e00-\u9fa5]{2,10}$/,
  // 英文姓名
  ENGLISH_NAME: /^[a-zA-Z\s]{2,50}$/,
  // URL
  URL: /^https?:\/\/(www\.)?[-a-zA-Z0-9@:%._+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_+.~#?&//=]*)$/,
  // IP地址
  IP: /^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$/,
  // 数字
  NUMBER: /^\d+$/,
  // 小数
  DECIMAL: /^\d+(\.\d+)?$/,
  // 正整数
  POSITIVE_INTEGER: /^[1-9]\d*$/,
  // 非负整数
  NON_NEGATIVE_INTEGER: /^(0|[1-9]\d*)$/,
  // 邮政编码（中国）
  POSTAL_CODE: /^[1-9]\d{5}$/,
  // QQ号
  QQ: /^[1-9][0-9]{4,10}$/,
  // 微信号
  WECHAT: /^[a-zA-Z][-_a-zA-Z0-9]{5,19}$/
} as const

/**
 * 验证邮箱
 * @param email 邮箱地址
 */
export function validateEmail(email: string): ValidationResult {
  if (!email) {
    return { valid: false, message: '邮箱地址不能为空' }
  }

  if (!REGEX_PATTERNS.EMAIL.test(email)) {
    return { valid: false, message: '邮箱地址格式不正确' }
  }

  return { valid: true }
}

/**
 * 验证手机号
 * @param phone 手机号
 */
export function validatePhone(phone: string): ValidationResult {
  if (!phone) {
    return { valid: false, message: '手机号不能为空' }
  }

  if (!REGEX_PATTERNS.PHONE.test(phone)) {
    return { valid: false, message: '手机号格式不正确' }
  }

  return { valid: true }
}

/**
 * 验证密码
 * @param password 密码
 * @param strong 是否要求强密码
 */
export function validatePassword(password: string, strong: boolean = false): ValidationResult {
  if (!password) {
    return { valid: false, message: '密码不能为空' }
  }

  if (password.length < 8) {
    return { valid: false, message: '密码长度不能少于8位' }
  }

  if (password.length > 20) {
    return { valid: false, message: '密码长度不能超过20位' }
  }

  const pattern = strong ? REGEX_PATTERNS.STRONG_PASSWORD : REGEX_PATTERNS.PASSWORD
  if (!pattern.test(password)) {
    const message = strong ? '密码必须包含大小写字母、数字和特殊字符' : '密码必须包含字母和数字'
    return { valid: false, message }
  }

  return { valid: true }
}

/**
 * 验证用户名
 * @param username 用户名
 */
export function validateUsername(username: string): ValidationResult {
  if (!username) {
    return { valid: false, message: '用户名不能为空' }
  }

  if (!REGEX_PATTERNS.USERNAME.test(username)) {
    return { valid: false, message: '用户名只能包含字母、数字和下划线，长度3-20位' }
  }

  return { valid: true }
}

/**
 * 验证中文姓名
 * @param name 姓名
 */
export function validateChineseName(name: string): ValidationResult {
  if (!name) {
    return { valid: false, message: '姓名不能为空' }
  }

  if (!REGEX_PATTERNS.CHINESE_NAME.test(name)) {
    return { valid: false, message: '请输入2-10位中文姓名' }
  }

  return { valid: true }
}

/**
 * 验证身份证号
 * @param idCard 身份证号
 */
export function validateIdCard(idCard: string): ValidationResult {
  if (!idCard) {
    return { valid: false, message: '身份证号不能为空' }
  }

  if (!REGEX_PATTERNS.ID_CARD.test(idCard)) {
    return { valid: false, message: '身份证号格式不正确' }
  }

  // 验证校验位
  const weights = [7, 9, 10, 5, 8, 4, 2, 1, 6, 3, 7, 9, 10, 5, 8, 4, 2]
  const checkCodes = ['1', '0', 'X', '9', '8', '7', '6', '5', '4', '3', '2']

  let sum = 0
  for (let i = 0; i < 17; i++) {
    sum += parseInt(idCard[i]) * weights[i]
  }

  const checkCode = checkCodes[sum % 11]
  if (idCard[17].toUpperCase() !== checkCode) {
    return { valid: false, message: '身份证号校验位不正确' }
  }

  return { valid: true }
}

/**
 * 验证URL
 * @param url URL地址
 */
export function validateUrl(url: string): ValidationResult {
  if (!url) {
    return { valid: false, message: 'URL不能为空' }
  }

  if (!REGEX_PATTERNS.URL.test(url)) {
    return { valid: false, message: 'URL格式不正确' }
  }

  return { valid: true }
}

/**
 * 验证数字
 * @param value 值
 * @param min 最小值
 * @param max 最大值
 */
export function validateNumber(value: any, min?: number, max?: number): ValidationResult {
  if (value === null || value === undefined || value === '') {
    return { valid: false, message: '数值不能为空' }
  }

  const num = Number(value)
  if (isNaN(num)) {
    return { valid: false, message: '请输入有效的数字' }
  }

  if (min !== undefined && num < min) {
    return { valid: false, message: `数值不能小于${min}` }
  }

  if (max !== undefined && num > max) {
    return { valid: false, message: `数值不能大于${max}` }
  }

  return { valid: true }
}

/**
 * 验证字符串长度
 * @param value 值
 * @param minLength 最小长度
 * @param maxLength 最大长度
 */
export function validateLength(
  value: string,
  minLength?: number,
  maxLength?: number
): ValidationResult {
  if (!value) {
    return { valid: false, message: '内容不能为空' }
  }

  if (minLength !== undefined && value.length < minLength) {
    return { valid: false, message: `长度不能少于${minLength}位` }
  }

  if (maxLength !== undefined && value.length > maxLength) {
    return { valid: false, message: `长度不能超过${maxLength}位` }
  }

  return { valid: true }
}

/**
 * 验证日期
 * @param date 日期
 * @param minDate 最小日期
 * @param maxDate 最大日期
 */
export function validateDate(date: any, minDate?: Date, maxDate?: Date): ValidationResult {
  if (!date) {
    return { valid: false, message: '日期不能为空' }
  }

  const d = new Date(date)
  if (isNaN(d.getTime())) {
    return { valid: false, message: '日期格式不正确' }
  }

  if (minDate && d < minDate) {
    return { valid: false, message: `日期不能早于${minDate.toLocaleDateString()}` }
  }

  if (maxDate && d > maxDate) {
    return { valid: false, message: `日期不能晚于${maxDate.toLocaleDateString()}` }
  }

  return { valid: true }
}

/**
 * 验证文件
 * @param file 文件
 * @param allowedTypes 允许的文件类型
 * @param maxSize 最大文件大小（字节）
 */
export function validateFile(
  file: File,
  allowedTypes?: string[],
  maxSize?: number
): ValidationResult {
  if (!file) {
    return { valid: false, message: '请选择文件' }
  }

  if (allowedTypes && allowedTypes.length > 0) {
    const fileType = file.type.toLowerCase()
    const fileName = file.name.toLowerCase()
    const isTypeAllowed = allowedTypes.some(type => {
      if (type.startsWith('.')) {
        return fileName.endsWith(type)
      }
      return fileType.includes(type)
    })

    if (!isTypeAllowed) {
      return { valid: false, message: `只允许上传${allowedTypes.join('、')}格式的文件` }
    }
  }

  if (maxSize && file.size > maxSize) {
    const maxSizeMB = (maxSize / 1024 / 1024).toFixed(1)
    return { valid: false, message: `文件大小不能超过${maxSizeMB}MB` }
  }

  return { valid: true }
}

/**
 * 通用验证函数
 * @param value 值
 * @param rules 验证规则
 */
export function validate(value: any, rules: ValidationRule[]): ValidationResult {
  for (const rule of rules) {
    // 必填验证
    if (rule.required && (value === null || value === undefined || value === '')) {
      return { valid: false, message: rule.message || '此字段为必填项' }
    }

    // 如果值为空且不是必填，跳过其他验证
    if (!rule.required && (value === null || value === undefined || value === '')) {
      continue
    }

    // 最小值验证
    if (rule.min !== undefined && Number(value) < rule.min) {
      return { valid: false, message: rule.message || `值不能小于${rule.min}` }
    }

    // 最大值验证
    if (rule.max !== undefined && Number(value) > rule.max) {
      return { valid: false, message: rule.message || `值不能大于${rule.max}` }
    }

    // 最小长度验证
    if (rule.minLength !== undefined && String(value).length < rule.minLength) {
      return { valid: false, message: rule.message || `长度不能少于${rule.minLength}位` }
    }

    // 最大长度验证
    if (rule.maxLength !== undefined && String(value).length > rule.maxLength) {
      return { valid: false, message: rule.message || `长度不能超过${rule.maxLength}位` }
    }

    // 正则验证
    if (rule.pattern && !rule.pattern.test(String(value))) {
      return { valid: false, message: rule.message || '格式不正确' }
    }

    // 自定义验证
    if (rule.validator) {
      const result = rule.validator(value)
      if (result !== true) {
        return {
          valid: false,
          message: typeof result === 'string' ? result : rule.message || '验证失败'
        }
      }
    }
  }

  return { valid: true }
}

/**
 * 验证表单
 * @param data 表单数据
 * @param rules 验证规则映射
 */
export function validateForm(
  data: Record<string, any>,
  rules: Record<string, ValidationRule[]>
): {
  valid: boolean
  errors: Record<string, string>
} {
  const errors: Record<string, string> = {}

  for (const [field, fieldRules] of Object.entries(rules)) {
    const result = validate(data[field], fieldRules)
    if (!result.valid && result.message) {
      errors[field] = result.message
    }
  }

  return {
    valid: Object.keys(errors).length === 0,
    errors
  }
}

/**
 * 密码强度检测
 * @param password 密码
 */
export function getPasswordStrength(password: string): {
  score: number
  level: 'weak' | 'medium' | 'strong' | 'very-strong'
  suggestions: string[]
} {
  let score = 0
  const suggestions: string[] = []

  if (!password) {
    return { score: 0, level: 'weak', suggestions: ['请输入密码'] }
  }

  // 长度检查
  if (password.length >= 8) score += 1
  else suggestions.push('密码长度至少8位')

  if (password.length >= 12) score += 1

  // 包含小写字母
  if (/[a-z]/.test(password)) score += 1
  else suggestions.push('包含小写字母')

  // 包含大写字母
  if (/[A-Z]/.test(password)) score += 1
  else suggestions.push('包含大写字母')

  // 包含数字
  if (/\d/.test(password)) score += 1
  else suggestions.push('包含数字')

  // 包含特殊字符
  if (/[!@#$%^&*(),.?":{}|<>]/.test(password)) score += 1
  else suggestions.push('包含特殊字符')

  // 没有连续字符
  if (!/(.)\1{2,}/.test(password)) score += 1
  else suggestions.push('避免连续相同字符')

  // 没有常见模式
  if (!/123|abc|qwe|password/i.test(password)) score += 1
  else suggestions.push('避免常见密码模式')

  let level: 'weak' | 'medium' | 'strong' | 'very-strong'
  if (score <= 2) level = 'weak'
  else if (score <= 4) level = 'medium'
  else if (score <= 6) level = 'strong'
  else level = 'very-strong'

  return { score, level, suggestions }
}
