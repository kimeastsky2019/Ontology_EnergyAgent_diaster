#!/usr/bin/env python3
"""
간단한 테스트 스크립트
"""

import sys
import os

def test_imports():
    """라이브러리 import 테스트"""
    print("=== 라이브러리 Import 테스트 ===")
    
    try:
        import numpy as np
        print("✅ NumPy: OK")
    except ImportError as e:
        print(f"❌ NumPy: {e}")
    
    try:
        import pandas as pd
        print("✅ Pandas: OK")
    except ImportError as e:
        print(f"❌ Pandas: {e}")
    
    try:
        import sklearn
        print("✅ Scikit-learn: OK")
    except ImportError as e:
        print(f"❌ Scikit-learn: {e}")
    
    try:
        import optuna
        print("✅ Optuna: OK")
    except ImportError as e:
        print(f"❌ Optuna: {e}")
    
    try:
        import xgboost
        print("✅ XGBoost: OK")
    except ImportError as e:
        print(f"❌ XGBoost: {e}")
    
    try:
        import tensorflow as tf
        print("✅ TensorFlow: OK")
        print(f"   버전: {tf.__version__}")
    except ImportError as e:
        print(f"❌ TensorFlow: {e}")

def test_basic_functionality():
    """기본 기능 테스트"""
    print("\n=== 기본 기능 테스트 ===")
    
    try:
        import numpy as np
        import pandas as pd
        
        # 간단한 데이터 생성
        data = np.random.randn(100, 5)
        df = pd.DataFrame(data, columns=['A', 'B', 'C', 'D', 'E'])
        
        print("✅ 데이터 생성: OK")
        print(f"   데이터 크기: {df.shape}")
        
        # 기본 통계
        stats = df.describe()
        print("✅ 통계 계산: OK")
        print(f"   평균: {df.mean().mean():.4f}")
        
        # 간단한 모델
        from sklearn.linear_model import LinearRegression
        from sklearn.model_selection import train_test_split
        
        X = df[['A', 'B', 'C', 'D']]
        y = df['E']
        
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        model = LinearRegression()
        model.fit(X_train, y_train)
        
        score = model.score(X_test, y_test)
        print("✅ 모델 훈련: OK")
        print(f"   R² 점수: {score:.4f}")
        
    except Exception as e:
        print(f"❌ 기본 기능 테스트 실패: {e}")

def test_mcp_server():
    """MCP 서버 테스트"""
    print("\n=== MCP 서버 테스트 ===")
    
    try:
        from fastmcp import FastMCP
        print("✅ FastMCP: OK")
        
        # 간단한 MCP 서버 생성
        mcp = FastMCP("Test Server", "1.0.0", "Test Description")
        print("✅ MCP 서버 생성: OK")
        
    except Exception as e:
        print(f"❌ MCP 서버 테스트 실패: {e}")

def main():
    """메인 함수"""
    print("🚀 에너지 분석 시스템 테스트 시작")
    print(f"Python 버전: {sys.version}")
    print(f"작업 디렉토리: {os.getcwd()}")
    
    test_imports()
    test_basic_functionality()
    test_mcp_server()
    
    print("\n🎉 테스트 완료!")

if __name__ == "__main__":
    main()
