"""
文档排版格式化模块
提供基础排版和AI增强排版功能
"""

import re
from pathlib import Path
from typing import List, Dict, Any, Optional
from loguru import logger


class DocumentFormatter:
    """文档格式化器"""
    
    def __init__(self, output_dir: str = "output/formatted"):
        """
        初始化格式化器
        
        Args:
            output_dir: 格式化文档保存目录
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # 段落分隔符模式
        self.paragraph_patterns = [
            r'[。！？]',  # 句号、感叹号、问号
            r'[，,；;]',  # 逗号、分号
            r'[：:]',     # 冒号
            r'[、]',      # 顿号
        ]
        
        # 标题识别模式
        self.title_patterns = [
            r'^第[一二三四五六七八九十\d]+[章节部分]',  # 第X章/节/部分
            r'^[一二三四五六七八九十\d]+[、．.]',      # 数字序号
            r'^[（(]\d+[）)]',                        # (1) (2) 等
            r'^[A-Za-z]\d*[、．.]',                   # A. B. 等
        ]
        
        # 列表识别模式
        self.list_patterns = [
            r'^\d+[、．.]',      # 1. 2. 等
            r'^[一二三四五六七八九十]+[、．.]',  # 一、二、等
            r'^[（(][一二三四五六七八九十\d]+[）)]',  # (一) (1) 等
        ]
    
    def format_transcript(self, text: str, title: str = "转录文本") -> Dict[str, Any]:
        """
        格式化转录文本
        
        Args:
            text: 原始转录文本
            title: 文档标题
            
        Returns:
            格式化结果字典
        """
        try:
            logger.info(f"开始格式化文档: {title}")
            
            # 1. 基础清理
            cleaned_text = self._clean_text(text)
            
            # 2. 段落分段
            paragraphs = self._split_paragraphs(cleaned_text)
            
            # 3. 识别结构
            structure = self._analyze_structure(paragraphs)
            
            # 4. 生成格式化文本
            formatted_text = self._generate_formatted_text(paragraphs, structure, title)
            
            # 5. 保存文件
            output_path = self._save_formatted_text(formatted_text, title)
            
            logger.success(f"文档格式化完成: {output_path}")
            
            return {
                'title': title,
                'formatted_text': formatted_text,
                'output_path': str(output_path),
                'structure': structure,
                'paragraph_count': len(paragraphs)
            }
            
        except Exception as e:
            logger.error(f"格式化文档失败: {str(e)}")
            return None
    
    def _clean_text(self, text: str) -> str:
        """清理文本"""
        # 移除多余空格
        text = re.sub(r'\s+', ' ', text)
        
        # 移除特殊字符
        text = re.sub(r'[^\w\s\u4e00-\u9fff，。！？：；、（）【】《》""''""''…—]', '', text)
        
        # 统一标点符号
        text = text.replace('，', '，').replace('。', '。')
        
        return text.strip()
    
    def _split_paragraphs(self, text: str) -> List[str]:
        """分段文本"""
        # 按句号、感叹号、问号分段
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
            
            # 判断是否应该分段
            if self._should_split_paragraph(current_paragraph):
                if current_paragraph.strip():
                    paragraphs.append(current_paragraph.strip())
                current_paragraph = ""
        
        # 添加最后一段
        if current_paragraph.strip():
            paragraphs.append(current_paragraph.strip())
        
        return paragraphs
    
    def _should_split_paragraph(self, text: str) -> bool:
        """判断是否应该分段"""
        # 按长度分段（超过200字符）
        if len(text) > 200:
            return True
        
        # 按关键词分段
        split_keywords = [
            '接下来', '下面', '最后', '总结', '总之',
            '第一部分', '第二部分', '第三部分',
            '首先', '其次', '然后', '最后'
        ]
        
        for keyword in split_keywords:
            if keyword in text:
                return True
        
        return False
    
    def _analyze_structure(self, paragraphs: List[str]) -> Dict[str, Any]:
        """分析文档结构"""
        structure = {
            'titles': [],
            'lists': [],
            'paragraphs': []
        }
        
        for i, paragraph in enumerate(paragraphs):
            # 识别标题
            if self._is_title(paragraph):
                structure['titles'].append({
                    'index': i,
                    'text': paragraph,
                    'level': self._get_title_level(paragraph)
                })
            
            # 识别列表
            elif self._is_list(paragraph):
                structure['lists'].append({
                    'index': i,
                    'text': paragraph,
                    'type': self._get_list_type(paragraph)
                })
            
            # 普通段落
            else:
                structure['paragraphs'].append({
                    'index': i,
                    'text': paragraph
                })
        
        return structure
    
    def _is_title(self, text: str) -> bool:
        """判断是否为标题"""
        for pattern in self.title_patterns:
            if re.match(pattern, text.strip()):
                return True
        return False
    
    def _is_list(self, text: str) -> bool:
        """判断是否为列表"""
        for pattern in self.list_patterns:
            if re.match(pattern, text.strip()):
                return True
        return False
    
    def _get_title_level(self, text: str) -> int:
        """获取标题级别"""
        if re.match(r'^第[一二三四五六七八九十\d]+[章节部分]', text):
            return 1
        elif re.match(r'^[一二三四五六七八九十\d]+[、．.]', text):
            return 2
        else:
            return 3
    
    def _get_list_type(self, text: str) -> str:
        """获取列表类型"""
        if re.match(r'^\d+[、．.]', text):
            return 'numbered'
        elif re.match(r'^[一二三四五六七八九十]+[、．.]', text):
            return 'chinese'
        else:
            return 'bullet'
    
    def _generate_formatted_text(self, paragraphs: List[str], structure: Dict[str, Any], title: str) -> str:
        """生成格式化文本"""
        formatted_lines = []
        
        # 添加标题
        formatted_lines.append(f"# {title}")
        formatted_lines.append("")
        
        # 添加目录（如果有标题）
        if structure['titles']:
            formatted_lines.append("## 目录")
            for title_info in structure['titles']:
                indent = "  " * (title_info['level'] - 1)
                formatted_lines.append(f"{indent}- {title_info['text']}")
            formatted_lines.append("")
        
        # 添加内容
        for i, paragraph in enumerate(paragraphs):
            # 检查是否为标题
            is_title = any(t['index'] == i for t in structure['titles'])
            is_list = any(l['index'] == i for l in structure['lists'])
            
            if is_title:
                title_info = next(t for t in structure['titles'] if t['index'] == i)
                level = "#" * (title_info['level'] + 1)
                formatted_lines.append(f"{level} {paragraph}")
                formatted_lines.append("")
            
            elif is_list:
                list_info = next(l for l in structure['lists'] if l['index'] == i)
                if list_info['type'] == 'numbered':
                    formatted_lines.append(f"1. {paragraph}")
                elif list_info['type'] == 'chinese':
                    formatted_lines.append(f"- {paragraph}")
                else:
                    formatted_lines.append(f"• {paragraph}")
            
            else:
                # 普通段落
                formatted_lines.append(paragraph)
                formatted_lines.append("")
        
        return "\n".join(formatted_lines)
    
    def _save_formatted_text(self, formatted_text: str, title: str) -> Path:
        """保存格式化文本"""
        # 清理文件名
        safe_title = re.sub(r'[^\w\s-]', '', title)
        safe_title = re.sub(r'\s+', '_', safe_title)
        
        # 保存为Markdown格式
        output_path = self.output_dir / f"{safe_title}_formatted.md"
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(formatted_text)
        
        return output_path
    
    def format_multiple_documents(self, documents: List[Dict[str, str]]) -> List[Dict[str, Any]]:
        """批量格式化文档"""
        results = []
        
        for i, doc in enumerate(documents, 1):
            logger.info(f"格式化文档 {i}/{len(documents)}: {doc.get('title', f'文档{i}')}")
            
            result = self.format_transcript(
                doc['text'], 
                doc.get('title', f'文档{i}')
            )
            
            if result:
                results.append(result)
            else:
                logger.error(f"文档 {i} 格式化失败")
        
        logger.info(f"批量格式化完成: {len(results)}/{len(documents)} 成功")
        return results


def main():
    """测试函数"""
    formatter = DocumentFormatter()
    
    # 测试格式化
    test_text = "这是第一段内容。这是第二段内容！这是第三段内容？"
    result = formatter.format_transcript(test_text, "测试文档")
    
    if result:
        print(f"格式化成功: {result['output_path']}")
        print(f"段落数量: {result['paragraph_count']}")
    else:
        print("格式化失败")


if __name__ == "__main__":
    main()
