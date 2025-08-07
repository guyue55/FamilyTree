<template>
  <div class="login-page">
    <div class="auth-container">
      <div class="auth-card">
        <div class="auth-header">
          <h1>登录</h1>
          <p>欢迎回到族谱系统</p>
        </div>

        <el-form ref="formRef" :model="form" :rules="rules" @submit.prevent="handleLogin">
          <el-form-item prop="email">
            <el-input
              v-model="form.email"
              type="email"
              placeholder="请输入邮箱地址"
              size="large"
              prefix-icon="message"
            />
          </el-form-item>

          <el-form-item prop="password">
            <el-input
              v-model="form.password"
              type="password"
              placeholder="请输入密码"
              size="large"
              prefix-icon="lock"
              show-password
            />
          </el-form-item>

          <el-form-item>
            <div class="form-options">
              <el-checkbox v-model="form.rememberMe">记住我</el-checkbox>
              <router-link to="/auth/forgot-password" class="forgot-link">忘记密码？</router-link>
            </div>
          </el-form-item>

          <el-form-item>
            <el-button
              type="primary"
              size="large"
              style="width: 100%"
              :loading="loading"
              @click="handleLogin"
            >
              登录
            </el-button>
          </el-form-item>
        </el-form>

        <div class="auth-footer">
          <span>还没有账号？</span>
          <router-link to="/auth/register" class="auth-link">立即注册</router-link>
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
  email: '',
  password: '',
  rememberMe: false
})

const rules = {
  email: [
    { required: true, message: '请输入邮箱地址', trigger: 'blur' },
    { type: 'email' as const, message: '请输入正确的邮箱格式', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码长度不能少于6位', trigger: 'blur' }
  ]
}

async function handleLogin() {
  try {
    await formRef.value.validate()
    loading.value = true

    // TODO: 实现登录逻辑
    await new Promise(resolve => setTimeout(resolve, 2000))

    ElMessage.success('登录成功')
    router.push('/dashboard')
  } catch (error) {
    console.error('登录失败:', error)
    ElMessage.error('登录失败，请检查邮箱和密码')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-page {
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

.form-options {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
}

.forgot-link {
  color: #409eff;
  text-decoration: none;
  font-size: 14px;
}

.forgot-link:hover {
  text-decoration: underline;
}

.auth-footer {
  text-align: center;
  margin-top: 20px;
  font-size: 14px;
  color: #606266;
}

.auth-link {
  color: #409eff;
  text-decoration: none;
  margin-left: 5px;
}

.auth-link:hover {
  text-decoration: underline;
}
</style>
