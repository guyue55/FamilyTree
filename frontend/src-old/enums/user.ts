/**
 * 用户相关枚举
 * 定义用户模块的枚举类型
 *
 * @author 古月
 * @version 1.0.0
 */

/**
 * 用户状态枚举
 */
export enum UserStatus {
  /** 未激活 */
  INACTIVE = 0,
  /** 正常 */
  ACTIVE = 1,
  /** 已暂停 */
  SUSPENDED = 2,
  /** 已删除 */
  DELETED = 3
}

/**
 * 用户角色枚举
 */
export enum UserRole {
  /** 创建者 */
  CREATOR = 1,
  /** 管理员 */
  ADMIN = 2,
  /** 编辑者 */
  EDITOR = 3,
  /** 查看者 */
  VIEWER = 4
}

/**
 * 性别枚举
 */
export enum Gender {
  /** 未知 */
  UNKNOWN = 0,
  /** 男性 */
  MALE = 1,
  /** 女性 */
  FEMALE = 2
}

/**
 * 用户认证状态枚举
 */
export enum AuthStatus {
  /** 未认证 */
  UNVERIFIED = 0,
  /** 邮箱已认证 */
  EMAIL_VERIFIED = 1,
  /** 手机已认证 */
  PHONE_VERIFIED = 2,
  /** 身份已认证 */
  IDENTITY_VERIFIED = 3
}

/**
 * 用户在线状态枚举
 */
export enum OnlineStatus {
  /** 离线 */
  OFFLINE = 0,
  /** 在线 */
  ONLINE = 1,
  /** 忙碌 */
  BUSY = 2,
  /** 离开 */
  AWAY = 3
}

/**
 * 用户偏好设置枚举
 */
export enum UserPreference {
  /** 接收邮件通知 */
  EMAIL_NOTIFICATIONS = 'email_notifications',
  /** 接收短信通知 */
  SMS_NOTIFICATIONS = 'sms_notifications',
  /** 接收推送通知 */
  PUSH_NOTIFICATIONS = 'push_notifications',
  /** 公开个人资料 */
  PUBLIC_PROFILE = 'public_profile',
  /** 允许搜索 */
  ALLOW_SEARCH = 'allow_search',
  /** 显示在线状态 */
  SHOW_ONLINE_STATUS = 'show_online_status'
}

/**
 * 账户类型枚举
 */
export enum AccountType {
  /** 普通用户 */
  REGULAR = 1,
  /** VIP用户 */
  VIP = 2,
  /** 企业用户 */
  ENTERPRISE = 3,
  /** 管理员 */
  ADMIN = 4
}

/**
 * 登录方式枚举
 */
export enum LoginMethod {
  /** 邮箱密码 */
  EMAIL_PASSWORD = 'email_password',
  /** 手机验证码 */
  PHONE_SMS = 'phone_sms',
  /** 微信登录 */
  WECHAT = 'wechat',
  /** QQ登录 */
  QQ = 'qq',
  /** 微博登录 */
  WEIBO = 'weibo',
  /** GitHub登录 */
  GITHUB = 'github'
}

/**
 * 用户操作类型枚举
 */
export enum UserActionType {
  /** 登录 */
  LOGIN = 'login',
  /** 登出 */
  LOGOUT = 'logout',
  /** 注册 */
  REGISTER = 'register',
  /** 更新资料 */
  UPDATE_PROFILE = 'update_profile',
  /** 修改密码 */
  CHANGE_PASSWORD = 'change_password',
  /** 绑定邮箱 */
  BIND_EMAIL = 'bind_email',
  /** 绑定手机 */
  BIND_PHONE = 'bind_phone',
  /** 实名认证 */
  IDENTITY_VERIFY = 'identity_verify',
  /** 创建族谱 */
  CREATE_FAMILY = 'create_family',
  /** 加入族谱 */
  JOIN_FAMILY = 'join_family',
  /** 离开族谱 */
  LEAVE_FAMILY = 'leave_family'
}
