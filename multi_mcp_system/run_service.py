#!/usr/bin/env python3
"""
Multi-MCP Time Series Analysis System 서비스 실행 스크립트
"""

import argparse
import subprocess
import sys
import os
import time
import signal
from pathlib import Path

def run_command(command, background=False):
    """명령어 실행"""
    if background:
        return subprocess.Popen(command, shell=True)
    else:
        return subprocess.run(command, shell=True)

def start_services(service_type="all"):
    """서비스 시작"""
    print("🌟 Multi-MCP Time Series Analysis System")
    print("=" * 50)
    
    if service_type == "all":
        print("🚀 Starting all services...")
        
        # Docker Compose로 모든 서비스 시작
        result = run_command("docker-compose up -d")
        if result.returncode == 0:
            print("✅ All services started successfully!")
            print("\n📊 Service URLs:")
            print("  Web Dashboard: http://localhost:5000")
            print("  REST API: http://localhost:5001")
            print("  Forecasting MCP: http://localhost:8001")
            print("  Anomaly MCP: http://localhost:8002")
            print("  Coordinator MCP: http://localhost:8003")
            print("  Prometheus: http://localhost:9090")
            print("  Grafana: http://localhost:3000 (admin/admin)")
            print("\n📝 To view logs: docker-compose logs -f")
            print("🛑 To stop: docker-compose down")
        else:
            print("❌ Failed to start services")
            return False
    
    elif service_type == "local":
        print("🏠 Starting services locally...")
        
        # 로컬에서 서비스들 시작
        processes = []
        
        try:
            # Forecasting MCP Server
            print("Starting Forecasting MCP Server...")
            proc1 = run_command("python forecasting_mcp_server.py", background=True)
            processes.append(proc1)
            time.sleep(2)
            
            # Anomaly Detection MCP Server
            print("Starting Anomaly Detection MCP Server...")
            proc2 = run_command("python anomaly_mcp_server.py", background=True)
            processes.append(proc2)
            time.sleep(2)
            
            # Coordinator MCP Server
            print("Starting Coordinator MCP Server...")
            proc3 = run_command("python coordinator_mcp_server.py", background=True)
            processes.append(proc3)
            time.sleep(2)
            
            # Web Dashboard
            print("Starting Web Dashboard...")
            proc4 = run_command("python web_service/app.py", background=True)
            processes.append(proc4)
            time.sleep(2)
            
            # REST API
            print("Starting REST API...")
            proc5 = run_command("python web_service/api/rest_api.py", background=True)
            processes.append(proc5)
            
            print("\n✅ All services started locally!")
            print("\n📊 Service URLs:")
            print("  Web Dashboard: http://localhost:5000")
            print("  REST API: http://localhost:5001")
            print("  Forecasting MCP: http://localhost:8001")
            print("  Anomaly MCP: http://localhost:8002")
            print("  Coordinator MCP: http://localhost:8003")
            print("\nPress Ctrl+C to stop all services")
            
            # 신호 처리
            def signal_handler(sig, frame):
                print("\n🛑 Stopping all services...")
                for proc in processes:
                    if proc.poll() is None:
                        proc.terminate()
                sys.exit(0)
            
            signal.signal(signal.SIGINT, signal_handler)
            
            # 모든 프로세스가 종료될 때까지 대기
            for proc in processes:
                proc.wait()
                
        except KeyboardInterrupt:
            print("\n🛑 Stopping all services...")
            for proc in processes:
                if proc.poll() is None:
                    proc.terminate()
    
    else:
        print(f"Starting {service_type} service...")
        if service_type == "web":
            run_command("python web_service/app.py")
        elif service_type == "api":
            run_command("python web_service/api/rest_api.py")
        elif service_type == "forecasting":
            run_command("python forecasting_mcp_server.py")
        elif service_type == "anomaly":
            run_command("python anomaly_mcp_server.py")
        elif service_type == "coordinator":
            run_command("python coordinator_mcp_server.py")
        else:
            print(f"Unknown service: {service_type}")
            return False
    
    return True

def stop_services():
    """서비스 중지"""
    print("🛑 Stopping all services...")
    result = run_command("docker-compose down")
    if result.returncode == 0:
        print("✅ All services stopped successfully!")
    else:
        print("❌ Failed to stop services")

def show_status():
    """서비스 상태 확인"""
    print("📊 Service Status:")
    result = run_command("docker-compose ps")
    return result.returncode == 0

def show_logs(service=None):
    """로그 확인"""
    if service:
        run_command(f"docker-compose logs -f {service}")
    else:
        run_command("docker-compose logs -f")

def main():
    parser = argparse.ArgumentParser(description="Multi-MCP Time Series Analysis System")
    parser.add_argument("command", choices=["start", "stop", "status", "logs", "restart"],
                       help="Command to execute")
    parser.add_argument("--service", choices=["all", "local", "web", "api", "forecasting", "anomaly", "coordinator"],
                       default="all", help="Service to start")
    parser.add_argument("--logs-service", help="Specific service to show logs for")
    
    args = parser.parse_args()
    
    if args.command == "start":
        success = start_services(args.service)
        sys.exit(0 if success else 1)
    
    elif args.command == "stop":
        stop_services()
    
    elif args.command == "status":
        show_status()
    
    elif args.command == "logs":
        show_logs(args.logs_service)
    
    elif args.command == "restart":
        stop_services()
        time.sleep(2)
        start_services(args.service)

if __name__ == "__main__":
    main()


