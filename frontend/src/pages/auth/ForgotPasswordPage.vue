<template>
  <div class="forgot-password-page">
    <div class="auth-container">
      <div class="auth-card">
        <div class="auth-header">
          <h1>忘记密码</h1>
          <p>请输入您的邮箱地址，我们将发送重置密码链接</p>
        </div>

        <el-form ref="formRef" :model="form" :rules="rules" @submit.prevent="handleSubmit">
          <el-form-item prop="email">
            <el-input
              v-model="form.email"
              type="email"
              placeholder="请输入邮箱地址"
              size="large"
              prefix-icon="message"
            />
          </el-form-item>

          <el-form-item>
            <el-button
              type="primary"
              size="large"
              style="width: 100%"
              :loading="loading"
              @click="handleSubmit"
            >
              发送重置链接
            </el-button>
          </el-form-item>
        </el-form>

        <div class="auth-footer">
          <router-link to="/auth/login" class="auth-link">返回登录</router-link>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'

const router = useRouter()
const formRef = ref()
const loading = ref(false)

const form = reactive({
  email: ''
})

const rules = {
  email: [
    { required: true, message: '请输入邮箱地址', trigger: 'blur' },
    { type: 'email' as const, message: '请输入正确的邮箱格式', trigger: 'blur' }
  ]
}

async function handleSubmit() {
  try {
    await formRef.value.validate()
    loading.value = true

    // TODO: 实现发送重置密码邮件逻辑
    await new Promise(resolve => setTimeout(resolve, 2000))

    ElMessage.success('重置密码链接已发送到您的邮箱')
    router.push('/auth/login')
  } catch (error) {
    console.error('发送重置链接失败:', error)
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.forgot-password-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.auth-container {
  width: 100%;
  max-width: 400px;
  padding: 20px;
}

.auth-card {
  background: #fff;
  border-radius: 12px;
  padding: 40px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
}

.auth-header {
  text-align: center;
  margin-bottom: 30px;
}

.auth-header h1 {
  color: #303133;
  margin-bottom: 10px;
  font-size: 28px;
}

.auth-header p {
  color: #606266;
  font-size: 14px;
  line-height: 1.5;
}

.auth-footer {
  text-align: center;
  margin-top: 20px;
}

.auth-link {
  color: #409eff;
  text-decoration: none;
  font-size: 14px;
}

.auth-link:hover {
  text-decoration: underline;
}
</style>
