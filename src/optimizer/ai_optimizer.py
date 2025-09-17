"""
AI文档优化器
使用AI模型对转录文本进行优化，提升可读性和结构
"""

import os
import json
import requests
from pathlib import Path
from typing import Dict, Any, Optional, List
from loguru import logger


class AIOptimizer:
    """AI文档优化器"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        初始化AI优化器
        
        Args:
            config: 配置字典，包含AI服务相关配置
        """
        self.config = config
        self.api_key = config.get('api_key')
        self.model = config.get('model', 'deepseek-chat')
        self.base_url = config.get('base_url', 'https://api.deepseek.com/v1')
        self.max_tokens = config.get('max_tokens', 4000)
        self.temperature = config.get('temperature', 0.7)
        
        # 优化提示词模板
        self.optimization_prompt = self._load_optimization_prompt()
        
    def _load_optimization_prompt(self) -> str:
        """加载优化提示词模板"""
        return """
请将以下转录文本优化为结构清晰、语言流畅的文档。

优化要求：
1. 修正错别字、语法错误和标点符号
2. 重新组织段落结构，添加合适的标题和子标题
3. 将口语化表达转换为书面语
4. 保持原文的核心观点和逻辑结构
5. 输出格式为Markdown，包含目录结构
6. 确保内容连贯性和可读性

原文内容：
{text}

请直接输出优化后的Markdown文档，不要包含其他说明文字。
"""
    
    def optimize_text(self, text: str, title: str = "优化文档") -> Dict[str, Any]:
        """
        优化文本内容
        
        Args:
            text: 原始转录文本
            title: 文档标题
            
        Returns:
            优化结果字典
        """
        try:
            logger.info(f"开始AI优化文档: {title}")
            
            # 预处理文本
            processed_text = self._preprocess_text(text)
            
            # 调用AI优化
            optimized_text = self._call_ai_optimization(processed_text)
            
            # 后处理优化结果
            final_text = self._postprocess_text(optimized_text, title)
            
            # 保存优化后的文档
            output_path = self._save_optimized_text(final_text, title)
            
            logger.success(f"AI优化完成: {output_path}")
            
            return {
                'title': title,
                'original_text': text,
                'optimized_text': final_text,
                'output_path': str(output_path),
                'optimization_stats': self._calculate_stats(text, final_text)
            }
            
        except Exception as e:
            logger.error(f"AI优化失败: {str(e)}")
            return None
    
    def _preprocess_text(self, text: str) -> str:
        """预处理文本"""
        # 清理多余的空白字符
        text = ' '.join(text.split())
        
        # 移除明显的转录错误标记
        text = text.replace('[音乐]', '').replace('[掌声]', '').replace('[笑声]', '')
        
        # 分段处理（按句号、问号、感叹号分段）
        import re
        sentences = re.split(r'[。！？]', text)
        paragraphs = []
        current_paragraph = ""
        
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue
                
            # 添加标点符号
            if sentence and not sentence.endswith(('。', '！', '？')):
                sentence += '。'
            
            current_paragraph += sentence
            
            # 按长度分段
            if len(current_paragraph) > 200:
                paragraphs.append(current_paragraph.strip())
                current_paragraph = ""
        
        if current_paragraph.strip():
            paragraphs.append(current_paragraph.strip())
        
        return '\n\n'.join(paragraphs)
    
    def _call_ai_optimization(self, text: str) -> str:
        """调用AI服务进行优化"""
        if not self.api_key:
            logger.warning("未配置API密钥，返回原始文本")
            return text
        
        # 构建请求数据
        prompt = self.optimization_prompt.format(text=text)
        
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
        
        data = {
            'model': self.model,
            'messages': [
                {
                    'role': 'user',
                    'content': prompt
                }
            ],
            'max_tokens': self.max_tokens,
            'temperature': self.temperature,
            'stream': False
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=data,
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                return result['choices'][0]['message']['content']
            else:
                logger.error(f"API调用失败: {response.status_code} - {response.text}")
                return text
                
        except Exception as e:
            logger.error(f"AI优化调用异常: {str(e)}")
            return text
    
    def _postprocess_text(self, text: str, title: str) -> str:
        """后处理优化结果"""
        # 添加标题
        if not text.startswith('#'):
            text = f"# {title}\n\n{text}"
        
        # 确保有目录结构
        if '##' in text and '目录' not in text:
            # 提取标题生成目录
            import re
            headers = re.findall(r'^(#{1,3})\s+(.+)$', text, re.MULTILINE)
            if headers:
                toc = "## 目录\n\n"
                for level, header in headers:
                    if level == '##':
                        toc += f"- [{header}](#{header.replace(' ', '-')})\n"
                text = text.replace('#', f"# {title}\n\n{toc}\n#", 1)
        
        return text
    
    def _save_optimized_text(self, text: str, title: str) -> Path:
        """保存优化后的文本"""
        output_dir = Path(self.config.get('output_dir', 'output/optimized'))
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # 生成文件名
        safe_title = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_')).rstrip()
        filename = f"{safe_title}_optimized.md"
        output_path = output_dir / filename
        
        # 保存文件
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(text)
        
        return output_path
    
    def _calculate_stats(self, original: str, optimized: str) -> Dict[str, Any]:
        """计算优化统计信息"""
        return {
            'original_length': len(original),
            'optimized_length': len(optimized),
            'length_change': len(optimized) - len(original),
            'paragraph_count': optimized.count('\n\n') + 1,
            'header_count': optimized.count('#')
        }