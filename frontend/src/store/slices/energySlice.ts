import { createSlice, PayloadAction } from '@reduxjs/toolkit'

interface EnergyState {
  assets: any[]
  selectedAsset: any | null
}

const initialState: EnergyState = {
  assets: [],
  selectedAsset: null,
}

const energySlice = createSlice({
  name: 'energy',
  initialState,
  reducers: {
    setAssets: (state, action: PayloadAction<any[]>) => {
      state.assets = action.payload
    },
    setSelectedAsset: (state, action: PayloadAction<any>) => {
      state.selectedAsset = action.payload
    },
  },
})

export const { setAssets, setSelectedAsset } = energySlice.actions
export default energySlice.reducer





