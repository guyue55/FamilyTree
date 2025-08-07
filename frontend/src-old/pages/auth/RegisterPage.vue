<template>
  <div class="register-page">
    <div class="auth-container">
      <div class="auth-card">
        <div class="auth-header">
          <h1>注册</h1>
          <p>创建您的族谱账号</p>
        </div>

        <el-form ref="formRef" :model="form" :rules="rules" @submit.prevent="handleRegister">
          <el-form-item prop="username">
            <el-input
              v-model="form.username"
              placeholder="请输入用户名"
              size="large"
              prefix-icon="user"
            />
          </el-form-item>

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

          <el-form-item prop="confirmPassword">
            <el-input
              v-model="form.confirmPassword"
              type="password"
              placeholder="请确认密码"
              size="large"
              prefix-icon="lock"
              show-password
            />
          </el-form-item>

          <el-form-item prop="agreement">
            <el-checkbox v-model="form.agreement">
              我已阅读并同意
              <a href="#" class="agreement-link">《用户协议》</a>
              和
              <a href="#" class="agreement-link">《隐私政策》</a>
            </el-checkbox>
          </el-form-item>

          <el-form-item>
            <el-button
              type="primary"
              size="large"
              style="width: 100%"
              :loading="loading"
              @click="handleRegister"
            >
              注册
            </el-button>
          </el-form-item>
        </el-form>

        <div class="auth-footer">
          <span>已有账号？</span>
          <router-link to="/auth/login" class="auth-link">立即登录</router-link>
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
  username: '',
  email: '',
  password: '',
  confirmPassword: '',
  agreement: false
})

const validateConfirmPassword = (rule: any, value: string, callback: Function) => {
  if (value !== form.password) {
    callback(new Error('两次输入的密码不一致'))
  } else {
    callback()
  }
}

const validateAgreement = (rule: any, value: boolean, callback: Function) => {
  if (!value) {
    callback(new Error('请同意用户协议和隐私政策'))
  } else {
    callback()
  }
}

const rules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, max: 20, message: '用户名长度在 3 到 20 个字符', trigger: 'blur' }
  ],
  email: [
    { required: true, message: '请输入邮箱地址', trigger: 'blur' },
    { type: 'email' as const, message: '请输入正确的邮箱格式', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码长度不能少于6位', trigger: 'blur' }
  ],
  confirmPassword: [
    { required: true, message: '请确认密码', trigger: 'blur' },
    { validator: validateConfirmPassword, trigger: 'blur' }
  ],
  agreement: [{ validator: validateAgreement, trigger: 'change' }]
}

async function handleRegister() {
  try {
    await formRef.value.validate()
    loading.value = true

    // TODO: 实现注册逻辑
    await new Promise(resolve => setTimeout(resolve, 2000))

    ElMessage.success('注册成功，请登录')
    router.push('/auth/login')
  } catch (error) {
    console.error('注册失败:', error)
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.register-page {
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

.agreement-link {
  color: #409eff;
  text-decoration: none;
}

.agreement-link:hover {
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
