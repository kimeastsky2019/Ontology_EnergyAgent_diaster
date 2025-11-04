import { configureStore } from '@reduxjs/toolkit'
import authSlice from './slices/authSlice'
import energySlice from './slices/energySlice'

export const store = configureStore({
  reducer: {
    auth: authSlice,
    energy: energySlice,
  },
})

export type RootState = ReturnType<typeof store.getState>
export type AppDispatch = typeof store.dispatch





