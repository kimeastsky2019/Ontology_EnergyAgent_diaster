"""
예측 모델링 도구

에너지 소비량 예측을 위한 다양한 머신러닝 모델을 제공합니다.
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

from fastmcp import FastMCP

class ModelingTools:
    """예측 모델링 관련 도구들"""
    
    def __init__(self, mcp: FastMCP):
        self.mcp = mcp
        self._register_tools()
    
    def _register_tools(self):
        """도구들을 MCP 서버에 등록"""
        
        @self.mcp.tool
        async def arima_forecast(data: List[Dict], value_column: str = "consumption", 
                               periods: int = 30, order: Tuple[int, int, int] = (1, 1, 1)) -> Dict[str, Any]:
            """
            ARIMA 모델을 사용하여 에너지 소비량을 예측합니다.
            
            Args:
                data: 시계열 데이터
                value_column: 값 컬럼명
                periods: 예측 기간
                order: ARIMA 모델 파라미터 (p, d, q)
                
            Returns:
                ARIMA 예측 결과
            """
            try:
                from statsmodels.tsa.arima.model import ARIMA
                
                # 데이터 준비
                df = pd.DataFrame(data)
                df['datetime'] = pd.to_datetime(df['datetime'])
                df = df.set_index('datetime')
                ts_data = df[value_column].dropna()
                
                if len(ts_data) < 50:
                    return {"error": "ARIMA 모델을 위해서는 최소 50개의 데이터 포인트가 필요합니다."}
                
                # ARIMA 모델 훈련
                model = ARIMA(ts_data, order=order)
                fitted_model = model.fit()
                
                # 예측 수행
                forecast = fitted_model.forecast(steps=periods)
                conf_int = fitted_model.get_forecast(steps=periods).conf_int()
                
                # 예측 날짜 생성
                last_date = ts_data.index[-1]
                forecast_dates = pd.date_range(start=last_date + timedelta(hours=1), periods=periods, freq='H')
                
                # 결과 정리
                forecast_data = []
                for i, (date, value, lower, upper) in enumerate(zip(forecast_dates, forecast, 
                                                                   conf_int.iloc[:, 0], conf_int.iloc[:, 1])):
                    forecast_data.append({
                        "datetime": str(date),
                        "forecast": float(value),
                        "lower_bound": float(lower),
                        "upper_bound": float(upper)
                    })
                
                # 모델 성능 지표
                aic = fitted_model.aic
                bic = fitted_model.bic
                
                return {
                    "success": True,
                    "model_type": "ARIMA",
                    "model_order": order,
                    "forecast_periods": periods,
                    "model_metrics": {
                        "aic": float(aic),
                        "bic": float(bic)
                    },
                    "forecast_data": forecast_data,
                    "training_data_points": len(ts_data)
                }
                
            except Exception as e:
                return {"error": f"ARIMA 예측 실패: {str(e)}"}
        
        @self.mcp.tool
        async def prophet_forecast(data: List[Dict], value_column: str = "consumption", 
                                 periods: int = 30, include_holidays: bool = False) -> Dict[str, Any]:
            """
            Prophet 모델을 사용하여 에너지 소비량을 예측합니다.
            
            Args:
                data: 시계열 데이터
                value_column: 값 컬럼명
                periods: 예측 기간
                include_holidays: 공휴일 포함 여부
                
            Returns:
                Prophet 예측 결과
            """
            try:
                from prophet import Prophet
                
                # 데이터 준비 (Prophet 형식으로 변환)
                df = pd.DataFrame(data)
                df['datetime'] = pd.to_datetime(df['datetime'])
                df = df.set_index('datetime')
                ts_data = df[value_column].dropna()
                
                if len(ts_data) < 50:
                    return {"error": "Prophet 모델을 위해서는 최소 50개의 데이터 포인트가 필요합니다."}
                
                # Prophet 형식으로 변환
                prophet_df = pd.DataFrame({
                    'ds': ts_data.index,
                    'y': ts_data.values
                })
                
                # Prophet 모델 설정
                model = Prophet(
                    daily_seasonality=True,
                    weekly_seasonality=True,
                    yearly_seasonality=True,
                    seasonality_mode='multiplicative'
                )
                
                if include_holidays:
                    # 한국 공휴일 추가 (간단한 예시)
                    holidays = pd.DataFrame({
                        'holiday': 'korean_holiday',
                        'ds': pd.to_datetime(['2024-01-01', '2024-02-09', '2024-02-10', '2024-02-11', '2024-02-12']),
                        'lower_window': 0,
                        'upper_window': 1,
                    })
                    model.add_country_holidays(country_name='KR')
                
                # 모델 훈련
                model.fit(prophet_df)
                
                # 미래 데이터프레임 생성
                future = model.make_future_dataframe(periods=periods, freq='H')
                
                # 예측 수행
                forecast = model.predict(future)
                
                # 예측 결과만 추출
                forecast_period = forecast.tail(periods)
                
                # 결과 정리
                forecast_data = []
                for _, row in forecast_period.iterrows():
                    forecast_data.append({
                        "datetime": str(row['ds']),
                        "forecast": float(row['yhat']),
                        "lower_bound": float(row['yhat_lower']),
                        "upper_bound": float(row['yhat_upper'])
                    })
                
                # 계절성 분석
                components = model.plot_components(forecast, figsize=(12, 8))
                
                return {
                    "success": True,
                    "model_type": "Prophet",
                    "forecast_periods": periods,
                    "include_holidays": include_holidays,
                    "forecast_data": forecast_data,
                    "training_data_points": len(ts_data),
                    "seasonality_detected": {
                        "daily": True,
                        "weekly": True,
                        "yearly": True
                    }
                }
                
            except Exception as e:
                return {"error": f"Prophet 예측 실패: {str(e)}"}
        
        @self.mcp.tool
        async def lstm_forecast(data: List[Dict], value_column: str = "consumption", 
                              periods: int = 30, sequence_length: int = 24, 
                              epochs: int = 50) -> Dict[str, Any]:
            """
            LSTM 모델을 사용하여 에너지 소비량을 예측합니다.
            
            Args:
                data: 시계열 데이터
                value_column: 값 컬럼명
                periods: 예측 기간
                sequence_length: 입력 시퀀스 길이
                epochs: 훈련 에포크 수
                
            Returns:
                LSTM 예측 결과
            """
            try:
                from sklearn.preprocessing import MinMaxScaler
                from tensorflow.keras.models import Sequential
                from tensorflow.keras.layers import LSTM, Dense, Dropout
                from tensorflow.keras.optimizers import Adam
                
                # 데이터 준비
                df = pd.DataFrame(data)
                df['datetime'] = pd.to_datetime(df['datetime'])
                df = df.set_index('datetime')
                ts_data = df[value_column].dropna()
                
                if len(ts_data) < 100:
                    return {"error": "LSTM 모델을 위해서는 최소 100개의 데이터 포인트가 필요합니다."}
                
                # 데이터 정규화
                scaler = MinMaxScaler()
                scaled_data = scaler.fit_transform(ts_data.values.reshape(-1, 1))
                
                # 시퀀스 데이터 생성
                def create_sequences(data, seq_length):
                    X, y = [], []
                    for i in range(seq_length, len(data)):
                        X.append(data[i-seq_length:i])
                        y.append(data[i])
                    return np.array(X), np.array(y)
                
                X, y = create_sequences(scaled_data, sequence_length)
                
                # 훈련/테스트 분할
                split_index = int(len(X) * 0.8)
                X_train, X_test = X[:split_index], X[split_index:]
                y_train, y_test = y[:split_index], y[split_index:]
                
                # LSTM 모델 구성
                model = Sequential([
                    LSTM(50, return_sequences=True, input_shape=(sequence_length, 1)),
                    Dropout(0.2),
                    LSTM(50, return_sequences=False),
                    Dropout(0.2),
                    Dense(1)
                ])
                
                model.compile(optimizer=Adam(learning_rate=0.001), loss='mse')
                
                # 모델 훈련
                history = model.fit(X_train, y_train, 
                                  validation_data=(X_test, y_test),
                                  epochs=epochs, 
                                  batch_size=32, 
                                  verbose=0)
                
                # 예측 수행
                last_sequence = scaled_data[-sequence_length:].reshape(1, sequence_length, 1)
                predictions = []
                
                for _ in range(periods):
                    pred = model.predict(last_sequence, verbose=0)
                    predictions.append(pred[0, 0])
                    
                    # 시퀀스 업데이트
                    last_sequence = np.append(last_sequence[:, 1:, :], pred.reshape(1, 1, 1), axis=1)
                
                # 예측 결과 역정규화
                predictions = scaler.inverse_transform(np.array(predictions).reshape(-1, 1))
                
                # 예측 날짜 생성
                last_date = ts_data.index[-1]
                forecast_dates = pd.date_range(start=last_date + timedelta(hours=1), periods=periods, freq='H')
                
                # 결과 정리
                forecast_data = []
                for date, pred in zip(forecast_dates, predictions):
                    forecast_data.append({
                        "datetime": str(date),
                        "forecast": float(pred[0])
                    })
                
                # 모델 성능 평가
                train_loss = history.history['loss'][-1]
                val_loss = history.history['val_loss'][-1]
                
                return {
                    "success": True,
                    "model_type": "LSTM",
                    "forecast_periods": periods,
                    "sequence_length": sequence_length,
                    "epochs": epochs,
                    "model_metrics": {
                        "final_train_loss": float(train_loss),
                        "final_val_loss": float(val_loss)
                    },
                    "forecast_data": forecast_data,
                    "training_data_points": len(ts_data)
                }
                
            except Exception as e:
                return {"error": f"LSTM 예측 실패: {str(e)}"}
        
        @self.mcp.tool
        async def compare_models(data: List[Dict], value_column: str = "consumption", 
                               periods: int = 30, test_split: float = 0.2) -> Dict[str, Any]:
            """
            여러 예측 모델의 성능을 비교합니다.
            
            Args:
                data: 시계열 데이터
                value_column: 값 컬럼명
                periods: 예측 기간
                test_split: 테스트 데이터 비율
                
            Returns:
                모델 비교 결과
            """
            try:
                from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
                
                # 데이터 준비
                df = pd.DataFrame(data)
                df['datetime'] = pd.to_datetime(df['datetime'])
                df = df.set_index('datetime')
                ts_data = df[value_column].dropna()
                
                if len(ts_data) < 100:
                    return {"error": "모델 비교를 위해서는 최소 100개의 데이터 포인트가 필요합니다."}
                
                # 훈련/테스트 분할
                split_index = int(len(ts_data) * (1 - test_split))
                train_data = ts_data[:split_index]
                test_data = ts_data[split_index:]
                
                results = {}
                
                # ARIMA 모델
                try:
                    from statsmodels.tsa.arima.model import ARIMA
                    arima_model = ARIMA(train_data, order=(1, 1, 1))
                    arima_fitted = arima_model.fit()
                    arima_forecast = arima_fitted.forecast(steps=len(test_data))
                    
                    results['ARIMA'] = {
                        'mae': float(mean_absolute_error(test_data, arima_forecast)),
                        'mse': float(mean_squared_error(test_data, arima_forecast)),
                        'rmse': float(np.sqrt(mean_squared_error(test_data, arima_forecast))),
                        'r2': float(r2_score(test_data, arima_forecast))
                    }
                except Exception as e:
                    results['ARIMA'] = {'error': str(e)}
                
                # Prophet 모델
                try:
                    from prophet import Prophet
                    prophet_df = pd.DataFrame({
                        'ds': train_data.index,
                        'y': train_data.values
                    })
                    prophet_model = Prophet()
                    prophet_model.fit(prophet_df)
                    
                    future = prophet_model.make_future_dataframe(periods=len(test_data), freq='H')
                    prophet_forecast = prophet_model.predict(future)
                    prophet_predictions = prophet_forecast['yhat'].tail(len(test_data))
                    
                    results['Prophet'] = {
                        'mae': float(mean_absolute_error(test_data, prophet_predictions)),
                        'mse': float(mean_squared_error(test_data, prophet_predictions)),
                        'rmse': float(np.sqrt(mean_squared_error(test_data, prophet_predictions))),
                        'r2': float(r2_score(test_data, prophet_predictions))
                    }
                except Exception as e:
                    results['Prophet'] = {'error': str(e)}
                
                # 모델 성능 순위
                model_rankings = []
                for model_name, metrics in results.items():
                    if 'error' not in metrics:
                        model_rankings.append({
                            'model': model_name,
                            'mae': metrics['mae'],
                            'rmse': metrics['rmse'],
                            'r2': metrics['r2']
                        })
                
                # MAE 기준으로 정렬
                model_rankings.sort(key=lambda x: x['mae'])
                
                return {
                    "success": True,
                    "test_data_points": len(test_data),
                    "model_results": results,
                    "rankings": model_rankings,
                    "best_model": model_rankings[0]['model'] if model_rankings else None
                }
                
            except Exception as e:
                return {"error": f"모델 비교 실패: {str(e)}"}

