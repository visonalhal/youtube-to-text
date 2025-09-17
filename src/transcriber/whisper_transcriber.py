"""
语音转文本模块
使用 OpenAI Whisper 进行语音识别
"""

import os
import whisper
from pathlib import Path
from loguru import logger
from typing import Optional, Dict, Any, List
import json


class WhisperTranscriber:
    """Whisper 语音转文本器"""
    
    def __init__(self, model_size: str = "base", output_dir: str = "output/texts"):
        """
        初始化转录器
        
        Args:
            model_size: Whisper 模型大小 (tiny, base, small, medium, large)
            output_dir: 文本保存目录
        """
        self.model_size = model_size
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # 加载 Whisper 模型
        logger.info(f"正在加载 Whisper 模型: {model_size}")
        try:
            self.model = whisper.load_model(model_size)
            logger.success(f"Whisper 模型加载完成: {model_size}")
        except Exception as e:
            logger.error(f"模型加载失败: {str(e)}")
            self.model = None
    
    def transcribe_audio(self, audio_path: str, language: str = None, 
                        task: str = "transcribe") -> Optional[Dict[str, Any]]:
        """
        转录音频文件
        
        Args:
            audio_path: 音频文件路径
            language: 语言代码 (zh, en, ja 等)，None 为自动检测
            task: 任务类型 (transcribe 或 translate)
            
        Returns:
            转录结果字典
        """
        if not self.model:
            logger.error("Whisper 模型未加载")
            return None
        
        try:
            audio_file = Path(audio_path)
            if not audio_file.exists():
                logger.error(f"音频文件不存在: {audio_path}")
                return None
            
            logger.info(f"开始转录音频: {audio_file.name}")
            logger.info(f"语言: {language or '自动检测'}, 任务: {task}")
            
            # 执行转录
            result = self.model.transcribe(
                str(audio_file),
                language=language,
                task=task,
                verbose=True
            )
            
            # 提取转录文本
            text = result["text"].strip()
            segments = result.get("segments", [])
            
            # 生成输出文件名
            output_filename = f"{audio_file.stem}_transcript.txt"
            output_path = self.output_dir / output_filename
            
            # 保存转录结果
            self._save_transcript(text, segments, output_path)
            
            # 保存详细信息
            detail_filename = f"{audio_file.stem}_details.json"
            detail_path = self.output_dir / detail_filename
            self._save_transcript_details(result, detail_path)
            
            logger.success(f"转录完成: {output_path.name}")
            
            return {
                'text': text,
                'segments': segments,
                'language': result.get('language', 'unknown'),
                'output_path': str(output_path),
                'detail_path': str(detail_path),
                'audio_path': audio_path
            }
            
        except Exception as e:
            logger.error(f"转录失败: {str(e)}")
            return None
    
    def transcribe_with_timestamps(self, audio_path: str, language: str = None) -> Optional[Dict[str, Any]]:
        """
        带时间戳的转录
        
        Args:
            audio_path: 音频文件路径
            language: 语言代码
            
        Returns:
            带时间戳的转录结果
        """
        result = self.transcribe_audio(audio_path, language)
        if not result:
            return None
        
        # 生成带时间戳的文本
        timestamped_text = self._format_timestamped_text(result['segments'])
        
        # 保存带时间戳的文本
        audio_file = Path(audio_path)
        timestamp_filename = f"{audio_file.stem}_timestamped.txt"
        timestamp_path = self.output_dir / timestamp_filename
        
        with open(timestamp_path, 'w', encoding='utf-8') as f:
            f.write(timestamped_text)
        
        logger.success(f"带时间戳的转录完成: {timestamp_path.name}")
        
        result['timestamped_text'] = timestamped_text
        result['timestamp_path'] = str(timestamp_path)
        
        return result
    
    def _save_transcript(self, text: str, segments: List[Dict], output_path: Path):
        """保存转录文本"""
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(text)
    
    def _save_transcript_details(self, result: Dict, detail_path: Path):
        """保存转录详细信息"""
        with open(detail_path, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
    
    def _format_timestamped_text(self, segments: List[Dict]) -> str:
        """格式化带时间戳的文本"""
        timestamped_lines = []
        
        for segment in segments:
            start_time = self._format_time(segment['start'])
            end_time = self._format_time(segment['end'])
            text = segment['text'].strip()
            
            timestamped_lines.append(f"[{start_time} - {end_time}] {text}")
        
        return '\n'.join(timestamped_lines)
    
    def _format_time(self, seconds: float) -> str:
        """格式化时间"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        
        if hours > 0:
            return f"{hours:02d}:{minutes:02d}:{secs:02d}"
        else:
            return f"{minutes:02d}:{secs:02d}"
    
    def batch_transcribe(self, audio_files: List[str], language: str = None) -> List[Dict[str, Any]]:
        """
        批量转录音频文件
        
        Args:
            audio_files: 音频文件路径列表
            language: 语言代码
            
        Returns:
            转录结果列表
        """
        results = []
        
        for i, audio_path in enumerate(audio_files, 1):
            logger.info(f"处理文件 {i}/{len(audio_files)}: {Path(audio_path).name}")
            
            result = self.transcribe_audio(audio_path, language)
            if result:
                results.append(result)
            else:
                logger.error(f"文件转录失败: {audio_path}")
        
        logger.info(f"批量转录完成: {len(results)}/{len(audio_files)} 成功")
        return results


def main():
    """测试函数"""
    transcriber = WhisperTranscriber(model_size="base")
    
    # 测试转录
    test_audio = "output/audios/test.mp3"  # 示例音频路径
    if Path(test_audio).exists():
        result = transcriber.transcribe_audio(test_audio, language="zh")
        if result:
            print(f"转录成功: {result['text'][:100]}...")
            print(f"输出文件: {result['output_path']}")
    else:
        print("测试音频文件不存在")


if __name__ == "__main__":
    main()
