export interface User {
  id: string
  email: string
  full_name?: string
  role: string
  is_active: boolean
}

export interface EnergyAsset {
  id: string
  name: string
  type: string
  capacity_kw?: number
  status: string
  organization_id?: string
  metadata?: any
  created_at?: string
}

export interface DisasterAnalysis {
  agent: string
  disaster_type: string
  severity: string
  magnitude: number
  location?: any
  affected_radius_km: number
  priority: number
}

export interface EnergyAnalysis {
  agent: string
  balance: number
  balance_ratio: number
  status: string
  surplus_assets: string[]
  deficit_assets: string[]
  redistribution_needed: boolean
}




