export interface FamilyMember {
  id: string
  familyId: number
  name: string
  gender: 'male' | 'female'
  birthDate?: string | null
  deathDate?: string | null
  generation: number
  parentId?: string | null
  spouseId?: string | null
  children?: string[]
}

export interface Family {
  id: number
  name: string
  description?: string
  memberCount: number
  generationCount: number
  createdAt: string
  updatedAt: string
}