# -*- coding: utf-8 -*-
"""
다국어 번역 시스템
지원 언어: 한국어(ko), 영어(en), 중국어(zh)
"""

TRANSLATIONS = {
    "ko": {
        # 네비게이션
        "nav_home": "대시보드",
        "nav_health": "Health",
        "nav_ml_ai": "ML/AI Engine",
        "nav_demand": "Demand",
        "nav_supply": "Supply",
        "nav_control": "Control",
        "nav_api_docs": "API Docs",
        
        # 메인 대시보드
        "dashboard_title": "Energy Management System",
        "dashboard_subtitle": "통합 에너지 분석 및 관리 플랫폼",
        "card_health": "System Health",
        "card_health_desc": "실시간 시스템 상태 모니터링",
        "card_ml_ai": "ML/AI Engine",
        "card_ml_ai_desc": "ML/AI 모델 관리 및 테스트",
        "card_demand": "Energy Demand Monitoring",
        "card_demand_desc": "에너지 수요 분석 및 품질 관리",
        "card_supply": "Energy Supply Monitoring",
        "card_supply_desc": "에너지 공급 모니터링 및 관리",
        "card_control": "Demand Control",
        "card_control_desc": "수요 제어 및 시스템 관리",
        "card_api": "API Documentation",
        "card_api_desc": "API 문서 및 개발자 가이드",
        
        # Demand Control 페이지
        "demand_control_title": "Demand Control",
        "smart_ess_title": "Smart ESS (Energy Storage System)",
        "smart_ess_capacity": "Battery Capacity",
        "smart_ess_power": "Current Power",
        "smart_ess_efficiency": "System Efficiency",
        "smart_ess_status": "System Status",
        "supply_monitoring": "Supply-side Monitoring",
        "solar_generation": "Solar Generation",
        "wind_energy": "Wind Energy",
        "fuel_cells": "Fuel Cells",
        "environmental_sensors": "Environmental Sensors",
        "temperature": "Temperature",
        "humidity": "Humidity",
        "pressure": "Pressure",
        "illumination": "Illumination",
        "occupancy": "Occupancy",
        "controllable_units": "Controllable Units - Small Business Schools",
        "controllable": "Controllable",
        "selectable_control": "Selectable Control",
        "not_controllable": "Not Controllable",
        "light": "Light",
        "fan": "Fan",
        "copy_machine": "Copy Machine",
        "microwave": "Microwave",
        "tv": "TV",
        "manual_only": "Manual Only",
        "service_orchestration": "Service Orchestration Layer Platform",
        "local_aggregators": "Local Aggregators",
        "central_aggregator": "Central Aggregator",
        "applications": "Applications",
        "school_aggregator": "School Aggregator",
        "system_operator": "System Operator",
        "demand_forecasting": "Demand Forecasting",
        "dynamic_ess": "Dynamic ESS",
        "user_interface": "User Interface",
        "mcp_price_service": "MCP Aggregation Price Service",
        "current_price": "Current Price/kWh",
        "peak_price": "Peak Price/kWh",
        "off_peak_price": "Off-Peak Price/kWh",
        "active_bids": "Active Bids",
        "market_functions": "Market Functions",
        "bids_offers": "Bids/Offers Collection",
        "price_calculation": "Price Calculation",
        "market_settlement": "Market Settlement",
        "output_stations": "Output Stations - Demand Device Control",
        "controlled_devices": "Controlled Devices",
        "energy_saved": "Energy Saved",
        "response_time": "Response Time",
        "system_uptime": "System Uptime",
        "control_actions": "Control Actions",
        "temperature_control": "Temperature Control",
        "lighting_control": "Lighting Control",
        "ventilation_control": "Ventilation Control",
        "ess_management": "ESS Management",
        "optimized": "Optimized",
        "adjusting": "Adjusting",
        "active": "Active",
        "online": "Online",
        "standby": "Standby",
        
        # 공통
        "people": "people",
        "hours": "hours",
        "loading": "Loading...",
        "error": "Error",
        "success": "Success",
        "warning": "Warning",
        "info": "Info"
    },
    
    "en": {
        # Navigation
        "nav_home": "Dashboard",
        "nav_health": "Health",
        "nav_ml_ai": "ML/AI Engine",
        "nav_demand": "Demand",
        "nav_supply": "Supply",
        "nav_control": "Control",
        "nav_api_docs": "API Docs",
        
        # Main Dashboard
        "dashboard_title": "Energy Management System",
        "dashboard_subtitle": "Integrated Energy Analysis and Management Platform",
        "card_health": "System Health",
        "card_health_desc": "Real-time system status monitoring",
        "card_ml_ai": "ML/AI Engine",
        "card_ml_ai_desc": "ML/AI model management and testing",
        "card_demand": "Energy Demand Monitoring",
        "card_demand_desc": "Energy demand analysis and quality management",
        "card_supply": "Energy Supply Monitoring",
        "card_supply_desc": "Energy supply monitoring and management",
        "card_control": "Demand Control",
        "card_control_desc": "Demand control and system management",
        "card_api": "API Documentation",
        "card_api_desc": "API documentation and developer guide",
        
        # Demand Control Page
        "demand_control_title": "Demand Control",
        "smart_ess_title": "Smart ESS (Energy Storage System)",
        "smart_ess_capacity": "Battery Capacity",
        "smart_ess_power": "Current Power",
        "smart_ess_efficiency": "System Efficiency",
        "smart_ess_status": "System Status",
        "supply_monitoring": "Supply-side Monitoring",
        "solar_generation": "Solar Generation",
        "wind_energy": "Wind Energy",
        "fuel_cells": "Fuel Cells",
        "environmental_sensors": "Environmental Sensors",
        "temperature": "Temperature",
        "humidity": "Humidity",
        "pressure": "Pressure",
        "illumination": "Illumination",
        "occupancy": "Occupancy",
        "controllable_units": "Controllable Units - Small Business Schools",
        "controllable": "Controllable",
        "selectable_control": "Selectable Control",
        "not_controllable": "Not Controllable",
        "light": "Light",
        "fan": "Fan",
        "copy_machine": "Copy Machine",
        "microwave": "Microwave",
        "tv": "TV",
        "manual_only": "Manual Only",
        "service_orchestration": "Service Orchestration Layer Platform",
        "local_aggregators": "Local Aggregators",
        "central_aggregator": "Central Aggregator",
        "applications": "Applications",
        "school_aggregator": "School Aggregator",
        "system_operator": "System Operator",
        "demand_forecasting": "Demand Forecasting",
        "dynamic_ess": "Dynamic ESS",
        "user_interface": "User Interface",
        "mcp_price_service": "MCP Aggregation Price Service",
        "current_price": "Current Price/kWh",
        "peak_price": "Peak Price/kWh",
        "off_peak_price": "Off-Peak Price/kWh",
        "active_bids": "Active Bids",
        "market_functions": "Market Functions",
        "bids_offers": "Bids/Offers Collection",
        "price_calculation": "Price Calculation",
        "market_settlement": "Market Settlement",
        "output_stations": "Output Stations - Demand Device Control",
        "controlled_devices": "Controlled Devices",
        "energy_saved": "Energy Saved",
        "response_time": "Response Time",
        "system_uptime": "System Uptime",
        "control_actions": "Control Actions",
        "temperature_control": "Temperature Control",
        "lighting_control": "Lighting Control",
        "ventilation_control": "Ventilation Control",
        "ess_management": "ESS Management",
        "optimized": "Optimized",
        "adjusting": "Adjusting",
        "active": "Active",
        "online": "Online",
        "standby": "Standby",
        
        # Common
        "people": "people",
        "hours": "hours",
        "loading": "Loading...",
        "error": "Error",
        "success": "Success",
        "warning": "Warning",
        "info": "Info"
    },
    
    "zh": {
        # 导航
        "nav_home": "仪表板",
        "nav_health": "健康",
        "nav_ml_ai": "ML/AI引擎",
        "nav_demand": "需求",
        "nav_supply": "供应",
        "nav_control": "控制",
        "nav_api_docs": "API文档",
        
        # 主仪表板
        "dashboard_title": "能源管理系统",
        "dashboard_subtitle": "集成能源分析和管理平台",
        "card_health": "系统健康",
        "card_health_desc": "实时系统状态监控",
        "card_ml_ai": "ML/AI引擎",
        "card_ml_ai_desc": "ML/AI模型管理和测试",
        "card_demand": "能源需求监控",
        "card_demand_desc": "能源需求分析和质量管理",
        "card_supply": "能源供应监控",
        "card_supply_desc": "能源供应监控和管理",
        "card_control": "需求控制",
        "card_control_desc": "需求控制和系统管理",
        "card_api": "API文档",
        "card_api_desc": "API文档和开发者指南",
        
        # 需求控制页面
        "demand_control_title": "需求控制",
        "smart_ess_title": "智能ESS（储能系统）",
        "smart_ess_capacity": "电池容量",
        "smart_ess_power": "当前功率",
        "smart_ess_efficiency": "系统效率",
        "smart_ess_status": "系统状态",
        "supply_monitoring": "供应侧监控",
        "solar_generation": "太阳能发电",
        "wind_energy": "风能",
        "fuel_cells": "燃料电池",
        "environmental_sensors": "环境传感器",
        "temperature": "温度",
        "humidity": "湿度",
        "pressure": "压力",
        "illumination": "照度",
        "occupancy": "占用率",
        "controllable_units": "可控设备 - 小型企业学校",
        "controllable": "可控",
        "selectable_control": "可选控制",
        "not_controllable": "不可控",
        "light": "照明",
        "fan": "风扇",
        "copy_machine": "复印机",
        "microwave": "微波炉",
        "tv": "电视",
        "manual_only": "仅手动",
        "service_orchestration": "服务编排层平台",
        "local_aggregators": "本地聚合器",
        "central_aggregator": "中央聚合器",
        "applications": "应用程序",
        "school_aggregator": "学校聚合器",
        "system_operator": "系统运营商",
        "demand_forecasting": "需求预测",
        "dynamic_ess": "动态ESS",
        "user_interface": "用户界面",
        "mcp_price_service": "MCP聚合价格服务",
        "current_price": "当前价格/kWh",
        "peak_price": "峰值价格/kWh",
        "off_peak_price": "非峰值价格/kWh",
        "active_bids": "活跃投标",
        "market_functions": "市场功能",
        "bids_offers": "投标/报价收集",
        "price_calculation": "价格计算",
        "market_settlement": "市场结算",
        "output_stations": "输出站 - 需求设备控制",
        "controlled_devices": "受控设备",
        "energy_saved": "节能",
        "response_time": "响应时间",
        "system_uptime": "系统运行时间",
        "control_actions": "控制动作",
        "temperature_control": "温度控制",
        "lighting_control": "照明控制",
        "ventilation_control": "通风控制",
        "ess_management": "ESS管理",
        "optimized": "已优化",
        "adjusting": "调整中",
        "active": "活跃",
        "online": "在线",
        "standby": "待机",
        
        # 通用
        "people": "人",
        "hours": "小时",
        "loading": "加载中...",
        "error": "错误",
        "success": "成功",
        "warning": "警告",
        "info": "信息"
    }
}

def get_translation(key: str, language: str = "ko") -> str:
    """
    번역 키에 해당하는 텍스트를 반환
    
    Args:
        key: 번역 키
        language: 언어 코드 (ko, en, zh)
    
    Returns:
        번역된 텍스트
    """
    if language not in TRANSLATIONS:
        language = "ko"  # 기본값은 한국어
    
    return TRANSLATIONS[language].get(key, key)

def get_available_languages():
    """사용 가능한 언어 목록 반환"""
    return list(TRANSLATIONS.keys())

def get_language_name(lang_code: str) -> str:
    """언어 코드에 해당하는 언어명 반환"""
    language_names = {
        "ko": "한국어",
        "en": "English", 
        "zh": "中文"
    }
    return language_names.get(lang_code, lang_code)

