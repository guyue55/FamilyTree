<template>
  <div class="page page-wrap">
    <header class="page-header">
      <el-button size="small" @click="$router.back()">返回</el-button>
      <h1 class="page-title">编辑成员</h1>
      <el-button type="primary" size="small" @click="save">保存</el-button>
    </header>
    <el-card>
      <el-form :model="form" label-width="80px" style="max-width: 600px">
        <el-form-item label="姓名">
          <el-input v-model="form.name" />
        </el-form-item>
        <el-form-item label="性别">
          <el-radio-group v-model="form.gender">
            <el-radio value="male">男</el-radio>
            <el-radio value="female">女</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="世代">
          <el-input-number v-model="form.generation" :min="1" :max="20" />
        </el-form-item>
        <el-form-item label="出生">
          <el-date-picker v-model="form.birthDate" type="date" style="width: 100%" />
        </el-form-item>
        <el-form-item label="逝世">
          <el-date-picker v-model="form.deathDate" type="date" style="width: 100%" />
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()
const form = ref({
  id: String(route.params.id || '1'),
  name: '张三',
  gender: 'male',
  generation: 2,
  birthDate: '1990-01-01',
  deathDate: ''
})

const save = () => {
  // TODO: 保存逻辑
}
</script>

<style scoped>
.page-wrap { padding: 24px; }
.page-header { display: flex; align-items: center; gap: 12px; margin-bottom: 12px; }
.page-title { font-size: 18px; font-weight: 600; margin-left: auto; margin-right: auto; }
</style>


