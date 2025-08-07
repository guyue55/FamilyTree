/// <reference types="vite/client" />

/**
 * Vue单文件组件类型声明
 */
declare module '*.vue' {
  import type { DefineComponent } from 'vue'
  const component: DefineComponent<{}, {}, any>
  export default component
}

/**
 * 环境变量类型声明
 */
interface ImportMetaEnv {
  // 应用基础配置
  readonly VITE_APP_TITLE: string
  readonly VITE_APP_VERSION: string

  // API配置
  readonly VITE_API_BASE_URL: string
  readonly VITE_API_TIMEOUT: string

  // 上传配置
  readonly VITE_UPLOAD_MAX_SIZE: string
  readonly VITE_UPLOAD_ALLOWED_TYPES: string

  // 功能开关
  readonly VITE_ENABLE_MOCK: string
  readonly VITE_ENABLE_DEVTOOLS: string
  readonly VITE_ENABLE_PWA: string

  // 第三方服务
  readonly VITE_SENTRY_DSN: string
  readonly VITE_GOOGLE_ANALYTICS_ID: string

  // 地图服务
  readonly VITE_MAP_API_KEY: string

  // 主题配置
  readonly VITE_DEFAULT_THEME: string
  readonly VITE_ENABLE_DARK_MODE: string

  // 缓存配置
  readonly VITE_CACHE_EXPIRE_TIME: string

  // 调试配置
  readonly VITE_LOG_LEVEL: string
  readonly VITE_ENABLE_CONSOLE_LOG: string
}

interface ImportMeta {
  readonly env: ImportMetaEnv
}

/**
 * 静态资源类型声明
 */
declare module '*.svg' {
  const src: string
  export default src
}

declare module '*.png' {
  const src: string
  export default src
}

declare module '*.jpg' {
  const src: string
  export default src
}

declare module '*.jpeg' {
  const src: string
  export default src
}

declare module '*.gif' {
  const src: string
  export default src
}

declare module '*.webp' {
  const src: string
  export default src
}

declare module '*.ico' {
  const src: string
  export default src
}

/**
 * CSS模块类型声明
 */
declare module '*.module.css' {
  const classes: { readonly [key: string]: string }
  export default classes
}

declare module '*.module.scss' {
  const classes: { readonly [key: string]: string }
  export default classes
}

declare module '*.module.sass' {
  const classes: { readonly [key: string]: string }
  export default classes
}

/**
 * JSON文件类型声明
 */
declare module '*.json' {
  const value: any
  export default value
}

/**
 * 第三方库类型声明
 */
declare module 'nprogress' {
  interface NProgress {
    start(): NProgress
    done(force?: boolean): NProgress
    set(n: number): NProgress
    inc(amount?: number): NProgress
    configure(
      options: Partial<{
        minimum: number
        template: string
        easing: string
        speed: number
        trickle: boolean
        trickleSpeed: number
        showSpinner: boolean
        barSelector: string
        spinnerSelector: string
        parent: string
      }>
    ): NProgress
    status: number | null
  }

  const nprogress: NProgress
  export default nprogress
}

/**
 * 全局类型声明
 */
declare global {
  interface Window {
    // 可以在这里添加全局的window属性类型
  }
}

export {}
