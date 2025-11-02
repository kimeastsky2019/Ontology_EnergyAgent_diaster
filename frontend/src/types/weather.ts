export interface WeatherData {
  temperature: number
  condition: string
  humidity: number
  windSpeed: number
  visibility: number
  pressure: number
  sunrise: string
  sunset: string
  location: string
  timezone?: string
}

export interface WeatherForecast {
  date: string
  tempMax: number
  tempMin: number
  condition: string
  icon?: string
}

