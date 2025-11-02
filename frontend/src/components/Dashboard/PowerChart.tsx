import React, { useState } from 'react'
import { Box, Typography, ToggleButtonGroup, ToggleButton } from '@mui/material'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler
} from 'chart.js'
import { Line } from 'react-chartjs-2'

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler
)

interface PowerChartProps {
  data: Array<{
    timestamp: string
    power_kw: number
  }>
}

const PowerChart: React.FC<PowerChartProps> = ({ data }) => {
  const [timeRange, setTimeRange] = useState('hour')

  const chartData = {
    labels:
      data.length > 0
        ? data.map((d) =>
            new Date(d.timestamp).toLocaleTimeString('ko-KR', {
              hour: '2-digit',
              minute: '2-digit'
            })
          )
        : [],
    datasets: [
      {
        label: 'Power (kW)',
        data: data.map((d) => d.power_kw),
        borderColor: '#66bb6a',
        backgroundColor: 'rgba(102, 187, 106, 0.3)',
        fill: true,
        tension: 0.4,
        pointRadius: 0,
        borderWidth: 2
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
        mode: 'index' as const,
        intersect: false,
        callbacks: {
          label: (context: any) => `${context.parsed.y.toFixed(2)} kW`
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
          callback: (value: any) => `${value} kW`
        }
      }
    },
    interaction: {
      mode: 'nearest' as const,
      axis: 'x' as const,
      intersect: false
    }
  }

  // 최신 값 표시
  const latestValue = data.length > 0 ? data[data.length - 1].power_kw : 0

  return (
    <Box sx={{ height: '100%', position: 'relative' }}>
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
          <Typography variant="h6">실시간 전력 생산</Typography>
          <Typography variant="h4" sx={{ color: '#66bb6a', fontWeight: 'bold' }}>
            {latestValue.toFixed(2)} kW
          </Typography>
        </Box>

        {/* 시간 범위 선택 */}
        <ToggleButtonGroup
          value={timeRange}
          exclusive
          onChange={(e, value) => value && setTimeRange(value)}
          size="small"
        >
          <ToggleButton value="hour">Hour</ToggleButton>
          <ToggleButton value="day">Day</ToggleButton>
          <ToggleButton value="month">Month</ToggleButton>
          <ToggleButton value="year">Year</ToggleButton>
        </ToggleButtonGroup>
      </Box>

      {/* 차트 */}
      {data.length > 0 ? (
        <Box sx={{ height: 'calc(100% - 100px)' }}>
          <Line data={chartData} options={options} />
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

export default PowerChart

