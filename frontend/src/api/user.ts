/**
 * 用户相关API接口
 *
 * @author 古月
 * @version 1.0.0
 */

import { api } from './index'
import type {
  User,
  UserLoginForm,
  UserRegisterForm,
  UserUpdateForm,
  PasswordChangeForm,
  UserSearchParams
} from '@/types/user'
import type { ApiResponse, PaginatedResponse } from '@/types'

/**
 * 用户认证API
 */
export const authApi = {
  /**
   * 用户登录
   */
  login(
    data: UserLoginForm
  ): Promise<ApiResponse<{ user: User; token: string; refresh_token: string }>> {
    return api.post('/auth/login', data)
  },

  /**
   * 用户注册
   */
  register(
    data: UserRegisterForm
  ): Promise<ApiResponse<{ user: User; token: string; refresh_token: string }>> {
    return api.post('/auth/register', data)
  },

  /**
   * 用户登出
   */
  logout(): Promise<ApiResponse<null>> {
    return api.post('/auth/logout')
  },

  /**
   * 刷新token
   */
  refreshToken(
    refreshToken: string
  ): Promise<ApiResponse<{ token: string; refresh_token: string }>> {
    return api.post('/auth/refresh', { refresh_token: refreshToken })
  },

  /**
   * 发送验证码
   */
  sendVerificationCode(data: {
    email?: string
    phone?: string
    type: 'register' | 'reset_password' | 'change_phone' | 'change_email'
  }): Promise<ApiResponse<null>> {
    return api.post('/auth/send-verification-code', data)
  },

  /**
   * 验证验证码
   */
  verifyCode(data: {
    email?: string
    phone?: string
    code: string
    type: string
  }): Promise<ApiResponse<{ verified: boolean }>> {
    return api.post('/auth/verify-code', data)
  },

  /**
   * 忘记密码
   */
  forgotPassword(data: { email: string }): Promise<ApiResponse<null>> {
    return api.post('/auth/forgot-password', data)
  },

  /**
   * 重置密码
   */
  resetPassword(data: { 
    email: string
    code: string
    newPassword: string 
  }): Promise<ApiResponse<null>> {
    return api.post('/auth/reset-password', data)
  },

  /**
   * 获取当前用户信息
   */
  getCurrentUser(): Promise<ApiResponse<User>> {
    return api.get('/auth/me')
  }
}

/**
 * 用户管理API
 */
export const userApi = {
  /**
   * 获取用户列表
   */
  getUsers(params?: UserSearchParams): Promise<ApiResponse<PaginatedResponse<User>>> {
    return api.get('/users', { params })
  },

  /**
   * 根据ID获取用户
   */
  getUserById(id: string): Promise<ApiResponse<User>> {
    return api.get(`/users/${id}`)
  },

  /**
   * 更新用户信息
   */
  updateUser(id: string, data: UserUpdateForm): Promise<ApiResponse<User>> {
    return api.put(`/users/${id}`, data)
  },

  /**
   * 更新当前用户信息
   */
  updateCurrentUser(data: UserUpdateForm): Promise<ApiResponse<User>> {
    return api.put('/users/me', data)
  },

  /**
   * 修改密码
   */
  changePassword(data: PasswordChangeForm): Promise<ApiResponse<null>> {
    return api.post('/users/change-password', data)
  },

  /**
   * 上传头像
   */
  uploadAvatar(file: File): Promise<ApiResponse<{ avatar_url: string }>> {
    const formData = new FormData()
    formData.append('avatar', file)
    return api.upload('/users/avatar', formData)
  },

  /**
   * 删除用户
   */
  deleteUser(id: string): Promise<ApiResponse<null>> {
    return api.delete(`/users/${id}`)
  },

  /**
   * 激活用户
   */
  activateUser(id: string): Promise<ApiResponse<User>> {
    return api.post(`/users/${id}/activate`)
  },

  /**
   * 禁用用户
   */
  deactivateUser(id: string): Promise<ApiResponse<User>> {
    return api.post(`/users/${id}/deactivate`)
  },

  /**
   * 搜索用户
   */
  searchUsers(
    keyword: string,
    params?: { limit?: number; exclude_ids?: string[] }
  ): Promise<ApiResponse<User[]>> {
    return api.get('/users/search', {
      params: {
        q: keyword,
        ...params
      }
    })
  },

  /**
   * 获取用户统计信息
   */
  getUserStats(id: string): Promise<
    ApiResponse<{
      families_count: number
      members_count: number
      created_at: string
      last_login_at: string
    }>
  > {
    return api.get(`/users/${id}/stats`)
  },

  /**
   * 获取用户活动记录
   */
  getUserActivities(
    id: string,
    params?: { page?: number; limit?: number }
  ): Promise<ApiResponse<PaginatedResponse<any>>> {
    return api.get(`/users/${id}/activities`, { params })
  },

  /**
   * 更新用户设置
   */
  updateUserSettings(data: {
    language?: string
    theme?: string
    timezone?: string
    email_notifications?: boolean
    push_notifications?: boolean
    privacy_settings?: Record<string, any>
  }): Promise<ApiResponse<null>> {
    return api.put('/users/settings', data)
  },

  /**
   * 获取用户设置
   */
  getUserSettings(): Promise<
    ApiResponse<{
      language: string
      theme: string
      timezone: string
      email_notifications: boolean
      push_notifications: boolean
      privacy_settings: Record<string, any>
    }>
  > {
    return api.get('/users/settings')
  },

  /**
   * 绑定第三方账号
   */
  bindThirdPartyAccount(data: {
    provider: 'wechat' | 'qq' | 'weibo' | 'github'
    code: string
    state?: string
  }): Promise<ApiResponse<null>> {
    return api.post('/users/bind-account', data)
  },

  /**
   * 解绑第三方账号
   */
  unbindThirdPartyAccount(provider: string): Promise<ApiResponse<null>> {
    return api.delete(`/users/bind-account/${provider}`)
  },

  /**
   * 获取绑定的第三方账号
   */
  getBoundAccounts(): Promise<
    ApiResponse<
      Array<{
        provider: string
        account_id: string
        account_name: string
        bound_at: string
      }>
    >
  > {
    return api.get('/users/bound-accounts')
  }
}
