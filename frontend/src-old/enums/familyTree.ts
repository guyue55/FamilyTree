/**
 * 族谱相关枚举
 * 定义族谱模块的枚举类型
 *
 * @author 古月
 * @version 1.0.0
 */

/**
 * 族谱可见性枚举
 */
export enum FamilyTreeVisibility {
  /** 公开 - 所有人可见 */
  PUBLIC = 1,
  /** 家族内 - 仅家族成员可见 */
  FAMILY = 2,
  /** 私有 - 仅创建者可见 */
  PRIVATE = 3
}

/**
 * 族谱状态枚举
 */
export enum FamilyTreeStatus {
  /** 草稿 */
  DRAFT = 0,
  /** 正常 */
  ACTIVE = 1,
  /** 已归档 */
  ARCHIVED = 2,
  /** 已删除 */
  DELETED = 3
}

/**
 * 关系类型枚举
 */
export enum RelationshipType {
  /** 父子/母子关系 */
  PARENT_CHILD = 1,
  /** 祖孙关系 */
  GRANDPARENT_GRANDCHILD = 2,
  /** 兄弟姐妹关系 */
  SIBLING = 3,
  /** 叔侄关系 */
  UNCLE_NEPHEW = 4,
  /** 姑侄关系 */
  AUNT_NIECE = 5,
  /** 堂兄弟姐妹关系 */
  COUSIN = 6,
  /** 配偶关系 */
  SPOUSE = 10,
  /** 姻亲关系 */
  IN_LAW = 20,
  /** 收养关系 */
  ADOPTIVE = 30,
  /** 其他关系 */
  OTHER = 99
}

/**
 * 家族成员角色枚举
 */
export enum FamilyMemberRole {
  /** 族谱创建者 */
  OWNER = 1,
  /** 管理员 */
  ADMIN = 2,
  /** 编辑者 */
  EDITOR = 3,
  /** 查看者 */
  VIEWER = 4
}

/**
 * 家族成员状态枚举
 */
export enum FamilyMemberStatus {
  /** 待审核 */
  PENDING = 0,
  /** 正常 */
  ACTIVE = 1,
  /** 已暂停 */
  SUSPENDED = 2,
  /** 已移除 */
  REMOVED = 3
}

/**
 * 邀请状态枚举
 */
export enum InvitationStatus {
  /** 待处理 */
  PENDING = 0,
  /** 已接受 */
  ACCEPTED = 1,
  /** 已拒绝 */
  REJECTED = 2,
  /** 已过期 */
  EXPIRED = 3,
  /** 已撤销 */
  CANCELLED = 4
}

/**
 * 族谱布局类型枚举
 */
export enum TreeLayoutType {
  /** 水平布局 */
  HORIZONTAL = 'horizontal',
  /** 垂直布局 */
  VERTICAL = 'vertical',
  /** 径向布局 */
  RADIAL = 'radial',
  /** 紧凑布局 */
  COMPACT = 'compact'
}

/**
 * G6图形布局类型枚举
 */
export enum LayoutType {
  /** 树形布局 */
  TREE = 'tree',
  /** 力导向布局 */
  FORCE = 'force',
  /** 环形布局 */
  CIRCULAR = 'circular',
  /** 径向布局 */
  RADIAL = 'radial'
}

/**
 * 节点形状枚举
 */
export enum NodeShape {
  /** 圆形 */
  CIRCLE = 'circle',
  /** 方形 */
  SQUARE = 'square',
  /** 圆角矩形 */
  ROUNDED_RECT = 'rounded_rect',
  /** 椭圆形 */
  ELLIPSE = 'ellipse'
}

/**
 * 连线样式枚举
 */
export enum EdgeStyle {
  /** 直线 */
  STRAIGHT = 'straight',
  /** 曲线 */
  CURVED = 'curved',
  /** 直角线 */
  ORTHOGONAL = 'orthogonal',
  /** 贝塞尔曲线 */
  BEZIER = 'bezier'
}

/**
 * 媒体文件类型枚举
 */
export enum MediaType {
  /** 图片 */
  IMAGE = 'image',
  /** 视频 */
  VIDEO = 'video',
  /** 音频 */
  AUDIO = 'audio',
  /** 文档 */
  DOCUMENT = 'document',
  /** 其他 */
  OTHER = 'other'
}

/**
 * 媒体文件状态枚举
 */
export enum MediaStatus {
  /** 上传中 */
  UPLOADING = 0,
  /** 处理中 */
  PROCESSING = 1,
  /** 已完成 */
  COMPLETED = 2,
  /** 失败 */
  FAILED = 3
}

/**
 * 导出格式枚举
 */
export enum ExportFormat {
  /** Excel格式 */
  EXCEL = 'excel',
  /** CSV格式 */
  CSV = 'csv',
  /** JSON格式 */
  JSON = 'json',
  /** PDF格式 */
  PDF = 'pdf',
  /** GEDCOM格式 */
  GEDCOM = 'gedcom',
  /** 图片格式 */
  IMAGE = 'image'
}

/**
 * 操作类型枚举
 */
export enum OperationType {
  /** 创建 */
  CREATE = 'create',
  /** 更新 */
  UPDATE = 'update',
  /** 删除 */
  DELETE = 'delete',
  /** 查看 */
  VIEW = 'view',
  /** 邀请 */
  INVITE = 'invite',
  /** 加入 */
  JOIN = 'join',
  /** 离开 */
  LEAVE = 'leave',
  /** 导出 */
  EXPORT = 'export',
  /** 导入 */
  IMPORT = 'import'
}

/**
 * 通知类型枚举
 */
export enum NotificationType {
  /** 系统通知 */
  SYSTEM = 'system',
  /** 邀请通知 */
  INVITATION = 'invitation',
  /** 成员变更 */
  MEMBER_CHANGE = 'member_change',
  /** 内容更新 */
  CONTENT_UPDATE = 'content_update',
  /** 权限变更 */
  PERMISSION_CHANGE = 'permission_change',
  /** 安全提醒 */
  SECURITY_ALERT = 'security_alert'
}
