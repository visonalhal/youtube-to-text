"""
OpenAI API适配器
"""

import requests
from typing import Dict, Any, Optional
from loguru import logger


class OpenAIAdapter:
    """OpenAI API适配器"""
    
    def __init__(self, api_key: str, base_url: str = "https://api.openai.com/v1"):
        """
        初始化OpenAI适配器
        
        Args:
            api_key: API密钥
            base_url: API基础URL
        """
        self.api_key = api_key
        self.base_url = base_url
        self.headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }
    
    def optimize_text(self, text: str, prompt: str, **kwargs) -> Optional[str]:
        """
        使用OpenAI优化文本
        
        Args:
            text: 原始文本
            prompt: 优化提示词
            **kwargs: 其他参数
            
        Returns:
            优化后的文本
        """
        try:
            data = {
                'model': kwargs.get('model', 'gpt-3.5-turbo'),
                'messages': [
                    {
                        'role': 'user',
                        'content': prompt.format(text=text)
                    }
                ],
                'max_tokens': kwargs.get('max_tokens', 4000),
                'temperature': kwargs.get('temperature', 0.7),
                'stream': False
            }
            
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=self.headers,
                json=data,
                timeout=kwargs.get('timeout', 60)
            )
            
            if response.status_code == 200:
                result = response.json()
                return result['choices'][0]['message']['content']
            else:
                logger.error(f"OpenAI API调用失败: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"OpenAI API调用异常: {str(e)}")
            return None
    
    def get_models(self) -> list:
        """获取可用模型列表"""
        try:
            response = requests.get(
                f"{self.base_url}/models",
                headers=self.headers,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                return [model['id'] for model in result.get('data', [])]
            else:
                logger.error(f"获取模型列表失败: {response.status_code}")
                return []
                
        except Exception as e:
            logger.error(f"获取模型列表异常: {str(e)}")
            return []