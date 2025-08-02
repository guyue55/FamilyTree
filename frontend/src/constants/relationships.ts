/**
 * 关系类型常量
 * 定义族谱中的各种关系类型
 *
 * @author 古月
 * @version 1.0.0
 */

/**
 * 关系类型常量
 * 与后端数据库设计保持一致
 */
export const RELATIONSHIP_TYPES = {
  // 血缘关系
  PARENT_CHILD: 1, // 父子/母子关系
  GRANDPARENT_GRANDCHILD: 2, // 祖孙关系
  SIBLING: 3, // 兄弟姐妹关系
  UNCLE_NEPHEW: 4, // 叔侄关系
  AUNT_NIECE: 5, // 姑侄关系
  COUSIN: 6, // 堂兄弟姐妹关系

  // 婚姻关系
  SPOUSE: 10, // 配偶关系

  // 姻亲关系
  IN_LAW: 20, // 姻亲关系

  // 收养关系
  ADOPTIVE: 30, // 收养关系

  // 其他关系
  OTHER: 99 // 其他关系
} as const

/**
 * 关系描述映射
 */
export const RELATIONSHIP_DESCRIPTIONS = {
  [RELATIONSHIP_TYPES.PARENT_CHILD]: '父子/母子',
  [RELATIONSHIP_TYPES.GRANDPARENT_GRANDCHILD]: '祖孙',
  [RELATIONSHIP_TYPES.SIBLING]: '兄弟姐妹',
  [RELATIONSHIP_TYPES.UNCLE_NEPHEW]: '叔侄',
  [RELATIONSHIP_TYPES.AUNT_NIECE]: '姑侄',
  [RELATIONSHIP_TYPES.COUSIN]: '堂兄弟姐妹',
  [RELATIONSHIP_TYPES.SPOUSE]: '配偶',
  [RELATIONSHIP_TYPES.IN_LAW]: '姻亲',
  [RELATIONSHIP_TYPES.ADOPTIVE]: '收养',
  [RELATIONSHIP_TYPES.OTHER]: '其他'
} as const

/**
 * 血缘关系类型
 */
export const BLOOD_RELATIONSHIP_TYPES = {
  FATHER: 'father', // 父亲
  MOTHER: 'mother', // 母亲
  SON: 'son', // 儿子
  DAUGHTER: 'daughter', // 女儿
  GRANDFATHER: 'grandfather', // 祖父
  GRANDMOTHER: 'grandmother', // 祖母
  GRANDSON: 'grandson', // 孙子
  GRANDDAUGHTER: 'granddaughter', // 孙女
  BROTHER: 'brother', // 兄弟
  SISTER: 'sister', // 姐妹
  UNCLE: 'uncle', // 叔叔/伯伯
  AUNT: 'aunt', // 姑姑/阿姨
  NEPHEW: 'nephew', // 侄子
  NIECE: 'niece', // 侄女
  COUSIN_MALE: 'cousin_male', // 堂兄弟
  COUSIN_FEMALE: 'cousin_female' // 堂姐妹
} as const

/**
 * 血缘关系显示文本
 */
export const BLOOD_RELATIONSHIP_LABELS = {
  [BLOOD_RELATIONSHIP_TYPES.FATHER]: '父亲',
  [BLOOD_RELATIONSHIP_TYPES.MOTHER]: '母亲',
  [BLOOD_RELATIONSHIP_TYPES.SON]: '儿子',
  [BLOOD_RELATIONSHIP_TYPES.DAUGHTER]: '女儿',
  [BLOOD_RELATIONSHIP_TYPES.GRANDFATHER]: '祖父',
  [BLOOD_RELATIONSHIP_TYPES.GRANDMOTHER]: '祖母',
  [BLOOD_RELATIONSHIP_TYPES.GRANDSON]: '孙子',
  [BLOOD_RELATIONSHIP_TYPES.GRANDDAUGHTER]: '孙女',
  [BLOOD_RELATIONSHIP_TYPES.BROTHER]: '兄弟',
  [BLOOD_RELATIONSHIP_TYPES.SISTER]: '姐妹',
  [BLOOD_RELATIONSHIP_TYPES.UNCLE]: '叔叔/伯伯',
  [BLOOD_RELATIONSHIP_TYPES.AUNT]: '姑姑/阿姨',
  [BLOOD_RELATIONSHIP_TYPES.NEPHEW]: '侄子',
  [BLOOD_RELATIONSHIP_TYPES.NIECE]: '侄女',
  [BLOOD_RELATIONSHIP_TYPES.COUSIN_MALE]: '堂兄弟',
  [BLOOD_RELATIONSHIP_TYPES.COUSIN_FEMALE]: '堂姐妹'
} as const

/**
 * 婚姻关系类型
 */
export const MARRIAGE_RELATIONSHIP_TYPES = {
  HUSBAND: 'husband', // 丈夫
  WIFE: 'wife', // 妻子
  EX_HUSBAND: 'ex_husband', // 前夫
  EX_WIFE: 'ex_wife' // 前妻
} as const

/**
 * 婚姻关系显示文本
 */
export const MARRIAGE_RELATIONSHIP_LABELS = {
  [MARRIAGE_RELATIONSHIP_TYPES.HUSBAND]: '丈夫',
  [MARRIAGE_RELATIONSHIP_TYPES.WIFE]: '妻子',
  [MARRIAGE_RELATIONSHIP_TYPES.EX_HUSBAND]: '前夫',
  [MARRIAGE_RELATIONSHIP_TYPES.EX_WIFE]: '前妻'
} as const

/**
 * 姻亲关系类型
 */
export const IN_LAW_RELATIONSHIP_TYPES = {
  FATHER_IN_LAW: 'father_in_law', // 岳父/公公
  MOTHER_IN_LAW: 'mother_in_law', // 岳母/婆婆
  SON_IN_LAW: 'son_in_law', // 女婿
  DAUGHTER_IN_LAW: 'daughter_in_law', // 儿媳
  BROTHER_IN_LAW: 'brother_in_law', // 姐夫/妹夫/内兄/内弟
  SISTER_IN_LAW: 'sister_in_law' // 嫂子/弟媳/大姨子/小姨子
} as const

/**
 * 姻亲关系显示文本
 */
export const IN_LAW_RELATIONSHIP_LABELS = {
  [IN_LAW_RELATIONSHIP_TYPES.FATHER_IN_LAW]: '岳父/公公',
  [IN_LAW_RELATIONSHIP_TYPES.MOTHER_IN_LAW]: '岳母/婆婆',
  [IN_LAW_RELATIONSHIP_TYPES.SON_IN_LAW]: '女婿',
  [IN_LAW_RELATIONSHIP_TYPES.DAUGHTER_IN_LAW]: '儿媳',
  [IN_LAW_RELATIONSHIP_TYPES.BROTHER_IN_LAW]: '姐夫/妹夫/内兄/内弟',
  [IN_LAW_RELATIONSHIP_TYPES.SISTER_IN_LAW]: '嫂子/弟媳/大姨子/小姨子'
} as const

/**
 * 关系方向常量
 */
export const RELATIONSHIP_DIRECTIONS = {
  BIDIRECTIONAL: 'bidirectional', // 双向关系（如兄弟姐妹）
  UNIDIRECTIONAL: 'unidirectional' // 单向关系（如父子）
} as const

/**
 * 关系强度常量
 */
export const RELATIONSHIP_STRENGTH = {
  PRIMARY: 1, // 直系关系
  SECONDARY: 2, // 旁系关系
  TERTIARY: 3 // 远亲关系
} as const

/**
 * 关系强度显示文本
 */
export const RELATIONSHIP_STRENGTH_LABELS = {
  [RELATIONSHIP_STRENGTH.PRIMARY]: '直系',
  [RELATIONSHIP_STRENGTH.SECONDARY]: '旁系',
  [RELATIONSHIP_STRENGTH.TERTIARY]: '远亲'
} as const
