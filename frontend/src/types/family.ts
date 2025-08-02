/**
 * 家族相关类型定义
 *
 * 定义家族模块的所有类型接口
 * 与后端API保持一致
 */

import type { BaseEntity, VisibilityType, StatusType, Address } from './index'

// 性别枚举
export enum Gender {
  MALE = 'male',
  FEMALE = 'female',
  UNKNOWN = 'unknown'
}

// 家族成员
export interface FamilyMember extends BaseEntity {
  family_id: number
  name: string
  gender: Gender
  birth_date?: string
  death_date?: string
  birth_place?: string
  death_place?: string
  occupation?: string
  education?: string
  bio?: string
  avatar?: string
  photos?: string[]
  generation: number
  father_id?: number
  mother_id?: number
  spouse_ids?: number[]
  children_ids?: number[]
  notes?: string
  is_alive: boolean
  contact?: {
    email?: string
    phone?: string
    address?: Address
  }
  metadata?: Record<string, any>
}

// 家族成员创建表单
export interface FamilyMemberCreateForm {
  name: string
  gender: Gender
  birth_date?: string
  death_date?: string
  birth_place?: string
  death_place?: string
  occupation?: string
  education?: string
  bio?: string
  avatar?: string
  generation?: number
  father_id?: number
  mother_id?: number
  spouse_ids?: number[]
  notes?: string
  is_alive?: boolean
  contact?: {
    email?: string
    phone?: string
    address?: Address
  }
}

// 家族成员更新表单
export interface FamilyMemberUpdateForm {
  name?: string
  gender?: Gender
  birth_date?: string
  death_date?: string
  birth_place?: string
  death_place?: string
  occupation?: string
  education?: string
  bio?: string
  avatar?: string
  generation?: number
  father_id?: number
  mother_id?: number
  spouse_ids?: number[]
  notes?: string
  is_alive?: boolean
  contact?: {
    email?: string
    phone?: string
    address?: Address
  }
}

// 家族基础信息
export interface Family extends BaseEntity {
  name: string
  description?: string
  creatorId: number
  avatar?: string
  coverImage?: string
  visibility: VisibilityType
  status: StatusType
  allowJoin: boolean
  memberCount: number
  generationCount: number
  tags: string[]
  origin?: Address
  motto?: string
  foundedDate?: string
  website?: string
  contact?: {
    email?: string
    phone?: string
    address?: Address
  }
}

// 家族设置
export interface FamilySettings extends BaseEntity {
  familyId: number
  treeLayout: 'horizontal' | 'vertical' | 'radial'
  defaultGenerations: number
  displayOptions: {
    showPhotos: boolean
    showBirthDates: boolean
    showDeathDates: boolean
    showOccupation: boolean
    showLocation: boolean
    showRelationshipLabels: boolean
  }
  theme: {
    primaryColor: string
    fontFamily: string
    nodeStyle: 'circle' | 'square' | 'rounded'
    lineStyle: 'straight' | 'curved' | 'orthogonal'
  }
  privacy: {
    requireApproval: boolean
    allowMemberInvitation: boolean
    allowPublicSearch: boolean
    allowDataExport: boolean
  }
  notifications: {
    newMembers: boolean
    memberUpdates: boolean
    relationshipChanges: boolean
    mediaUploads: boolean
    systemAnnouncements: boolean
  }
}

// 家族邀请
export interface FamilyInvitation extends BaseEntity {
  familyId: number
  inviterId: number
  inviteeEmail?: string
  inviteePhone?: string
  inviteeName?: string
  status: 'pending' | 'accepted' | 'rejected' | 'expired'
  message?: string
  code: string
  expiresAt: string
  processedAt?: string
  processorId?: number
  rejectionReason?: string
}

// 家族成员关系
export interface FamilyMembership extends BaseEntity {
  familyId: number
  userId: number
  role: 'owner' | 'admin' | 'moderator' | 'member'
  permissions: {
    canInviteMembers: boolean
    canManageMembers: boolean
    canEditFamily: boolean
    canManageMedia: boolean
    canExportData: boolean
    canManageSettings: boolean
  }
  joinedAt: string
  invitedBy?: number
  status: StatusType
  nickname?: string
  bio?: string
}

// 家族创建表单
export interface FamilyCreateForm {
  name: string
  description?: string
  avatar?: string
  coverImage?: string
  visibility: VisibilityType
  allowJoin: boolean
  tags: string[]
  origin?: Address
  motto?: string
  foundedDate?: string
  website?: string
  contact?: {
    email?: string
    phone?: string
    address?: Address
  }
}

// 家族更新表单
export interface FamilyUpdateForm {
  name?: string
  description?: string
  avatar?: string
  coverImage?: string
  visibility?: VisibilityType
  allowJoin?: boolean
  tags?: string[]
  origin?: Address
  motto?: string
  foundedDate?: string
  website?: string
  contact?: {
    email?: string
    phone?: string
    address?: Address
  }
}

// 家族搜索参数
export interface FamilySearchParams {
  keyword?: string
  visibility?: VisibilityType
  status?: StatusType
  allowJoin?: boolean
  tags?: string[]
  location?: string
  memberCountMin?: number
  memberCountMax?: number
  createdAfter?: string
  createdBefore?: string
  sortBy?: 'name' | 'memberCount' | 'createdAt' | 'updatedAt'
  sortOrder?: 'asc' | 'desc'
}

// 家族统计信息
export interface FamilyStatistics {
  totalFamilies: number
  activeFamilies: number
  publicFamilies: number
  privateFamilies: number
  newFamiliesToday: number
  newFamiliesThisWeek: number
  newFamiliesThisMonth: number
  averageMemberCount: number
  largestFamily: {
    id: number
    name: string
    memberCount: number
  }
  memberDistribution: {
    small: number // 1-10 members
    medium: number // 11-50 members
    large: number // 51-200 members
    huge: number // 200+ members
  }
  visibilityDistribution: {
    public: number
    family: number
    private: number
  }
}

// 家族活动日志
export interface FamilyActivity {
  id: number
  familyId: number
  userId: number
  userName: string
  action: string
  target?: string
  targetId?: number
  description: string
  metadata?: Record<string, any>
  createdAt: string
}

// 家族角色权限
export interface FamilyRole {
  name: string
  code: 'owner' | 'admin' | 'moderator' | 'member'
  description: string
  permissions: {
    canInviteMembers: boolean
    canManageMembers: boolean
    canEditFamily: boolean
    canManageMedia: boolean
    canExportData: boolean
    canManageSettings: boolean
    canDeleteFamily: boolean
    canTransferOwnership: boolean
  }
  isDefault: boolean
  isSystemRole: boolean
}

// 家族邀请表单
export interface FamilyInviteForm {
  inviteeEmail?: string
  inviteePhone?: string
  inviteeName?: string
  message?: string
  role?: 'member' | 'moderator'
  expiresIn?: number // days
}

// 家族加入申请
export interface FamilyJoinRequest extends BaseEntity {
  familyId: number
  userId: number
  userName: string
  userEmail: string
  message?: string
  status: 'pending' | 'approved' | 'rejected'
  processedAt?: string
  processorId?: number
  rejectionReason?: string
}

// 家族导出选项
export interface FamilyExportOptions {
  format: 'excel' | 'csv' | 'json' | 'gedcom'
  includeMembers: boolean
  includeRelationships: boolean
  includeMedia: boolean
  includeNotes: boolean
  generationRange?: {
    min: number
    max: number
  }
  memberFields: string[]
  dateRange?: {
    start: string
    end: string
  }
}

// 家族树配置
export interface FamilyTreeConfig {
  layout: 'horizontal' | 'vertical' | 'radial'
  generations: number
  showPhotos: boolean
  showDates: boolean
  showOccupation: boolean
  nodeSize: 'small' | 'medium' | 'large'
  spacing: 'compact' | 'normal' | 'loose'
  theme: string
  centerMemberId?: number
}

// 家族公告
export interface FamilyAnnouncement extends BaseEntity {
  familyId: number
  authorId: number
  authorName: string
  title: string
  content: string
  type: 'general' | 'event' | 'news' | 'urgent'
  isPinned: boolean
  isPublished: boolean
  publishedAt?: string
  expiresAt?: string
  viewCount: number
  attachments?: string[]
}
