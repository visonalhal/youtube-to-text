"""
本地视频文件处理模块
处理本地视频文件，跳过下载步骤
"""

import os
from pathlib import Path
from loguru import logger
from typing import Optional, Dict, Any
import mimetypes


class LocalVideoProcessor:
    """本地视频文件处理器"""
    
    def __init__(self, output_dir: str = "output/videos"):
        """
        初始化处理器
        
        Args:
            output_dir: 视频保存目录（用于复制文件）
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # 支持的视频格式
        self.supported_formats = {
            '.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv', 
            '.webm', '.m4v', '.3gp', '.ogv', '.ts', '.mts'
        }
    
    def process_local_video(self, video_path: str, copy_to_output: bool = True) -> Optional[Dict[str, Any]]:
        """
        处理本地视频文件
        
        Args:
            video_path: 本地视频文件路径
            copy_to_output: 是否复制到输出目录
            
        Returns:
            处理信息字典
        """
        try:
            video_file = Path(video_path)
            
            # 检查文件是否存在
            if not video_file.exists():
                logger.error(f"视频文件不存在: {video_path}")
                return None
            
            # 检查文件格式
            if video_file.suffix.lower() not in self.supported_formats:
                logger.error(f"不支持的视频格式: {video_file.suffix}")
                logger.info(f"支持的格式: {', '.join(self.supported_formats)}")
                return None
            
            # 获取文件信息
            file_size = video_file.stat().st_size / (1024 * 1024)  # MB
            mime_type, _ = mimetypes.guess_type(str(video_file))
            
            logger.info(f"处理本地视频: {video_file.name}")
            logger.info(f"文件大小: {file_size:.2f} MB")
            logger.info(f"文件类型: {mime_type or '未知'}")
            
            # 复制文件到输出目录（如果需要）
            if copy_to_output:
                output_path = self.output_dir / video_file.name
                if not output_path.exists():
                    import shutil
                    shutil.copy2(video_file, output_path)
                    logger.info(f"视频文件已复制到: {output_path}")
                else:
                    logger.info(f"输出文件已存在: {output_path}")
            else:
                output_path = video_file
            
            return {
                'title': video_file.stem,
                'video_path': str(output_path),
                'original_path': str(video_file),
                'file_size': file_size,
                'mime_type': mime_type,
                'is_local': True
            }
            
        except Exception as e:
            logger.error(f"处理本地视频失败: {str(e)}")
            return None
    
    def validate_video_file(self, video_path: str) -> bool:
        """
        验证视频文件是否有效
        
        Args:
            video_path: 视频文件路径
            
        Returns:
            是否有效
        """
        try:
            video_file = Path(video_path)
            
            # 检查文件是否存在
            if not video_file.exists():
                logger.error(f"文件不存在: {video_path}")
                return False
            
            # 检查文件大小
            file_size = video_file.stat().st_size
            if file_size == 0:
                logger.error(f"文件为空: {video_path}")
                return False
            
            # 检查文件格式
            if video_file.suffix.lower() not in self.supported_formats:
                logger.error(f"不支持的视频格式: {video_file.suffix}")
                return False
            
            # 检查 MIME 类型
            mime_type, _ = mimetypes.guess_type(str(video_file))
            if mime_type and not mime_type.startswith('video/'):
                logger.warning(f"文件可能不是视频格式: {mime_type}")
            
            logger.success(f"视频文件验证通过: {video_file.name}")
            return True
            
        except Exception as e:
            logger.error(f"验证视频文件失败: {str(e)}")
            return False
    
    def get_video_info(self, video_path: str) -> Optional[Dict[str, Any]]:
        """
        获取视频文件信息
        
        Args:
            video_path: 视频文件路径
            
        Returns:
            视频信息字典
        """
        try:
            video_file = Path(video_path)
            if not video_file.exists():
                return None
            
            # 基本文件信息
            stat = video_file.stat()
            file_size = stat.st_size / (1024 * 1024)  # MB
            mime_type, _ = mimetypes.guess_type(str(video_file))
            
            return {
                'name': video_file.name,
                'stem': video_file.stem,
                'suffix': video_file.suffix,
                'size_mb': file_size,
                'mime_type': mime_type,
                'created': stat.st_ctime,
                'modified': stat.st_mtime
            }
            
        except Exception as e:
            logger.error(f"获取视频信息失败: {str(e)}")
            return None
    
    def batch_process_local_videos(self, video_paths: list, copy_to_output: bool = True) -> list:
        """
        批量处理本地视频文件
        
        Args:
            video_paths: 视频文件路径列表
            copy_to_output: 是否复制到输出目录
            
        Returns:
            处理结果列表
        """
        results = []
        
        for i, video_path in enumerate(video_paths, 1):
            logger.info(f"处理本地视频 {i}/{len(video_paths)}: {Path(video_path).name}")
            
            # 验证文件
            if not self.validate_video_file(video_path):
                logger.error(f"视频文件验证失败: {video_path}")
                results.append(None)
                continue
            
            # 处理文件
            result = self.process_local_video(video_path, copy_to_output)
            results.append(result)
            
            if result:
                logger.success(f"本地视频 {i} 处理成功")
            else:
                logger.error(f"本地视频 {i} 处理失败")
        
        success_count = sum(1 for r in results if r is not None)
        logger.info(f"批量处理完成: {success_count}/{len(video_paths)} 成功")
        
        return results


def main():
    """测试函数"""
    processor = LocalVideoProcessor()
    
    # 测试处理本地视频
    test_video = "test_video.mp4"  # 示例视频路径
    if Path(test_video).exists():
        result = processor.process_local_video(test_video)
        if result:
            print(f"处理成功: {result['title']}")
            print(f"文件路径: {result['video_path']}")
    else:
        print("测试视频文件不存在")


if __name__ == "__main__":
    main()
