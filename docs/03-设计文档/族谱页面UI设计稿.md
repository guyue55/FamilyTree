# 族谱页面UI设计稿

## 📋 文档信息
- **设计版本**: v1.0
- **创建日期**: 2024年12月
- **设计目标**: 族谱页面完整UI设计方案
- **技术栈**: Vue 3.4+ + TypeScript + Element Plus + G6
- **设计原则**: 传统与现代结合、简洁直观、响应式设计

## 🎯 设计目标与需求

### 核心功能需求
1. **族谱图形展示** - 支持多种布局的树形结构可视化
2. **交互操作** - 节点点击、拖拽、缩放、搜索等
3. **信息管理** - 成员详情、关系查询、筛选功能
4. **协作功能** - 多用户编辑、权限控制、实时同步
5. **数据导入导出** - 支持多种格式的数据交换

### 用户体验目标
- 直观的族谱关系展示
- 流畅的交互操作体验
- 高效的信息查找和管理
- 友好的多设备适配

## 🎨 整体页面布局设计

### 页面结构框架
```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           顶部导航栏 (60px)                                   │
│  Logo + 族谱名称                    搜索框        用户菜单 + 设置              │
├─────────────────────────────────────────────────────────────────────────────┤
│                           工具栏 (50px)                                      │
│  布局选择 | 世代筛选 | 搜索成员 | 称呼查询 | 缩放控制 | 视图选项 | 导出功能      │
├─────────┬───────────────────────────────────────────────────────────────────┤
│         │                                                                   │
│  侧边栏  │                     主图形展示区域                                  │
│ (280px) │                   (族谱树形结构)                                    │
│         │                                                                   │
│ 族谱信息 │                                                                   │
│ 筛选器   │                                                                   │
│ 成员列表 │                                                                   │
│ 统计信息 │                                                                   │
│         │                                                                   │
├─────────┴───────────────────────────────────────────────────────────────────┤
│                           底部状态栏 (40px)                                   │
│  总成员数: 156 | 世代数: 8 | 缩放: 100% | 选中: 张德明 | 最后更新: 2024-12-01  │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 响应式布局适配
- **桌面端 (>1024px)**: 完整布局，侧边栏固定显示
- **平板端 (768-1024px)**: 侧边栏可折叠，工具栏简化
- **移动端 (<768px)**: 侧边栏抽屉式，工具栏垂直排列

## 🔧 顶部导航栏设计

### 布局结构 (高度: 60px)
```
┌─────────────────────────────────────────────────────────────────────────────┐
│ [Logo] 张氏家族族谱              🔍 [搜索框]        🔔 👤 [用户] ⚙️ [设置]    │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 组件详细设计

#### 左侧区域
- **系统Logo**: 24px × 24px，族谱图标
- **族谱名称**: 18px 字体，主色调，可点击返回族谱列表
- **面包屑导航**: 族谱管理 > 张氏家族 > 族谱图形

#### 中间区域
- **全局搜索框**: 
  - 宽度: 300px
  - 占位符: "搜索成员姓名、关键词..."
  - 支持实时搜索建议
  - 快捷键: Ctrl+K

#### 右侧区域
- **通知图标**: 消息提醒，显示未读数量
- **用户头像**: 下拉菜单包含个人资料、设置、退出
- **设置按钮**: 族谱设置、主题切换、帮助

### 样式规范
```css
.header {
  height: 60px;
  background: #ffffff;
  border-bottom: 1px solid #e8e8e8;
  box-shadow: 0 2px 4px rgba(0,0,0,0.05);
  display: flex;
  align-items: center;
  padding: 0 24px;
}

.header-logo {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 18px;
  font-weight: 600;
  color: var(--primary-color);
}

.header-search {
  width: 300px;
  margin: 0 auto;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 16px;
}
```

## 🛠️ 工具栏设计

### 布局结构 (高度: 50px)
```
┌─────────────────────────────────────────────────────────────────────────────┐
│ [布局] [世代] [搜索成员] [称呼查询] | [放大] [缩小] [100%] [适应] | [照片] [日期] [导出] │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 功能组件详细设计

#### 布局控制组
```html
<el-select v-model="layoutType" placeholder="选择布局">
  <el-option label="垂直树形" value="tree-vertical" />
  <el-option label="水平树形" value="tree-horizontal" />
  <el-option label="径向布局" value="radial" />
  <el-option label="力导向" value="force" />
</el-select>
```

#### 世代筛选组
```html
<el-select v-model="generationFilter" placeholder="筛选世代">
  <el-option label="全部世代" value="all" />
  <el-option label="第1-3代" value="1-3" />
  <el-option label="第4-6代" value="4-6" />
  <el-option label="第7-9代" value="7-9" />
</el-select>
```

#### 搜索组件
```html
<el-input 
  v-model="searchKeyword" 
  placeholder="搜索成员..."
  prefix-icon="Search"
  clearable
  @input="handleSearch"
/>
```

#### 称呼查询
```html
<el-button type="primary" @click="openRelationshipQuery">
  <el-icon><Connection /></el-icon>
  称呼查询
</el-button>
```

#### 缩放控制组
```html
<el-button-group>
  <el-button @click="zoomIn">
    <el-icon><ZoomIn /></el-icon>
  </el-button>
  <el-button @click="resetZoom">{{ zoomLevel }}%</el-button>
  <el-button @click="zoomOut">
    <el-icon><ZoomOut /></el-icon>
  </el-button>
  <el-button @click="fitToScreen">适应屏幕</el-button>
</el-button-group>
```

#### 视图选项组
```html
<el-checkbox-group v-model="viewOptions">
  <el-checkbox label="photos">显示照片</el-checkbox>
  <el-checkbox label="dates">显示日期</el-checkbox>
  <el-checkbox label="generation">显示世代</el-checkbox>
</el-checkbox-group>
```

#### 导出功能
```html
<el-dropdown @command="handleExport">
  <el-button type="primary">
    导出 <el-icon><ArrowDown /></el-icon>
  </el-button>
  <template #dropdown>
    <el-dropdown-menu>
      <el-dropdown-item command="png">导出为图片</el-dropdown-item>
      <el-dropdown-item command="pdf">导出为PDF</el-dropdown-item>
      <el-dropdown-item command="excel">导出为Excel</el-dropdown-item>
    </el-dropdown-menu>
  </template>
</el-dropdown>
```

### 样式规范
```css
.toolbar {
  height: 50px;
  background: #fafafa;
  border-bottom: 1px solid #e8e8e8;
  display: flex;
  align-items: center;
  padding: 0 24px;
  gap: 16px;
}

.toolbar-group {
  display: flex;
  align-items: center;
  gap: 8px;
}

.toolbar-divider {
  width: 1px;
  height: 24px;
  background: #e8e8e8;
  margin: 0 8px;
}
```

## 📊 侧边栏设计

### 整体结构 (宽度: 280px)
```
┌─────────────────────────────────┐
│           族谱信息卡片            │
├─────────────────────────────────┤
│           筛选器组件             │
├─────────────────────────────────┤
│           成员列表              │
├─────────────────────────────────┤
│           统计信息              │
└─────────────────────────────────┘
```

### 族谱信息卡片
```html
<el-card class="family-info-card">
  <template #header>
    <div class="card-header">
      <span>张氏家族</span>
      <el-button type="text" @click="toggleSidebar">
        <el-icon><Fold /></el-icon>
      </el-button>
    </div>
  </template>
  
  <div class="family-info">
    <div class="info-item">
      <span class="label">创建者:</span>
      <span class="value">张德明</span>
    </div>
    <div class="info-item">
      <span class="label">创建时间:</span>
      <span class="value">2024-01-15</span>
    </div>
    <div class="info-item">
      <span class="label">祖籍地:</span>
      <span class="value">山西洪洞</span>
    </div>
    <div class="info-item">
      <span class="label">族谱描述:</span>
      <span class="value">张氏家族自明朝洪武年间迁至此地...</span>
    </div>
  </div>
  
  <div class="stats-grid">
    <div class="stat-item">
      <div class="stat-number">156</div>
      <div class="stat-label">总成员</div>
    </div>
    <div class="stat-item">
      <div class="stat-number">8</div>
      <div class="stat-label">世代数</div>
    </div>
    <div class="stat-item">
      <div class="stat-number">89</div>
      <div class="stat-label">男性</div>
    </div>
    <div class="stat-item">
      <div class="stat-number">67</div>
      <div class="stat-label">女性</div>
    </div>
  </div>
</el-card>
```

### 筛选器组件
```html
<el-card class="filter-card">
  <template #header>
    <span>筛选器</span>
  </template>
  
  <div class="filter-group">
    <div class="filter-title">性别</div>
    <el-radio-group v-model="filters.gender" size="small">
      <el-radio-button label="all">全部</el-radio-button>
      <el-radio-button label="male">男性</el-radio-button>
      <el-radio-button label="female">女性</el-radio-button>
    </el-radio-group>
  </div>
  
  <div class="filter-group">
    <div class="filter-title">在世状态</div>
    <el-radio-group v-model="filters.status" size="small">
      <el-radio-button label="all">全部</el-radio-button>
      <el-radio-button label="alive">在世</el-radio-button>
      <el-radio-button label="deceased">已故</el-radio-button>
    </el-radio-group>
  </div>
  
  <div class="filter-group">
    <div class="filter-title">婚姻状态</div>
    <el-radio-group v-model="filters.marriage" size="small">
      <el-radio-button label="all">全部</el-radio-button>
      <el-radio-button label="married">已婚</el-radio-button>
      <el-radio-button label="single">未婚</el-radio-button>
    </el-radio-group>
  </div>
  
  <el-button type="primary" size="small" @click="applyFilters">
    应用筛选
  </el-button>
  <el-button size="small" @click="resetFilters">
    重置
  </el-button>
</el-card>
```

### 成员列表
```html
<el-card class="member-list-card">
  <template #header>
    <div class="card-header">
      <span>成员列表 (156)</span>
      <el-button type="primary" size="small" @click="addMember">
        <el-icon><Plus /></el-icon>
        添加
      </el-button>
    </div>
  </template>
  
  <div class="member-search">
    <el-input 
      v-model="memberSearchKeyword"
      placeholder="搜索成员..."
      prefix-icon="Search"
      size="small"
      clearable
    />
  </div>
  
  <div class="member-list">
    <div 
      v-for="member in filteredMembers" 
      :key="member.id"
      class="member-item"
      :class="{ active: selectedMember?.id === member.id }"
      @click="selectMember(member)"
    >
      <el-avatar 
        :size="40" 
        :src="member.avatar"
        :style="{ 
          border: `2px solid ${member.gender === 1 ? '#1890ff' : '#eb2f96'}` 
        }"
      >
        {{ member.name.charAt(0) }}
      </el-avatar>
      
      <div class="member-info">
        <div class="member-name">{{ member.name }}</div>
        <div class="member-details">
          <span class="generation">第{{ member.generation }}代</span>
          <span class="dates">{{ member.birthYear }}-{{ member.deathYear || '至今' }}</span>
        </div>
      </div>
      
      <div class="member-actions">
        <el-button type="text" size="small" @click.stop="editMember(member)">
          <el-icon><Edit /></el-icon>
        </el-button>
        <el-button type="text" size="small" @click.stop="viewMemberDetail(member)">
          <el-icon><View /></el-icon>
        </el-button>
      </div>
    </div>
  </div>
</el-card>
```

### 样式规范
```css
.sidebar {
  width: 280px;
  background: #ffffff;
  border-right: 1px solid #e8e8e8;
  height: calc(100vh - 110px);
  overflow-y: auto;
  padding: 16px;
}

.sidebar.collapsed {
  width: 60px;
}

.family-info-card,
.filter-card,
.member-list-card {
  margin-bottom: 16px;
}

.stats-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
  margin-top: 16px;
}

.stat-item {
  text-align: center;
  padding: 8px;
  background: #f5f5f5;
  border-radius: 6px;
}

.stat-number {
  font-size: 20px;
  font-weight: 600;
  color: var(--primary-color);
}

.stat-label {
  font-size: 12px;
  color: #666;
  margin-top: 4px;
}

.member-item {
  display: flex;
  align-items: center;
  padding: 12px;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s;
}

.member-item:hover {
  background: #f5f5f5;
}

.member-item.active {
  background: #e6f7ff;
  border: 1px solid var(--primary-color);
}

.member-info {
  flex: 1;
  margin-left: 12px;
}

.member-name {
  font-weight: 500;
  color: #333;
}

.member-details {
  font-size: 12px;
  color: #666;
  margin-top: 4px;
}
```

## 🌳 主图形展示区域设计

### 整体布局
```html
<div class="graph-container">
  <!-- 图形画布 -->
  <div id="family-tree-graph" class="graph-canvas"></div>
  
  <!-- 图形控制器 -->
  <div class="graph-controls">
    <el-button-group>
      <el-button @click="fitToScreen">
        <el-icon><FullScreen /></el-icon>
      </el-button>
      <el-button @click="centerGraph">
        <el-icon><Aim /></el-icon>
      </el-button>
      <el-button @click="toggleFullscreen">
        <el-icon><ScaleToOriginal /></el-icon>
      </el-button>
    </el-button-group>
  </div>
  
  <!-- 缩略图导航 -->
  <div class="minimap-container">
    <div id="minimap" class="minimap"></div>
  </div>
</div>
```

### 族谱节点设计

#### 节点结构
```typescript
interface FamilyTreeNode {
  id: string;
  name: string;
  gender: 1 | 2; // 1-男性, 2-女性
  avatar?: string;
  birthYear?: number;
  deathYear?: number;
  generation: number;
  isAlive: boolean;
  children?: FamilyTreeNode[];
  spouse?: FamilyTreeNode;
}
```

#### 节点视觉设计
```css
.tree-node {
  width: 120px;
  height: 80px;
  background: #ffffff;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.tree-node:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0,0,0,0.15);
}

.tree-node.male {
  border-left: 4px solid #1890ff;
}

.tree-node.female {
  border-left: 4px solid #eb2f96;
}

.tree-node.selected {
  border: 2px solid var(--primary-color);
  background: #e6f7ff;
}

.node-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  margin-bottom: 4px;
}

.node-name {
  font-size: 14px;
  font-weight: 500;
  color: #333;
  text-align: center;
  margin-bottom: 2px;
}

.node-dates {
  font-size: 10px;
  color: #666;
  text-align: center;
}

.node-generation {
  position: absolute;
  top: -8px;
  right: -8px;
  background: var(--primary-color);
  color: white;
  font-size: 10px;
  padding: 2px 6px;
  border-radius: 10px;
}
```

#### 连接线设计
```css
.connection-line {
  stroke: #d9d9d9;
  stroke-width: 2px;
  fill: none;
}

.connection-line.blood-relation {
  stroke: #1890ff;
  stroke-width: 2px;
}

.connection-line.marriage-relation {
  stroke: #eb2f96;
  stroke-width: 2px;
  stroke-dasharray: 5,5;
}

.connection-line.adoption-relation {
  stroke: #52c41a;
  stroke-width: 2px;
  stroke-dasharray: 2,2;
}
```

### G6图形配置
```typescript
const graphConfig = {
  container: 'family-tree-graph',
  width: 800,
  height: 600,
  modes: {
    default: [
      'drag-canvas',
      'zoom-canvas',
      'drag-node',
      'click-select',
    ],
  },
  defaultNode: {
    type: 'family-member',
    size: [120, 80],
    style: {
      fill: '#ffffff',
      stroke: '#d9d9d9',
      lineWidth: 1,
      radius: 8,
    },
    labelCfg: {
      position: 'center',
      style: {
        fontSize: 14,
        fontWeight: 500,
      },
    },
  },
  defaultEdge: {
    type: 'cubic-horizontal',
    style: {
      stroke: '#d9d9d9',
      lineWidth: 2,
    },
  },
  layout: {
    type: 'dagre',
    direction: 'TB',
    rankdir: 'TB',
    nodesep: 30,
    ranksep: 50,
  },
};
```

## 💬 成员详情弹窗设计

### 弹窗结构
```html
<el-dialog 
  v-model="memberDetailVisible"
  :title="selectedMember?.name"
  width="800px"
  class="member-detail-dialog"
>
  <div class="member-detail-content">
    <!-- 头部信息 -->
    <div class="member-header">
      <el-avatar :size="80" :src="selectedMember?.avatar">
        {{ selectedMember?.name?.charAt(0) }}
      </el-avatar>
      
      <div class="member-basic-info">
        <h3>{{ selectedMember?.name }}</h3>
        <div class="basic-details">
          <el-tag :type="selectedMember?.gender === 1 ? 'primary' : 'danger'">
            {{ selectedMember?.gender === 1 ? '男性' : '女性' }}
          </el-tag>
          <span class="generation-tag">第{{ selectedMember?.generation }}代</span>
          <span class="dates">
            {{ selectedMember?.birthYear }} - {{ selectedMember?.deathYear || '至今' }}
          </span>
        </div>
      </div>
      
      <div class="member-actions">
        <el-button type="primary" @click="editMember">编辑</el-button>
        <el-button @click="viewRelationships">查看关系</el-button>
      </div>
    </div>
    
    <!-- 详细信息标签页 -->
    <el-tabs v-model="activeTab" class="member-tabs">
      <el-tab-pane label="基本信息" name="basic">
        <div class="info-grid">
          <div class="info-item">
            <span class="label">姓名:</span>
            <span class="value">{{ selectedMember?.name }}</span>
          </div>
          <div class="info-item">
            <span class="label">性别:</span>
            <span class="value">{{ selectedMember?.gender === 1 ? '男性' : '女性' }}</span>
          </div>
          <div class="info-item">
            <span class="label">出生日期:</span>
            <span class="value">{{ selectedMember?.birthDate }}</span>
          </div>
          <div class="info-item">
            <span class="label">出生地:</span>
            <span class="value">{{ selectedMember?.birthPlace }}</span>
          </div>
          <div class="info-item">
            <span class="label">职业:</span>
            <span class="value">{{ selectedMember?.occupation }}</span>
          </div>
          <div class="info-item">
            <span class="label">学历:</span>
            <span class="value">{{ selectedMember?.education }}</span>
          </div>
        </div>
      </el-tab-pane>
      
      <el-tab-pane label="关系网络" name="relationships">
        <div class="relationships-content">
          <div class="relationship-group">
            <h4>父母</h4>
            <div class="relationship-list">
              <div v-for="parent in selectedMember?.parents" :key="parent.id" class="relationship-item">
                <el-avatar :size="32" :src="parent.avatar">{{ parent.name.charAt(0) }}</el-avatar>
                <span>{{ parent.name }}</span>
                <el-tag size="small">{{ parent.relation }}</el-tag>
              </div>
            </div>
          </div>
          
          <div class="relationship-group">
            <h4>配偶</h4>
            <div class="relationship-list">
              <div v-for="spouse in selectedMember?.spouses" :key="spouse.id" class="relationship-item">
                <el-avatar :size="32" :src="spouse.avatar">{{ spouse.name.charAt(0) }}</el-avatar>
                <span>{{ spouse.name }}</span>
                <el-tag size="small" type="danger">配偶</el-tag>
              </div>
            </div>
          </div>
          
          <div class="relationship-group">
            <h4>子女</h4>
            <div class="relationship-list">
              <div v-for="child in selectedMember?.children" :key="child.id" class="relationship-item">
                <el-avatar :size="32" :src="child.avatar">{{ child.name.charAt(0) }}</el-avatar>
                <span>{{ child.name }}</span>
                <el-tag size="small" type="success">{{ child.relation }}</el-tag>
              </div>
            </div>
          </div>
        </div>
      </el-tab-pane>
      
      <el-tab-pane label="照片相册" name="photos">
        <div class="photos-grid">
          <div v-for="photo in selectedMember?.photos" :key="photo.id" class="photo-item">
            <el-image 
              :src="photo.url" 
              :preview-src-list="[photo.url]"
              fit="cover"
              class="photo-image"
            />
            <div class="photo-info">
              <div class="photo-title">{{ photo.title }}</div>
              <div class="photo-date">{{ photo.date }}</div>
            </div>
          </div>
        </div>
      </el-tab-pane>
      
      <el-tab-pane label="生平事迹" name="biography">
        <div class="biography-content">
          <el-timeline>
            <el-timeline-item 
              v-for="event in selectedMember?.lifeEvents" 
              :key="event.id"
              :timestamp="event.date"
            >
              <h4>{{ event.title }}</h4>
              <p>{{ event.description }}</p>
            </el-timeline-item>
          </el-timeline>
        </div>
      </el-tab-pane>
    </el-tabs>
  </div>
  
  <template #footer>
    <el-button @click="memberDetailVisible = false">关闭</el-button>
    <el-button type="primary" @click="editMember">编辑信息</el-button>
  </template>
</el-dialog>
```

## 🔍 称呼查询功能设计

### 查询界面
```html
<el-dialog 
  v-model="relationshipQueryVisible"
  title="称呼关系查询"
  width="600px"
  class="relationship-query-dialog"
>
  <div class="query-content">
    <!-- 选择基准人员 -->
    <div class="query-section">
      <h4>选择基准人员</h4>
      <el-select 
        v-model="baseMember" 
        placeholder="请选择基准人员"
        filterable
        clearable
      >
        <el-option 
          v-for="member in allMembers"
          :key="member.id"
          :label="member.name"
          :value="member"
        >
          <div class="member-option">
            <el-avatar :size="24" :src="member.avatar">
              {{ member.name.charAt(0) }}
            </el-avatar>
            <span>{{ member.name }}</span>
            <span class="generation">第{{ member.generation }}代</span>
          </div>
        </el-option>
      </el-select>
    </div>
    
    <!-- 查询结果 -->
    <div v-if="baseMember" class="query-results">
      <h4>{{ baseMember.name }} 对其他成员的称呼</h4>
      
      <div class="relationship-grid">
        <div 
          v-for="relationship in calculatedRelationships" 
          :key="relationship.targetId"
          class="relationship-card"
        >
          <el-avatar :size="40" :src="relationship.target.avatar">
            {{ relationship.target.name.charAt(0) }}
          </el-avatar>
          
          <div class="relationship-info">
            <div class="target-name">{{ relationship.target.name }}</div>
            <div class="relationship-title">{{ relationship.title }}</div>
            <div class="relationship-dialect">{{ relationship.dialect }}</div>
          </div>
          
          <div class="relationship-path">
            <el-tag size="small" type="info">
              {{ relationship.path }}
            </el-tag>
          </div>
        </div>
      </div>
    </div>
  </div>
  
  <template #footer>
    <el-button @click="relationshipQueryVisible = false">关闭</el-button>
    <el-button type="primary" @click="exportRelationships">导出称呼表</el-button>
  </template>
</el-dialog>
```

### 称呼计算逻辑
```typescript
interface RelationshipResult {
  targetId: string;
  target: FamilyMember;
  title: string;        // 标准称呼
  dialect: string;      // 方言称呼
  path: string;         // 关系路径
  distance: number;     // 关系距离
}

class RelationshipCalculator {
  /**
   * 计算两个成员之间的称呼关系
   */
  calculateRelationship(
    baseMember: FamilyMember, 
    targetMember: FamilyMember
  ): RelationshipResult {
    // 实现称呼计算逻辑
    const path = this.findRelationshipPath(baseMember, targetMember);
    const title = this.getStandardTitle(path);
    const dialect = this.getDialectTitle(path);
    
    return {
      targetId: targetMember.id,
      target: targetMember,
      title,
      dialect,
      path: this.formatPath(path),
      distance: path.length,
    };
  }
  
  /**
   * 查找关系路径
   */
  private findRelationshipPath(
    from: FamilyMember, 
    to: FamilyMember
  ): RelationshipPath[] {
    // 使用广度优先搜索找到最短路径
    // 实现具体的路径查找算法
  }
  
  /**
   * 获取标准称呼
   */
  private getStandardTitle(path: RelationshipPath[]): string {
    // 根据关系路径计算标准称呼
    // 实现称呼规则映射
  }
}
```

## 📱 响应式设计适配

### 移动端适配 (<768px)
```css
@media (max-width: 767px) {
  .header {
    padding: 0 16px;
  }
  
  .header-search {
    width: 200px;
  }
  
  .toolbar {
    flex-direction: column;
    height: auto;
    padding: 12px 16px;
  }
  
  .toolbar-group {
    width: 100%;
    justify-content: space-between;
    margin-bottom: 8px;
  }
  
  .sidebar {
    position: fixed;
    left: -280px;
    top: 110px;
    z-index: 1000;
    transition: left 0.3s ease;
  }
  
  .sidebar.open {
    left: 0;
  }
  
  .graph-container {
    padding: 8px;
  }
  
  .tree-node {
    width: 80px;
    height: 60px;
    padding: 4px;
  }
  
  .node-avatar {
    width: 24px;
    height: 24px;
  }
  
  .node-name {
    font-size: 10px;
  }
  
  .member-detail-dialog {
    width: 95% !important;
    margin: 5vh auto;
  }
}
```

### 平板端适配 (768px-1024px)
```css
@media (min-width: 768px) and (max-width: 1024px) {
  .sidebar {
    width: 240px;
  }
  
  .toolbar-group {
    gap: 12px;
  }
  
  .tree-node {
    width: 100px;
    height: 70px;
  }
  
  .member-detail-dialog {
    width: 80%;
  }
}
```

## 🎨 主题和样式系统

### CSS变量定义
```css
:root {
  /* 主色调 */
  --primary-color: #C8102E;
  --primary-light: #E8394A;
  --primary-dark: #A00D24;
  
  /* 辅助色 */
  --secondary-color: #D4AF37;
  --success-color: #52C41A;
  --warning-color: #FAAD14;
  --error-color: #FF4D4F;
  --info-color: #1890FF;
  
  /* 中性色 */
  --text-primary: #333333;
  --text-secondary: #666666;
  --text-placeholder: #999999;
  --border-color: #E8E8E8;
  --background-color: #FFFFFF;
  --background-light: #FAFAFA;
  
  /* 间距 */
  --spacing-xs: 4px;
  --spacing-sm: 8px;
  --spacing-md: 16px;
  --spacing-lg: 24px;
  --spacing-xl: 32px;
  
  /* 圆角 */
  --border-radius-sm: 4px;
  --border-radius-md: 6px;
  --border-radius-lg: 8px;
  
  /* 阴影 */
  --shadow-sm: 0 1px 2px rgba(0,0,0,0.05);
  --shadow-md: 0 2px 8px rgba(0,0,0,0.1);
  --shadow-lg: 0 4px 12px rgba(0,0,0,0.15);
  
  /* 字体 */
  --font-family: "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", sans-serif;
  --font-size-xs: 10px;
  --font-size-sm: 12px;
  --font-size-md: 14px;
  --font-size-lg: 16px;
  --font-size-xl: 18px;
}
```

### 深色主题支持
```css
[data-theme="dark"] {
  --text-primary: #FFFFFF;
  --text-secondary: #CCCCCC;
  --text-placeholder: #999999;
  --border-color: #404040;
  --background-color: #1F1F1F;
  --background-light: #2A2A2A;
}
```

## 🔧 组件状态管理

### Pinia Store设计
```typescript
// stores/familyTree.ts
export const useFamilyTreeStore = defineStore('familyTree', {
  state: () => ({
    // 当前族谱信息
    currentFamilyTree: null as FamilyTree | null,
    
    // 成员数据
    members: [] as FamilyMember[],
    selectedMember: null as FamilyMember | null,
    
    // 视图状态
    layoutType: 'tree-vertical' as LayoutType,
    zoomLevel: 100,
    viewOptions: {
      showPhotos: true,
      showDates: true,
      showGeneration: true,
    },
    
    // 筛选状态
    filters: {
      gender: 'all',
      status: 'all',
      marriage: 'all',
      generation: 'all',
    },
    
    // UI状态
    sidebarCollapsed: false,
    memberDetailVisible: false,
    relationshipQueryVisible: false,
    
    // 搜索状态
    searchKeyword: '',
    memberSearchKeyword: '',
  }),
  
  getters: {
    filteredMembers: (state) => {
      return state.members.filter(member => {
        // 实现筛选逻辑
        return true;
      });
    },
    
    membersByGeneration: (state) => {
      return state.members.reduce((acc, member) => {
        const gen = member.generation;
        if (!acc[gen]) acc[gen] = [];
        acc[gen].push(member);
        return acc;
      }, {} as Record<number, FamilyMember[]>);
    },
  },
  
  actions: {
    // 加载族谱数据
    async loadFamilyTree(id: string) {
      // 实现数据加载逻辑
    },
    
    // 选择成员
    selectMember(member: FamilyMember) {
      this.selectedMember = member;
    },
    
    // 更新视图选项
    updateViewOptions(options: Partial<ViewOptions>) {
      this.viewOptions = { ...this.viewOptions, ...options };
    },
    
    // 应用筛选器
    applyFilters(filters: Partial<FilterOptions>) {
      this.filters = { ...this.filters, ...filters };
    },
    
    // 切换侧边栏
    toggleSidebar() {
      this.sidebarCollapsed = !this.sidebarCollapsed;
    },
  },
});
```

## 📋 开发实现清单

### 第一阶段：基础框架 (1-2周)
- [ ] 页面布局组件开发
- [ ] 顶部导航栏组件
- [ ] 侧边栏组件
- [ ] 工具栏组件
- [ ] 基础状态管理

### 第二阶段：图形展示 (2-3周)
- [ ] G6图形引擎集成
- [ ] 族谱节点组件
- [ ] 连接线渲染
- [ ] 布局算法实现
- [ ] 交互功能开发

### 第三阶段：功能完善 (2-3周)
- [ ] 成员详情弹窗
- [ ] 称呼查询功能
- [ ] 筛选和搜索
- [ ] 数据导入导出
- [ ] 权限控制

### 第四阶段：优化完善 (1-2周)
- [ ] 响应式适配
- [ ] 性能优化
- [ ] 无障碍支持
- [ ] 测试和调试

## 🎯 设计总结

这个族谱页面UI设计方案具有以下特点：

### 设计优势
1. **功能完整** - 涵盖族谱展示、管理、查询的所有核心功能
2. **用户友好** - 直观的界面设计和流畅的交互体验
3. **技术先进** - 基于Vue 3和G6的现代化技术栈
4. **扩展性强** - 模块化设计，便于后续功能扩展
5. **响应式** - 完美适配各种设备和屏幕尺寸

### 创新亮点
1. **智能称呼查询** - 自动计算家族成员间的称呼关系
2. **多样化布局** - 支持多种族谱展示布局
3. **实时协作** - 支持多用户同时编辑族谱
4. **丰富交互** - 拖拽、缩放、搜索等多种交互方式

这个设计方案为族谱系统提供了坚实的UI基础，确保能够构建出功能强大、用户体验优秀的族谱管理平台。

## 设计概述

### 页面定位
族谱页面是系统的核心功能页面，主要用于展示和管理家族族谱的树形结构，支持成员信息查看、关系查询、协作编辑等功能。

### 设计目标
1. **直观展示**: 清晰展示家族关系树形结构
2. **高效操作**: 提供便捷的成员管理和关系建立功能
3. **信息丰富**: 支持多层次信息展示和查询
4. **交互友好**: 提供流畅的缩放、拖拽、搜索等交互体验

## 页面布局设计

### 整体布局结构
```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                              顶部工具栏 (60px)                                    │
├─────────────────────────────────────────────────────────────────────────────────┤
│  侧边栏  │                                                                       │
│ (280px) │                        族谱图形展示区域                                  │
│         │                                                                       │
│ 成员列表 │                                                                       │
│ 筛选器   │                                                                       │
│ 统计信息 │                                                                       │
│         │                                                                       │
├─────────────────────────────────────────────────────────────────────────────────┤
│                              底部状态栏 (40px)                                    │
└─────────────────────────────────────────────────────────────────────────────────┘
```

### 响应式布局
- **桌面端 (>1200px)**: 完整三栏布局
- **平板端 (768px-1200px)**: 侧边栏可收缩，主要展示图形区域
- **移动端 (<768px)**: 侧边栏改为抽屉式，图形区域全屏显示

## 详细设计规范

### 1. 顶部工具栏设计

#### 1.1 布局结构
```css
.graph-toolbar {
  height: 60px;
  background: #ffffff;
  border-bottom: 1px solid #e4e7ed;
  padding: 0 24px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}
```

#### 1.2 左侧控制区域
```html
<div class="toolbar-left">
  <!-- 布局选择器 -->
  <el-select v-model="layoutType" placeholder="布局方式" size="default" style="width: 140px;">
    <el-option label="垂直树形" value="tree-vertical" />
    <el-option label="水平树形" value="tree-horizontal" />
    <el-option label="径向布局" value="radial" />
    <el-option label="力导向图" value="force" />
  </el-select>

  <!-- 世代筛选器 -->
  <el-select v-model="generationFilter" placeholder="世代范围" size="default" style="width: 120px;">
    <el-option label="全部世代" value="all" />
    <el-option label="1-3世代" value="1-3" />
    <el-option label="1-5世代" value="1-5" />
    <el-option label="1-7世代" value="1-7" />
  </el-select>

  <!-- 搜索框 -->
  <el-input 
    v-model="searchKeyword" 
    placeholder="搜索成员姓名" 
    size="default" 
    style="width: 200px;"
    clearable
  >
    <template #prefix>
      <el-icon><Search /></el-icon>
    </template>
  </el-input>

  <!-- 称呼查询按钮 -->
  <el-button type="primary" size="default" :icon="Connection">
    称呼查询
  </el-button>
</div>
```

#### 1.3 右侧操作区域
```html
<div class="toolbar-right">
  <!-- 缩放控制 -->
  <el-button-group>
    <el-button size="default" :icon="ZoomIn" @click="zoomIn">放大</el-button>
    <el-button size="default" :icon="ZoomOut" @click="zoomOut">缩小</el-button>
    <el-button size="default" :icon="Refresh" @click="resetZoom">重置</el-button>
    <el-button size="default" :icon="FullScreen" @click="toggleFullscreen">全屏</el-button>
  </el-button-group>

  <!-- 视图选项 -->
  <el-dropdown @command="handleViewOption">
    <el-button size="default">
      视图选项 <el-icon class="el-icon--right"><ArrowDown /></el-icon>
    </el-button>
    <template #dropdown>
      <el-dropdown-menu>
        <el-dropdown-item command="show-photos">显示照片</el-dropdown-item>
        <el-dropdown-item command="show-dates">显示生卒年</el-dropdown-item>
        <el-dropdown-item command="show-generation">显示世代</el-dropdown-item>
        <el-dropdown-item command="show-relationship">显示关系线</el-dropdown-item>
      </el-dropdown-menu>
    </template>
  </el-dropdown>

  <!-- 导出功能 -->
  <el-dropdown @command="handleExport">
    <el-button type="primary" size="default">
      导出 <el-icon class="el-icon--right"><Download /></el-icon>
    </el-button>
    <template #dropdown>
      <el-dropdown-menu>
        <el-dropdown-item command="export-png">导出PNG图片</el-dropdown-item>
        <el-dropdown-item command="export-pdf">导出PDF文档</el-dropdown-item>
        <el-dropdown-item command="export-excel">导出Excel表格</el-dropdown-item>
      </el-dropdown-menu>
    </template>
  </el-dropdown>
</div>
```

### 2. 侧边栏设计

#### 2.1 整体结构
```css
.sidebar {
  width: 280px;
  background: #fafafa;
  border-right: 1px solid #e4e7ed;
  display: flex;
  flex-direction: column;
  height: 100%;
}
```

#### 2.2 族谱信息卡片
```html
<div class="family-info-card">
  <div class="family-header">
    <div class="family-avatar">
      <img src="family-cover.jpg" alt="族谱封面" />
    </div>
    <div class="family-details">
      <h3 class="family-name">张氏族谱</h3>
      <p class="family-description">源远流长的张氏家族</p>
      <div class="family-meta">
        <span class="meta-item">
          <el-icon><User /></el-icon>
          <span>125人</span>
        </span>
        <span class="meta-item">
          <el-icon><Calendar /></el-icon>
          <span>8世代</span>
        </span>
      </div>
    </div>
  </div>
</div>
```

#### 2.3 快速筛选器
```html
<div class="quick-filters">
  <h4 class="filter-title">快速筛选</h4>
  
  <!-- 性别筛选 -->
  <div class="filter-group">
    <label class="filter-label">性别</label>
    <el-checkbox-group v-model="genderFilter" size="small">
      <el-checkbox label="male">男性</el-checkbox>
      <el-checkbox label="female">女性</el-checkbox>
    </el-checkbox-group>
  </div>

  <!-- 世代筛选 -->
  <div class="filter-group">
    <label class="filter-label">世代</label>
    <el-slider 
      v-model="generationRange" 
      range 
      :min="1" 
      :max="10" 
      :marks="generationMarks"
    />
  </div>

  <!-- 年龄筛选 -->
  <div class="filter-group">
    <label class="filter-label">年龄</label>
    <el-radio-group v-model="ageFilter" size="small">
      <el-radio label="all">全部</el-radio>
      <el-radio label="living">在世</el-radio>
      <el-radio label="deceased">已故</el-radio>
    </el-radio-group>
  </div>
</div>
```

#### 2.4 成员列表
```html
<div class="member-list">
  <div class="list-header">
    <h4>成员列表</h4>
    <el-button type="text" size="small" @click="addMember">
      <el-icon><Plus /></el-icon>
      添加成员
    </el-button>
  </div>

  <div class="list-content">
    <el-virtual-list 
      :data="filteredMembers" 
      :height="400" 
      :item-size="60"
    >
      <template #default="{ item }">
        <div class="member-item" @click="selectMember(item)">
          <el-avatar :src="item.avatar" :size="40" class="member-avatar">
            {{ item.name.charAt(0) }}
          </el-avatar>
          <div class="member-info">
            <div class="member-name">{{ item.name }}</div>
            <div class="member-meta">
              <span class="generation">第{{ item.generation }}世</span>
              <span class="gender" :class="item.gender">
                {{ item.gender === 'male' ? '男' : '女' }}
              </span>
            </div>
          </div>
          <div class="member-actions">
            <el-button type="text" size="small" @click.stop="editMember(item)">
              <el-icon><Edit /></el-icon>
            </el-button>
          </div>
        </div>
      </template>
    </el-virtual-list>
  </div>
</div>
```

### 3. 主图形展示区域设计

#### 3.1 容器结构
```css
.graph-container {
  flex: 1;
  position: relative;
  background: #ffffff;
  overflow: hidden;
}

.graph-canvas {
  width: 100%;
  height: 100%;
  cursor: grab;
}

.graph-canvas:active {
  cursor: grabbing;
}
```

#### 3.2 节点设计规范

##### 3.2.1 基础节点样式
```css
.graph-node {
  position: relative;
  cursor: pointer;
  transition: all 0.3s ease;
}

.graph-node:hover {
  transform: scale(1.05);
  filter: drop-shadow(0 4px 8px rgba(0, 0, 0, 0.15));
}

.graph-node.selected {
  transform: scale(1.1);
  filter: drop-shadow(0 6px 12px rgba(200, 16, 46, 0.3));
}
```

##### 3.2.2 男性节点样式
```css
.node-male {
  .node-border {
    border: 3px solid #1890ff;
    background: linear-gradient(135deg, #e6f7ff 0%, #bae7ff 100%);
  }
  
  .node-avatar {
    border: 2px solid #1890ff;
  }
}
```

##### 3.2.3 女性节点样式
```css
.node-female {
  .node-border {
    border: 3px solid #eb2f96;
    background: linear-gradient(135deg, #fff0f6 0%, #ffadd6 100%);
  }
  
  .node-avatar {
    border: 2px solid #eb2f96;
  }
}
```

##### 3.2.4 节点内容结构
```html
<div class="graph-node" :class="[`node-${member.gender}`, { selected: isSelected }]">
  <!-- 节点主体 -->
  <div class="node-body">
    <!-- 头像区域 -->
    <div class="node-avatar">
      <img v-if="member.avatar" :src="member.avatar" :alt="member.name" />
      <div v-else class="avatar-placeholder">
        {{ member.name.charAt(0) }}
      </div>
    </div>
    
    <!-- 信息区域 -->
    <div class="node-info">
      <div class="node-name">{{ member.name }}</div>
      <div class="node-dates" v-if="showDates">
        {{ formatDates(member.birthDate, member.deathDate) }}
      </div>
      <div class="node-generation" v-if="showGeneration">
        第{{ member.generation }}世
      </div>
    </div>
  </div>
  
  <!-- 状态指示器 -->
  <div class="node-indicators">
    <div v-if="member.isAlive" class="indicator alive"></div>
    <div v-if="member.hasChildren" class="indicator has-children"></div>
    <div v-if="member.isMarried" class="indicator married"></div>
  </div>
  
  <!-- 操作按钮 -->
  <div class="node-actions" v-show="isHovered">
    <el-button type="primary" size="small" circle @click.stop="viewDetails">
      <el-icon><View /></el-icon>
    </el-button>
    <el-button type="success" size="small" circle @click.stop="editMember">
      <el-icon><Edit /></el-icon>
    </el-button>
    <el-button type="info" size="small" circle @click.stop="addRelation">
      <el-icon><Connection /></el-icon>
    </el-button>
  </div>
</div>
```

#### 3.3 连线设计规范

##### 3.3.1 血缘关系线
```css
.relationship-line.blood {
  stroke: #1890ff;
  stroke-width: 2px;
  fill: none;
}

.relationship-line.blood.parent-child {
  stroke-dasharray: none;
}

.relationship-line.blood.sibling {
  stroke-dasharray: 5,5;
}
```

##### 3.3.2 婚姻关系线
```css
.relationship-line.marriage {
  stroke: #eb2f96;
  stroke-width: 3px;
  fill: none;
  stroke-dasharray: none;
}
```

##### 3.3.3 收养关系线
```css
.relationship-line.adoption {
  stroke: #52c41a;
  stroke-width: 2px;
  fill: none;
  stroke-dasharray: 10,5;
}
```

### 4. 底部状态栏设计

#### 4.1 布局结构
```css
.status-bar {
  height: 40px;
  background: #f5f5f5;
  border-top: 1px solid #e4e7ed;
  padding: 0 24px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  font-size: 12px;
  color: #666;
}
```

#### 4.2 内容设计
```html
<div class="status-bar">
  <div class="status-left">
    <span class="status-item">
      总成员: <strong>{{ totalMembers }}</strong>
    </span>
    <span class="status-item">
      已选择: <strong>{{ selectedMembers.length }}</strong>
    </span>
    <span class="status-item" v-if="lastOperation">
      {{ lastOperation }}
    </span>
  </div>
  
  <div class="status-right">
    <span class="status-item">
      缩放: <strong>{{ Math.round(zoomLevel * 100) }}%</strong>
    </span>
    <span class="status-item">
      布局: <strong>{{ layoutTypeText }}</strong>
    </span>
    <span class="status-item">
      最后更新: <strong>{{ formatTime(lastUpdateTime) }}</strong>
    </span>
  </div>
</div>
```

## 交互设计规范

### 1. 节点交互

#### 1.1 点击交互
- **单击**: 选中节点，显示基本信息
- **双击**: 打开成员详情弹窗
- **右键**: 显示上下文菜单

#### 1.2 悬浮交互
- **悬浮进入**: 节点放大，显示操作按钮
- **悬浮离开**: 恢复原始大小，隐藏操作按钮

#### 1.3 拖拽交互
- **拖拽节点**: 调整节点位置（仅在自由布局模式下）
- **拖拽到其他节点**: 建立关系连线

### 2. 画布交互

#### 2.1 缩放交互
- **鼠标滚轮**: 以鼠标位置为中心缩放
- **双指手势**: 移动端缩放支持
- **缩放范围**: 10% - 500%

#### 2.2 平移交互
- **鼠标拖拽**: 拖拽空白区域平移画布
- **键盘方向键**: 精确平移控制

#### 2.3 框选交互
- **按住Ctrl+拖拽**: 框选多个节点
- **框选反馈**: 显示选择框和选中数量

### 3. 搜索交互

#### 3.1 实时搜索
- **输入响应**: 300ms防抖延迟
- **高亮显示**: 匹配的节点高亮显示
- **自动定位**: 自动移动到第一个匹配结果

#### 3.2 搜索结果
- **结果列表**: 显示所有匹配的成员
- **快速跳转**: 点击结果直接定位到节点

## 弹窗和抽屉设计

### 1. 成员详情弹窗

#### 1.1 弹窗结构
```html
<el-dialog 
  v-model="memberDetailVisible" 
  :title="selectedMember?.name" 
  width="800px"
  :before-close="handleDetailClose"
>
  <div class="member-detail-content">
    <!-- 头部信息 -->
    <div class="detail-header">
      <div class="member-avatar-large">
        <img :src="selectedMember.avatar" :alt="selectedMember.name" />
      </div>
      <div class="member-basic-info">
        <h2 class="member-name">{{ selectedMember.name }}</h2>
        <div class="member-tags">
          <el-tag :type="genderTagType">{{ genderText }}</el-tag>
          <el-tag type="info">第{{ selectedMember.generation }}世</el-tag>
          <el-tag :type="aliveTagType">{{ aliveText }}</el-tag>
        </div>
        <div class="member-dates">
          <p><strong>出生:</strong> {{ formatDate(selectedMember.birthDate) }}</p>
          <p v-if="selectedMember.deathDate">
            <strong>逝世:</strong> {{ formatDate(selectedMember.deathDate) }}
          </p>
        </div>
      </div>
    </div>

    <!-- 标签页内容 -->
    <el-tabs v-model="activeTab" type="border-card">
      <el-tab-pane label="基本信息" name="basic">
        <MemberBasicInfo :member="selectedMember" />
      </el-tab-pane>
      <el-tab-pane label="家庭关系" name="relations">
        <MemberRelations :member="selectedMember" />
      </el-tab-pane>
      <el-tab-pane label="生平事迹" name="biography">
        <MemberBiography :member="selectedMember" />
      </el-tab-pane>
      <el-tab-pane label="照片相册" name="photos">
        <MemberPhotos :member="selectedMember" />
      </el-tab-pane>
    </el-tabs>
  </div>

  <template #footer>
    <div class="dialog-footer">
      <el-button @click="memberDetailVisible = false">关闭</el-button>
      <el-button type="primary" @click="editMember">编辑信息</el-button>
      <el-button type="success" @click="calculateRelationship">计算称呼</el-button>
    </div>
  </template>
</el-dialog>
```

### 2. 称呼查询抽屉

#### 2.1 抽屉结构
```html
<el-drawer 
  v-model="relationshipDrawerVisible" 
  title="称呼关系查询" 
  direction="rtl" 
  size="400px"
>
  <div class="relationship-content">
    <!-- 基准人员选择 -->
    <div class="base-member-section">
      <h4>基准人员</h4>
      <div class="base-member-card">
        <el-avatar :src="baseMember.avatar" :size="60">
          {{ baseMember.name.charAt(0) }}
        </el-avatar>
        <div class="member-info">
          <div class="member-name">{{ baseMember.name }}</div>
          <div class="member-meta">第{{ baseMember.generation }}世</div>
        </div>
      </div>
    </div>

    <!-- 称呼结果 -->
    <div class="relationship-results">
      <h4>称呼关系</h4>
      <div class="results-list">
        <div 
          v-for="relation in relationshipResults" 
          :key="relation.memberId"
          class="relation-item"
        >
          <div class="relation-member">
            <el-avatar :src="relation.member.avatar" :size="40">
              {{ relation.member.name.charAt(0) }}
            </el-avatar>
            <span class="member-name">{{ relation.member.name }}</span>
          </div>
          <div class="relation-info">
            <div class="relation-title">{{ relation.title }}</div>
            <div class="relation-dialect" v-if="relation.dialectTitle">
              ({{ relation.dialectTitle }})
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 方言切换 -->
    <div class="dialect-selector">
      <h4>方言选择</h4>
      <el-radio-group v-model="selectedDialect">
        <el-radio label="standard">标准称呼</el-radio>
        <el-radio label="northern">北方方言</el-radio>
        <el-radio label="southern">南方方言</el-radio>
        <el-radio label="local">本地方言</el-radio>
      </el-radio-group>
    </div>
  </div>
</el-drawer>
```

## 样式规范

### 1. 颜色规范
```css
:root {
  /* 主色调 */
  --primary-color: #C8102E;
  --primary-light: #E8394A;
  --primary-dark: #A00D24;
  
  /* 性别色彩 */
  --male-color: #1890FF;
  --female-color: #EB2F96;
  --unknown-color: #8C8C8C;
  
  /* 功能色彩 */
  --success-color: #52C41A;
  --warning-color: #FAAD14;
  --error-color: #FF4D4F;
  --info-color: #1890FF;
  
  /* 中性色彩 */
  --text-primary: #262626;
  --text-secondary: #595959;
  --text-disabled: #BFBFBF;
  --border-color: #D9D9D9;
  --background-color: #FAFAFA;
}
```

### 2. 字体规范
```css
.family-tree-page {
  font-family: "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", sans-serif;
}

.node-name {
  font-size: 14px;
  font-weight: 500;
  color: var(--text-primary);
}

.node-dates {
  font-size: 12px;
  color: var(--text-secondary);
}

.toolbar-text {
  font-size: 14px;
  color: var(--text-primary);
}
```

### 3. 间距规范
```css
.spacing-xs { margin: 4px; }
.spacing-sm { margin: 8px; }
.spacing-md { margin: 16px; }
.spacing-lg { margin: 24px; }
.spacing-xl { margin: 32px; }
```

## 响应式设计

### 1. 桌面端 (>1200px)
- 完整三栏布局
- 侧边栏宽度280px
- 工具栏完整显示所有功能
- 支持键盘快捷键

### 2. 平板端 (768px-1200px)
- 侧边栏可收缩至60px
- 工具栏部分功能合并到下拉菜单
- 触摸优化的交互体验

### 3. 移动端 (<768px)
- 侧边栏改为抽屉式
- 工具栏简化为必要功能
- 支持触摸手势操作
- 节点大小适当增大便于触摸

## 开发实现要点

### 1. 技术栈
- Vue 3 + TypeScript
- Element Plus UI组件库
- G6图形可视化库
- Pinia状态管理

### 2. 关键组件
- FamilyTreeGraph.vue (主图形组件)
- MemberDetailCard.vue (成员详情卡片)
- RelationshipCalculator.vue (称呼计算器)
- GraphToolbar.vue (图形工具栏)

### 3. 性能优化
- 虚拟滚动处理大量成员列表
- 图形渲染优化和懒加载
- 防抖处理搜索和筛选
- 缓存机制减少重复请求

### 4. 无障碍支持
- 键盘导航支持
- 屏幕阅读器兼容
- 高对比度模式
- 字体大小调节

这份设计稿提供了族谱页面的完整UI设计方案，包含了详细的布局、交互、样式规范，为后续开发提供了清晰的指导。