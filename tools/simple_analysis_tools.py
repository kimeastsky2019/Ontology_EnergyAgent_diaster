"""
간소화된 데이터 분석 도구

LangGraph Agent와 함께 사용하기 위한 간단하고 직관적인 데이터 분석 도구들을 제공합니다.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, Any, List, Optional, Union
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score, root_mean_squared_error
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.svm import SVC, SVR
from fastmcp import FastMCP
import os

class SimpleAnalysisTools:
    """간소화된 데이터 분석 도구들"""
    
    def __init__(self, mcp: FastMCP):
        self.mcp = mcp
        self._register_tools()
    
    def _register_tools(self):
        """도구들을 MCP 서버에 등록"""
        
        @self.mcp.tool
        async def describe_energy_column(csv_path: str, column: str) -> Dict[str, Any]:
            """
            에너지 데이터의 특정 컬럼에 대한 요약 통계를 제공합니다.
            
            Args:
                csv_path: CSV 파일 경로
                column: 분석할 컬럼명
                
            Returns:
                컬럼의 요약 통계 정보
            """
            try:
                df = pd.read_csv(csv_path)
                if column not in df.columns:
                    return {"error": f"컬럼 '{column}'을 찾을 수 없습니다."}
                
                stats = df[column].describe().to_dict()
                
                # 추가 통계 정보
                additional_stats = {
                    "missing_count": df[column].isnull().sum(),
                    "missing_percentage": (df[column].isnull().sum() / len(df)) * 100,
                    "unique_count": df[column].nunique(),
                    "data_type": str(df[column].dtype)
                }
                
                return {
                    "basic_stats": stats,
                    "additional_info": additional_stats,
                    "column_name": column,
                    "total_rows": len(df)
                }
                
            except Exception as e:
                return {"error": f"데이터 분석 중 오류 발생: {str(e)}"}
        
        @self.mcp.tool
        async def plot_energy_distribution(csv_path: str, column: str, bins: int = 20, 
                                         chart_type: str = "histogram") -> Dict[str, Any]:
            """
            에너지 데이터의 분포를 시각화합니다.
            
            Args:
                csv_path: CSV 파일 경로
                column: 시각화할 컬럼명
                bins: 히스토그램 구간 수
                chart_type: 차트 유형 (histogram, density, box)
                
            Returns:
                생성된 차트 파일 경로와 정보
            """
            try:
                df = pd.read_csv(csv_path)
                if column not in df.columns:
                    return {"error": f"컬럼 '{column}'을 찾을 수 없습니다."}
                
                # 데이터 정리
                data = df[column].dropna()
                
                if len(data) == 0:
                    return {"error": "시각화할 데이터가 없습니다."}
                
                # 차트 생성
                plt.figure(figsize=(10, 6))
                
                if chart_type == "histogram":
                    sns.histplot(
                        data,
                        bins=bins,
                        kde=True,
                        stat="density",
                        edgecolor="black",
                        alpha=0.6
                    )
                    plt.title(f"에너지 데이터 분포: {column}")
                    
                elif chart_type == "density":
                    sns.histplot(
                        data,
                        kde=True,
                        stat="density",
                        alpha=0.6
                    )
                    plt.title(f"에너지 데이터 밀도: {column}")
                    
                elif chart_type == "box":
                    sns.boxplot(y=data)
                    plt.title(f"에너지 데이터 박스플롯: {column}")
                
                plt.xlabel(column)
                plt.ylabel("빈도" if chart_type != "box" else "값")
                
                # 파일 저장
                output_path = f"energy_{column}_{chart_type}.png"
                plt.savefig(output_path, dpi=300, bbox_inches='tight')
                plt.close()
                
                return {
                    "chart_path": output_path,
                    "column": column,
                    "chart_type": chart_type,
                    "data_points": len(data),
                    "statistics": {
                        "mean": float(data.mean()),
                        "std": float(data.std()),
                        "min": float(data.min()),
                        "max": float(data.max())
                    }
                }
                
            except Exception as e:
                return {"error": f"시각화 중 오류 발생: {str(e)}"}
        
        @self.mcp.tool
        async def train_energy_model(csv_path: str, x_columns: List[str], y_column: str, 
                                   model_type: str = "auto") -> Dict[str, Any]:
            """
            에너지 데이터에 대한 예측 모델을 자동으로 학습합니다.
            
            Args:
                csv_path: CSV 파일 경로
                x_columns: 특성 컬럼 목록
                y_column: 타겟 컬럼명
                model_type: 모델 유형 (auto, classification, regression)
                
            Returns:
                모델 학습 결과 및 성능 지표
            """
            try:
                df = pd.read_csv(csv_path)
                
                # 컬럼 존재 확인
                for col in x_columns + [y_column]:
                    if col not in df.columns:
                        return {"error": f"컬럼 '{col}'을 찾을 수 없습니다."}
                
                # 데이터 준비
                X = df[x_columns].copy()
                y = df[y_column].copy()
                
                # 범주형 변수 인코딩
                for col in X.select_dtypes(include=["object"]).columns:
                    le = LabelEncoder()
                    X[col] = le.fit_transform(X[col].astype(str))
                
                # 타겟 변수 타입 확인
                if model_type == "auto":
                    is_classification = y.dtype == "object" or len(y.unique()) <= 10
                else:
                    is_classification = model_type == "classification"
                
                if is_classification:
                    y = LabelEncoder().fit_transform(y.astype(str))
                    models = {
                        "RandomForest": RandomForestClassifier(n_estimators=100, random_state=42),
                        "SVM": SVC(random_state=42)
                    }
                    metric_name = "accuracy"
                else:
                    models = {
                        "RandomForest": RandomForestRegressor(n_estimators=100, random_state=42),
                        "LinearRegression": LinearRegression(),
                        "SVM": SVR()
                    }
                    metric_name = "rmse"
                
                # 데이터 분할
                X_train, X_test, y_train, y_test = train_test_split(
                    X, y, test_size=0.2, random_state=42
                )
                
                # 모델 학습 및 평가
                results = {}
                best_model = None
                best_score = -np.inf if is_classification else np.inf
                
                for model_name, model in models.items():
                    try:
                        model.fit(X_train, y_train)
                        y_pred = model.predict(X_test)
                        
                        if is_classification:
                            score = accuracy_score(y_test, y_pred)
                        else:
                            score = root_mean_squared_error(y_test, y_pred, squared=False)
                        
                        results[model_name] = {
                            "score": float(score),
                            "model_type": "classification" if is_classification else "regression"
                        }
                        
                        # 최고 성능 모델 선택
                        if is_classification and score > best_score:
                            best_score = score
                            best_model = model_name
                        elif not is_classification and score < best_score:
                            best_score = score
                            best_model = model_name
                            
                    except Exception as e:
                        results[model_name] = {"error": str(e)}
                
                return {
                    "model_results": results,
                    "best_model": best_model,
                    "best_score": float(best_score),
                    "metric": metric_name,
                    "target_type": "classification" if is_classification else "regression",
                    "feature_columns": x_columns,
                    "target_column": y_column,
                    "training_samples": len(X_train),
                    "test_samples": len(X_test)
                }
                
            except Exception as e:
                return {"error": f"모델 학습 중 오류 발생: {str(e)}"}
        
        @self.mcp.tool
        async def analyze_energy_correlation(csv_path: str, columns: List[str]) -> Dict[str, Any]:
            """
            에너지 데이터 컬럼들 간의 상관관계를 분석합니다.
            
            Args:
                csv_path: CSV 파일 경로
                columns: 분석할 컬럼 목록
                
            Returns:
                상관관계 분석 결과
            """
            try:
                df = pd.read_csv(csv_path)
                
                # 컬럼 존재 확인
                missing_cols = [col for col in columns if col not in df.columns]
                if missing_cols:
                    return {"error": f"다음 컬럼들을 찾을 수 없습니다: {missing_cols}"}
                
                # 수치형 컬럼만 선택
                numeric_df = df[columns].select_dtypes(include=[np.number])
                
                if len(numeric_df.columns) < 2:
                    return {"error": "상관관계 분석을 위해 최소 2개의 수치형 컬럼이 필요합니다."}
                
                # 상관관계 계산
                correlation_matrix = numeric_df.corr()
                
                # 히트맵 생성
                plt.figure(figsize=(10, 8))
                sns.heatmap(
                    correlation_matrix,
                    annot=True,
                    cmap='coolwarm',
                    center=0,
                    square=True,
                    fmt='.2f'
                )
                plt.title("에너지 데이터 상관관계 히트맵")
                plt.tight_layout()
                
                # 히트맵 저장
                heatmap_path = "energy_correlation_heatmap.png"
                plt.savefig(heatmap_path, dpi=300, bbox_inches='tight')
                plt.close()
                
                # 강한 상관관계 찾기
                strong_correlations = []
                for i in range(len(correlation_matrix.columns)):
                    for j in range(i+1, len(correlation_matrix.columns)):
                        corr_value = correlation_matrix.iloc[i, j]
                        if abs(corr_value) > 0.7:  # 강한 상관관계
                            strong_correlations.append({
                                "column1": correlation_matrix.columns[i],
                                "column2": correlation_matrix.columns[j],
                                "correlation": float(corr_value)
                            })
                
                return {
                    "correlation_matrix": correlation_matrix.to_dict(),
                    "heatmap_path": heatmap_path,
                    "strong_correlations": strong_correlations,
                    "analyzed_columns": list(numeric_df.columns),
                    "total_columns": len(columns)
                }
                
            except Exception as e:
                return {"error": f"상관관계 분석 중 오류 발생: {str(e)}"}
        
        @self.mcp.tool
        async def get_energy_data_info(csv_path: str) -> Dict[str, Any]:
            """
            에너지 데이터 파일의 기본 정보를 제공합니다.
            
            Args:
                csv_path: CSV 파일 경로
                
            Returns:
                데이터 파일의 기본 정보
            """
            try:
                df = pd.read_csv(csv_path)
                
                info = {
                    "file_path": csv_path,
                    "total_rows": len(df),
                    "total_columns": len(df.columns),
                    "columns": list(df.columns),
                    "data_types": df.dtypes.to_dict(),
                    "missing_values": df.isnull().sum().to_dict(),
                    "memory_usage": f"{df.memory_usage(deep=True).sum() / 1024 / 1024:.2f} MB",
                    "file_size": f"{os.path.getsize(csv_path) / 1024 / 1024:.2f} MB" if os.path.exists(csv_path) else "Unknown"
                }
                
                # 수치형 컬럼의 기본 통계
                numeric_cols = df.select_dtypes(include=[np.number]).columns
                if len(numeric_cols) > 0:
                    info["numeric_summary"] = df[numeric_cols].describe().to_dict()
                
                # 범주형 컬럼의 기본 정보
                categorical_cols = df.select_dtypes(include=['object']).columns
                if len(categorical_cols) > 0:
                    cat_info = {}
                    for col in categorical_cols:
                        cat_info[col] = {
                            "unique_count": df[col].nunique(),
                            "most_common": df[col].mode().iloc[0] if not df[col].mode().empty else None,
                            "most_common_count": df[col].value_counts().iloc[0] if not df[col].empty else 0
                        }
                    info["categorical_summary"] = cat_info
                
                return info
                
            except Exception as e:
                return {"error": f"데이터 정보 조회 중 오류 발생: {str(e)}"}
