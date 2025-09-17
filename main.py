"""
YouTube 视频转文本主程序
完整的处理流程：下载视频 -> 转换音频 -> 语音识别 -> 保存文本
"""

import sys
from pathlib import Path
from loguru import logger
from typing import List, Dict, Any

# 添加 src 目录到 Python 路径
sys.path.append(str(Path(__file__).parent / "src"))

from downloader.youtube_downloader import YouTubeDownloader
from downloader.local_video_processor import LocalVideoProcessor
from converter.audio_converter import AudioConverter
from transcriber.whisper_transcriber import WhisperTranscriber
from src.formatter.document_formatter import DocumentFormatter
from optimizer.ai_optimizer import AIOptimizer
from utils.config import Config


class YouTubeToTextProcessor:
    """YouTube 视频转文本处理器"""
    
    def __init__(self, config_path: str = "config.yaml"):
        """
        初始化处理器
        
        Args:
            config_path: 配置文件路径
        """
        self.config = Config(config_path)
        self._setup_logging()
        
        # 初始化各个组件
        self.downloader = YouTubeDownloader(
            output_dir=self.config.get('download.output_dir', 'output/videos')
        )
        self.local_processor = LocalVideoProcessor(
            output_dir=self.config.get('download.output_dir', 'output/videos')
        )
        self.converter = AudioConverter(
            output_dir=self.config.get('converter.output_dir', 'output/audios')
        )
        self.transcriber = WhisperTranscriber(
            model_size=self.config.get('transcriber.model_size', 'base'),
            output_dir=self.config.get('transcriber.output_dir', 'output/texts')
        )
        self.formatter = DocumentFormatter(
            output_dir=self.config.get('formatter.output_dir', 'output/formatted')
        )
        
        # 初始化AI优化器（如果启用）
        self.optimizer = None
        if self.config.get('optimizer.enable_ai_optimization', False):
            optimizer_config = self.config.get('optimizer', {})
            # 从环境变量获取API密钥
            import os
            api_key = os.getenv('DEEPSEEK_API_KEY') or optimizer_config.get('api_key', '')
            if api_key:
                optimizer_config['api_key'] = api_key
                self.optimizer = AIOptimizer(optimizer_config)
                logger.info("AI优化器已启用")
            else:
                logger.warning("未配置API密钥，AI优化功能将不可用")
    
    def _setup_logging(self):
        """设置日志"""
        log_level = self.config.get('logging.level', 'INFO')
        log_format = self.config.get('logging.format', '{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}')
        log_file = self.config.get('logging.file', 'logs/app.log')
        
        # 创建日志目录
        Path(log_file).parent.mkdir(parents=True, exist_ok=True)
        
        # 配置日志
        logger.remove()  # 移除默认处理器
        logger.add(sys.stderr, level=log_level, format=log_format)
        logger.add(log_file, level=log_level, format=log_format, rotation="10 MB")
    
    def process_single_video(self, input_path: str, language: str = None) -> Dict[str, Any]:
        """
        处理单个视频（支持 YouTube 链接或本地文件）
        
        Args:
            input_path: YouTube 视频链接或本地视频文件路径
            language: 转录语言
            
        Returns:
            处理结果字典
        """
        logger.info(f"开始处理视频: {input_path}")
        
        result = {
            'input_path': input_path,
            'success': False,
            'steps': {}
        }
        
        try:
            # 判断输入类型
            if self._is_youtube_url(input_path):
                # 处理 YouTube 视频
                result = self._process_youtube_video(input_path, language)
            elif self._is_local_file(input_path):
                # 处理本地视频
                result = self._process_local_video(input_path, language)
            else:
                logger.error(f"不支持的输入类型: {input_path}")
                result['error'] = "不支持的输入类型"
                return result
            
        except Exception as e:
            logger.error(f"处理过程中发生错误: {str(e)}")
            result['error'] = str(e)
        
        return result
    
    def _is_youtube_url(self, input_path: str) -> bool:
        """判断是否为 YouTube URL"""
        youtube_domains = ['youtube.com', 'youtu.be', 'm.youtube.com']
        return any(domain in input_path.lower() for domain in youtube_domains)
    
    def _is_local_file(self, input_path: str) -> bool:
        """判断是否为本地文件"""
        return Path(input_path).exists()
    
    def _process_youtube_video(self, url: str, language: str = None) -> Dict[str, Any]:
        """处理 YouTube 视频"""
        result = {
            'input_path': url,
            'success': False,
            'steps': {}
        }
        
        # 步骤1: 下载视频
        logger.info("步骤1: 下载 YouTube 视频")
        if self.config.get('download.audio_only', False):
            download_result = self.downloader.download_audio_only(url)
            if not download_result:
                logger.error("音频下载失败")
                return result
            result['steps']['download'] = download_result
            audio_path = download_result['audio_path']
        else:
            download_result = self.downloader.download_video(url)
            if not download_result:
                logger.error("视频下载失败")
                return result
            result['steps']['download'] = download_result
            
            # 步骤2: 转换音频
            logger.info("步骤2: 转换音频")
            audio_path = self.converter.video_to_audio(
                download_result['video_path'],
                audio_format=self.config.get('converter.audio_format', 'mp3'),
                quality=self.config.get('converter.quality', '192k')
            )
            if not audio_path:
                logger.error("音频转换失败")
                return result
            result['steps']['convert'] = {'audio_path': audio_path}
        
        # 步骤3: 语音识别
        result = self._perform_transcription(result, audio_path, language)
        return result
    
    def _process_local_video(self, video_path: str, language: str = None) -> Dict[str, Any]:
        """处理本地视频"""
        result = {
            'input_path': video_path,
            'success': False,
            'steps': {}
        }
        
        # 步骤1: 处理本地视频
        logger.info("步骤1: 处理本地视频")
        local_result = self.local_processor.process_local_video(
            video_path, 
            copy_to_output=self.config.get('download.copy_local_files', True)
        )
        if not local_result:
            logger.error("本地视频处理失败")
            return result
        result['steps']['local_process'] = local_result
        
        # 步骤2: 转换音频
        logger.info("步骤2: 转换音频")
        audio_path = self.converter.video_to_audio(
            local_result['video_path'],
            audio_format=self.config.get('converter.audio_format', 'mp3'),
            quality=self.config.get('converter.quality', '192k')
        )
        if not audio_path:
            logger.error("音频转换失败")
            return result
        result['steps']['convert'] = {'audio_path': audio_path}
        
        # 步骤3: 语音识别
        result = self._perform_transcription(result, audio_path, language)
        return result
    
    def _perform_transcription(self, result: Dict[str, Any], audio_path: str, language: str = None) -> Dict[str, Any]:
        """执行语音识别"""
        logger.info("步骤3: 语音识别")
        transcribe_language = language or self.config.get('transcriber.language')
        transcript_result = self.transcriber.transcribe_audio(
            audio_path,
            language=transcribe_language,
            task=self.config.get('transcriber.task', 'transcribe')
        )
        if not transcript_result:
            logger.error("语音识别失败")
            return result
        result['steps']['transcribe'] = transcript_result
        
        result['success'] = True
        logger.success(f"视频处理完成: {transcript_result.get('text', '')[:100]}...")
        
        # 步骤4: 文档格式化
        if self.config.get('formatter.enable_basic_formatting', True):
            logger.info("步骤4: 文档格式化")
            format_result = self.formatter.format_transcript(
                transcript_result['text'],
                transcript_result.get('title', '转录文档')
            )
            if format_result:
                result['steps']['format'] = format_result
                logger.success(f"文档格式化完成: {format_result['output_path']}")
            else:
                logger.warning("文档格式化失败，但转录已完成")
        
        # 步骤5: AI优化（如果启用）
        if self.optimizer and self.config.get('optimizer.enable_ai_optimization', False):
            logger.info("步骤5: AI文档优化")
            # 使用原始转录文本进行AI优化
            original_text = transcript_result['text']
            title = transcript_result.get('title', '转录文档')
            
            optimization_result = self.optimizer.optimize_text(original_text, title)
            if optimization_result:
                result['steps']['ai_optimization'] = optimization_result
                logger.success(f"AI优化完成: {optimization_result['output_path']}")
            else:
                logger.warning("AI优化失败，但基础处理已完成")
        
        return result
    
    def process_multiple_videos(self, input_paths: List[str], language: str = None) -> List[Dict[str, Any]]:
        """
        处理多个视频（支持 YouTube 链接和本地文件混合）
        
        Args:
            input_paths: 视频链接或文件路径列表
            language: 转录语言
            
        Returns:
            处理结果列表
        """
        logger.info(f"开始批量处理 {len(input_paths)} 个视频")
        
        results = []
        for i, input_path in enumerate(input_paths, 1):
            logger.info(f"处理视频 {i}/{len(input_paths)}: {input_path}")
            result = self.process_single_video(input_path, language)
            results.append(result)
            
            if result['success']:
                logger.success(f"视频 {i} 处理成功")
            else:
                logger.error(f"视频 {i} 处理失败")
        
        success_count = sum(1 for r in results if r['success'])
        logger.info(f"批量处理完成: {success_count}/{len(input_paths)} 成功")
        
        return results
    
    def process_from_file(self, file_path: str, language: str = None) -> List[Dict[str, Any]]:
        """
        从文件读取路径列表进行处理（支持 YouTube 链接和本地文件路径混合）
        
        Args:
            file_path: 包含路径的文件路径
            language: 转录语言
            
        Returns:
            处理结果列表
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                input_paths = [line.strip() for line in f if line.strip() and not line.startswith('#')]
            
            logger.info(f"从文件读取到 {len(input_paths)} 个路径")
            return self.process_multiple_videos(input_paths, language)
            
        except Exception as e:
            logger.error(f"读取文件失败: {str(e)}")
            return []


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='视频转文本工具（支持 YouTube 和本地视频）')
    parser.add_argument('input', nargs='?', help='YouTube 视频链接或本地视频文件路径')
    parser.add_argument('-f', '--file', help='包含路径列表的文件（支持 YouTube 链接和本地文件路径）')
    parser.add_argument('-l', '--language', help='转录语言 (zh, en, ja 等)')
    parser.add_argument('-c', '--config', default='config.yaml', help='配置文件路径')
    parser.add_argument('--audio-only', action='store_true', help='仅下载音频（仅对 YouTube 有效）')
    
    args = parser.parse_args()
    
    # 创建处理器
    processor = YouTubeToTextProcessor(args.config)
    
    # 如果指定了仅下载音频
    if args.audio_only:
        processor.config.set('download.audio_only', True)
    
    if args.input:
        # 处理单个视频
        result = processor.process_single_video(args.input, args.language)
        if result['success']:
            print(f"处理成功！文本已保存到: {result['steps']['transcribe']['output_path']}")
        else:
            print("处理失败！")
            sys.exit(1)
    
    elif args.file:
        # 批量处理
        results = processor.process_from_file(args.file, args.language)
        success_count = sum(1 for r in results if r['success'])
        print(f"批量处理完成: {success_count}/{len(results)} 成功")
    
    else:
        # 交互模式
        print("视频转文本工具（支持 YouTube 和本地视频）")
        print("=" * 50)
        
        while True:
            input_path = input("请输入 YouTube 视频链接或本地视频文件路径 (输入 'quit' 退出): ").strip()
            if input_path.lower() == 'quit':
                break
            
            if not input_path:
                continue
            
            result = processor.process_single_video(input_path, args.language)
            if result['success']:
                print(f"处理成功！文本已保存到: {result['steps']['transcribe']['output_path']}")
            else:
                print("处理失败！")


if __name__ == "__main__":
    main()
