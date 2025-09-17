# 视频转文本工具

一个完整的视频处理工具，支持 YouTube 视频下载和本地视频文件处理，可以将视频转换为音频，并使用 AI 语音识别技术将音频转换为文本。

## 功能特性

- 🎥 **多源支持**: 支持 YouTube 视频下载和本地视频文件处理
- 🎵 **音频提取**: 将视频转换为高质量音频文件
- 🗣️ **语音识别**: 使用 OpenAI Whisper 进行高精度语音转文本
- 📝 **智能排版**: 自动格式化文档，提升可读性
- ⚙️ **灵活配置**: 支持自定义各种参数
- 📊 **批量处理**: 支持批量处理多个视频（可混合 YouTube 和本地文件）
- 🌍 **多语言支持**: 支持中文、英文等多种语言
- 🔄 **智能识别**: 自动识别输入类型（YouTube 链接或本地文件）

## 技术栈

- **Python 3.8+**
- **yt-dlp**: YouTube 视频下载
- **OpenAI Whisper**: 语音识别
- **FFmpeg**: 音频处理
- **Loguru**: 日志管理

## 安装说明

### 1. 克隆项目

```bash
git clone <repository-url>
cd youtube-to-text
```

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 安装 FFmpeg

**macOS:**
```bash
brew install ffmpeg
```

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install ffmpeg
```

**Windows:**
下载 FFmpeg 并添加到系统 PATH

## 使用方法

### 基本使用

```bash
# 处理 YouTube 视频
python main.py "https://www.youtube.com/watch?v=VIDEO_ID"

# 处理本地视频文件
python main.py "/path/to/your/video.mp4"

# 指定语言
python main.py "https://www.youtube.com/watch?v=VIDEO_ID" -l zh
python main.py "/path/to/your/video.mp4" -l zh

# 仅下载音频（仅对 YouTube 有效，更快）
python main.py "https://www.youtube.com/watch?v=VIDEO_ID" --audio-only
```

### 批量处理

```bash
# 从文件读取路径列表（支持混合 YouTube 链接和本地文件）
python main.py -f paths.txt -l zh
```

### 交互模式

```bash
# 启动交互模式（支持 YouTube 链接和本地文件）
python main.py
```

## 配置文件

项目使用 `config.yaml` 进行配置，主要配置项：

```yaml
# 下载配置
download:
  output_dir: "output/videos"          # 视频保存目录
  format: "best[height<=720]"          # 视频格式
  audio_only: false                    # 是否仅下载音频（仅对 YouTube 有效）
  copy_local_files: true               # 是否复制本地文件到输出目录

# 转录配置
transcriber:
  model_size: "base"                   # Whisper模型大小
  language: null                       # 语言代码
  task: "transcribe"                   # 任务类型

# 格式化配置
formatter:
  output_dir: "output/formatted"       # 格式化文档保存目录
  enable_basic_formatting: true        # 启用基础排版
  enable_ai_enhancement: false         # 启用AI增强排版（可选）
  output_formats: ["markdown"]         # 输出格式
```

## 输出文件

处理完成后，会在以下目录生成文件：

```
output/
├── videos/           # 下载的视频文件
├── audios/           # 转换的音频文件
├── texts/            # 转录的文本文件
│   ├── video_title_transcript.txt      # 纯文本
│   ├── video_title_timestamped.txt     # 带时间戳的文本
│   └── video_title_details.json        # 详细信息
└── formatted/        # 格式化文档
    └── video_title_formatted.md        # 格式化后的Markdown文档
```

## Whisper 模型选择

| 模型大小 | 参数量 | 内存需求 | 速度 | 准确度 |
|---------|--------|----------|------|--------|
| tiny    | 39M    | ~1GB     | 最快 | 较低   |
| base    | 74M    | ~1GB     | 快   | 中等   |
| small   | 244M   | ~2GB     | 中等 | 较好   |
| medium  | 769M   | ~5GB     | 慢   | 好     |
| large   | 1550M  | ~10GB    | 最慢 | 最好   |

## 使用示例

### 示例1: 处理 YouTube 中文视频

```bash
python main.py "https://www.youtube.com/watch?v=VIDEO_ID" -l zh
```

### 示例2: 处理本地视频

```bash
python main.py "/path/to/your/chinese_video.mp4" -l zh
```

### 示例3: 混合批量处理

创建 `paths.txt` 文件：
```
# YouTube 视频
https://www.youtube.com/watch?v=VIDEO_ID_1
https://www.youtube.com/watch?v=VIDEO_ID_2

# 本地视频文件
/path/to/local_video1.mp4
/path/to/local_video2.avi
./videos/sample.mkv
```

运行批量处理：
```bash
python main.py -f paths.txt -l zh
```

### 示例4: 仅下载音频（YouTube）

```bash
python main.py "https://www.youtube.com/watch?v=VIDEO_ID" --audio-only
```

## 高级功能

### 自定义配置

修改 `config.yaml` 文件来自定义各种参数：

```yaml
transcriber:
  model_size: "large"        # 使用更大的模型提高准确度
  language: "zh"             # 强制使用中文
  task: "translate"          # 翻译为英文
```

### 处理长视频

对于很长的视频，建议：

1. 使用 `audio_only: true` 仅下载音频
2. 使用较小的模型如 `base` 或 `small`
3. 分段处理（可以修改代码实现）

## 故障排除

### 常见问题

1. **下载失败**
   - 检查网络连接
   - 更新 yt-dlp: `pip install --upgrade yt-dlp`

2. **转录失败**
   - 检查音频文件是否存在
   - 确保 FFmpeg 已正确安装

3. **内存不足**
   - 使用更小的 Whisper 模型
   - 仅下载音频而不是完整视频

### 日志查看

查看详细日志：
```bash
tail -f logs/app.log
```

## 注意事项

- 请遵守 YouTube 的服务条款
- 仅用于个人学习，不得用于商业用途
- 注意版权问题
- 合理使用，避免对服务器造成过大负担

## 许可证

本项目仅供学习和研究使用。

## 贡献

欢迎提交 Issue 和 Pull Request！

## 支持的视频格式

### YouTube 视频
- 支持所有 YouTube 公开视频
- 自动选择最佳质量（可配置）

### 本地视频文件
支持以下格式：
- **MP4** (.mp4)
- **AVI** (.avi)
- **MKV** (.mkv)
- **MOV** (.mov)
- **WMV** (.wmv)
- **FLV** (.flv)
- **WebM** (.webm)
- **M4V** (.m4v)
- **3GP** (.3gp)
- **OGV** (.ogv)
- **TS** (.ts)
- **MTS** (.mts)

## 更新日志

- v1.1.0: 添加本地视频文件支持，支持混合批量处理
- v1.0.0: 初始版本，支持基本的 YouTube 视频转文本功能
