<template>
  <div :class="['family-member-card', { 'is-selected': isSelected }]">
    <div class="member-avatar" :class="member.gender">
      {{ member.name.charAt(0) }}
    </div>
    <div class="member-info">
      <div class="member-name">{{ member.name }}</div>
      <div class="member-dates">{{ formatDateRange(member.birthDate, member.deathDate) }}</div>
      <div class="member-generation">第{{ member.generation }}代</div>
    </div>
  </div>
</template>

<script setup lang="ts">

interface FamilyMember {
  id: string
  name: string
  gender: 'male' | 'female'
  birthDate?: string | null
  deathDate?: string | null
  generation: number
}

defineProps<{
  member: FamilyMember
  isSelected?: boolean
}>()

const formatDateRange = (birthDate?: string | null, deathDate?: string | null): string => {
  if (!birthDate) return '未知'
  
  const birth = new Date(birthDate).getFullYear()
  const death = deathDate ? new Date(deathDate).getFullYear() : '至今'
  
  return `${birth} - ${death}`
}
</script>

<style scoped>
.family-member-card {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 12px;
  border-radius: 8px;
  background-color: #fff;
  border: 1px solid #e5e7eb;
  cursor: pointer;
  transition: all 0.2s;
}

.family-member-card:hover {
  background-color: #f5f5f5;
  transform: translateY(-2px);
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

.family-member-card.is-selected {
  border-color: #4a6cf7;
  background-color: #e8f0fe;
}

.member-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background-color: #4a6cf7;
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 16px;
  font-weight: 600;
}

.member-avatar.female {
  background-color: #f97316;
}

.member-info {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.member-name {
  font-size: 14px;
  font-weight: 500;
}

.member-dates {
  font-size: 12px;
  color: #999;
}

.member-generation {
  padding: 2px 6px;
  border-radius: 4px;
  background-color: #f0f0f0;
  font-size: 11px;
  width: fit-content;
  margin-top: 2px;
}
</style>