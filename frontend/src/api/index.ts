/**
 * API配置文件
 * 统一管理API相关配置
 *
 * @author 古月
 * @version 1.0.0
 */

import axios, { AxiosInstance, AxiosRequestConfig, AxiosResponse, AxiosError } from 'axios'
import { ElMessage } from 'element-plus'
import { SYSTEM_CONSTANTS } from '@/constants/system'
import { HttpStatus } from '@/enums'
import type { ApiResponse } from '@/types'
import { API_CONFIG } from '@/config/api'

// 使用从配置文件导入的API_CONFIG，移除重复定义

/**
 * 请求头配置
 */
const DEFAULT_HEADERS = {
  'Content-Type': 'application/json',
  Accept: 'application/json',
  'X-Requested-With': 'XMLHttpRequest'
}

/**
 * 创建axios实例
 */
const createAxiosInstance = (): AxiosInstance => {
  const instance = axios.create({
    baseURL: API_CONFIG.BASE_URL,
    timeout: API_CONFIG.TIMEOUT,
    headers: DEFAULT_HEADERS
  })

  // 请求拦截器
  instance.interceptors.request.use(
    config => {
      // 添加认证token
      const token = localStorage.getItem('familytree_token')
      if (token) {
        config.headers.Authorization = `Bearer ${token}`
      }

      // 添加请求时间戳
      config.metadata = { startTime: Date.now() }

      return config
    },
    (error: AxiosError) => {
      console.error('请求拦截器错误:', error)
      return Promise.reject(error)
    }
  )

  // 响应拦截器
  instance.interceptors.response.use(
    (response: AxiosResponse<ApiResponse>) => {
      // 计算请求耗时
      const endTime = Date.now()
      const startTime = response.config.metadata?.startTime || endTime
      const duration = endTime - startTime

      console.log(`API请求耗时: ${duration}ms - ${response.config.url}`)

      // 检查业务状态码
      const { code, message } = response.data

      if (code === HttpStatus.OK || code === HttpStatus.CREATED) {
        return response
      }

      // 处理业务错误
      ElMessage.error(message || '请求失败')
      return Promise.reject(new Error(message || '请求失败'))
    },
    async (error: AxiosError<ApiResponse>) => {
      const { response } = error

      // 处理网络错误
      if (!response) {
        ElMessage.error('网络连接失败，请检查网络设置')
        return Promise.reject(error)
      }

      const { status, data } = response

      // 处理HTTP状态码错误
      switch (status) {
        case HttpStatus.UNAUTHORIZED:
          // 清除token并跳转到登录页
          localStorage.removeItem('familytree_token')
          localStorage.removeItem('familytree_refresh_token')
          window.location.href = '/auth/login'
          ElMessage.error('登录已过期，请重新登录')
          break

        case HttpStatus.FORBIDDEN:
          ElMessage.error('没有权限访问该资源')
          break

        case HttpStatus.NOT_FOUND:
          ElMessage.error('请求的资源不存在')
          break

        case HttpStatus.TOO_MANY_REQUESTS:
          ElMessage.error('请求过于频繁，请稍后再试')
          break

        case HttpStatus.INTERNAL_SERVER_ERROR:
          ElMessage.error('服务器内部错误')
          break

        case HttpStatus.SERVICE_UNAVAILABLE:
          ElMessage.error('服务暂时不可用')
          break

        default:
          ElMessage.error(data?.message || `请求失败 (${status})`)
      }

      return Promise.reject(error)
    }
  )

  return instance
}

/**
 * API实例
 */
export const apiClient = createAxiosInstance()

/**
 * 请求重试函数
 */
export const retryRequest = async <T>(
  requestFn: () => Promise<T>,
  retries: number = API_CONFIG.RETRY_TIMES,
  delay: number = API_CONFIG.RETRY_DELAY
): Promise<T> => {
  try {
    return await requestFn()
  } catch (error) {
    if (retries > 0) {
      await new Promise(resolve => setTimeout(resolve, delay))
      return retryRequest(requestFn, retries - 1, delay * 2)
    }
    throw error
  }
}

/**
 * 基础请求方法
 */
export const request = {
  /**
   * GET请求
   */
  get: <T = any>(
    url: string,
    config?: AxiosRequestConfig
  ): Promise<AxiosResponse<ApiResponse<T>>> => {
    return apiClient.get(url, config)
  },

  /**
   * POST请求
   */
  post: <T = any>(
    url: string,
    data?: any,
    config?: AxiosRequestConfig
  ): Promise<AxiosResponse<ApiResponse<T>>> => {
    return apiClient.post(url, data, config)
  },

  /**
   * PUT请求
   */
  put: <T = any>(
    url: string,
    data?: any,
    config?: AxiosRequestConfig
  ): Promise<AxiosResponse<ApiResponse<T>>> => {
    return apiClient.put(url, data, config)
  },

  /**
   * PATCH请求
   */
  patch: <T = any>(
    url: string,
    data?: any,
    config?: AxiosRequestConfig
  ): Promise<AxiosResponse<ApiResponse<T>>> => {
    return apiClient.patch(url, data, config)
  },

  /**
   * DELETE请求
   */
  delete: <T = any>(
    url: string,
    config?: AxiosRequestConfig
  ): Promise<AxiosResponse<ApiResponse<T>>> => {
    return apiClient.delete(url, config)
  }
}

/**
 * 通用API实例
 */
export const api = {
  /**
   * GET请求
   */
  get: <T = any>(url: string, config?: AxiosRequestConfig): Promise<ApiResponse<T>> => {
    return request.get<T>(url, config).then(response => response.data)
  },

  /**
   * POST请求
   */
  post: <T = any>(
    url: string,
    data?: any,
    config?: AxiosRequestConfig
  ): Promise<ApiResponse<T>> => {
    return request.post<T>(url, data, config).then(response => response.data)
  },

  /**
   * PUT请求
   */
  put: <T = any>(url: string, data?: any, config?: AxiosRequestConfig): Promise<ApiResponse<T>> => {
    return request.put<T>(url, data, config).then(response => response.data)
  },

  /**
   * PATCH请求
   */
  patch: <T = any>(
    url: string,
    data?: any,
    config?: AxiosRequestConfig
  ): Promise<ApiResponse<T>> => {
    return request.patch<T>(url, data, config).then(response => response.data)
  },

  /**
   * DELETE请求
   */
  delete: <T = any>(url: string, config?: AxiosRequestConfig): Promise<ApiResponse<T>> => {
    return request.delete<T>(url, config).then(response => response.data)
  },

  /**
   * 上传文件
   */
  upload: <T = any>(
    url: string,
    formData: FormData,
    onProgress?: (progress: number) => void
  ): Promise<ApiResponse<T>> => {
    return apiClient
      .post(url, formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        },
        onUploadProgress: progressEvent => {
          if (onProgress && progressEvent.total) {
            const progress = Math.round((progressEvent.loaded * 100) / progressEvent.total)
            onProgress(progress)
          }
        }
      })
      .then(response => response.data)
  },

  /**
   * 下载文件
   */
  download: (url: string, params?: any): Promise<Blob> => {
    return apiClient
      .get(url, {
        params,
        responseType: 'blob'
      })
      .then(response => response.data)
  }
}

// 扩展axios配置类型以支持metadata
declare module 'axios' {
  interface AxiosRequestConfig {
    metadata?: {
      startTime: number
    }
  }
}

export { userApi } from './user'
export { familyApi, familyMemberApi } from './family'
export { uploadApi } from './upload'
