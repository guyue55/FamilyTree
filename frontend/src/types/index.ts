/**
 * 通用类型定义
 *
 * 定义项目中使用的通用类型和接口
 * 遵循TypeScript最佳实践和前端开发规范
 */

// 基础类型
export type ID = number | string

// API响应基础类型
export interface ApiResponse<T = any> {
  code: number
  message: string
  data: T
}

// 分页响应类型
export interface PaginatedResponse<T> {
  code: number
  message: string
  data: {
    items: T[]
    total: number
    page: number
    pageSize: number
    totalPages: number
  }
}

// 基础实体类型
export interface BaseEntity {
  id: ID
  createdAt: string
  updatedAt: string
  isDeleted?: boolean
}

// 可见性选择
export type VisibilityType = 'public' | 'family' | 'private'

// 性别类型
export type GenderType = 'male' | 'female' | 'unknown'

// 状态类型
export type StatusType = 'active' | 'inactive' | 'pending' | 'deleted'

// 文件类型
export type FileType = 'image' | 'video' | 'audio' | 'document' | 'other'

// 错误类型
export interface ApiError {
  code: number
  message: string
  details?: Record<string, any>
}

// 表单验证规则类型
export interface ValidationRule {
  required?: boolean
  min?: number
  max?: number
  pattern?: RegExp
  message?: string
  validator?: (value: any) => boolean | string
}

// 表单字段类型
export interface FormField {
  name: string
  label: string
  type: 'text' | 'email' | 'password' | 'number' | 'date' | 'select' | 'textarea'
  placeholder?: string
  rules?: ValidationRule[]
  options?: Array<{ label: string; value: any }>
}

// 菜单项类型
export interface MenuItem {
  id: string
  title: string
  icon?: string
  path?: string
  children?: MenuItem[]
  permission?: string
  hidden?: boolean
}

// 面包屑类型
export interface BreadcrumbItem {
  title: string
  path?: string
}

// 表格列定义
export interface TableColumn {
  key: string
  title: string
  width?: number
  sortable?: boolean
  filterable?: boolean
  render?: (value: any, record: any) => any
}

// 搜索参数类型
export interface SearchParams {
  keyword?: string
  page?: number
  pageSize?: number
  sortBy?: string
  sortOrder?: 'asc' | 'desc'
  filters?: Record<string, any>
}

// 上传文件类型
export interface UploadFile {
  id?: ID
  name: string
  size: number
  type: string
  url?: string
  status: 'uploading' | 'success' | 'error'
  progress?: number
}

// 通知类型
export interface Notification {
  id: ID
  type: 'success' | 'warning' | 'error' | 'info'
  title: string
  message: string
  duration?: number
  timestamp: string
  read?: boolean
}

// 权限类型
export interface Permission {
  id: ID
  name: string
  code: string
  description?: string
  module: string
}

// 角色类型
export interface Role {
  id: ID
  name: string
  code: string
  description?: string
  permissions: Permission[]
}

// 地址类型
export interface Address {
  province?: string
  city?: string
  district?: string
  street?: string
  detail?: string
  postalCode?: string
  coordinates?: {
    latitude: number
    longitude: number
  }
}

// 联系方式类型
export interface Contact {
  phone?: string
  email?: string
  wechat?: string
  qq?: string
  address?: Address
}

// 统计数据类型
export interface Statistics {
  total: number
  active: number
  inactive: number
  growth?: number
  percentage?: number
}

// 图表数据类型
export interface ChartData {
  labels: string[]
  datasets: Array<{
    label: string
    data: number[]
    backgroundColor?: string[]
    borderColor?: string[]
  }>
}

// 导出选项类型
export interface ExportOptions {
  format: 'excel' | 'csv' | 'pdf'
  filename?: string
  fields?: string[]
  filters?: Record<string, any>
}

// 主题配置类型
export interface ThemeConfig {
  mode: 'light' | 'dark' | 'auto'
  primaryColor: string
  fontSize: 'small' | 'medium' | 'large'
  borderRadius: number
}

// 语言配置类型
export interface LanguageConfig {
  locale: string
  name: string
  flag?: string
}

// 应用配置类型
export interface AppConfig {
  name: string
  version: string
  description?: string
  logo?: string
  theme: ThemeConfig
  language: LanguageConfig
  features: Record<string, boolean>
}
