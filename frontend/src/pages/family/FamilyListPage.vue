<template>
  <div class="family-list-page">
    <div class="page-header">
      <div class="header-left">
        <h1>我的族谱</h1>
        <p>管理和查看您的族谱</p>
      </div>
      <div class="header-actions">
        <el-button type="primary" @click="$router.push('/family/create')">
          <el-icon><Plus /></el-icon>
          创建族谱
        </el-button>
      </div>
    </div>

    <div class="filter-bar">
      <el-row :gutter="20">
        <el-col :span="8">
          <el-input
            v-model="searchQuery"
            placeholder="搜索族谱名称"
            prefix-icon="Search"
            @input="handleSearch"
          />
        </el-col>
        <el-col :span="6">
          <el-select v-model="filterVisibility" placeholder="可见性" @change="handleFilter">
            <el-option label="全部" value="" />
            <el-option label="公开" value="public" />
            <el-option label="家族内部" value="family" />
            <el-option label="私密" value="private" />
          </el-select>
        </el-col>
        <el-col :span="6">
          <el-select v-model="sortBy" placeholder="排序方式" @change="handleSort">
            <el-option label="创建时间" value="createdAt" />
            <el-option label="更新时间" value="updatedAt" />
            <el-option label="成员数量" value="memberCount" />
            <el-option label="名称" value="name" />
          </el-select>
        </el-col>
        <el-col :span="4">
          <el-button-group>
            <el-button :type="viewMode === 'grid' ? 'primary' : ''" @click="setViewMode('grid')">
              <el-icon><Grid /></el-icon>
            </el-button>
            <el-button :type="viewMode === 'list' ? 'primary' : ''" @click="setViewMode('list')">
              <el-icon><List /></el-icon>
            </el-button>
          </el-button-group>
        </el-col>
      </el-row>
    </div>

    <div class="family-content">
      <!-- 网格视图 -->
      <div v-if="viewMode === 'grid'" class="grid-view">
        <el-row :gutter="20">
          <el-col v-for="family in filteredFamilies" :key="family.id" :span="6">
            <el-card class="family-card" @click="viewFamily(family.id)">
              <div class="family-cover">
                <img v-if="family.coverImage" :src="family.coverImage" alt="族谱封面" />
                <div v-else class="default-cover">
                  <el-icon><House /></el-icon>
                </div>
              </div>
              <div class="family-info">
                <h3>{{ family.name }}</h3>
                <p>{{ family.description }}</p>
                <div class="family-meta">
                  <span>{{ family.memberCount }} 位成员</span>
                  <el-tag :type="getVisibilityType(family.visibility)" size="small">
                    {{ getVisibilityText(family.visibility) }}
                  </el-tag>
                </div>
              </div>
              <div class="family-actions" @click.stop>
                <el-button type="text" @click="viewFamily(family.id)">查看</el-button>
                <el-button type="text" @click="editFamily(family.id)">编辑</el-button>
                <el-dropdown @command="(command: string) => handleFamilyAction(command, family)">
                  <el-button type="text">
                    <el-icon><MoreFilled /></el-icon>
                  </el-button>
                  <template #dropdown>
                    <el-dropdown-menu>
                      <el-dropdown-item command="settings">设置</el-dropdown-item>
                      <el-dropdown-item command="members">成员管理</el-dropdown-item>
                      <el-dropdown-item command="delete" divided>删除</el-dropdown-item>
                    </el-dropdown-menu>
                  </template>
                </el-dropdown>
              </div>
            </el-card>
          </el-col>
        </el-row>
      </div>

      <!-- 列表视图 -->
      <div v-else class="list-view">
        <el-table :data="filteredFamilies" style="width: 100%">
          <el-table-column prop="name" label="族谱名称" min-width="200">
            <template #default="scope">
              <div class="family-name-cell">
                <el-avatar :size="40" :src="scope.row.coverImage">
                  {{ scope.row.name.charAt(0) }}
                </el-avatar>
                <div class="name-info">
                  <div class="name">{{ scope.row.name }}</div>
                  <div class="desc">{{ scope.row.description }}</div>
                </div>
              </div>
            </template>
          </el-table-column>
          <el-table-column prop="memberCount" label="成员数量" width="120" />
          <el-table-column prop="visibility" label="可见性" width="120">
            <template #default="scope">
              <el-tag :type="getVisibilityType(scope.row.visibility)">
                {{ getVisibilityText(scope.row.visibility) }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="createdAt" label="创建时间" width="180" />
          <el-table-column prop="updatedAt" label="更新时间" width="180" />
          <el-table-column label="操作" width="200">
            <template #default="scope">
              <el-button size="small" @click="viewFamily(scope.row.id)">查看</el-button>
              <el-button size="small" @click="editFamily(scope.row.id)">编辑</el-button>
              <el-dropdown @command="(command: string) => handleFamilyAction(command, scope.row)">
                <el-button size="small">
                  更多
                  <el-icon class="el-icon--right"><arrow-down /></el-icon>
                </el-button>
                <template #dropdown>
                  <el-dropdown-menu>
                    <el-dropdown-item command="settings">设置</el-dropdown-item>
                    <el-dropdown-item command="members">成员管理</el-dropdown-item>
                    <el-dropdown-item command="delete" divided>删除</el-dropdown-item>
                  </el-dropdown-menu>
                </template>
              </el-dropdown>
            </template>
          </el-table-column>
        </el-table>
      </div>

      <!-- 空状态 -->
      <div v-if="!filteredFamilies.length" class="empty-state">
        <el-empty description="暂无族谱数据">
          <el-button type="primary" @click="$router.push('/family/create')">
            创建第一个族谱
          </el-button>
        </el-empty>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Search, Grid, List, House, MoreFilled, ArrowDown } from '@element-plus/icons-vue'

const router = useRouter()

const searchQuery = ref('')
const filterVisibility = ref('')
const sortBy = ref('createdAt')
const viewMode = ref('grid')

const families = ref([
  {
    id: 1,
    name: '张氏族谱',
    description: '张氏家族的族谱记录',
    memberCount: 25,
    visibility: 'public',
    coverImage: '',
    createdAt: '2024-01-01',
    updatedAt: '2024-01-15'
  },
  {
    id: 2,
    name: '李氏族谱',
    description: '李氏家族的族谱记录',
    memberCount: 18,
    visibility: 'family',
    coverImage: '',
    createdAt: '2024-01-05',
    updatedAt: '2024-01-20'
  },
  {
    id: 3,
    name: '王氏族谱',
    description: '王氏家族的族谱记录',
    memberCount: 32,
    visibility: 'private',
    coverImage: '',
    createdAt: '2024-01-10',
    updatedAt: '2024-01-25'
  }
])

const filteredFamilies = computed(() => {
  let result = families.value

  // 搜索过滤
  if (searchQuery.value) {
    result = result.filter(
      family =>
        family.name.toLowerCase().includes(searchQuery.value.toLowerCase()) ||
        family.description.toLowerCase().includes(searchQuery.value.toLowerCase())
    )
  }

  // 可见性过滤
  if (filterVisibility.value) {
    result = result.filter(family => family.visibility === filterVisibility.value)
  }

  // 排序
  result.sort((a, b) => {
    const aValue = a[sortBy.value as keyof typeof a]
    const bValue = b[sortBy.value as keyof typeof b]

    if (typeof aValue === 'string' && typeof bValue === 'string') {
      return bValue.localeCompare(aValue)
    }

    return (bValue as number) - (aValue as number)
  })

  return result
})

function getVisibilityType(visibility: string): 'primary' | 'success' | 'info' | 'warning' | 'danger' {
  const types: Record<string, 'primary' | 'success' | 'info' | 'warning' | 'danger'> = {
    public: 'success',
    family: 'warning',
    private: 'danger'
  }
  return types[visibility] || 'info'
}

function getVisibilityText(visibility: string) {
  const texts: Record<string, string> = {
    public: '公开',
    family: '家族内部',
    private: '私密'
  }
  return texts[visibility] || '未知'
}

function setViewMode(mode: string) {
  viewMode.value = mode
}

function handleSearch() {
  // 搜索逻辑已在计算属性中处理
}

function handleFilter() {
  // 过滤逻辑已在计算属性中处理
}

function handleSort() {
  // 排序逻辑已在计算属性中处理
}

function viewFamily(id: number) {
  router.push(`/family/${id}`)
}

function editFamily(id: number) {
  router.push(`/family/${id}/edit`)
}

async function handleFamilyAction(command: string, family: any) {
  switch (command) {
    case 'settings':
      router.push(`/family/${family.id}/settings`)
      break
    case 'members':
      router.push(`/family/${family.id}/members`)
      break
    case 'delete':
      try {
        await ElMessageBox.confirm(`确定要删除族谱"${family.name}"吗？`, '警告', {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning'
        })
        // TODO: 实现删除逻辑
        ElMessage.success('族谱删除成功')
      } catch {
        ElMessage.info('已取消删除')
      }
      break
  }
}

onMounted(() => {
  // TODO: 加载族谱列表数据
  console.log('加载族谱列表')
})
</script>

<style scoped>
.family-list-page {
  padding: 20px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
}

.header-left h1 {
  color: #303133;
  margin-bottom: 10px;
}

.header-left p {
  color: #606266;
  margin: 0;
}

.filter-bar {
  margin-bottom: 20px;
  padding: 20px;
  background: #fff;
  border-radius: 8px;
}

.family-content {
  min-height: 400px;
}

.grid-view .family-card {
  cursor: pointer;
  transition:
    transform 0.2s,
    box-shadow 0.2s;
  margin-bottom: 20px;
}

.grid-view .family-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.family-cover {
  height: 120px;
  background: #f5f7fa;
  border-radius: 4px;
  margin-bottom: 15px;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
}

.family-cover img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.default-cover {
  font-size: 40px;
  color: #c0c4cc;
}

.family-info h3 {
  margin: 0 0 10px 0;
  color: #303133;
  font-size: 16px;
}

.family-info p {
  margin: 0 0 15px 0;
  color: #606266;
  font-size: 14px;
  line-height: 1.4;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.family-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 12px;
  color: #909399;
}

.family-actions {
  margin-top: 15px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.list-view {
  background: #fff;
  border-radius: 8px;
}

.family-name-cell {
  display: flex;
  align-items: center;
}

.name-info {
  margin-left: 10px;
}

.name-info .name {
  font-weight: 500;
  color: #303133;
  margin-bottom: 5px;
}

.name-info .desc {
  font-size: 12px;
  color: #909399;
}

.empty-state {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 400px;
  background: #fff;
  border-radius: 8px;
}
</style>
