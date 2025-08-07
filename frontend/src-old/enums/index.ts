/**
 * 枚举类型统一导出
 *
 * @author 古月
 * @version 1.0.0
 */

// 用户相关枚举
export * from './user'

// 族谱相关枚举
export * from './familyTree'

// 通用枚举
export enum Theme {
  /** 浅色主题 */
  LIGHT = 'light',
  /** 深色主题 */
  DARK = 'dark',
  /** 自动主题 */
  AUTO = 'auto'
}

export enum Language {
  /** 简体中文 */
  ZH_CN = 'zh-CN',
  /** 英文 */
  EN_US = 'en-US',
  /** 繁体中文 */
  ZH_TW = 'zh-TW'
}

export enum HttpStatus {
  /** 成功 */
  OK = 200,
  /** 已创建 */
  CREATED = 201,
  /** 无内容 */
  NO_CONTENT = 204,
  /** 错误请求 */
  BAD_REQUEST = 400,
  /** 未授权 */
  UNAUTHORIZED = 401,
  /** 禁止访问 */
  FORBIDDEN = 403,
  /** 未找到 */
  NOT_FOUND = 404,
  /** 方法不允许 */
  METHOD_NOT_ALLOWED = 405,
  /** 冲突 */
  CONFLICT = 409,
  /** 请求实体过大 */
  PAYLOAD_TOO_LARGE = 413,
  /** 请求过于频繁 */
  TOO_MANY_REQUESTS = 429,
  /** 服务器内部错误 */
  INTERNAL_SERVER_ERROR = 500,
  /** 服务不可用 */
  SERVICE_UNAVAILABLE = 503
}

export enum LoadingState {
  /** 空闲 */
  IDLE = 'idle',
  /** 加载中 */
  LOADING = 'loading',
  /** 成功 */
  SUCCESS = 'success',
  /** 错误 */
  ERROR = 'error'
}

export enum SortOrder {
  /** 升序 */
  ASC = 'asc',
  /** 降序 */
  DESC = 'desc'
}
