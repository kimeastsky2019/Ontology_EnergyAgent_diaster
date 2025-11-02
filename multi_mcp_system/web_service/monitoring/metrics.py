"""
메트릭 수집 및 모니터링 시스템
"""

import time
import psutil
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from collections import defaultdict, deque
import json
import logging

logger = logging.getLogger(__name__)


@dataclass
class MetricPoint:
    """메트릭 데이터 포인트"""
    timestamp: datetime
    value: float
    labels: Dict[str, str] = None


class MetricsCollector:
    """메트릭 수집기"""
    
    def __init__(self, max_history: int = 1000):
        self.max_history = max_history
        self.metrics = defaultdict(lambda: deque(maxlen=max_history))
        self.lock = threading.Lock()
        self.start_time = datetime.now()
        
    def add_metric(self, name: str, value: float, labels: Dict[str, str] = None):
        """메트릭 추가"""
        with self.lock:
            metric_point = MetricPoint(
                timestamp=datetime.now(),
                value=value,
                labels=labels or {}
            )
            self.metrics[name].append(metric_point)
    
    def get_metric(self, name: str, duration: Optional[timedelta] = None) -> List[MetricPoint]:
        """메트릭 조회"""
        with self.lock:
            if name not in self.metrics:
                return []
            
            points = list(self.metrics[name])
            
            if duration:
                cutoff_time = datetime.now() - duration
                points = [p for p in points if p.timestamp >= cutoff_time]
            
            return points
    
    def get_metric_summary(self, name: str, duration: Optional[timedelta] = None) -> Dict[str, Any]:
        """메트릭 요약 통계"""
        points = self.get_metric(name, duration)
        
        if not points:
            return {
                "count": 0,
                "min": None,
                "max": None,
                "avg": None,
                "latest": None
            }
        
        values = [p.value for p in points]
        
        return {
            "count": len(values),
            "min": min(values),
            "max": max(values),
            "avg": sum(values) / len(values),
            "latest": values[-1] if values else None,
            "first_timestamp": points[0].timestamp.isoformat(),
            "last_timestamp": points[-1].timestamp.isoformat()
        }
    
    def get_all_metrics(self) -> Dict[str, List[MetricPoint]]:
        """모든 메트릭 조회"""
        with self.lock:
            return {name: list(points) for name, points in self.metrics.items()}


class SystemMetricsCollector:
    """시스템 메트릭 수집기"""
    
    def __init__(self, metrics_collector: MetricsCollector):
        self.metrics_collector = metrics_collector
        self.running = False
        self.thread = None
        
    def start(self, interval: int = 10):
        """메트릭 수집 시작"""
        if self.running:
            return
        
        self.running = True
        self.thread = threading.Thread(target=self._collect_loop, args=(interval,))
        self.thread.daemon = True
        self.thread.start()
        logger.info("System metrics collection started")
    
    def stop(self):
        """메트릭 수집 중지"""
        self.running = False
        if self.thread:
            self.thread.join()
        logger.info("System metrics collection stopped")
    
    def _collect_loop(self, interval: int):
        """메트릭 수집 루프"""
        while self.running:
            try:
                self._collect_system_metrics()
                time.sleep(interval)
            except Exception as e:
                logger.error(f"Error collecting system metrics: {e}")
                time.sleep(interval)
    
    def _collect_system_metrics(self):
        """시스템 메트릭 수집"""
        try:
            # CPU 사용률
            cpu_percent = psutil.cpu_percent(interval=1)
            self.metrics_collector.add_metric(
                "system_cpu_percent", 
                cpu_percent,
                {"type": "cpu"}
            )
            
            # 메모리 사용률
            memory = psutil.virtual_memory()
            self.metrics_collector.add_metric(
                "system_memory_percent",
                memory.percent,
                {"type": "memory"}
            )
            
            # 디스크 사용률
            disk = psutil.disk_usage('/')
            self.metrics_collector.add_metric(
                "system_disk_percent",
                (disk.used / disk.total) * 100,
                {"type": "disk"}
            )
            
            # 네트워크 I/O
            net_io = psutil.net_io_counters()
            self.metrics_collector.add_metric(
                "system_network_bytes_sent",
                net_io.bytes_sent,
                {"type": "network", "direction": "sent"}
            )
            self.metrics_collector.add_metric(
                "system_network_bytes_recv",
                net_io.bytes_recv,
                {"type": "network", "direction": "received"}
            )
            
            # 프로세스 수
            process_count = len(psutil.pids())
            self.metrics_collector.add_metric(
                "system_process_count",
                process_count,
                {"type": "process"}
            )
            
        except Exception as e:
            logger.error(f"Error collecting system metrics: {e}")


class ApplicationMetricsCollector:
    """애플리케이션 메트릭 수집기"""
    
    def __init__(self, metrics_collector: MetricsCollector):
        self.metrics_collector = metrics_collector
        self.request_count = 0
        self.error_count = 0
        self.response_times = deque(maxlen=1000)
        
    def record_request(self, endpoint: str, method: str, status_code: int, 
                      response_time: float):
        """요청 메트릭 기록"""
        self.request_count += 1
        
        # 응답 시간 기록
        self.response_times.append(response_time)
        
        # 요청 수 메트릭
        self.metrics_collector.add_metric(
            "app_requests_total",
            1,
            {
                "endpoint": endpoint,
                "method": method,
                "status_code": str(status_code)
            }
        )
        
        # 응답 시간 메트릭
        self.metrics_collector.add_metric(
            "app_response_time_seconds",
            response_time,
            {
                "endpoint": endpoint,
                "method": method
            }
        )
        
        # 에러 카운트
        if status_code >= 400:
            self.error_count += 1
            self.metrics_collector.add_metric(
                "app_errors_total",
                1,
                {
                    "endpoint": endpoint,
                    "method": method,
                    "status_code": str(status_code)
                }
            )
    
    def record_model_training(self, model_type: str, model_name: str, 
                            training_time: float, success: bool):
        """모델 훈련 메트릭 기록"""
        self.metrics_collector.add_metric(
            "model_training_duration_seconds",
            training_time,
            {
                "model_type": model_type,
                "model_name": model_name,
                "success": str(success)
            }
        )
        
        self.metrics_collector.add_metric(
            "model_training_total",
            1,
            {
                "model_type": model_type,
                "success": str(success)
            }
        )
    
    def record_prediction(self, model_type: str, model_name: str, 
                         prediction_time: float, success: bool):
        """예측 메트릭 기록"""
        self.metrics_collector.add_metric(
            "model_prediction_duration_seconds",
            prediction_time,
            {
                "model_type": model_type,
                "model_name": model_name,
                "success": str(success)
            }
        )
    
    def record_anomaly_detection(self, model_type: str, model_name: str,
                               detection_time: float, anomaly_count: int):
        """이상치 탐지 메트릭 기록"""
        self.metrics_collector.add_metric(
            "anomaly_detection_duration_seconds",
            detection_time,
            {
                "model_type": model_type,
                "model_name": model_name
            }
        )
        
        self.metrics_collector.add_metric(
            "anomaly_detection_count",
            anomaly_count,
            {
                "model_type": model_type,
                "model_name": model_name
            }
        )
    
    def get_application_stats(self) -> Dict[str, Any]:
        """애플리케이션 통계 조회"""
        avg_response_time = (
            sum(self.response_times) / len(self.response_times) 
            if self.response_times else 0
        )
        
        return {
            "total_requests": self.request_count,
            "total_errors": self.error_count,
            "error_rate": self.error_count / max(self.request_count, 1),
            "average_response_time": avg_response_time,
            "uptime_seconds": (datetime.now() - self.metrics_collector.start_time).total_seconds()
        }


class MetricsExporter:
    """메트릭 내보내기"""
    
    def __init__(self, metrics_collector: MetricsCollector):
        self.metrics_collector = metrics_collector
    
    def export_prometheus_format(self) -> str:
        """Prometheus 형식으로 메트릭 내보내기"""
        lines = []
        
        for metric_name, points in self.metrics_collector.get_all_metrics().items():
            if not points:
                continue
            
            # 메트릭 헤더
            lines.append(f"# HELP {metric_name} {metric_name}")
            lines.append(f"# TYPE {metric_name} gauge")
            
            # 메트릭 포인트들
            for point in points:
                labels_str = ""
                if point.labels:
                    label_pairs = [f'{k}="{v}"' for k, v in point.labels.items()]
                    labels_str = "{" + ",".join(label_pairs) + "}"
                
                timestamp_ms = int(point.timestamp.timestamp() * 1000)
                lines.append(f"{metric_name}{labels_str} {point.value} {timestamp_ms}")
        
        return "\n".join(lines)
    
    def export_json_format(self) -> Dict[str, Any]:
        """JSON 형식으로 메트릭 내보내기"""
        result = {
            "timestamp": datetime.now().isoformat(),
            "metrics": {}
        }
        
        for metric_name, points in self.metrics_collector.get_all_metrics().items():
            result["metrics"][metric_name] = [
                {
                    "timestamp": point.timestamp.isoformat(),
                    "value": point.value,
                    "labels": point.labels
                }
                for point in points
            ]
        
        return result


# 전역 메트릭 수집기 인스턴스
metrics_collector = MetricsCollector()
system_metrics = SystemMetricsCollector(metrics_collector)
app_metrics = ApplicationMetricsCollector(metrics_collector)
metrics_exporter = MetricsExporter(metrics_collector)


def start_monitoring():
    """모니터링 시작"""
    system_metrics.start(interval=10)
    logger.info("Monitoring started")


def stop_monitoring():
    """모니터링 중지"""
    system_metrics.stop()
    logger.info("Monitoring stopped")


def get_metrics_summary() -> Dict[str, Any]:
    """메트릭 요약 조회"""
    summary = {
        "system": {},
        "application": app_metrics.get_application_stats(),
        "timestamp": datetime.now().isoformat()
    }
    
    # 시스템 메트릭 요약
    system_metrics_list = [
        "system_cpu_percent",
        "system_memory_percent", 
        "system_disk_percent",
        "system_process_count"
    ]
    
    for metric in system_metrics_list:
        summary["system"][metric] = metrics_collector.get_metric_summary(
            metric, timedelta(minutes=5)
        )
    
    return summary


