export interface EnergyReading {
  timestamp: string
  power_kw: number
  energy_kwh: number
}

export interface FacilityInfo {
  id: string
  name: string
  location: string
  capacity_kw: number
  current_power: number
  status: 'online' | 'offline' | 'maintenance'
}

export interface DailyEnergyData {
  hour: string
  energy_kwh: number
  cumulative_kwh: number
}

export interface RealtimePowerResponse {
  facility_id: string
  current_power: number
  timestamp: string
  history: Array<{
    timestamp: string
    power_kw: number
  }>
}


