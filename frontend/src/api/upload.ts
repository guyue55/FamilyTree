/**
 * 文件上传相关API接口
 *
 * @author 古月
 * @version 1.0.0
 */

import { api } from './index'
import type { ApiResponse } from '@/types'

/**
 * 文件信息接口
 */
export interface FileInfo {
  id: string
  filename: string
  original_name: string
  file_type: string
  file_size: number
  file_url: string
  thumbnail_url?: string
  upload_time: string
  uploader_id: string
  uploader_name: string
  description?: string
  tags?: string[]
  is_public: boolean
  download_count: number
  metadata?: Record<string, any>
}

/**
 * 上传进度回调
 */
export interface UploadProgress {
  loaded: number
  total: number
  percentage: number
}

/**
 * 上传选项
 */
export interface UploadOptions {
  onProgress?: (progress: UploadProgress) => void
  description?: string
  tags?: string[]
  is_public?: boolean
  folder?: string
}

/**
 * 文件上传API
 */
export const uploadApi = {
  /**
   * 上传单个文件
   */
  uploadFile(file: File, options?: UploadOptions): Promise<ApiResponse<FileInfo>> {
    const formData = new FormData()
    formData.append('file', file)

    if (options?.description) {
      formData.append('description', options.description)
    }
    if (options?.tags) {
      formData.append('tags', JSON.stringify(options.tags))
    }
    if (options?.is_public !== undefined) {
      formData.append('is_public', String(options.is_public))
    }
    if (options?.folder) {
      formData.append('folder', options.folder)
    }

    return api.upload('/upload/file', formData, (progress: number) => {
      if (options?.onProgress) {
        const progressInfo: UploadProgress = {
          loaded: 0,
          total: 100,
          percentage: progress
        }
        options.onProgress(progressInfo)
      }
    })
  },

  /**
   * 上传多个文件
   */
  uploadFiles(files: File[], options?: UploadOptions): Promise<ApiResponse<FileInfo[]>> {
    const formData = new FormData()
    files.forEach((file, index) => {
      formData.append(`files[${index}]`, file)
    })

    if (options?.description) {
      formData.append('description', options.description)
    }
    if (options?.tags) {
      formData.append('tags', JSON.stringify(options.tags))
    }
    if (options?.is_public !== undefined) {
      formData.append('is_public', String(options.is_public))
    }
    if (options?.folder) {
      formData.append('folder', options.folder)
    }

    return api.upload('/upload/files', formData, (progress: number) => {
      if (options?.onProgress) {
        const progressInfo: UploadProgress = {
          loaded: 0,
          total: 100,
          percentage: progress
        }
        options.onProgress(progressInfo)
      }
    })
  },

  /**
   * 上传头像
   */
  uploadAvatar(file: File, options?: UploadOptions): Promise<ApiResponse<{ avatar_url: string }>> {
    const formData = new FormData()
    formData.append('avatar', file)

    return api.upload('/upload/avatar', formData, (progress: number) => {
      if (options?.onProgress) {
        const progressInfo: UploadProgress = {
          loaded: 0,
          total: 100,
          percentage: progress
        }
        options.onProgress(progressInfo)
      }
    })
  },

  /**
   * 上传族谱成员照片
   */
  uploadMemberPhoto(
    file: File,
    options?: UploadOptions
  ): Promise<ApiResponse<{ photo_url: string }>> {
    const formData = new FormData()
    formData.append('photo', file)

    return api.upload('/upload/member-photo', formData, (progress: number) => {
      if (options?.onProgress) {
        const progressInfo: UploadProgress = {
          loaded: 0,
          total: 100,
          percentage: progress
        }
        options.onProgress(progressInfo)
      }
    })
  },

  /**
   * 分片上传大文件
   */
  uploadLargeFile(
    file: File,
    options?: UploadOptions & {
      chunkSize?: number
      onChunkProgress?: (chunkIndex: number, totalChunks: number) => void
    }
  ): Promise<ApiResponse<FileInfo>> {
    const chunkSize = options?.chunkSize || 1024 * 1024 * 5 // 5MB per chunk
    const totalChunks = Math.ceil(file.size / chunkSize)
    const uploadId = Date.now().toString()

    const uploadChunk = async (chunkIndex: number): Promise<void> => {
      const start = chunkIndex * chunkSize
      const end = Math.min(start + chunkSize, file.size)
      const chunk = file.slice(start, end)

      const formData = new FormData()
      formData.append('chunk', chunk)
      formData.append('uploadId', uploadId)
      formData.append('chunkIndex', chunkIndex.toString())
      formData.append('totalChunks', totalChunks.toString())
      formData.append('filename', file.name)

      await api.upload('/upload/chunk', formData)

      if (options?.onChunkProgress) {
        options.onChunkProgress(chunkIndex + 1, totalChunks)
      }
    }

    return new Promise(async (resolve, reject) => {
      try {
        // 上传所有分片
        for (let i = 0; i < totalChunks; i++) {
          await uploadChunk(i)
        }

        // 合并分片
        const mergeData = {
          uploadId,
          filename: file.name,
          totalChunks,
          description: options?.description,
          tags: options?.tags,
          is_public: options?.is_public,
          folder: options?.folder
        }

        const result = await api.post('/upload/merge', mergeData)
        resolve(result)
      } catch (error) {
        reject(error)
      }
    })
  },

  /**
   * 获取文件信息
   */
  getFileInfo(fileId: string): Promise<ApiResponse<FileInfo>> {
    return api.get(`/files/${fileId}`)
  },

  /**
   * 获取文件列表
   */
  getFiles(params?: {
    page?: number
    limit?: number
    file_type?: string
    folder?: string
    search?: string
    sort?: 'name' | 'size' | 'upload_time'
    order?: 'asc' | 'desc'
  }): Promise<
    ApiResponse<{
      files: FileInfo[]
      total: number
      page: number
      limit: number
    }>
  > {
    return api.get('/files', { params })
  },

  /**
   * 删除文件
   */
  deleteFile(fileId: string): Promise<ApiResponse<null>> {
    return api.delete(`/files/${fileId}`)
  },

  /**
   * 批量删除文件
   */
  deleteFiles(fileIds: string[]): Promise<ApiResponse<null>> {
    return api.delete('/files/batch', { data: { file_ids: fileIds } })
  },

  /**
   * 更新文件信息
   */
  updateFile(
    fileId: string,
    data: {
      description?: string
      tags?: string[]
      is_public?: boolean
    }
  ): Promise<ApiResponse<FileInfo>> {
    return api.put(`/files/${fileId}`, data)
  },

  /**
   * 下载文件
   */
  downloadFile(fileId: string): Promise<Blob> {
    return api.download(`/files/${fileId}/download`)
  },

  /**
   * 获取文件下载链接
   */
  getDownloadUrl(
    fileId: string,
    expires?: number
  ): Promise<ApiResponse<{ download_url: string; expires_at: string }>> {
    return api.get(`/files/${fileId}/download-url`, {
      params: { expires }
    })
  },

  /**
   * 创建文件夹
   */
  createFolder(
    name: string,
    parentFolder?: string
  ): Promise<
    ApiResponse<{
      id: string
      name: string
      path: string
      parent_id?: string
      created_at: string
    }>
  > {
    return api.post('/folders', { name, parent_folder: parentFolder })
  },

  /**
   * 获取文件夹列表
   */
  getFolders(parentFolder?: string): Promise<
    ApiResponse<
      Array<{
        id: string
        name: string
        path: string
        parent_id?: string
        file_count: number
        created_at: string
      }>
    >
  > {
    return api.get('/folders', { params: { parent_folder: parentFolder } })
  },

  /**
   * 删除文件夹
   */
  deleteFolder(folderId: string): Promise<ApiResponse<null>> {
    return api.delete(`/folders/${folderId}`)
  },

  /**
   * 移动文件到文件夹
   */
  moveFile(fileId: string, folderId?: string): Promise<ApiResponse<null>> {
    return api.put(`/files/${fileId}/move`, { folder_id: folderId })
  },

  /**
   * 复制文件
   */
  copyFile(fileId: string, folderId?: string): Promise<ApiResponse<FileInfo>> {
    return api.post(`/files/${fileId}/copy`, { folder_id: folderId })
  },

  /**
   * 获取存储统计
   */
  getStorageStats(): Promise<
    ApiResponse<{
      total_files: number
      total_size: number
      used_space: number
      available_space: number
      file_type_stats: Record<string, { count: number; size: number }>
    }>
  > {
    return api.get('/storage/stats')
  }
}
