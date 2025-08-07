<template>
  <div class="main-layout">
    <el-container>
      <!-- 顶部导航栏 -->
      <el-header class="header">
        <div class="header-left">
          <h1 class="logo">族谱系统</h1>
        </div>
        <div class="header-right">
          <el-button type="primary" @click="logout">退出登录</el-button>
        </div>
      </el-header>

      <el-container>
        <!-- 侧边栏 -->
        <el-aside class="sidebar" width="200px">
          <el-menu :default-active="$route.path" router class="sidebar-menu">
            <el-menu-item index="/dashboard">
              <span>控制台</span>
            </el-menu-item>
            <el-menu-item index="/family">
              <span>族谱管理</span>
            </el-menu-item>
            <el-menu-item index="/user">
              <span>个人中心</span>
            </el-menu-item>
          </el-menu>
        </el-aside>

        <!-- 主内容区 -->
        <el-main class="main-content">
          <router-view />
        </el-main>
      </el-container>
    </el-container>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'

const router = useRouter()

function logout() {
  // 清除用户信息和token
  localStorage.removeItem('token')
  localStorage.removeItem('userInfo')
  router.push('/login')
}
</script>

<style scoped>
.main-layout {
  height: 100vh;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: #fff;
  border-bottom: 1px solid #e4e7ed;
  padding: 0 20px;
}

.logo {
  margin: 0;
  color: #409eff;
  font-size: 1.5rem;
}

.sidebar {
  background: #f5f5f5;
  border-right: 1px solid #e4e7ed;
}

.sidebar-menu {
  border: none;
  background: transparent;
}

.main-content {
  padding: 20px;
  background: #f5f5f5;
}
</style>
