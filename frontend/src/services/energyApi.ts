import { api } from './api'
import type { RealtimePowerResponse, DailyEnergyData, FacilityInfo } from '../types/energy'

export const energyApi = {
  // 실시간 전력 데이터
  getRealtimePower: async (facilityId: string = 'U0089'): Promise<RealtimePowerResponse> => {
    try {
      const response = await api.get(`/api/v1/energy/realtime-power`, {
        params: { facility_id: facilityId }
      })
      console.log('Realtime power response:', response.data)
      return response.data
    } catch (err: any) {
      console.error('Error fetching realtime power:', err)
      console.error('Error details:', err.response?.data)
      throw err
    }
  },

  // 일일 에너지 데이터
  getDailyEnergy: async (facilityId: string = 'U0089', date?: Date): Promise<DailyEnergyData[]> => {
    try {
      const params: any = { facility_id: facilityId }
      if (date) {
        params.date = date.toISOString().split('T')[0]
      }
      const response = await api.get(`/api/v1/energy/daily-energy`, { params })
      console.log('Daily energy response:', response.data)
      return response.data
    } catch (err: any) {
      console.error('Error fetching daily energy:', err)
      console.error('Error details:', err.response?.data)
      throw err
    }
  },

  // 시설 정보
  getFacilityInfo: async (facilityId: string = 'U0089'): Promise<FacilityInfo> => {
    const response = await api.get(`/api/v1/energy/facility-info`, {
      params: { facility_id: facilityId }
    })
    return response.data
  }
}

