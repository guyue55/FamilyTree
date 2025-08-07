<template>
  <div class="family-detail-page">
    <div class="page-header">
      <div class="family-info">
        <h1>{{ family.name }}</h1>
        <p>{{ family.description }}</p>
        <div class="family-meta">
          <span>创建者：{{ family.creator }}</span>
          <span>成员数：{{ family.memberCount }}</span>
          <span>创建时间：{{ family.createdAt }}</span>
        </div>
      </div>
      <div class="actions">
        <el-button type="primary" @click="viewTree">查看族谱</el-button>
        <el-button v-if="canEdit" @click="editFamily">编辑</el-button>
        <el-button v-if="!isMember" @click="joinFamily">加入族谱</el-button>
      </div>
    </div>

    <div class="detail-content">
      <el-tabs v-model="activeTab">
        <el-tab-pane label="族谱概览" name="overview">
          <div class="overview-content">
            <el-row :gutter="20">
              <el-col :span="12">
                <el-card title="基本信息">
                  <div class="info-item">
                    <label>族谱名称：</label>
                    <span>{{ family.name }}</span>
                  </div>
                  <div class="info-item">
                    <label>可见性：</label>
                    <el-tag :type="getVisibilityType(family.visibility)">
                      {{ getVisibilityText(family.visibility) }}
                    </el-tag>
                  </div>
                  <div class="info-item">
                    <label>允许加入：</label>
                    <el-tag :type="family.allowJoin ? 'success' : 'danger'">
                      {{ family.allowJoin ? '是' : '否' }}
                    </el-tag>
                  </div>
                </el-card>
              </el-col>
              <el-col :span="12">
                <el-card title="统计信息">
                  <div class="stats">
                    <div class="stat-item">
                      <div class="stat-value">{{ family.memberCount }}</div>
                      <div class="stat-label">成员数量</div>
                    </div>
                    <div class="stat-item">
                      <div class="stat-value">{{ family.generationCount }}</div>
                      <div class="stat-label">世代数</div>
                    </div>
                    <div class="stat-item">
                      <div class="stat-value">{{ family.photoCount }}</div>
                      <div class="stat-label">照片数量</div>
                    </div>
                  </div>
                </el-card>
              </el-col>
            </el-row>
          </div>
        </el-tab-pane>

        <el-tab-pane label="成员列表" name="members">
          <div class="members-content">
            <el-table :data="members" style="width: 100%">
              <el-table-column prop="name" label="姓名" />
              <el-table-column prop="role" label="角色" />
              <el-table-column prop="generation" label="世代" />
              <el-table-column prop="joinedAt" label="加入时间" />
            </el-table>
          </div>
        </el-tab-pane>

        <el-tab-pane label="活动记录" name="activities">
          <div class="activities-content">
            <el-timeline>
              <el-timeline-item
                v-for="activity in activities"
                :key="activity.id"
                :timestamp="activity.timestamp"
              >
                {{ activity.description }}
              </el-timeline-item>
            </el-timeline>
          </div>
        </el-tab-pane>
      </el-tabs>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { ArrowDown } from '@element-plus/icons-vue'

const route = useRoute()
const router = useRouter()
const activeTab = ref('overview')

const family = ref({
  id: 1,
  name: '示例族谱',
  description: '这是一个示例族谱的详细描述',
  creator: '张三',
  memberCount: 25,
  generationCount: 4,
  photoCount: 120,
  visibility: 'public',
  allowJoin: true,
  createdAt: '2024-01-01'
})

const members = ref([
  { id: 1, name: '张三', role: '创建者', generation: 1, joinedAt: '2024-01-01' },
  { id: 2, name: '李四', role: '管理员', generation: 2, joinedAt: '2024-01-02' },
  { id: 3, name: '王五', role: '成员', generation: 3, joinedAt: '2024-01-03' }
])

const activities = ref([
  { id: 1, description: '张三创建了族谱', timestamp: '2024-01-01 10:00' },
  { id: 2, description: '李四加入了族谱', timestamp: '2024-01-02 14:30' },
  { id: 3, description: '王五上传了照片', timestamp: '2024-01-03 16:45' }
])

const isMember = ref(true)
const canEdit = ref(true)

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

function viewTree() {
  router.push(`/family/${family.value.id}/tree`)
}

function editFamily() {
  router.push(`/family/${family.value.id}/edit`)
}

function joinFamily() {
  // TODO: 实现加入族谱逻辑
  ElMessage.success('加入申请已发送')
}

onMounted(() => {
  // TODO: 根据路由参数加载族谱详情
  const familyId = route.params.id
  console.log('加载族谱详情:', familyId)
})
</script>

<style scoped>
.family-detail-page {
  padding: 20px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 30px;
  padding: 20px;
  background: #fff;
  border-radius: 8px;
}

.family-info h1 {
  margin: 0 0 10px 0;
  color: #303133;
}

.family-info p {
  margin: 0 0 15px 0;
  color: #606266;
}

.family-meta {
  display: flex;
  gap: 20px;
  font-size: 14px;
  color: #909399;
}

.detail-content {
  background: #fff;
  border-radius: 8px;
  padding: 20px;
}

.info-item {
  display: flex;
  align-items: center;
  margin-bottom: 15px;
}

.info-item label {
  width: 100px;
  color: #606266;
}

.stats {
  display: flex;
  justify-content: space-around;
}

.stat-item {
  text-align: center;
}

.stat-value {
  font-size: 24px;
  font-weight: bold;
  color: #409eff;
  margin-bottom: 5px;
}

.stat-label {
  font-size: 14px;
  color: #909399;
}

.members-content,
.activities-content {
  margin-top: 20px;
}
</style>
