/**
 * 组件相关类型定义
 * 
 * @author 古月
 * @version 1.0.0
 */

import type { Component, VNode } from 'vue';

/**
 * 组件大小类型
 */
export type ComponentSize = 'small' | 'medium' | 'large';

/**
 * 组件状态类型
 */
export type ComponentStatus = 'default' | 'primary' | 'success' | 'warning' | 'danger' | 'info';

/**
 * 按钮类型
 */
export interface ButtonProps {
  type?: ComponentStatus;
  size?: ComponentSize;
  disabled?: boolean;
  loading?: boolean;
  icon?: string | Component;
  round?: boolean;
  circle?: boolean;
  plain?: boolean;
  text?: boolean;
  link?: boolean;
  block?: boolean;
  nativeType?: 'button' | 'submit' | 'reset';
}

/**
 * 输入框类型
 */
export interface InputProps {
  type?: 'text' | 'password' | 'email' | 'number' | 'tel' | 'url' | 'search';
  size?: ComponentSize;
  disabled?: boolean;
  readonly?: boolean;
  clearable?: boolean;
  showPassword?: boolean;
  placeholder?: string;
  maxlength?: number;
  minlength?: number;
  prefixIcon?: string | Component;
  suffixIcon?: string | Component;
  rows?: number;
  autosize?: boolean | { minRows?: number; maxRows?: number };
  resize?: 'none' | 'both' | 'horizontal' | 'vertical';
}

/**
 * 选择器选项
 */
export interface SelectOption {
  label: string;
  value: any;
  disabled?: boolean;
  children?: SelectOption[];
}

/**
 * 选择器类型
 */
export interface SelectProps {
  options: SelectOption[];
  size?: ComponentSize;
  disabled?: boolean;
  clearable?: boolean;
  filterable?: boolean;
  multiple?: boolean;
  multipleLimit?: number;
  placeholder?: string;
  noDataText?: string;
  noMatchText?: string;
  loading?: boolean;
  loadingText?: string;
  remote?: boolean;
  remoteMethod?: (query: string) => void;
  allowCreate?: boolean;
  defaultFirstOption?: boolean;
  reserveKeyword?: boolean;
  collapseTags?: boolean;
  collapseTagsTooltip?: boolean;
  maxCollapseTags?: number;
}

/**
 * 表格列配置
 */
export interface TableColumn {
  prop?: string;
  label: string;
  width?: string | number;
  minWidth?: string | number;
  fixed?: boolean | 'left' | 'right';
  sortable?: boolean | 'custom';
  sortMethod?: (a: any, b: any) => number;
  sortBy?: string | string[] | ((row: any, index: number) => string);
  resizable?: boolean;
  formatter?: (row: any, column: TableColumn, cellValue: any, index: number) => any;
  showOverflowTooltip?: boolean;
  align?: 'left' | 'center' | 'right';
  headerAlign?: 'left' | 'center' | 'right';
  className?: string;
  labelClassName?: string;
  selectable?: (row: any, index: number) => boolean;
  reserveSelection?: boolean;
  filters?: Array<{ text: string; value: any }>;
  filterPlacement?: string;
  filterMultiple?: boolean;
  filterMethod?: (value: any, row: any, column: TableColumn) => boolean;
  filteredValue?: any[];
}

/**
 * 表格类型
 */
export interface TableProps {
  data: any[];
  columns: TableColumn[];
  height?: string | number;
  maxHeight?: string | number;
  stripe?: boolean;
  border?: boolean;
  size?: ComponentSize;
  fit?: boolean;
  showHeader?: boolean;
  highlightCurrentRow?: boolean;
  currentRowKey?: string | number;
  rowClassName?: string | ((row: any, index: number) => string);
  rowStyle?: object | ((row: any, index: number) => object);
  cellClassName?: string | ((row: any, column: TableColumn, rowIndex: number, columnIndex: number) => string);
  cellStyle?: object | ((row: any, column: TableColumn, rowIndex: number, columnIndex: number) => object);
  headerRowClassName?: string | ((row: any, index: number) => string);
  headerRowStyle?: object | ((row: any, index: number) => object);
  headerCellClassName?: string | ((row: any, column: TableColumn, rowIndex: number, columnIndex: number) => string);
  headerCellStyle?: object | ((row: any, column: TableColumn, rowIndex: number, columnIndex: number) => object);
  rowKey?: string | ((row: any) => string);
  emptyText?: string;
  defaultExpandAll?: boolean;
  expandRowKeys?: any[];
  defaultSort?: { prop: string; order: 'ascending' | 'descending' };
  tooltipEffect?: 'dark' | 'light';
  showSummary?: boolean;
  sumText?: string;
  summaryMethod?: (param: { columns: TableColumn[]; data: any[] }) => any[];
  spanMethod?: (param: { row: any; column: TableColumn; rowIndex: number; columnIndex: number }) => number[] | { rowspan: number; colspan: number };
  selectOnIndeterminate?: boolean;
  indent?: number;
  lazy?: boolean;
  load?: (row: any, treeNode: any, resolve: (data: any[]) => void) => void;
  treeProps?: { hasChildren?: string; children?: string };
}

/**
 * 分页类型
 */
export interface PaginationProps {
  total: number;
  currentPage: number;
  pageSize: number;
  pageSizes?: number[];
  layout?: string;
  background?: boolean;
  small?: boolean;
  disabled?: boolean;
  hideOnSinglePage?: boolean;
  prevText?: string;
  nextText?: string;
  pagerCount?: number;
  popperClass?: string;
}

/**
 * 对话框类型
 */
export interface DialogProps {
  title?: string;
  width?: string | number;
  fullscreen?: boolean;
  top?: string;
  modal?: boolean;
  modalClass?: string;
  appendToBody?: boolean;
  lockScroll?: boolean;
  customClass?: string;
  openDelay?: number;
  closeDelay?: number;
  closeOnClickModal?: boolean;
  closeOnPressEscape?: boolean;
  showClose?: boolean;
  beforeClose?: (done: () => void) => void;
  draggable?: boolean;
  center?: boolean;
  alignCenter?: boolean;
  destroyOnClose?: boolean;
}

/**
 * 抽屉类型
 */
export interface DrawerProps {
  title?: string;
  size?: string | number;
  direction?: 'rtl' | 'ltr' | 'ttb' | 'btt';
  modal?: boolean;
  modalClass?: string;
  appendToBody?: boolean;
  lockScroll?: boolean;
  customClass?: string;
  openDelay?: number;
  closeDelay?: number;
  closeOnClickModal?: boolean;
  closeOnPressEscape?: boolean;
  showClose?: boolean;
  beforeClose?: (done: () => void) => void;
  destroyOnClose?: boolean;
  withHeader?: boolean;
}

/**
 * 消息提示类型
 */
export interface MessageOptions {
  message: string | VNode;
  type?: 'success' | 'warning' | 'info' | 'error';
  iconClass?: string;
  dangerouslyUseHTMLString?: boolean;
  customClass?: string;
  duration?: number;
  showClose?: boolean;
  center?: boolean;
  onClose?: () => void;
  offset?: number;
  appendTo?: string | HTMLElement;
  grouping?: boolean;
}

/**
 * 通知类型
 */
export interface NotificationOptions {
  title?: string;
  message?: string | VNode;
  type?: 'success' | 'warning' | 'info' | 'error';
  iconClass?: string;
  customClass?: string;
  duration?: number;
  position?: 'top-right' | 'top-left' | 'bottom-right' | 'bottom-left';
  showClose?: boolean;
  onClose?: () => void;
  onClick?: () => void;
  offset?: number;
  appendTo?: string | HTMLElement;
  zIndex?: number;
}

/**
 * 加载类型
 */
export interface LoadingOptions {
  target?: string | HTMLElement;
  body?: boolean;
  fullscreen?: boolean;
  lock?: boolean;
  text?: string;
  spinner?: string | Component;
  background?: string;
  customClass?: string;
}

/**
 * 确认框类型
 */
export interface MessageBoxOptions {
  title?: string;
  message?: string | VNode;
  type?: 'success' | 'info' | 'warning' | 'error';
  iconClass?: string;
  customClass?: string;
  callback?: (action: 'confirm' | 'cancel' | 'close', instance: any) => void;
  showClose?: boolean;
  beforeClose?: (action: 'confirm' | 'cancel' | 'close', instance: any, done: () => void) => void;
  distinguishCancelAndClose?: boolean;
  lockScroll?: boolean;
  showCancelButton?: boolean;
  showConfirmButton?: boolean;
  cancelButtonText?: string;
  confirmButtonText?: string;
  cancelButtonClass?: string;
  confirmButtonClass?: string;
  closeOnClickModal?: boolean;
  closeOnPressEscape?: boolean;
  closeOnHashChange?: boolean;
  showInput?: boolean;
  inputPlaceholder?: string;
  inputType?: string;
  inputValue?: string;
  inputPattern?: RegExp;
  inputValidator?: (value: string) => boolean | string;
  inputErrorMessage?: string;
  center?: boolean;
  draggable?: boolean;
  roundButton?: boolean;
  buttonSize?: ComponentSize;
}

/**
 * 表单项类型
 */
export interface FormItemProps {
  label?: string;
  labelWidth?: string | number;
  prop?: string;
  required?: boolean;
  rules?: any | any[];
  error?: string;
  validateStatus?: 'success' | 'warning' | 'error' | 'validating';
  for?: string;
  inlineMessage?: boolean | string;
  showMessage?: boolean;
  size?: ComponentSize;
}

/**
 * 表单类型
 */
export interface FormProps {
  model: Record<string, any>;
  rules?: Record<string, any>;
  inline?: boolean;
  labelPosition?: 'left' | 'right' | 'top';
  labelWidth?: string | number;
  labelSuffix?: string;
  hideRequiredAsterisk?: boolean;
  showMessage?: boolean;
  inlineMessage?: boolean;
  statusIcon?: boolean;
  validateOnRuleChange?: boolean;
  size?: ComponentSize;
  disabled?: boolean;
  scrollToError?: boolean;
  scrollIntoViewOptions?: boolean | ScrollIntoViewOptions;
}

/**
 * 上传文件类型
 */
export interface UploadFile {
  name: string;
  percentage?: number;
  status?: 'ready' | 'uploading' | 'success' | 'fail';
  size?: number;
  response?: any;
  uid: number;
  url?: string;
  raw?: File;
}

/**
 * 上传组件类型
 */
export interface UploadProps {
  action?: string;
  headers?: Record<string, any>;
  method?: string;
  multiple?: boolean;
  data?: Record<string, any>;
  name?: string;
  withCredentials?: boolean;
  showFileList?: boolean;
  drag?: boolean;
  accept?: string;
  onPreview?: (file: UploadFile) => void;
  onRemove?: (file: UploadFile, fileList: UploadFile[]) => void;
  onSuccess?: (response: any, file: UploadFile, fileList: UploadFile[]) => void;
  onError?: (error: Error, file: UploadFile, fileList: UploadFile[]) => void;
  onProgress?: (event: ProgressEvent, file: UploadFile, fileList: UploadFile[]) => void;
  onChange?: (file: UploadFile, fileList: UploadFile[]) => void;
  beforeUpload?: (file: File) => boolean | Promise<File>;
  beforeRemove?: (file: UploadFile, fileList: UploadFile[]) => boolean | Promise<boolean>;
  listType?: 'text' | 'picture' | 'picture-card';
  autoUpload?: boolean;
  fileList?: UploadFile[];
  httpRequest?: (options: any) => void;
  disabled?: boolean;
  limit?: number;
  onExceed?: (files: File[], fileList: UploadFile[]) => void;
}

/**
 * 树形控件节点类型
 */
export interface TreeNode {
  id: string | number;
  label: string;
  children?: TreeNode[];
  disabled?: boolean;
  isLeaf?: boolean;
  [key: string]: any;
}

/**
 * 树形控件类型
 */
export interface TreeProps {
  data: TreeNode[];
  emptyText?: string;
  nodeKey?: string;
  props?: {
    label?: string;
    children?: string;
    disabled?: string;
    isLeaf?: string;
  };
  renderAfterExpand?: boolean;
  load?: (node: any, resolve: (data: TreeNode[]) => void) => void;
  renderContent?: (h: any, context: { node: any; data: TreeNode; store: any }) => VNode;
  highlightCurrent?: boolean;
  defaultExpandAll?: boolean;
  expandOnClickNode?: boolean;
  checkOnClickNode?: boolean;
  autoExpandParent?: boolean;
  defaultExpandedKeys?: (string | number)[];
  showCheckbox?: boolean;
  checkStrictly?: boolean;
  defaultCheckedKeys?: (string | number)[];
  currentNodeKey?: string | number;
  filterNodeMethod?: (value: string, data: TreeNode, node: any) => boolean;
  accordion?: boolean;
  indent?: number;
  iconClass?: string;
  lazy?: boolean;
  draggable?: boolean;
  allowDrag?: (node: any) => boolean;
  allowDrop?: (draggingNode: any, dropNode: any, type: 'prev' | 'inner' | 'next') => boolean;
}