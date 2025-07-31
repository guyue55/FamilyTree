/**
 * 用户相关类型定义
 *
 * 定义用户模块的所有类型接口
 * 与后端API保持一致
 */

import type { BaseEntity, Contact, GenderType, StatusType, VisibilityType } from './index'

// 用户基础信息
export interface User extends BaseEntity {
  username: string
  email: string
  phone?: string
  avatar?: string
  nickname?: string
  gender: GenderType
  birthDate?: string
  bio?: string
  isVerified: boolean
  isPremium: boolean
  lastLoginIp?: string
  loginCount: number
  status: StatusType
}

// 用户资料
export interface UserProfile extends BaseEntity {
  userId: number
  privacy: {
    showEmail: boolean
    showPhone: boolean
    showBirthDate: boolean
    allowSearch: boolean
    allowInvitation: boolean
  }
  notifications: {
    email: boolean
    sms: boolean
    push: boolean
    familyUpdates: boolean
    memberUpdates: boolean
    systemNotices: boolean
  }
  preferences: {
    theme: 'light' | 'dark' | 'auto'
    language: string
    timezone: string
    dateFormat: string
  }
}

// 用户登录日志
export interface UserLoginLog extends BaseEntity {
  userId: number
  ipAddress: string
  userAgent: string
  loginType: 'web' | 'mobile' | 'api'
  isSuccess: boolean
  failureReason?: string
  location?: string
  deviceInfo?: {
    browser: string
    os: string
    device: string
  }
}

// 用户注册表单
export interface UserRegisterForm {
  username: string
  email: string
  password: string
  confirmPassword: string
  phone?: string
  nickname?: string
  gender?: GenderType
  agreementAccepted: boolean
  invitationCode?: string
}

// 用户登录表单
export interface UserLoginForm {
  username: string
  password: string
  rememberMe?: boolean
  captcha?: string
}

// 用户更新表单
export interface UserUpdateForm {
  nickname?: string
  avatar?: string
  gender?: GenderType
  birthDate?: string
  bio?: string
  phone?: string
}

// 密码修改表单
export interface PasswordChangeForm {
  currentPassword: string
  newPassword: string
  confirmPassword: string
}

// 用户搜索参数
export interface UserSearchParams {
  keyword?: string
  gender?: GenderType
  status?: StatusType
  isVerified?: boolean
  isPremium?: boolean
  registeredAfter?: string
  registeredBefore?: string
  lastLoginAfter?: string
  lastLoginBefore?: string
}

// 用户统计信息
export interface UserStatistics {
  totalUsers: number
  activeUsers: number
  verifiedUsers: number
  premiumUsers: number
  newUsersToday: number
  newUsersThisWeek: number
  newUsersThisMonth: number
  loginUsersToday: number
  genderDistribution: {
    male: number
    female: number
    unknown: number
  }
  ageDistribution: {
    under18: number
    age18to30: number
    age31to50: number
    age51to70: number
    over70: number
  }
}

// 用户权限
export interface UserPermission {
  canCreateFamily: boolean
  canJoinFamily: boolean
  canInviteMembers: boolean
  canManageFamily: boolean
  canUploadMedia: boolean
  canExportData: boolean
  maxFamilies: number
  maxMembers: number
  maxStorage: number // MB
}

// 用户设置
export interface UserSettings {
  profile: UserProfile
  permissions: UserPermission
  subscription?: {
    type: 'free' | 'premium' | 'enterprise'
    startDate: string
    endDate?: string
    features: string[]
  }
}

// 用户会话信息
export interface UserSession {
  user: User
  token: string
  refreshToken?: string
  expiresAt: string
  permissions: string[]
  roles: string[]
}

// 用户邀请
export interface UserInvitation {
  id: number
  inviterName: string
  familyName: string
  message?: string
  code: string
  expiresAt: string
  status: 'pending' | 'accepted' | 'rejected' | 'expired'
}

// 用户活动日志
export interface UserActivity {
  id: number
  userId: number
  action: string
  target?: string
  targetId?: number
  description: string
  ipAddress: string
  userAgent: string
  createdAt: string
}

// 用户导出选项
export interface UserExportOptions {
  format: 'excel' | 'csv' | 'json'
  fields: string[]
  filters?: UserSearchParams
  includeProfile?: boolean
  includeLoginLogs?: boolean
  includeActivities?: boolean
}
