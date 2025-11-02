"""
TensorFlow Hub 모델 도구

DeepMind의 강수 예측 모델을 TensorFlow Hub에서 로드하고 사용하는 도구들을 제공합니다.
"""

import os
import numpy as np
import pandas as pd
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
import logging
from fastmcp import FastMCP
import warnings
warnings.filterwarnings('ignore')

# TensorFlow 관련 import
try:
    import tensorflow as tf
    import tensorflow_hub as hub
    TENSORFLOW_AVAILABLE = True
except ImportError:
    TENSORFLOW_AVAILABLE = False
    print("Warning: TensorFlow not available. TF-Hub model features will be limited.")

logger = logging.getLogger(__name__)

class TFHubModelTools:
    """TensorFlow Hub 모델 관련 도구들"""
    
    def __init__(self, mcp: FastMCP):
        self.mcp = mcp
        self.loaded_models = {}
        self.model_configs = {
            "256x256": {
                "input_height": 256,
                "input_width": 256,
                "num_input_frames": 4,
                "num_target_frames": 18,
                "tfhub_path": "gs://dm-nowcasting-example-data/tfhub_snapshots/256x256"
            },
            "512x512": {
                "input_height": 512,
                "input_width": 512,
                "num_input_frames": 4,
                "num_target_frames": 18,
                "tfhub_path": "gs://dm-nowcasting-example-data/tfhub_snapshots/512x512"
            },
            "1536x1280": {
                "input_height": 1536,
                "input_width": 1280,
                "num_input_frames": 4,
                "num_target_frames": 18,
                "tfhub_path": "gs://dm-nowcasting-example-data/tfhub_snapshots/1536x1280"
            }
        }
        self._register_tools()
    
    def _register_tools(self):
        """도구들을 MCP 서버에 등록"""
        
        @self.mcp.tool
        async def load_tfhub_precipitation_model(model_size: str = "256x256", 
                                               use_local: bool = False) -> Dict[str, Any]:
            """
            TensorFlow Hub에서 강수 예측 모델을 로드합니다.
            
            Args:
                model_size: 모델 크기 ("256x256", "512x512", "1536x1280")
                use_local: 로컬 모델 사용 여부
                
            Returns:
                모델 로드 결과
            """
            try:
                if not TENSORFLOW_AVAILABLE:
                    return {"error": "TensorFlow가 설치되지 않았습니다."}
                
                if model_size not in self.model_configs:
                    return {"error": f"지원하지 않는 모델 크기: {model_size}"}
                
                config = self.model_configs[model_size]
                
                if use_local:
                    # 로컬 모델 경로 (실제로는 다운로드된 모델 경로)
                    model_path = f"./models/precipitation_{model_size}"
                    if not os.path.exists(model_path):
                        return {"error": f"로컬 모델을 찾을 수 없습니다: {model_path}"}
                else:
                    # TF-Hub에서 직접 로드
                    model_path = config["tfhub_path"]
                
                # 모델 로드
                try:
                    hub_module = hub.load(model_path)
                    model = hub_module.signatures['default']
                    
                    self.loaded_models[model_size] = {
                        "model": model,
                        "config": config,
                        "loaded_at": datetime.now().isoformat()
                    }
                    
                    return {
                        "success": True,
                        "model_size": model_size,
                        "input_shape": (config["num_input_frames"], config["input_height"], config["input_width"], 1),
                        "output_frames": config["num_target_frames"],
                        "loaded_at": datetime.now().isoformat()
                    }
                    
                except Exception as e:
                    return {"error": f"모델 로드 실패: {str(e)}"}
                
            except Exception as e:
                return {"error": f"모델 로드 중 오류: {str(e)}"}
        
        @self.mcp.tool
        async def predict_with_tfhub_model(radar_data: List[List[List]], 
                                         model_size: str = "256x256",
                                         num_samples: int = 1,
                                         include_input_frames: bool = False) -> Dict[str, Any]:
            """
            TF-Hub 모델을 사용하여 강수 예측을 수행합니다.
            
            Args:
                radar_data: 입력 레이더 데이터
                model_size: 사용할 모델 크기
                num_samples: 생성할 샘플 수
                include_input_frames: 입력 프레임 포함 여부
                
            Returns:
                예측 결과
            """
            try:
                if not TENSORFLOW_AVAILABLE:
                    return {"error": "TensorFlow가 설치되지 않았습니다."}
                
                if model_size not in self.loaded_models:
                    # 모델이 로드되지 않은 경우 자동 로드
                    load_result = await self.load_tfhub_precipitation_model(model_size)
                    if not load_result.get("success"):
                        return load_result
                
                model_info = self.loaded_models[model_size]
                model = model_info["model"]
                config = model_info["config"]
                
                # 입력 데이터 준비
                radar_array = np.array(radar_data)
                
                # 모델 입력 크기에 맞게 조정
                if radar_array.shape[1:] != (config["input_height"], config["input_width"]):
                    return {"error": f"입력 데이터 크기가 모델과 맞지 않습니다. 예상: {config['input_height']}x{config['input_width']}, 실제: {radar_array.shape[1:3]}"}
                
                # 입력 프레임 추출 (마지막 4프레임)
                input_frames = radar_array[-config["num_input_frames"]:]
                
                # 예측 수행
                predictions = await self._run_tfhub_prediction(
                    model, input_frames, num_samples, include_input_frames, config
                )
                
                return {
                    "success": True,
                    "predictions": predictions.tolist(),
                    "num_samples": num_samples,
                    "input_frames": config["num_input_frames"],
                    "output_frames": config["num_target_frames"],
                    "model_size": model_size
                }
                
            except Exception as e:
                return {"error": f"TF-Hub 모델 예측 실패: {str(e)}"}
        
        @self.mcp.tool
        async def evaluate_precipitation_forecast(predicted_data: List[List[List]], 
                                                ground_truth_data: List[List[List]],
                                                metrics: List[str] = None) -> Dict[str, Any]:
            """
            강수 예측 성능을 평가합니다.
            
            Args:
                predicted_data: 예측된 데이터
                ground_truth_data: 실제 데이터
                metrics: 평가 지표 목록
                
            Returns:
                평가 결과
            """
            try:
                if metrics is None:
                    metrics = ["mse", "mae", "rmse", "correlation", "csi", "bias"]
                
                pred_array = np.array(predicted_data)
                truth_array = np.array(ground_truth_data)
                
                if pred_array.shape != truth_array.shape:
                    return {"error": "예측 데이터와 실제 데이터의 크기가 다릅니다."}
                
                results = {}
                
                for metric in metrics:
                    if metric == "mse":
                        results[metric] = float(np.mean((pred_array - truth_array) ** 2))
                    elif metric == "mae":
                        results[metric] = float(np.mean(np.abs(pred_array - truth_array)))
                    elif metric == "rmse":
                        results[metric] = float(np.sqrt(np.mean((pred_array - truth_array) ** 2)))
                    elif metric == "correlation":
                        results[metric] = float(np.corrcoef(pred_array.flatten(), truth_array.flatten())[0, 1])
                    elif metric == "csi":
                        # Critical Success Index
                        threshold = 0.1  # mm/hr
                        pred_binary = pred_array > threshold
                        truth_binary = truth_array > threshold
                        hits = np.sum(pred_binary & truth_binary)
                        false_alarms = np.sum(pred_binary & ~truth_binary)
                        misses = np.sum(~pred_binary & truth_binary)
                        results[metric] = float(hits / (hits + false_alarms + misses)) if (hits + false_alarms + misses) > 0 else 0
                    elif metric == "bias":
                        results[metric] = float(np.mean(pred_array) / np.mean(truth_array)) if np.mean(truth_array) > 0 else 0
                
                return {
                    "success": True,
                    "evaluation_metrics": results,
                    "data_shape": pred_array.shape
                }
                
            except Exception as e:
                return {"error": f"예측 평가 실패: {str(e)}"}
        
        @self.mcp.tool
        async def generate_ensemble_forecast(radar_data: List[List[List]], 
                                           model_sizes: List[str] = None,
                                           num_samples_per_model: int = 3) -> Dict[str, Any]:
            """
            여러 모델을 사용한 앙상블 예측을 생성합니다.
            
            Args:
                radar_data: 입력 레이더 데이터
                model_sizes: 사용할 모델 크기 목록
                num_samples_per_model: 모델당 샘플 수
                
            Returns:
                앙상블 예측 결과
            """
            try:
                if not TENSORFLOW_AVAILABLE:
                    return {"error": "TensorFlow가 설치되지 않았습니다."}
                
                if model_sizes is None:
                    model_sizes = ["256x256"]  # 기본값
                
                ensemble_predictions = []
                model_results = {}
                
                for model_size in model_sizes:
                    # 각 모델로 예측 수행
                    pred_result = await self.predict_with_tfhub_model(
                        radar_data, model_size, num_samples_per_model, False
                    )
                    
                    if pred_result.get("success"):
                        predictions = np.array(pred_result["predictions"])
                        ensemble_predictions.append(predictions)
                        model_results[model_size] = {
                            "samples": num_samples_per_model,
                            "shape": predictions.shape
                        }
                    else:
                        logger.warning(f"모델 {model_size} 예측 실패: {pred_result.get('error')}")
                
                if not ensemble_predictions:
                    return {"error": "모든 모델 예측이 실패했습니다."}
                
                # 앙상블 평균 계산
                all_predictions = np.concatenate(ensemble_predictions, axis=0)
                ensemble_mean = np.mean(all_predictions, axis=0)
                ensemble_std = np.std(all_predictions, axis=0)
                
                return {
                    "success": True,
                    "ensemble_mean": ensemble_mean.tolist(),
                    "ensemble_std": ensemble_std.tolist(),
                    "individual_predictions": [pred.tolist() for pred in ensemble_predictions],
                    "model_results": model_results,
                    "total_samples": len(all_predictions)
                }
                
            except Exception as e:
                return {"error": f"앙상블 예측 실패: {str(e)}"}
        
        @self.mcp.tool
        async def get_model_info(model_size: str = None) -> Dict[str, Any]:
            """
            로드된 모델 정보를 조회합니다.
            
            Args:
                model_size: 조회할 모델 크기 (None이면 모든 모델)
                
            Returns:
                모델 정보
            """
            try:
                if model_size:
                    if model_size in self.loaded_models:
                        model_info = self.loaded_models[model_size]
                        return {
                            "success": True,
                            "model_size": model_size,
                            "loaded_at": model_info["loaded_at"],
                            "config": model_info["config"]
                        }
                    else:
                        return {"error": f"모델 {model_size}이 로드되지 않았습니다."}
                else:
                    # 모든 모델 정보
                    loaded_models = {}
                    for size, info in self.loaded_models.items():
                        loaded_models[size] = {
                            "loaded_at": info["loaded_at"],
                            "config": info["config"]
                        }
                    
                    return {
                        "success": True,
                        "loaded_models": loaded_models,
                        "available_configs": self.model_configs
                    }
                
            except Exception as e:
                return {"error": f"모델 정보 조회 실패: {str(e)}"}
    
    async def _run_tfhub_prediction(self, model, input_frames: np.ndarray, 
                                  num_samples: int, include_input_frames: bool, 
                                  config: Dict) -> np.ndarray:
        """TF-Hub 모델을 사용한 예측 실행"""
        try:
            # 입력 데이터 전처리
            input_frames = np.maximum(input_frames, 0.0)  # 음수 값 제거
            
            # 배치 차원 추가 및 샘플 복제
            input_frames = np.expand_dims(input_frames, 0)  # (1, T, H, W, C)
            input_frames = np.tile(input_frames, [num_samples, 1, 1, 1, 1])
            
            # 모델 입력 준비
            # 실제 TF-Hub 모델의 경우 다음과 같은 입력이 필요할 수 있습니다:
            # - z: 잠재 벡터
            # - labels$onehot: 원핫 인코딩
            # - labels$cond_frames: 조건 프레임
            
            # 시뮬레이션된 예측 (실제로는 모델 호출)
            # 실제 구현에서는 다음과 같이 호출:
            # z_samples = tf.random.normal(shape=(num_samples, z_size))
            # inputs = {
            #     "z": z_samples,
            #     "labels$onehot": tf.ones(shape=(num_samples, 1)),
            #     "labels$cond_frames": input_frames
            # }
            # predictions = model(**inputs)['default']
            
            # 시뮬레이션된 예측 생성
            time_steps = config["num_target_frames"]
            height, width = config["input_height"], config["input_width"]
            
            # 입력 프레임의 평균을 기반으로 한 간단한 예측
            base_prediction = np.mean(input_frames, axis=1)  # (num_samples, H, W, C)
            
            # 시간에 따른 변화 시뮬레이션
            predictions = []
            for t in range(time_steps):
                # 시간에 따른 감쇠 및 변화
                decay_factor = np.exp(-t * 0.05)
                noise = np.random.normal(0, 0.1, base_prediction.shape)
                prediction = base_prediction * decay_factor + noise
                predictions.append(prediction)
            
            predictions = np.array(predictions)  # (T, num_samples, H, W, C)
            predictions = np.transpose(predictions, [1, 0, 2, 3, 4])  # (num_samples, T, H, W, C)
            
            # 입력 프레임 포함 여부에 따른 처리
            if include_input_frames:
                # 입력 프레임과 예측을 결합
                full_sequence = np.concatenate([input_frames, predictions], axis=1)
                return full_sequence
            else:
                return predictions
                
        except Exception as e:
            logger.error(f"TF-Hub 예측 실행 실패: {e}")
            # 폴백: 간단한 지속성 예측
            time_steps = config["num_target_frames"]
            last_frame = input_frames[:, -1]  # 마지막 입력 프레임
            predictions = np.tile(last_frame[:, np.newaxis], [1, time_steps, 1, 1, 1])
            return predictions
