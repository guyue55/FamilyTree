<template>
  <div class="reset-password-page">
    <div class="auth-container">
      <div class="auth-card">
        <div class="auth-header">
          <h1>重置密码</h1>
          <p>请输入您的新密码</p>
        </div>

        <el-form ref="formRef" :model="form" :rules="rules" @submit.prevent="handleSubmit">
          <el-form-item prop="password">
            <el-input
              v-model="form.password"
              type="password"
              placeholder="请输入新密码"
              size="large"
              prefix-icon="Lock"
              show-password
            />
          </el-form-item>

          <el-form-item prop="confirmPassword">
            <el-input
              v-model="form.confirmPassword"
              type="password"
              placeholder="请确认新密码"
              size="large"
              prefix-icon="Lock"
              show-password
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
              重置密码
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
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'

const route = useRoute()
const router = useRouter()
const formRef = ref()
const loading = ref(false)

const form = reactive({
  password: '',
  confirmPassword: ''
})

const validateConfirmPassword = (rule: any, value: string, callback: Function) => {
  if (value !== form.password) {
    callback(new Error('两次输入的密码不一致'))
  } else {
    callback()
  }
}

const rules = {
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码长度不能少于6位', trigger: 'blur' }
  ],
  confirmPassword: [
    { required: true, message: '请确认密码', trigger: 'blur' },
    { validator: validateConfirmPassword, trigger: 'blur' }
  ]
}

async function handleSubmit() {
  try {
    await formRef.value.validate()
    loading.value = true

    const token = route.query.token as string
    if (!token) {
      ElMessage.error('重置链接无效')
      return
    }

    // TODO: 实现重置密码逻辑
    await new Promise(resolve => setTimeout(resolve, 2000))

    ElMessage.success('密码重置成功')
    router.push('/auth/login')
  } catch (error) {
    console.error('重置密码失败:', error)
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.reset-password-page {
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
