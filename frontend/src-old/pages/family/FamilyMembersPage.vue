<template>
  <div class="family-members-page">
    <div class="page-header">
      <h1>成员管理</h1>
      <p>管理族谱成员信息</p>
      <el-button type="primary" @click="showAddMemberDialog">添加成员</el-button>
    </div>

    <div class="members-content">
      <el-table :data="members" style="width: 100%">
        <el-table-column prop="name" label="姓名" />
        <el-table-column prop="role" label="角色" />
        <el-table-column prop="status" label="状态" />
        <el-table-column prop="joinedAt" label="加入时间" />
        <el-table-column label="操作" width="200">
          <template #default="scope">
            <el-button size="small" @click="editMember(scope.row)">编辑</el-button>
            <el-button size="small" type="danger" @click="removeMember(scope.row)">移除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <!-- 添加成员对话框 -->
    <el-dialog v-model="addMemberDialogVisible" title="添加成员">
      <el-form :model="newMemberForm" label-width="100px">
        <el-form-item label="姓名">
          <el-input v-model="newMemberForm.name" />
        </el-form-item>
        <el-form-item label="角色">
          <el-select v-model="newMemberForm.role">
            <el-option label="成员" value="member" />
            <el-option label="管理员" value="admin" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="addMemberDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="addMember">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { ElMessage } from 'element-plus'

const members = ref([
  { id: 1, name: '张三', role: '管理员', status: '活跃', joinedAt: '2024-01-01' },
  { id: 2, name: '李四', role: '成员', status: '活跃', joinedAt: '2024-01-02' }
])

const addMemberDialogVisible = ref(false)
const newMemberForm = ref({
  name: '',
  role: 'member'
})

function showAddMemberDialog() {
  addMemberDialogVisible.value = true
}

function addMember() {
  // TODO: 实现添加成员逻辑
  ElMessage.success('成员添加成功')
  addMemberDialogVisible.value = false
}

function editMember(member: any) {
  // TODO: 实现编辑成员逻辑
  ElMessage.info('编辑成员功能待实现')
}

function removeMember(member: any) {
  // TODO: 实现移除成员逻辑
  ElMessage.success('成员移除成功')
}
</script>

<style scoped>
.family-members-page {
  padding: 20px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
}

.page-header h1 {
  margin: 0;
  color: #303133;
}

.page-header p {
  margin: 5px 0 0 0;
  color: #606266;
}

.members-content {
  background: #fff;
  border-radius: 8px;
  padding: 20px;
}
</style>
