import client from './client'
import type { KinshipResponse, KinshipCalculateRequest } from '@/types/kinship'

export const kinshipApi = {
  calculate: (data: KinshipCalculateRequest) => {
    return client.post<KinshipResponse>('/kinship/calculate', data)
  },
  
  getTitles: (dialect: string = 'standard') => {
    return client.get('/kinship/titles', { params: { dialect } })
  }
}
