"""
Energy Demand Analysis AI Agent
Features: Data Preprocessing, Time Series Forecasting, Anomaly Detection, Data Quality Validation
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from sklearn.ensemble import IsolationForest, RandomForestRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import warnings
warnings.filterwarnings('ignore')

class EnergyDemandAgent:
    def __init__(self, data_path):
        self.data_path = data_path
        self.raw_data = None
        self.clean_data = None
        self.quality_report = {}
        self.anomalies = None
        self.predictions = None
        self.model = None
        self.scaler = StandardScaler()
        
    def load_data(self):
        """Load and perform initial data inspection"""
        print("🔄 Loading data...")
        self.raw_data = pd.read_csv(self.data_path)
        
        # Keep only relevant columns (first few columns contain the actual data)
        relevant_cols = ['time', 'kWh', 'kW', 'year', 'month', 'day']
        self.raw_data = self.raw_data[relevant_cols]
        
        print(f"✅ Loaded {len(self.raw_data)} records")
        return self.raw_data
    
    def validate_data_quality(self):
        """Comprehensive data quality validation"""
        print("\n🔍 Validating data quality...")
        
        report = {
            'total_records': len(self.raw_data),
            'missing_values': {},
            'duplicates': 0,
            'outliers': {},
            'data_types': {},
            'date_range': {},
            'quality_score': 0
        }
        
        # Check missing values
        for col in self.raw_data.columns:
            missing = self.raw_data[col].isnull().sum()
            missing_pct = (missing / len(self.raw_data)) * 100
            report['missing_values'][col] = {
                'count': int(missing),
                'percentage': round(missing_pct, 2)
            }
        
        # Check duplicates
        report['duplicates'] = int(self.raw_data.duplicated().sum())
        
        # Check data types
        for col in self.raw_data.columns:
            report['data_types'][col] = str(self.raw_data[col].dtype)
        
        # Check numeric outliers using IQR method
        for col in ['kWh', 'kW']:
            if col in self.raw_data.columns:
                Q1 = self.raw_data[col].quantile(0.25)
                Q3 = self.raw_data[col].quantile(0.75)
                IQR = Q3 - Q1
                outliers = ((self.raw_data[col] < (Q1 - 1.5 * IQR)) | 
                           (self.raw_data[col] > (Q3 + 1.5 * IQR))).sum()
                report['outliers'][col] = int(outliers)
        
        # Date range
        try:
            self.raw_data['time'] = pd.to_datetime(self.raw_data['time'])
            report['date_range'] = {
                'start': str(self.raw_data['time'].min()),
                'end': str(self.raw_data['time'].max()),
                'duration_days': int((self.raw_data['time'].max() - self.raw_data['time'].min()).days)
            }
        except:
            pass
        
        # Calculate quality score
        quality_score = 100
        quality_score -= min(report['missing_values'].get('kWh', {}).get('percentage', 0), 20)
        quality_score -= min(report['missing_values'].get('kW', {}).get('percentage', 0), 20)
        quality_score -= min((report['duplicates'] / len(self.raw_data)) * 100, 10)
        report['quality_score'] = round(max(quality_score, 0), 2)
        
        self.quality_report = report
        print(f"✅ Data Quality Score: {report['quality_score']}/100")
        return report
    
    def preprocess_data(self):
        """Clean and prepare data for analysis"""
        print("\n🧹 Preprocessing data...")
        
        df = self.raw_data.copy()
        
        # Convert time to datetime
        df['time'] = pd.to_datetime(df['time'], errors='coerce')
        
        # Remove rows with invalid timestamps
        df = df.dropna(subset=['time'])
        
        # Handle missing values in kWh and kW
        df['kWh'] = pd.to_numeric(df['kWh'], errors='coerce')
        df['kW'] = pd.to_numeric(df['kW'], errors='coerce')
        
        # Fill missing values with interpolation
        df['kWh'] = df['kWh'].interpolate(method='linear')
        df['kW'] = df['kW'].interpolate(method='linear')
        
        # Remove remaining NaN values
        df = df.dropna(subset=['kWh', 'kW'])
        
        # Remove duplicates
        df = df.drop_duplicates(subset=['time'], keep='first')
        
        # Sort by time
        df = df.sort_values('time').reset_index(drop=True)
        
        # Add temporal features
        df['hour'] = df['time'].dt.hour
        df['day_of_week'] = df['time'].dt.dayofweek
        df['day_of_year'] = df['time'].dt.dayofyear
        df['week_of_year'] = df['time'].dt.isocalendar().week
        df['is_weekend'] = df['day_of_week'].isin([5, 6]).astype(int)
        
        # Add rolling statistics
        df['kWh_rolling_mean_24h'] = df['kWh'].rolling(window=48, min_periods=1).mean()
        df['kWh_rolling_std_24h'] = df['kWh'].rolling(window=48, min_periods=1).std()
        df['kW_rolling_mean_24h'] = df['kW'].rolling(window=48, min_periods=1).mean()
        
        self.clean_data = df
        print(f"✅ Preprocessed {len(df)} records")
        return df
    
    def detect_anomalies(self):
        """Detect anomalies using Isolation Forest"""
        print("\n🚨 Detecting anomalies...")
        
        df = self.clean_data.copy()
        
        # Features for anomaly detection
        features = ['kWh', 'kW', 'hour', 'day_of_week', 'is_weekend']
        X = df[features].fillna(0)
        
        # Normalize features
        X_scaled = self.scaler.fit_transform(X)
        
        # Isolation Forest
        iso_forest = IsolationForest(
            contamination=0.05,  # 5% anomalies
            random_state=42,
            n_estimators=100
        )
        
        df['anomaly'] = iso_forest.fit_predict(X_scaled)
        df['anomaly_score'] = iso_forest.score_samples(X_scaled)
        
        # Mark anomalies (1 = normal, -1 = anomaly)
        df['is_anomaly'] = (df['anomaly'] == -1).astype(int)
        
        anomaly_count = df['is_anomaly'].sum()
        anomaly_pct = (anomaly_count / len(df)) * 100
        
        self.anomalies = df[df['is_anomaly'] == 1].copy()
        self.clean_data = df
        
        print(f"✅ Found {anomaly_count} anomalies ({anomaly_pct:.2f}%)")
        return self.anomalies
    
    def create_features_for_prediction(self, df):
        """Create features for machine learning model"""
        features = [
            'hour', 'day_of_week', 'day_of_year', 'week_of_year',
            'is_weekend', 'kWh_rolling_mean_24h', 'kWh_rolling_std_24h',
            'kW_rolling_mean_24h'
        ]
        
        X = df[features].fillna(method='ffill').fillna(0)
        y = df['kWh']
        
        return X, y
    
    def train_forecast_model(self):
        """Train Random Forest model for forecasting"""
        print("\n🤖 Training forecasting model...")
        
        # Split data: 80% train, 20% test
        split_idx = int(len(self.clean_data) * 0.8)
        train_data = self.clean_data.iloc[:split_idx]
        test_data = self.clean_data.iloc[split_idx:]
        
        # Create features
        X_train, y_train = self.create_features_for_prediction(train_data)
        X_test, y_test = self.create_features_for_prediction(test_data)
        
        # Train Random Forest model
        self.model = RandomForestRegressor(
            n_estimators=100,
            max_depth=15,
            min_samples_split=5,
            random_state=42,
            n_jobs=-1
        )
        
        self.model.fit(X_train, y_train)
        
        # Make predictions on test set
        y_pred = self.model.predict(X_test)
        
        # Calculate metrics
        mae = mean_absolute_error(y_test, y_pred)
        rmse = np.sqrt(mean_squared_error(y_test, y_pred))
        r2 = r2_score(y_test, y_pred)
        mape = np.mean(np.abs((y_test - y_pred) / y_test)) * 100
        
        metrics = {
            'MAE': round(mae, 2),
            'RMSE': round(rmse, 2),
            'R2': round(r2, 4),
            'MAPE': round(mape, 2)
        }
        
        print(f"✅ Model trained - R²: {r2:.4f}, MAE: {mae:.2f} kWh")
        return metrics, test_data, y_pred
    
    def generate_future_predictions(self, hours_ahead=168):  # 7 days
        """Generate future predictions"""
        print(f"\n🔮 Generating predictions for next {hours_ahead} hours...")
        
        last_timestamp = self.clean_data['time'].max()
        last_record = self.clean_data.iloc[-1]
        
        future_predictions = []
        
        for i in range(1, hours_ahead + 1):
            future_time = last_timestamp + timedelta(minutes=30 * i)
            
            # Create features for future timestamp
            future_features = {
                'hour': future_time.hour,
                'day_of_week': future_time.dayofweek,
                'day_of_year': future_time.dayofyear,
                'week_of_year': future_time.isocalendar()[1],
                'is_weekend': 1 if future_time.dayofweek in [5, 6] else 0,
                'kWh_rolling_mean_24h': last_record['kWh_rolling_mean_24h'],
                'kWh_rolling_std_24h': last_record['kWh_rolling_std_24h'],
                'kW_rolling_mean_24h': last_record['kW_rolling_mean_24h']
            }
            
            X_future = pd.DataFrame([future_features])
            prediction = self.model.predict(X_future)[0]
            
            future_predictions.append({
                'time': future_time,
                'predicted_kWh': prediction,
                'confidence_lower': prediction * 0.85,
                'confidence_upper': prediction * 1.15
            })
        
        self.predictions = pd.DataFrame(future_predictions)
        print(f"✅ Generated {len(self.predictions)} predictions")
        return self.predictions
    
    def get_statistics(self):
        """Calculate key statistics"""
        stats = {
            'total_energy_consumed': round(self.clean_data['kWh'].sum(), 2),
            'average_consumption': round(self.clean_data['kWh'].mean(), 2),
            'peak_demand': round(self.clean_data['kW'].max(), 2),
            'min_demand': round(self.clean_data['kW'].min(), 2),
            'std_deviation': round(self.clean_data['kWh'].std(), 2),
            'total_records': len(self.clean_data),
            'anomalies_detected': int(self.clean_data['is_anomaly'].sum()),
            'data_quality_score': self.quality_report.get('quality_score', 0)
        }
        
        # Peak hours analysis
        hourly_avg = self.clean_data.groupby('hour')['kWh'].mean()
        stats['peak_hour'] = int(hourly_avg.idxmax())
        stats['off_peak_hour'] = int(hourly_avg.idxmin())
        
        return stats
    
    def run_full_analysis(self):
        """Run complete analysis pipeline"""
        print("=" * 60)
        print("🚀 ENERGY DEMAND ANALYSIS AI AGENT")
        print("=" * 60)
        
        # Step 1: Load data
        self.load_data()
        
        # Step 2: Data quality validation
        quality = self.validate_data_quality()
        
        # Step 3: Preprocess data
        self.preprocess_data()
        
        # Step 4: Detect anomalies
        self.detect_anomalies()
        
        # Step 5: Train forecasting model
        metrics, test_data, predictions = self.train_forecast_model()
        
        # Step 6: Generate future predictions
        self.generate_future_predictions()
        
        # Step 7: Calculate statistics
        stats = self.get_statistics()
        
        print("\n" + "=" * 60)
        print("✅ ANALYSIS COMPLETE")
        print("=" * 60)
        
        return {
            'quality_report': quality,
            'metrics': metrics,
            'statistics': stats,
            'clean_data': self.clean_data,
            'anomalies': self.anomalies,
            'predictions': self.predictions
        }


if __name__ == "__main__":
    # Initialize and run agent
    agent = EnergyDemandAgent('/mnt/user-data/uploads/202407_202510.csv')
    results = agent.run_full_analysis()
    
    # Save processed data
    agent.clean_data.to_csv('/home/claude/processed_energy_data.csv', index=False)
    agent.predictions.to_csv('/home/claude/energy_predictions.csv', index=False)
    
    print("\n📊 Files saved:")
    print("  - processed_energy_data.csv")
    print("  - energy_predictions.csv")
