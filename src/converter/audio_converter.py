"""
音频转换模块
将视频文件转换为音频文件
"""

import os
import ffmpeg
from pathlib import Path
from loguru import logger
from typing import Optional, Dict, Any


class AudioConverter:
    """音频转换器"""
    
    def __init__(self, output_dir: str = "output/audios"):
        """
        初始化转换器
        
        Args:
            output_dir: 音频保存目录
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def video_to_audio(self, video_path: str, audio_format: str = "mp3", 
                      quality: str = "192k") -> Optional[str]:
        """
        将视频转换为音频
        
        Args:
            video_path: 视频文件路径
            audio_format: 音频格式 (mp3, wav, m4a)
            quality: 音频质量 (128k, 192k, 320k)
            
        Returns:
            音频文件路径
        """
        try:
            video_file = Path(video_path)
            if not video_file.exists():
                logger.error(f"视频文件不存在: {video_path}")
                return None
            
            # 生成音频文件名
            audio_filename = f"{video_file.stem}.{audio_format}"
            audio_path = self.output_dir / audio_filename
            
            logger.info(f"开始转换视频到音频: {video_file.name}")
            logger.info(f"目标格式: {audio_format}, 质量: {quality}")
            
            # 使用 ffmpeg 转换
            (
                ffmpeg
                .input(str(video_file))
                .output(
                    str(audio_path),
                    acodec='mp3' if audio_format == 'mp3' else audio_format,
                    audio_bitrate=quality,
                    ac=1  # 单声道，减少文件大小
                )
                .overwrite_output()
                .run(quiet=True)
            )
            
            if audio_path.exists():
                file_size = audio_path.stat().st_size / (1024 * 1024)  # MB
                logger.success(f"音频转换完成: {audio_path.name} ({file_size:.2f} MB)")
                return str(audio_path)
            else:
                logger.error("音频转换失败")
                return None
                
        except ffmpeg.Error as e:
            logger.error(f"FFmpeg 转换失败: {e}")
            return None
        except Exception as e:
            logger.error(f"音频转换失败: {str(e)}")
            return None
    
    def extract_audio_segment(self, video_path: str, start_time: float, 
                            duration: float, audio_format: str = "mp3") -> Optional[str]:
        """
        提取视频中的音频片段
        
        Args:
            video_path: 视频文件路径
            start_time: 开始时间（秒）
            duration: 持续时间（秒）
            audio_format: 音频格式
            
        Returns:
            音频文件路径
        """
        try:
            video_file = Path(video_path)
            if not video_file.exists():
                logger.error(f"视频文件不存在: {video_path}")
                return None
            
            # 生成音频文件名
            audio_filename = f"{video_file.stem}_segment_{start_time}s_{duration}s.{audio_format}"
            audio_path = self.output_dir / audio_filename
            
            logger.info(f"提取音频片段: {start_time}s - {start_time + duration}s")
            
            # 使用 ffmpeg 提取片段
            (
                ffmpeg
                .input(str(video_file), ss=start_time, t=duration)
                .output(
                    str(audio_path),
                    acodec='mp3' if audio_format == 'mp3' else audio_format,
                    ac=1
                )
                .overwrite_output()
                .run(quiet=True)
            )
            
            if audio_path.exists():
                logger.success(f"音频片段提取完成: {audio_path.name}")
                return str(audio_path)
            else:
                logger.error("音频片段提取失败")
                return None
                
        except Exception as e:
            logger.error(f"音频片段提取失败: {str(e)}")
            return None
    
    def get_audio_info(self, audio_path: str) -> Optional[Dict[str, Any]]:
        """
        获取音频文件信息
        
        Args:
            audio_path: 音频文件路径
            
        Returns:
            音频信息字典
        """
        try:
            audio_file = Path(audio_path)
            if not audio_file.exists():
                logger.error(f"音频文件不存在: {audio_path}")
                return None
            
            # 使用 ffprobe 获取音频信息
            probe = ffmpeg.probe(str(audio_file))
            audio_stream = next(
                (stream for stream in probe['streams'] if stream['codec_type'] == 'audio'),
                None
            )
            
            if audio_stream:
                duration = float(audio_stream.get('duration', 0))
                bitrate = int(audio_stream.get('bit_rate', 0))
                sample_rate = int(audio_stream.get('sample_rate', 0))
                channels = int(audio_stream.get('channels', 0))
                
                return {
                    'duration': duration,
                    'bitrate': bitrate,
                    'sample_rate': sample_rate,
                    'channels': channels,
                    'file_size': audio_file.stat().st_size
                }
            else:
                logger.error("无法获取音频流信息")
                return None
                
        except Exception as e:
            logger.error(f"获取音频信息失败: {str(e)}")
            return None


def main():
    """测试函数"""
    converter = AudioConverter()
    
    # 测试转换
    test_video = "output/videos/test.mp4"  # 示例视频路径
    if Path(test_video).exists():
        audio_path = converter.video_to_audio(test_video)
        if audio_path:
            print(f"转换成功: {audio_path}")
            
            # 获取音频信息
            info = converter.get_audio_info(audio_path)
            if info:
                print(f"音频信息: {info}")
    else:
        print("测试视频文件不存在")


if __name__ == "__main__":
    main()
