import { api } from './api'
import type { WeatherData, WeatherForecast } from '../types/weather'

export const weatherApi = {
  // 현재 날씨
  getCurrentWeather: async (location: string = 'Shanghai'): Promise<WeatherData> => {
    const response = await api.get(`/api/v1/weather/current`, {
      params: { location }
    })
    return response.data
  },

  // 날씨 예보
  getForecast: async (location: string = 'Shanghai', days: number = 7): Promise<WeatherForecast[]> => {
    const response = await api.get(`/api/v1/weather/forecast`, {
      params: { location, days }
    })
    return response.data
  }
}


