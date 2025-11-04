import React from 'react'
import { Box, Typography, IconButton } from '@mui/material'
import { ChevronLeft, ChevronRight } from '@mui/icons-material'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend
} from 'chart.js'
import { Bar } from 'react-chartjs-2'

ChartJS.register(CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend)

interface EnergyBarChartProps {
  data: Array<{
    hour: string
    energy_kwh: number
    cumulative_kwh: number
  }>
  selectedDate: Date
  onDateChange: (date: Date) => void
}

const EnergyBarChart: React.FC<EnergyBarChartProps> = ({
  data,
  selectedDate,
  onDateChange
}) => {
  const chartData = {
    labels: data.map((d) => d.hour),
    datasets: [
      {
        label: 'Energy (kWh)',
        data: data.map((d) => d.cumulative_kwh),
        backgroundColor: '#66bb6a',
        barThickness: 20
      }
    ]
  }

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        display: false
      },
      tooltip: {
        callbacks: {
          label: (context: any) => `${context.parsed.y.toFixed(2)} kWh`,
          afterLabel: (context: any) => {
            const hourData = data[context.dataIndex]
            return `이번 시간: ${hourData.energy_kwh.toFixed(2)} kWh`
          }
        }
      }
    },
    scales: {
      x: {
        grid: {
          display: false
        }
      },
      y: {
        beginAtZero: true,
        grid: {
          color: 'rgba(0, 0, 0, 0.05)'
        },
        ticks: {
          callback: (value: any) => `${value} kWh`
        }
      }
    }
  }

  // 총 에너지 계산
  const totalEnergy = data.reduce((sum, d) => sum + d.energy_kwh, 0)

  const handlePrevDay = () => {
    const prevDay = new Date(selectedDate)
    prevDay.setDate(prevDay.getDate() - 1)
    onDateChange(prevDay)
  }

  const handleNextDay = () => {
    const nextDay = new Date(selectedDate)
    nextDay.setDate(nextDay.getDate() + 1)
    onDateChange(nextDay)
  }

  return (
    <Box sx={{ height: '100%' }}>
      {/* 헤더 */}
      <Box
        sx={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          mb: 2
        }}
      >
        <Box>
          <Typography variant="h6">일일 에너지 생산</Typography>
          <Typography variant="h4" sx={{ color: '#66bb6a', fontWeight: 'bold' }}>
            {totalEnergy.toFixed(2)} kWh
          </Typography>
        </Box>

        {/* 날짜 선택 */}
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <IconButton onClick={handlePrevDay} size="small">
            <ChevronLeft />
          </IconButton>
          <Typography>
            {selectedDate.toLocaleDateString('ko-KR')}
          </Typography>
          <IconButton onClick={handleNextDay} size="small">
            <ChevronRight />
          </IconButton>
        </Box>
      </Box>

      {/* 차트 */}
      {data.length > 0 ? (
        <Box sx={{ height: 'calc(100% - 100px)' }}>
          <Bar data={chartData} options={options} />
        </Box>
      ) : (
        <Box
          sx={{
            height: 'calc(100% - 100px)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center'
          }}
        >
          <Typography variant="body2" color="text.secondary">
            데이터가 없습니다.
          </Typography>
        </Box>
      )}
    </Box>
  )
}

export default EnergyBarChart


