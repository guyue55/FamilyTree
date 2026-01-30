import client from './client'
import type { KinshipResponse, KinshipCalculateRequest, BatchKinshipRequest, BatchKinshipResponse } from '@/types/kinship'

export const kinshipApi = {
  calculate: (data: KinshipCalculateRequest) => {
    return client.post<KinshipResponse>('/kinship/calculate', data)
  },

  batchCalculate: (data: BatchKinshipRequest) => {
    return client.post<BatchKinshipResponse>('/kinship/batch-calculate', data)
  },
  
  getTitles: (dialect: string = 'standard') => {
    return client.get('/kinship/titles', { params: { dialect } })
  }
}
