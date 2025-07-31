/**
 * API 请求和响应类型定义
 *
 * 定义所有API接口的请求和响应类型
 * 确保前后端数据结构一致性
 */

import type { ApiResponse, PaginatedResponse, SearchParams, ApiError } from './index'
import type {
  User,
  UserProfile,
  UserLoginForm,
  UserRegisterForm,
  UserUpdateForm,
  UserSearchParams,
  UserStatistics
} from './user'
import type {
  Family,
  FamilySettings,
  FamilyInvitation,
  FamilyCreateForm,
  FamilyUpdateForm,
  FamilySearchParams,
  FamilyStatistics
} from './family'

// 通用API响应类型
export type ApiResult<T = any> = Promise<ApiResponse<T>>
export type PaginatedResult<T = any> = Promise<PaginatedResponse<T>>

// 认证相关API
export namespace AuthAPI {
  // 登录
  export interface LoginRequest extends UserLoginForm {}
  export interface LoginResponse {
    user: User
    token: string
    refreshToken: string
    expiresAt: string
    permissions: string[]
  }

  // 注册
  export interface RegisterRequest extends UserRegisterForm {}
  export interface RegisterResponse {
    user: User
    message: string
    requiresVerification: boolean
  }

  // 刷新令牌
  export interface RefreshTokenRequest {
    refreshToken: string
  }
  export interface RefreshTokenResponse {
    token: string
    expiresAt: string
  }

  // 忘记密码
  export interface ForgotPasswordRequest {
    email: string
  }
  export interface ForgotPasswordResponse {
    message: string
    resetToken?: string
  }

  // 重置密码
  export interface ResetPasswordRequest {
    token: string
    newPassword: string
    confirmPassword: string
  }
  export interface ResetPasswordResponse {
    message: string
  }

  // 验证邮箱
  export interface VerifyEmailRequest {
    token: string
  }
  export interface VerifyEmailResponse {
    message: string
    user: User
  }
}

// 用户相关API
export namespace UserAPI {
  // 获取用户信息
  export interface GetUserRequest {
    id: number
  }
  export interface GetUserResponse extends User {}

  // 更新用户信息
  export interface UpdateUserRequest extends UserUpdateForm {}
  export interface UpdateUserResponse extends User {}

  // 获取用户资料
  export interface GetUserProfileRequest {
    userId: number
  }
  export interface GetUserProfileResponse extends UserProfile {}

  // 更新用户资料
  export interface UpdateUserProfileRequest extends Partial<UserProfile> {}
  export interface UpdateUserProfileResponse extends UserProfile {}

  // 搜索用户
  export interface SearchUsersRequest extends UserSearchParams, SearchParams {}
  export interface SearchUsersResponse {
    users: User[]
    total: number
    page: number
    pageSize: number
  }

  // 获取用户统计
  export interface GetUserStatisticsRequest {
    dateRange?: {
      start: string
      end: string
    }
  }
  export interface GetUserStatisticsResponse extends UserStatistics {}

  // 上传头像
  export interface UploadAvatarRequest {
    file: File
  }
  export interface UploadAvatarResponse {
    url: string
    filename: string
    size: number
  }

  // 删除用户
  export interface DeleteUserRequest {
    id: number
    reason?: string
  }
  export interface DeleteUserResponse {
    message: string
  }
}

// 家族相关API
export namespace FamilyAPI {
  // 创建家族
  export interface CreateFamilyRequest extends FamilyCreateForm {}
  export interface CreateFamilyResponse extends Family {}

  // 获取家族信息
  export interface GetFamilyRequest {
    id: number
  }
  export interface GetFamilyResponse extends Family {}

  // 更新家族信息
  export interface UpdateFamilyRequest extends FamilyUpdateForm {
    id: number
  }
  export interface UpdateFamilyResponse extends Family {}

  // 搜索家族
  export interface SearchFamiliesRequest extends Omit<SearchParams, 'sortBy'>, FamilySearchParams {}
  export interface SearchFamiliesResponse {
    families: Family[]
    total: number
    page: number
    pageSize: number
  }

  // 获取家族设置
  export interface GetFamilySettingsRequest {
    familyId: number
  }
  export interface GetFamilySettingsResponse extends FamilySettings {}

  // 更新家族设置
  export interface UpdateFamilySettingsRequest extends Partial<FamilySettings> {
    familyId: number
  }
  export interface UpdateFamilySettingsResponse extends FamilySettings {}

  // 邀请成员
  export interface InviteMemberRequest {
    familyId: number
    inviteeEmail?: string
    inviteePhone?: string
    inviteeName?: string
    message?: string
    role?: string
  }
  export interface InviteMemberResponse extends FamilyInvitation {}

  // 获取家族统计
  export interface GetFamilyStatisticsRequest {
    familyId?: number
    dateRange?: {
      start: string
      end: string
    }
  }
  export interface GetFamilyStatisticsResponse extends FamilyStatistics {}

  // 删除家族
  export interface DeleteFamilyRequest {
    id: number
    reason?: string
  }
  export interface DeleteFamilyResponse {
    message: string
  }
}

// 文件上传相关API
export namespace UploadAPI {
  // 上传文件
  export interface UploadFileRequest {
    file: File
    type?: 'avatar' | 'cover' | 'media' | 'document'
    familyId?: number
  }
  export interface UploadFileResponse {
    id: number
    url: string
    filename: string
    originalName: string
    size: number
    mimeType: string
    width?: number
    height?: number
    duration?: number
  }

  // 批量上传
  export interface BatchUploadRequest {
    files: File[]
    type?: string
    familyId?: number
  }
  export interface BatchUploadResponse {
    success: UploadFileResponse[]
    failed: Array<{
      filename: string
      error: string
    }>
  }

  // 删除文件
  export interface DeleteFileRequest {
    id: number
  }
  export interface DeleteFileResponse {
    message: string
  }
}

// 系统配置相关API
export namespace SystemAPI {
  // 获取系统配置
  export interface GetConfigRequest {
    key?: string
  }
  export interface GetConfigResponse {
    [key: string]: any
  }

  // 更新系统配置
  export interface UpdateConfigRequest {
    configs: Record<string, any>
  }
  export interface UpdateConfigResponse {
    message: string
  }

  // 获取系统状态
  export interface GetSystemStatusRequest {}
  export interface GetSystemStatusResponse {
    status: 'healthy' | 'warning' | 'error'
    version: string
    uptime: number
    database: {
      status: 'connected' | 'disconnected'
      responseTime: number
    }
    cache: {
      status: 'connected' | 'disconnected'
      hitRate: number
    }
    storage: {
      used: number
      total: number
      available: number
    }
  }
}

// 错误处理类型
export interface ApiErrorResponse extends ApiError {
  timestamp: string
  path: string
  method: string
  details?: {
    field?: string
    code?: string
    message?: string
  }[]
}

// 请求配置类型
export interface RequestConfig {
  timeout?: number
  retries?: number
  cache?: boolean
  headers?: Record<string, string>
  params?: Record<string, any>
}

// 响应拦截器类型
export interface ResponseInterceptor {
  onSuccess?: (response: any) => any
  onError?: (error: ApiErrorResponse) => any
}

// 请求拦截器类型
export interface RequestInterceptor {
  onRequest?: (config: RequestConfig) => RequestConfig
  onError?: (error: any) => any
}
