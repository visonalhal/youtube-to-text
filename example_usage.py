"""
AI优化功能使用示例
"""

import sys
from pathlib import Path

# 添加 src 目录到 Python 路径
sys.path.append(str(Path(__file__).parent / "src"))

from main import YouTubeToTextProcessor


def example_with_ai_optimization():
    """演示带AI优化的处理流程"""
    
    print("=== YouTube转文本工具 - AI优化示例 ===\n")
    
    # 创建处理器
    processor = YouTubeToTextProcessor("config.yaml")
    
    # 示例：处理YouTube视频（需要配置API密钥）
    video_url = "https://www.youtube.com/watch?v=example"
    
    print(f"处理视频: {video_url}")
    print("处理流程:")
    print("1. 下载视频/音频")
    print("2. 语音识别转录")
    print("3. 基础格式化")
    print("4. AI智能优化 ✨")
    print("5. 生成最终文档")
    
    # 注意：实际使用时需要配置API密钥
    print("\n注意：使用AI优化功能需要配置API密钥")
    print("export DEEPSEEK_API_KEY=your_api_key_here")
    
    # 处理结果会包含以下文件：
    print("\n输出文件:")
    print("├── output/videos/          # 原始视频")
    print("├── output/audios/          # 提取的音频")
    print("├── output/texts/           # 转录文本")
    print("├── output/formatted/       # 格式化文档")
    print("└── output/optimized/       # AI优化文档 ✨")
    
    print("\nAI优化效果:")
    print("✅ 修正错别字和语法错误")
    print("✅ 重新组织段落结构")
    print("✅ 添加合适的标题")
    print("✅ 转换为书面语")
    print("✅ 生成专业Markdown文档")


if __name__ == "__main__":
    example_with_ai_optimization()