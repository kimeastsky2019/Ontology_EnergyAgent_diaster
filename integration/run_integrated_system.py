#!/usr/bin/env python3
"""
통합 에너지 분석 시스템 실행 스크립트
"""

import argparse
import subprocess
import sys
import os
import time
import signal
import threading
from pathlib import Path

def run_command(command, background=False):
    """명령어 실행"""
    if background:
        return subprocess.Popen(command, shell=True)
    else:
        return subprocess.run(command, shell=True)

def start_integrated_system(service_type="all"):
    """통합 시스템 시작"""
    print("🔋 통합 에너지 분석 시스템")
    print("=" * 50)
    
    if service_type == "all":
        print("🚀 모든 서비스 시작 중...")
        
        processes = []
        
        try:
            # 1. 기존 Energy Analysis MCP Server
            print("Starting Energy Analysis MCP Server...")
            proc1 = run_command("cd .. && python server.py", background=True)
            processes.append(("Energy Analysis MCP", proc1))
            time.sleep(3)
            
            # 2. Multi-MCP Time Series Analysis System
            print("Starting Multi-MCP Time Series Analysis System...")
            proc2 = run_command("cd ../multi_mcp_system && python run_service.py start --service local", background=True)
            processes.append(("Multi-MCP System", proc2))
            time.sleep(5)
            
            # 3. 통합 MCP 서버
            print("Starting Integrated MCP Server...")
            proc3 = run_command("python energy_mcp_integration.py", background=True)
            processes.append(("Integrated MCP", proc3))
            time.sleep(3)
            
            # 4. 통합 API 서버
            print("Starting Unified API Server...")
            proc4 = run_command("python unified_api.py", background=True)
            processes.append(("Unified API", proc4))
            time.sleep(3)
            
            # 5. 에너지 대시보드
            print("Starting Energy Dashboard...")
            proc5 = run_command("python energy_dashboard.py", background=True)
            processes.append(("Energy Dashboard", proc5))
            
            print("\n✅ 모든 서비스가 시작되었습니다!")
            print("\n📊 서비스 접근 URL:")
            print("  🔋 Energy Dashboard: http://localhost:5002")
            print("  🔌 Unified API: http://localhost:5003")
            print("  📈 Multi-MCP Dashboard: http://localhost:5000")
            print("  🔌 Multi-MCP API: http://localhost:5001")
            print("  📊 Forecasting MCP: http://localhost:8001")
            print("  🔍 Anomaly MCP: http://localhost:8002")
            print("  🤝 Coordinator MCP: http://localhost:8003")
            print("  📊 Prometheus: http://localhost:9090")
            print("  📈 Grafana: http://localhost:3000")
            print("\nPress Ctrl+C to stop all services")
            
            # 신호 처리
            def signal_handler(sig, frame):
                print("\n🛑 모든 서비스 중지 중...")
                for name, proc in processes:
                    if proc.poll() is None:
                        print(f"Stopping {name}...")
                        proc.terminate()
                sys.exit(0)
            
            signal.signal(signal.SIGINT, signal_handler)
            
            # 모든 프로세스가 종료될 때까지 대기
            for name, proc in processes:
                proc.wait()
                
        except KeyboardInterrupt:
            print("\n🛑 모든 서비스 중지 중...")
            for name, proc in processes:
                if proc.poll() is None:
                    print(f"Stopping {name}...")
                    proc.terminate()
    
    elif service_type == "integration":
        print("🔗 통합 서비스만 시작...")
        
        processes = []
        
        try:
            # 통합 MCP 서버
            print("Starting Integrated MCP Server...")
            proc1 = run_command("python energy_mcp_integration.py", background=True)
            processes.append(("Integrated MCP", proc1))
            time.sleep(3)
            
            # 통합 API 서버
            print("Starting Unified API Server...")
            proc2 = run_command("python unified_api.py", background=True)
            processes.append(("Unified API", proc2))
            time.sleep(3)
            
            # 에너지 대시보드
            print("Starting Energy Dashboard...")
            proc3 = run_command("python energy_dashboard.py", background=True)
            processes.append(("Energy Dashboard", proc3))
            
            print("\n✅ 통합 서비스가 시작되었습니다!")
            print("\n📊 서비스 접근 URL:")
            print("  🔋 Energy Dashboard: http://localhost:5002")
            print("  🔌 Unified API: http://localhost:5003")
            print("\nPress Ctrl+C to stop services")
            
            # 신호 처리
            def signal_handler(sig, frame):
                print("\n🛑 서비스 중지 중...")
                for name, proc in processes:
                    if proc.poll() is None:
                        print(f"Stopping {name}...")
                        proc.terminate()
                sys.exit(0)
            
            signal.signal(signal.SIGINT, signal_handler)
            
            # 모든 프로세스가 종료될 때까지 대기
            for name, proc in processes:
                proc.wait()
                
        except KeyboardInterrupt:
            print("\n🛑 서비스 중지 중...")
            for name, proc in processes:
                if proc.poll() is None:
                    print(f"Stopping {name}...")
                    proc.terminate()
    
    else:
        print(f"Starting {service_type} service...")
        if service_type == "integration-mcp":
            run_command("python energy_mcp_integration.py")
        elif service_type == "unified-api":
            run_command("python unified_api.py")
        elif service_type == "dashboard":
            run_command("python energy_dashboard.py")
        else:
            print(f"Unknown service: {service_type}")
            return False
    
    return True

def test_integration():
    """통합 시스템 테스트"""
    print("🧪 통합 시스템 테스트 시작...")
    
    import requests
    import json
    
    # 테스트할 API 엔드포인트들
    test_endpoints = [
        {
            "name": "Health Check",
            "url": "http://localhost:5003/api/v1/health",
            "method": "GET"
        },
        {
            "name": "Sample Data Generation",
            "url": "http://localhost:5003/api/v1/energy/sample-data",
            "method": "POST",
            "data": {"n_samples": 100, "include_weather": True}
        },
        {
            "name": "Energy Forecast",
            "url": "http://localhost:5003/api/v1/energy/forecast",
            "method": "POST",
            "data": {"use_sample_data": True, "model_type": "ensemble"}
        },
        {
            "name": "Anomaly Detection",
            "url": "http://localhost:5003/api/v1/energy/anomaly",
            "method": "POST",
            "data": {"use_sample_data": True, "detection_methods": ["prophet"]}
        },
        {
            "name": "Available Models",
            "url": "http://localhost:5003/api/v1/energy/models",
            "method": "GET"
        }
    ]
    
    results = []
    
    for endpoint in test_endpoints:
        try:
            print(f"Testing {endpoint['name']}...")
            
            if endpoint['method'] == 'GET':
                response = requests.get(endpoint['url'], timeout=10)
            else:
                response = requests.post(
                    endpoint['url'], 
                    json=endpoint.get('data', {}), 
                    timeout=10
                )
            
            if response.status_code == 200:
                result = response.json()
                print(f"  ✅ {endpoint['name']}: SUCCESS")
                results.append({
                    "endpoint": endpoint['name'],
                    "status": "success",
                    "response_time": response.elapsed.total_seconds()
                })
            else:
                print(f"  ❌ {endpoint['name']}: FAILED (Status: {response.status_code})")
                results.append({
                    "endpoint": endpoint['name'],
                    "status": "failed",
                    "status_code": response.status_code
                })
                
        except Exception as e:
            print(f"  ❌ {endpoint['name']}: ERROR - {str(e)}")
            results.append({
                "endpoint": endpoint['name'],
                "status": "error",
                "error": str(e)
            })
    
    # 테스트 결과 요약
    print("\n📊 테스트 결과 요약:")
    print("=" * 30)
    
    successful = len([r for r in results if r['status'] == 'success'])
    total = len(results)
    
    for result in results:
        status_icon = "✅" if result['status'] == 'success' else "❌"
        print(f"{status_icon} {result['endpoint']}: {result['status'].upper()}")
        if 'response_time' in result:
            print(f"   응답 시간: {result['response_time']:.2f}초")
    
    print(f"\n총 {total}개 테스트 중 {successful}개 성공 ({successful/total*100:.1f}%)")
    
    if successful == total:
        print("🎉 모든 테스트가 성공했습니다!")
        return True
    else:
        print("⚠️ 일부 테스트가 실패했습니다.")
        return False

def main():
    parser = argparse.ArgumentParser(description="통합 에너지 분석 시스템")
    parser.add_argument("command", choices=["start", "test", "stop"],
                       help="실행할 명령어")
    parser.add_argument("--service", choices=["all", "integration", "integration-mcp", "unified-api", "dashboard"],
                       default="all", help="시작할 서비스")
    
    args = parser.parse_args()
    
    if args.command == "start":
        success = start_integrated_system(args.service)
        sys.exit(0 if success else 1)
    
    elif args.command == "test":
        success = test_integration()
        sys.exit(0 if success else 1)
    
    elif args.command == "stop":
        print("🛑 서비스 중지...")
        # 프로세스 종료 로직 (실제로는 각 서비스의 PID를 추적해야 함)
        print("서비스를 수동으로 중지해주세요 (Ctrl+C)")
    
    else:
        print("Unknown command")

if __name__ == "__main__":
    main()


