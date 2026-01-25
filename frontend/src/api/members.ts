import client from './client'

export async function getFamilyMembersFlat(familyId: number) {
  const res = await client.get(`/members/family/${familyId}/flat`)
  return res.data?.data || []
}

// eslint-disable-next-line @typescript-eslint/no-explicit-any
export async function createMember(data: any) {
  const res = await client.post('/members', data)
  return res.data
}

// eslint-disable-next-line @typescript-eslint/no-explicit-any
export async function updateMember(id: string, data: any) {
  const res = await client.put(`/members/${id}`, data)
  return res.data
}

export async function deleteMember(id: string) {
  const res = await client.delete(`/members/${id}`)
  return res.data
}
