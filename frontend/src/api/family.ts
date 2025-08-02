/**
 * 族谱相关API接口
 * 
 * @author 古月
 * @version 1.0.0
 */

import { api } from './index';
import type { 
  Family, 
  FamilyMember, 
  FamilyCreateForm, 
  FamilyUpdateForm,
  FamilySearchParams,
  FamilyMemberCreateForm,
  FamilyMemberUpdateForm,
  FamilyInvitation
} from '@/types/family';
import type { ApiResponse, PaginatedResponse } from '@/types';

/**
 * 族谱管理API
 */
export const familyApi = {
  /**
   * 获取族谱列表
   */
  getFamilies(params?: FamilySearchParams): Promise<ApiResponse<PaginatedResponse<Family>>> {
    return api.get('/families', { params });
  },

  /**
   * 根据ID获取族谱
   */
  getFamilyById(id: string): Promise<ApiResponse<Family>> {
    return api.get(`/families/${id}`);
  },

  /**
   * 创建族谱
   */
  createFamily(data: FamilyCreateForm): Promise<ApiResponse<Family>> {
    return api.post('/families', data);
  },

  /**
   * 更新族谱
   */
  updateFamily(id: string, data: FamilyUpdateForm): Promise<ApiResponse<Family>> {
    return api.put(`/families/${id}`, data);
  },

  /**
   * 删除族谱
   */
  deleteFamily(id: string): Promise<ApiResponse<null>> {
    return api.delete(`/families/${id}`);
  },

  /**
   * 获取族谱统计信息
   */
  getFamilyStats(id: string): Promise<ApiResponse<{
    members_count: number;
    generations_count: number;
    relationships_count: number;
    created_at: string;
    updated_at: string;
  }>> {
    return api.get(`/families/${id}/stats`);
  },

  /**
   * 搜索族谱
   */
  searchFamilies(keyword: string, params?: { limit?: number; visibility?: string }): Promise<ApiResponse<Family[]>> {
    return api.get('/families/search', { 
      params: { 
        q: keyword,
        ...params 
      } 
    });
  },

  /**
   * 获取我的族谱
   */
  getMyFamilies(params?: { page?: number; limit?: number }): Promise<ApiResponse<PaginatedResponse<Family>>> {
    return api.get('/families/my', { params });
  },

  /**
   * 获取我参与的族谱
   */
  getJoinedFamilies(params?: { page?: number; limit?: number }): Promise<ApiResponse<PaginatedResponse<Family>>> {
    return api.get('/families/joined', { params });
  },

  /**
   * 复制族谱
   */
  cloneFamily(id: string, data: { name: string; description?: string }): Promise<ApiResponse<Family>> {
    return api.post(`/families/${id}/clone`, data);
  },

  /**
   * 导出族谱
   */
  exportFamily(id: string, format: 'pdf' | 'excel' | 'json'): Promise<Blob> {
    return api.download(`/families/${id}/export`, { format });
  },

  /**
   * 导入族谱
   */
  importFamily(file: File, options?: { merge_strategy?: 'replace' | 'merge' }): Promise<ApiResponse<Family>> {
    const formData = new FormData();
    formData.append('file', file);
    if (options) {
      Object.entries(options).forEach(([key, value]) => {
        formData.append(key, String(value));
      });
    }
    return api.upload('/families/import', formData);
  },
};

/**
 * 族谱成员API
 */
export const familyMemberApi = {
  /**
   * 获取族谱成员列表
   */
  getFamilyMembers(familyId: string, params?: { page?: number; limit?: number; search?: string }): Promise<ApiResponse<PaginatedResponse<FamilyMember>>> {
    return api.get(`/families/${familyId}/members`, { params });
  },

  /**
   * 根据ID获取成员
   */
  getMemberById(familyId: string, memberId: string): Promise<ApiResponse<FamilyMember>> {
    return api.get(`/families/${familyId}/members/${memberId}`);
  },

  /**
   * 添加族谱成员
   */
  createMember(familyId: string, data: FamilyMemberCreateForm): Promise<ApiResponse<FamilyMember>> {
    return api.post(`/families/${familyId}/members`, data);
  },

  /**
   * 更新族谱成员
   */
  updateMember(familyId: string, memberId: string, data: FamilyMemberUpdateForm): Promise<ApiResponse<FamilyMember>> {
    return api.put(`/families/${familyId}/members/${memberId}`, data);
  },

  /**
   * 删除族谱成员
   */
  deleteMember(familyId: string, memberId: string): Promise<ApiResponse<null>> {
    return api.delete(`/families/${familyId}/members/${memberId}`);
  },

  /**
   * 批量添加成员
   */
  batchCreateMembers(familyId: string, data: { members: FamilyMemberCreateForm[] }): Promise<ApiResponse<FamilyMember[]>> {
    return api.post(`/families/${familyId}/members/batch`, data);
  },

  /**
   * 搜索族谱成员
   */
  searchMembers(familyId: string, keyword: string, params?: { limit?: number }): Promise<ApiResponse<FamilyMember[]>> {
    return api.get(`/families/${familyId}/members/search`, { 
      params: { 
        q: keyword,
        ...params 
      } 
    });
  },

  /**
   * 上传成员照片
   */
  uploadMemberPhoto(familyId: string, memberId: string, file: File): Promise<ApiResponse<{ photo_url: string }>> {
    const formData = new FormData();
    formData.append('photo', file);
    return api.upload(`/families/${familyId}/members/${memberId}/photo`, formData);
  },

  /**
   * 获取成员关系
   */
  getMemberRelationships(familyId: string, memberId: string): Promise<ApiResponse<any[]>> {
    return api.get(`/families/${familyId}/members/${memberId}/relationships`);
  },

  /**
   * 添加成员关系
   */
  createRelationship(familyId: string, data: {
    member_id: string;
    related_member_id: string;
    relationship_type: string;
    description?: string;
  }): Promise<ApiResponse<any>> {
    return api.post(`/families/${familyId}/relationships`, data);
  },

  /**
   * 更新成员关系
   */
  updateRelationship(familyId: string, relationshipId: string, data: {
    relationship_type?: string;
    description?: string;
  }): Promise<ApiResponse<any>> {
    return api.put(`/families/${familyId}/relationships/${relationshipId}`, data);
  },

  /**
   * 删除成员关系
   */
  deleteRelationship(familyId: string, relationshipId: string): Promise<ApiResponse<null>> {
    return api.delete(`/families/${familyId}/relationships/${relationshipId}`);
  },
};

/**
 * 族谱树API
 */
export const familyTreeApi = {
  /**
   * 获取族谱树数据
   */
  getFamilyTree(familyId: string, params?: {
    root_member_id?: string;
    max_generations?: number;
    include_spouses?: boolean;
  }): Promise<ApiResponse<any[]>> {
    return api.get(`/families/${familyId}/tree`, { params });
  },

  /**
   * 获取成员的家族路径
   */
  getMemberPath(familyId: string, memberId: string): Promise<ApiResponse<{
    path: FamilyMember[];
    generation: number;
  }>> {
    return api.get(`/families/${familyId}/members/${memberId}/path`);
  },

  /**
   * 计算两个成员的关系
   */
  calculateRelationship(familyId: string, member1Id: string, member2Id: string): Promise<ApiResponse<{
    relationship: string;
    path: FamilyMember[];
    description: string;
  }>> {
    return api.get(`/families/${familyId}/calculate-relationship`, {
      params: {
        member1_id: member1Id,
        member2_id: member2Id,
      }
    });
  },

  /**
   * 获取族谱统计
   */
  getTreeStatistics(familyId: string): Promise<ApiResponse<{
    total_members: number;
    generations: number;
    male_count: number;
    female_count: number;
    married_count: number;
    single_count: number;
    age_distribution: Record<string, number>;
    generation_distribution: Record<string, number>;
  }>> {
    return api.get(`/families/${familyId}/tree/statistics`);
  },
};

/**
 * 族谱邀请API
 */
export const familyInvitationApi = {
  /**
   * 发送邀请
   */
  sendInvitation(familyId: string, data: {
    email?: string;
    phone?: string;
    role: string;
    message?: string;
  }): Promise<ApiResponse<FamilyInvitation>> {
    return api.post(`/families/${familyId}/invitations`, data);
  },

  /**
   * 获取邀请列表
   */
  getInvitations(familyId: string, params?: { page?: number; limit?: number; status?: string }): Promise<ApiResponse<PaginatedResponse<FamilyInvitation>>> {
    return api.get(`/families/${familyId}/invitations`, { params });
  },

  /**
   * 接受邀请
   */
  acceptInvitation(invitationId: string): Promise<ApiResponse<null>> {
    return api.post(`/invitations/${invitationId}/accept`);
  },

  /**
   * 拒绝邀请
   */
  rejectInvitation(invitationId: string): Promise<ApiResponse<null>> {
    return api.post(`/invitations/${invitationId}/reject`);
  },

  /**
   * 取消邀请
   */
  cancelInvitation(invitationId: string): Promise<ApiResponse<null>> {
    return api.delete(`/invitations/${invitationId}`);
  },

  /**
   * 重新发送邀请
   */
  resendInvitation(invitationId: string): Promise<ApiResponse<null>> {
    return api.post(`/invitations/${invitationId}/resend`);
  },

  /**
   * 获取我的邀请
   */
  getMyInvitations(params?: { page?: number; limit?: number; status?: string }): Promise<ApiResponse<PaginatedResponse<FamilyInvitation>>> {
    return api.get('/invitations/my', { params });
  },
};