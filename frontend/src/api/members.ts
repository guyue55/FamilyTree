import client from './client'

export async function getFamilyMembersFlat(familyId: number) {
  const res = await client.get(`/members/family/${familyId}/flat`)
  return res.data?.data || []
}

// eslint-disable-next-line @typescript-eslint/no-explicit-any
function toSnakeCase(data: any) {
  const result: any = { ...data }
  const mapping: Record<string, string> = {
    familyId: 'family_id',
    parentId: 'parent_id',
    spouseId: 'spouse_id',
    birthDate: 'birth_date',
    deathDate: 'death_date',
    userId: 'user_id',
    englishName: 'english_name',
    birthPlace: 'birth_place',
    currentLocation: 'current_location',
    isAlive: 'is_alive',
    sortOrder: 'sort_order'
  }

  Object.keys(mapping).forEach(key => {
    if (result[key] !== undefined) {
      result[mapping[key]] = result[key]
      delete result[key]
    }
  })
  
  return result
}

// eslint-disable-next-line @typescript-eslint/no-explicit-any
export async function createMember(data: any) {
  const res = await client.post('/members', toSnakeCase(data))
  return res.data?.data
}

// eslint-disable-next-line @typescript-eslint/no-explicit-any
export async function updateMember(id: string, data: any) {
  const res = await client.put(`/members/${id}`, toSnakeCase(data))
  return res.data?.data
}

export async function deleteMember(id: string) {
  const res = await client.delete(`/members/${id}`)
  return res.data
}
