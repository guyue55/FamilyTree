<template>
  <div class="family-edit-page">
    <div class="page-header">
      <h1>编辑族谱</h1>
      <p>修改族谱信息</p>
    </div>

    <div class="edit-content">
      <el-card>
        <el-form ref="formRef" :model="familyForm" :rules="rules" label-width="120px">
          <el-form-item label="族谱名称" prop="name">
            <el-input v-model="familyForm.name" placeholder="请输入族谱名称" />
          </el-form-item>

          <el-form-item label="族谱描述" prop="description">
            <el-input
              v-model="familyForm.description"
              type="textarea"
              :rows="4"
              placeholder="请输入族谱描述"
            />
          </el-form-item>

          <el-form-item label="可见性" prop="visibility">
            <el-select v-model="familyForm.visibility" placeholder="请选择可见性">
              <el-option label="公开" value="public" />
              <el-option label="家族内部" value="family" />
              <el-option label="私密" value="private" />
            </el-select>
          </el-form-item>

          <el-form-item label="允许加入">
            <el-switch v-model="familyForm.allowJoin" />
          </el-form-item>

          <el-form-item label="族谱封面">
            <el-upload
              class="avatar-uploader"
              action="#"
              :show-file-list="false"
              :before-upload="beforeUpload"
            >
              <img v-if="familyForm.coverImage" :src="familyForm.coverImage" class="avatar" />
              <el-icon v-else class="avatar-uploader-icon"><Plus /></el-icon>
            </el-upload>
          </el-form-item>

          <el-form-item>
            <el-button type="primary" :loading="loading" @click="updateFamily">保存修改</el-button>
            <el-button @click="resetForm">重置</el-button>
            <el-button @click="$router.go(-1)">取消</el-button>
          </el-form-item>
        </el-form>
      </el-card>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'

const route = useRoute()
const router = useRouter()
const formRef = ref()
const loading = ref(false)

const familyForm = reactive({
  name: '',
  description: '',
  visibility: 'public',
  allowJoin: true,
  coverImage: ''
})

const rules = {
  name: [
    { required: true, message: '请输入族谱名称', trigger: 'blur' },
    { min: 2, max: 50, message: '长度在 2 到 50 个字符', trigger: 'blur' }
  ],
  description: [{ max: 500, message: '描述不能超过 500 个字符', trigger: 'blur' }],
  visibility: [{ required: true, message: '请选择可见性', trigger: 'change' }]
}

function beforeUpload(file: File) {
  const isJPG = file.type === 'image/jpeg' || file.type === 'image/png'
  const isLt2M = file.size / 1024 / 1024 < 2

  if (!isJPG) {
    ElMessage.error('上传头像图片只能是 JPG/PNG 格式!')
  }
  if (!isLt2M) {
    ElMessage.error('上传头像图片大小不能超过 2MB!')
  }
  return isJPG && isLt2M
}

async function updateFamily() {
  try {
    await formRef.value.validate()
    loading.value = true

    // TODO: 实现更新族谱逻辑
    await new Promise(resolve => setTimeout(resolve, 1000))

    ElMessage.success('族谱更新成功')
    router.push(`/family/${route.params.id}`)
  } catch (error) {
    console.error('更新族谱失败:', error)
  } finally {
    loading.value = false
  }
}

function resetForm() {
  formRef.value.resetFields()
}

async function loadFamilyData() {
  try {
    // TODO: 根据路由参数加载族谱数据
    const familyId = route.params.id
    console.log('加载族谱数据:', familyId)

    // 模拟数据
    Object.assign(familyForm, {
      name: '示例族谱',
      description: '这是一个示例族谱',
      visibility: 'public',
      allowJoin: true,
      coverImage: ''
    })
  } catch (error) {
    console.error('加载族谱数据失败:', error)
    ElMessage.error('加载族谱数据失败')
  }
}

onMounted(() => {
  loadFamilyData()
})
</script>

<style scoped>
.family-edit-page {
  padding: 20px;
  max-width: 600px;
  margin: 0 auto;
}

.page-header {
  text-align: center;
  margin-bottom: 30px;
}

.page-header h1 {
  color: #303133;
  margin-bottom: 10px;
}

.page-header p {
  color: #606266;
}

.edit-content {
  background: #fff;
}

.avatar-uploader .avatar {
  width: 178px;
  height: 178px;
  display: block;
}

.avatar-uploader .el-upload {
  border: 1px dashed #d9d9d9;
  border-radius: 6px;
  cursor: pointer;
  position: relative;
  overflow: hidden;
  transition: 0.2s;
}

.avatar-uploader .el-upload:hover {
  border-color: #409eff;
}

.avatar-uploader-icon {
  font-size: 28px;
  color: #8c939d;
  width: 178px;
  height: 178px;
  line-height: 178px;
  text-align: center;
}
</style>
