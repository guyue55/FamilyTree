import client from './client'

// eslint-disable-next-line @typescript-eslint/no-explicit-any
export async function listPublicFamilies(params: Record<string, any> = {}) {
  const res = await client.get('/family/public', { params })
  const data = res.data?.data
  return {
    items: data?.items || [],
    pagination: data?.pagination || { page: 1, page_size: 0, total: 0, total_pages: 1 }
  }
}

// eslint-disable-next-line @typescript-eslint/no-explicit-any
export async function listFamilies(params: Record<string, any> = {}) {
  const res = await client.get('/family', { params })
  const data = res.data?.data
  return {
    items: data?.items || [],
    pagination: data?.pagination || { page: 1, page_size: 0, total: 0, total_pages: 1 }
  }
}

export async function getFamilyDetail(familyId: number) {
  const res = await client.get(`/family/${familyId}`)
  return res.data?.data
}

export async function getFamilyPermissions(familyId: number) {
  const res = await client.get(`/family/${familyId}/permissions`)
  return res.data?.data
}

export async function joinFamily(familyId: number) {
  const res = await client.post(`/family/${familyId}/join`)
  return res.data?.data
}
