# 族谱系统前端

基于Vue.js 3.4 + Element Plus的现代化族谱管理系统前端应用。

## 技术栈

- **框架**: Vue.js 3.4+ (Composition API)
- **构建工具**: Vite 5.0+
- **UI组件库**: Element Plus 2.4+
- **状态管理**: Pinia 2.1+
- **路由**: Vue Router 4.2+
- **HTTP客户端**: Axios 1.6+
- **图形可视化**: G6 (AntV) 4.8+
- **类型系统**: TypeScript 5.0+
- **代码规范**: ESLint + Prettier
- **测试**: Vitest

## 项目结构

```
frontend/
├── public/              # 静态资源
├── src/                 # 源代码
│   ├── api/            # API接口层
│   ├── assets/         # 静态资源
│   ├── components/     # 公共组件
│   ├── composables/    # 组合式函数
│   ├── constants/      # 常量定义
│   ├── layouts/        # 布局组件
│   ├── pages/          # 页面组件
│   ├── plugins/        # 插件配置
│   ├── router/         # 路由配置
│   ├── stores/         # 状态管理
│   ├── types/          # 类型定义
│   └── utils/          # 工具函数
├── tests/              # 测试文件
└── package.json        # 依赖配置
```

## 快速开始

### 1. 环境准备

确保已安装：
- Node.js >= 18.0.0
- npm >= 9.0.0

### 2. 安装依赖

```bash
# 安装项目依赖
npm install
```

### 3. 环境配置

```bash
# 复制环境变量文件
cp .env.example .env

# 编辑环境变量
# 配置API地址等
```

### 4. 启动开发服务器

```bash
# 启动开发服务器
npm run dev

# 访问 http://localhost:3000
```

## 开发命令

```bash
# 开发服务器
npm run dev

# 构建生产版本
npm run build

# 预览生产版本
npm run preview

# 运行测试
npm run test

# 测试覆盖率
npm run test:coverage

# 代码检查
npm run lint

# 代码格式化
npm run format

# 类型检查
npm run type-check
```

## 开发规范

- 使用TypeScript严格模式
- 组件使用Composition API
- 遵循Vue.js官方风格指南
- 使用Element Plus组件库
- 所有组件必须有类型定义
- 测试覆盖率要求 > 80%

## 浏览器支持

- Chrome >= 87
- Firefox >= 78
- Safari >= 14
- Edge >= 88

## 部署

详见 [部署文档](../docs/06-部署文档/部署文档.md)

## 许可证

MIT License