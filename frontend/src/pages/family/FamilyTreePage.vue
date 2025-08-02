<template>
  <div class="family-tree-page">
    <div class="page-header">
      <div class="header-left">
        <h1>{{ familyName }} - 族谱图</h1>
        <p>查看和编辑族谱关系图</p>
      </div>
      <div class="header-actions">
        <el-button-group>
          <el-button :type="viewMode === 'tree' ? 'primary' : ''" @click="setViewMode('tree')">
            树形视图
          </el-button>
          <el-button :type="viewMode === 'graph' ? 'primary' : ''" @click="setViewMode('graph')">
            关系图
          </el-button>
        </el-button-group>
        <el-button type="primary" @click="addMember">添加成员</el-button>
        <el-dropdown @command="handleCommand">
          <el-button>
            更多操作
            <el-icon class="el-icon--right"><arrow-down /></el-icon>
          </el-button>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item command="export">导出图片</el-dropdown-item>
              <el-dropdown-item command="print">打印</el-dropdown-item>
              <el-dropdown-item command="fullscreen">全屏显示</el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </div>
    </div>

    <div ref="treeContainer" class="tree-container">
      <div class="tree-toolbar">
        <el-button-group>
          <el-button @click="zoomIn">放大</el-button>
          <el-button @click="zoomOut">缩小</el-button>
          <el-button @click="resetZoom">重置</el-button>
        </el-button-group>
        <el-select v-model="layoutType" style="margin-left: 10px" @change="changeLayout">
          <el-option label="水平布局" value="horizontal" />
          <el-option label="垂直布局" value="vertical" />
          <el-option label="径向布局" value="radial" />
        </el-select>
      </div>

      <div id="tree-graph" class="tree-content">
        <!-- 族谱图将在这里渲染 -->
        <div v-if="!treeData.length" class="tree-placeholder">
          <el-empty description="暂无族谱数据">
            <el-button type="primary" @click="addMember">添加第一个成员</el-button>
          </el-empty>
        </div>
      </div>
    </div>

    <!-- 成员详情侧边栏 -->
    <el-drawer v-model="memberDrawerVisible" title="成员详情" size="400px">
      <div v-if="selectedMember" class="member-detail">
        <div class="member-avatar">
          <el-avatar :size="80" :src="selectedMember.avatar">
            {{ selectedMember.name.charAt(0) }}
          </el-avatar>
        </div>
        <h3>{{ selectedMember.name }}</h3>
        <div class="member-info">
          <div class="info-item">
            <label>性别：</label>
            <span>{{ selectedMember.gender === 'male' ? '男' : '女' }}</span>
          </div>
          <div class="info-item">
            <label>出生日期：</label>
            <span>{{ selectedMember.birthDate || '未知' }}</span>
          </div>
          <div class="info-item">
            <label>世代：</label>
            <span>第{{ selectedMember.generation }}代</span>
          </div>
          <div class="info-item">
            <label>关系：</label>
            <span>{{ selectedMember.relationship || '根节点' }}</span>
          </div>
        </div>
        <div class="member-actions">
          <el-button type="primary" @click="editMember">编辑信息</el-button>
          <el-button @click="addChild">添加子女</el-button>
          <el-button @click="addSpouse">添加配偶</el-button>
        </div>
      </div>
    </el-drawer>

    <!-- 添加成员对话框 -->
    <el-dialog v-model="addMemberDialogVisible" title="添加成员" width="500px">
      <el-form :model="newMemberForm" label-width="100px">
        <el-form-item label="姓名" required>
          <el-input v-model="newMemberForm.name" />
        </el-form-item>
        <el-form-item label="性别" required>
          <el-radio-group v-model="newMemberForm.gender">
            <el-radio label="male">男</el-radio>
            <el-radio label="female">女</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="出生日期">
          <el-date-picker v-model="newMemberForm.birthDate" type="date" placeholder="选择日期" />
        </el-form-item>
        <el-form-item label="关系类型">
          <el-select v-model="newMemberForm.relationshipType">
            <el-option label="父亲" value="father" />
            <el-option label="母亲" value="mother" />
            <el-option label="儿子" value="son" />
            <el-option label="女儿" value="daughter" />
            <el-option label="配偶" value="spouse" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="addMemberDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="confirmAddMember">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, nextTick, withDefaults, defineProps, defineEmits } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { ArrowDown } from '@element-plus/icons-vue'

const route = useRoute()
const treeContainer = ref()
const familyName = ref('示例族谱')
const viewMode = ref('tree')
const layoutType = ref('horizontal')
const memberDrawerVisible = ref(false)
const addMemberDialogVisible = ref(false)

const selectedMember = ref<any>(null)
const treeData = ref([
  {
    id: 1,
    name: '张三',
    gender: 'male',
    birthDate: '1950-01-01',
    generation: 1,
    relationship: '根节点',
    avatar: '',
    children: [
      {
        id: 2,
        name: '张四',
        gender: 'male',
        birthDate: '1975-05-15',
        generation: 2,
        relationship: '儿子',
        avatar: ''
      }
    ]
  }
])

const newMemberForm = reactive({
  name: '',
  gender: 'male',
  birthDate: '' as string,
  relationshipType: 'son'
})

function setViewMode(mode: string) {
  viewMode.value = mode
  renderTree()
}

function changeLayout() {
  renderTree()
}

function zoomIn() {
  // TODO: 实现放大功能
  ElMessage.info('放大功能待实现')
}

function zoomOut() {
  // TODO: 实现缩小功能
  ElMessage.info('缩小功能待实现')
}

function resetZoom() {
  // TODO: 实现重置缩放功能
  ElMessage.info('重置缩放功能待实现')
}

function handleCommand(command: string) {
  switch (command) {
    case 'export':
      ElMessage.info('导出功能待实现')
      break
    case 'print':
      window.print()
      break
    case 'fullscreen':
      ElMessage.info('全屏功能待实现')
      break
  }
}

function addMember() {
  addMemberDialogVisible.value = true
}

function confirmAddMember() {
  // TODO: 实现添加成员逻辑
  ElMessage.success('成员添加成功')
  addMemberDialogVisible.value = false
  renderTree()
}

function editMember() {
  ElMessage.info('编辑成员功能待实现')
}

function addChild() {
  newMemberForm.relationshipType = 'son'
  addMemberDialogVisible.value = true
}

function addSpouse() {
  newMemberForm.relationshipType = 'spouse'
  addMemberDialogVisible.value = true
}

function renderTree() {
  // TODO: 使用 D3.js 或其他图形库渲染族谱图
  nextTick(() => {
    console.log('渲染族谱图', { viewMode: viewMode.value, layoutType: layoutType.value })
  })
}

function onMemberClick(member: any) {
  selectedMember.value = member
  memberDrawerVisible.value = true
}

onMounted(() => {
  const familyId = route.params.id
  console.log('加载族谱:', familyId)
  renderTree()
})
</script>

<style scoped>
.family-tree-page {
  height: 100vh;
  display: flex;
  flex-direction: column;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  background: #fff;
  border-bottom: 1px solid #e4e7ed;
}

.header-left h1 {
  margin: 0 0 5px 0;
  color: #303133;
}

.header-left p {
  margin: 0;
  color: #606266;
  font-size: 14px;
}

.header-actions {
  display: flex;
  gap: 10px;
  align-items: center;
}

.tree-container {
  flex: 1;
  display: flex;
  flex-direction: column;
  background: #f5f7fa;
}

.tree-toolbar {
  display: flex;
  align-items: center;
  padding: 10px 20px;
  background: #fff;
  border-bottom: 1px solid #e4e7ed;
}

.tree-content {
  flex: 1;
  position: relative;
  overflow: hidden;
}

.tree-placeholder {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100%;
}

.member-detail {
  text-align: center;
}

.member-avatar {
  margin-bottom: 20px;
}

.member-detail h3 {
  margin: 0 0 20px 0;
  color: #303133;
}

.member-info {
  text-align: left;
  margin-bottom: 30px;
}

.info-item {
  display: flex;
  margin-bottom: 10px;
}

.info-item label {
  width: 80px;
  color: #606266;
}

.member-actions {
  display: flex;
  flex-direction: column;
  gap: 10px;
}
</style>