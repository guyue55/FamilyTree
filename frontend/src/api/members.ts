import client from './client'

export async function getFamilyMembersFlat(familyId: number) {
  const res = await client.get(`/members/family/${familyId}/flat`)
  return res.data?.data || []
}
