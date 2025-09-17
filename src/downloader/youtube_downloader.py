"""
YouTube 视频下载模块
使用 yt-dlp 下载 YouTube 视频
"""

import os
import yt_dlp
from pathlib import Path
from loguru import logger
from typing import Optional, Dict, Any


class YouTubeDownloader:
    """YouTube 视频下载器"""
    
    def __init__(self, output_dir: str = "output/videos"):
        """
        初始化下载器
        
        Args:
            output_dir: 视频保存目录
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # 配置 yt-dlp 选项
        self.ydl_opts = {
            'outtmpl': str(self.output_dir / '%(title)s.%(ext)s'),
            'format': 'best[height<=720]',  # 下载720p以下视频，节省空间
            'writesubtitles': False,
            'writeautomaticsub': False,
        }
    
    def download_video(self, url: str) -> Optional[Dict[str, Any]]:
        """
        下载单个视频
        
        Args:
            url: YouTube 视频链接
            
        Returns:
            下载信息字典，包含文件路径等
        """
        try:
            with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
                # 获取视频信息
                info = ydl.extract_info(url, download=False)
                title = info.get('title', 'Unknown')
                duration = info.get('duration', 0)
                
                logger.info(f"开始下载视频: {title}")
                logger.info(f"视频时长: {duration} 秒")
                
                # 下载视频
                ydl.download([url])
                
                # 查找下载的文件
                video_file = self._find_downloaded_file(title)
                
                if video_file:
                    logger.success(f"视频下载完成: {video_file}")
                    return {
                        'title': title,
                        'duration': duration,
                        'video_path': str(video_file),
                        'url': url
                    }
                else:
                    logger.error("未找到下载的视频文件")
                    return None
                    
        except Exception as e:
            logger.error(f"下载视频失败: {str(e)}")
            return None
    
    def download_audio_only(self, url: str) -> Optional[Dict[str, Any]]:
        """
        仅下载音频
        
        Args:
            url: YouTube 视频链接
            
        Returns:
            下载信息字典
        """
        audio_opts = self.ydl_opts.copy()
        audio_opts.update({
            'format': 'bestaudio/best',
            'outtmpl': str(self.output_dir / '%(title)s.%(ext)s'),
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
        })
        
        try:
            with yt_dlp.YoutubeDL(audio_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                title = info.get('title', 'Unknown')
                
                logger.info(f"开始下载音频: {title}")
                ydl.download([url])
                
                # 查找下载的音频文件
                audio_file = self._find_downloaded_file(title, extensions=['.mp3', '.m4a', '.webm'])
                
                if audio_file:
                    logger.success(f"音频下载完成: {audio_file}")
                    return {
                        'title': title,
                        'audio_path': str(audio_file),
                        'url': url
                    }
                else:
                    logger.error("未找到下载的音频文件")
                    return None
                    
        except Exception as e:
            logger.error(f"下载音频失败: {str(e)}")
            return None
    
    def _find_downloaded_file(self, title: str, extensions: list = None) -> Optional[Path]:
        """
        查找下载的文件
        
        Args:
            title: 视频标题
            extensions: 文件扩展名列表
            
        Returns:
            文件路径
        """
        if extensions is None:
            extensions = ['.mp4', '.mkv', '.webm', '.avi']
        
        # 清理标题，移除特殊字符
        clean_title = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_')).rstrip()
        
        for file_path in self.output_dir.iterdir():
            if file_path.is_file():
                file_name = file_path.stem
                file_ext = file_path.suffix.lower()
                
                # 检查文件名是否包含标题和扩展名
                if (clean_title.lower() in file_name.lower() or 
                    file_name.lower() in clean_title.lower()) and file_ext in extensions:
                    return file_path
        
        return None


def main():
    """测试函数"""
    downloader = YouTubeDownloader()
    
    # 测试下载
    test_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"  # 示例链接
    result = downloader.download_video(test_url)
    
    if result:
        print(f"下载成功: {result['title']}")
        print(f"文件路径: {result['video_path']}")
    else:
        print("下载失败")


if __name__ == "__main__":
    main()
