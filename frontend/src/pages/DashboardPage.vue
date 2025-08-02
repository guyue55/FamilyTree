<template>
  <div class="dashboard-page">
    <div class="dashboard-header">
      <h1>仪表盘</h1>
      <p>欢迎回到族谱系统</p>
    </div>

    <div class="dashboard-content">
      <el-row :gutter="20">
        <!-- 统计卡片 -->
        <el-col :span="6">
          <el-card class="stat-card">
            <div class="stat-content">
              <div class="stat-icon family">
                <el-icon><House /></el-icon>
              </div>
              <div class="stat-info">
                <div class="stat-value">{{ stats.familyCount }}</div>
                <div class="stat-label">我的族谱</div>
              </div>
            </div>
          </el-card>
        </el-col>

        <el-col :span="6">
          <el-card class="stat-card">
            <div class="stat-content">
              <div class="stat-icon member">
                <el-icon><User /></el-icon>
              </div>
              <div class="stat-info">
                <div class="stat-value">{{ stats.memberCount }}</div>
                <div class="stat-label">族谱成员</div>
              </div>
            </div>
          </el-card>
        </el-col>

        <el-col :span="6">
          <el-card class="stat-card">
            <div class="stat-content">
              <div class="stat-icon photo">
                <el-icon><Picture /></el-icon>
              </div>
              <div class="stat-info">
                <div class="stat-value">{{ stats.photoCount }}</div>
                <div class="stat-label">照片数量</div>
              </div>
            </div>
          </el-card>
        </el-col>

        <el-col :span="6">
          <el-card class="stat-card">
            <div class="stat-content">
              <div class="stat-icon activity">
                <el-icon><Bell /></el-icon>
              </div>
              <div class="stat-info">
                <div class="stat-value">{{ stats.activityCount }}</div>
                <div class="stat-label">最新动态</div>
              </div>
            </div>
          </el-card>
        </el-col>
      </el-row>

      <el-row :gutter="20" style="margin-top: 20px">
        <!-- 我的族谱 -->
        <el-col :span="12">
          <el-card>
            <template #header>
              <div class="card-header">
                <span>我的族谱</span>
                <el-button type="text" @click="$router.push('/family')">查看全部</el-button>
              </div>
            </template>
            <div class="family-list">
              <div
                v-for="family in recentFamilies"
                :key="family.id"
                class="family-item"
                @click="$router.push(`/family/${family.id}`)"
              >
                <div class="family-avatar">
                  <el-avatar :size="40" :src="family.avatar">
                    {{ family.name.charAt(0) }}
                  </el-avatar>
                </div>
                <div class="family-info">
                  <div class="family-name">{{ family.name }}</div>
                  <div class="family-desc">{{ family.memberCount }} 位成员</div>
                </div>
                <div class="family-action">
                  <el-button type="text" size="small">查看</el-button>
                </div>
              </div>
            </div>
          </el-card>
        </el-col>

        <!-- 最新动态 -->
        <el-col :span="12">
          <el-card>
            <template #header>
              <div class="card-header">
                <span>最新动态</span>
                <el-button type="text">查看全部</el-button>
              </div>
            </template>
            <div class="activity-list">
              <div v-for="activity in recentActivities" :key="activity.id" class="activity-item">
                <div class="activity-avatar">
                  <el-avatar :size="32" :src="activity.userAvatar">
                    {{ activity.userName.charAt(0) }}
                  </el-avatar>
                </div>
                <div class="activity-content">
                  <div class="activity-text">
                    <strong>{{ activity.userName }}</strong>
                    {{ activity.action }}
                  </div>
                  <div class="activity-time">{{ activity.time }}</div>
                </div>
              </div>
            </div>
          </el-card>
        </el-col>
      </el-row>

      <!-- 快速操作 -->
      <el-row style="margin-top: 20px">
        <el-col :span="24">
          <el-card>
            <template #header>
              <span>快速操作</span>
            </template>
            <div class="quick-actions">
              <el-button type="primary" @click="$router.push('/family/create')">
                <el-icon><Plus /></el-icon>
                创建族谱
              </el-button>
              <el-button @click="$router.push('/search')">
                <el-icon><Search /></el-icon>
                搜索族谱
              </el-button>
              <el-button @click="$router.push('/user/profile')">
                <el-icon><User /></el-icon>
                个人资料
              </el-button>
              <el-button @click="$router.push('/help')">
                <el-icon><QuestionFilled /></el-icon>
                帮助中心
              </el-button>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { House, User, Picture, Bell, Plus, Search, QuestionFilled } from '@element-plus/icons-vue'

const stats = ref({
  familyCount: 3,
  memberCount: 25,
  photoCount: 120,
  activityCount: 8
})

const recentFamilies = ref([
  {
    id: 1,
    name: '张氏族谱',
    memberCount: 15,
    avatar: ''
  },
  {
    id: 2,
    name: '李氏族谱',
    memberCount: 8,
    avatar: ''
  },
  {
    id: 3,
    name: '王氏族谱',
    memberCount: 12,
    avatar: ''
  }
])

const recentActivities = ref([
  {
    id: 1,
    userName: '张三',
    action: '添加了新成员',
    time: '2小时前',
    userAvatar: ''
  },
  {
    id: 2,
    userName: '李四',
    action: '上传了照片',
    time: '4小时前',
    userAvatar: ''
  },
  {
    id: 3,
    userName: '王五',
    action: '更新了个人信息',
    time: '1天前',
    userAvatar: ''
  }
])

onMounted(() => {
  // TODO: 加载仪表盘数据
  console.log('加载仪表盘数据')
})
</script>

<style scoped>
.dashboard-page {
  padding: 20px;
}

.dashboard-header {
  margin-bottom: 30px;
}

.dashboard-header h1 {
  color: #303133;
  margin-bottom: 10px;
}

.dashboard-header p {
  color: #606266;
}

.stat-card {
  height: 120px;
}

.stat-content {
  display: flex;
  align-items: center;
  height: 100%;
}

.stat-icon {
  width: 60px;
  height: 60px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 15px;
  font-size: 24px;
  color: #fff;
}

.stat-icon.family {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.stat-icon.member {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
}

.stat-icon.photo {
  background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
}

.stat-icon.activity {
  background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
}

.stat-value {
  font-size: 28px;
  font-weight: bold;
  color: #303133;
  margin-bottom: 5px;
}

.stat-label {
  font-size: 14px;
  color: #909399;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.family-list,
.activity-list {
  max-height: 300px;
  overflow-y: auto;
}

.family-item {
  display: flex;
  align-items: center;
  padding: 10px 0;
  border-bottom: 1px solid #f0f0f0;
  cursor: pointer;
  transition: background-color 0.2s;
}

.family-item:hover {
  background-color: #f5f7fa;
}

.family-item:last-child {
  border-bottom: none;
}

.family-avatar {
  margin-right: 15px;
}

.family-info {
  flex: 1;
}

.family-name {
  font-weight: 500;
  color: #303133;
  margin-bottom: 5px;
}

.family-desc {
  font-size: 12px;
  color: #909399;
}

.activity-item {
  display: flex;
  align-items: flex-start;
  padding: 10px 0;
  border-bottom: 1px solid #f0f0f0;
}

.activity-item:last-child {
  border-bottom: none;
}

.activity-avatar {
  margin-right: 10px;
}

.activity-content {
  flex: 1;
}

.activity-text {
  font-size: 14px;
  color: #303133;
  margin-bottom: 5px;
}

.activity-time {
  font-size: 12px;
  color: #909399;
}

.quick-actions {
  display: flex;
  gap: 15px;
}

.quick-actions .el-button {
  flex: 1;
  height: 60px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 5px;
}
</style>
