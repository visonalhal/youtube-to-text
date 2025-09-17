"""
AI优化提示词模板
包含不同场景的优化提示词
"""

# 基础优化提示词
BASIC_OPTIMIZATION_PROMPT = """
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

# 学术风格优化提示词
ACADEMIC_OPTIMIZATION_PROMPT = """
请将以下转录文本优化为学术风格的文档。

优化要求：
1. 修正错别字、语法错误和标点符号
2. 采用学术写作风格，语言严谨规范
3. 重新组织段落结构，添加合适的标题和子标题
4. 将口语化表达转换为书面语
5. 保持原文的核心观点和逻辑结构
6. 输出格式为Markdown，包含目录结构
7. 确保内容连贯性和可读性

原文内容：
{text}

请直接输出优化后的Markdown文档，不要包含其他说明文字。
"""

# 商业风格优化提示词
BUSINESS_OPTIMIZATION_PROMPT = """
请将以下转录文本优化为商业风格的文档。

优化要求：
1. 修正错别字、语法错误和标点符号
2. 采用商业写作风格，语言简洁明了
3. 重新组织段落结构，添加合适的标题和子标题
4. 将口语化表达转换为书面语
5. 保持原文的核心观点和逻辑结构
6. 输出格式为Markdown，包含目录结构
7. 确保内容连贯性和可读性
8. 突出关键信息和行动要点

原文内容：
{text}

请直接输出优化后的Markdown文档，不要包含其他说明文字。
"""

# 技术文档优化提示词
TECHNICAL_OPTIMIZATION_PROMPT = """
请将以下转录文本优化为技术文档。

优化要求：
1. 修正错别字、语法错误和标点符号
2. 采用技术写作风格，语言准确专业
3. 重新组织段落结构，添加合适的标题和子标题
4. 将口语化表达转换为书面语
5. 保持原文的核心观点和逻辑结构
6. 输出格式为Markdown，包含目录结构
7. 确保内容连贯性和可读性
8. 突出技术要点和操作步骤

原文内容：
{text}

请直接输出优化后的Markdown文档，不要包含其他说明文字。
"""

# 提示词模板映射
PROMPT_TEMPLATES = {
    'basic': BASIC_OPTIMIZATION_PROMPT,
    'academic': ACADEMIC_OPTIMIZATION_PROMPT,
    'business': BUSINESS_OPTIMIZATION_PROMPT,
    'technical': TECHNICAL_OPTIMIZATION_PROMPT
}

def get_prompt_template(style: str = 'basic') -> str:
    """
    获取指定风格的提示词模板
    
    Args:
        style: 文档风格 ('basic', 'academic', 'business', 'technical')
        
    Returns:
        提示词模板字符串
    """
    return PROMPT_TEMPLATES.get(style, BASIC_OPTIMIZATION_PROMPT)