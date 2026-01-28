# dinhui-range-search-001
为了顶会计划的第一步 - 面向特定研究领域的自动化文献综述系统
> "面向特定研究领域的自动化文献综述系统" —— 通过智能爬取、筛选、解析与总结学术论文，构建结构化知识库，并最终输出领域发展现状的综合分析报告。

## 项目结构

```
dinhui-range-search-001/
├── config/                  # 配置文件目录
│   ├── config.yaml          # 主配置文件
│   └── prompts/             # LLM提示词模板
├── src/                     # 源代码目录
│   ├── core/                # 核心模块
│   ├── crawler/             # 文献爬取模块
│   ├── pdf/                 # PDF处理模块
│   ├── llm/                 # LLM分析模块
│   ├── database/            # 数据库模块
│   └── report/              # 报告生成模块
├── scripts/                 # 脚本目录
│   ├── run.py               # 运行脚本
│   └── test.py              # 测试脚本
├── data/                    # 数据目录
│   ├── pdf/                 # PDF存储
│   ├── db/                  # 数据库文件
│   └── reports/             # 生成的报告
├── tests/                   # 测试目录
├── requirements.txt         # 依赖项
└── README.md                # 项目说明
```

## 功能特点

1. **智能文献爬取**：从arXiv和Google Scholar自动获取相关论文
2. **PDF自动下载**：支持从多个来源获取论文PDF
3. **高效PDF解析**：集成Grobid和PyMuPDF，提取论文文本和结构
4. **LLM结构化分析**：使用DeepSeek-R1提取研究问题、方法等关键信息
5. **结构化数据库**：使用SQLite存储论文信息，支持高级查询
6. **自动报告生成**：基于数据库内容生成综合综述报告，包含图表和分析

## 安装方法

1. **克隆代码库**：
   ```bash
   git clone <repository-url>
   cd dinhui-range-search-001
   ```

2. **安装依赖**：
   ```bash
   pip install -r requirements.txt
   ```

3. **配置系统**：
   - 编辑 `config/config.yaml` 文件，设置研究领域、时间范围等参数

4. **部署Grobid（可选）**：
   - 用于更准确的PDF解析
   - 参考：https://grobid.readthedocs.io/en/latest/Install-Grobid/

## 使用方法

### 运行完整工作流程

```bash
python scripts/run.py --domain "多模态大模型在医疗诊断中的应用" --start-year 2020
```

### 命令行参数

- `--domain`：研究领域名称
- `--start-year`：开始年份
- `--end-year`：结束年份（默认当前年份）
- `--keywords`：搜索关键词列表
- `--verbose`：启用详细输出

### 测试各个模块

```bash
python scripts/test.py
```

## 配置说明

主要配置文件：`config/config.yaml`

- **research**：研究领域和时间范围设置
- **sources**：文献来源配置（arXiv和Google Scholar）
- **pdf**：PDF下载和存储配置
- **pdf_parsing**：PDF解析配置
- **llm**：LLM分析配置
- **database**：数据库配置
- **report**：报告生成配置

## 技术栈

- **Python 3.9+**：核心开发语言
- **arXiv API + scholarly**：文献爬取
- **Grobid + PyMuPDF**：PDF解析
- **DeepSeek-R1**：LLM分析
- **SQLite**：数据存储
- **Jinja2 + matplotlib**：报告生成

## 注意事项

1. **反爬限制**：使用Google Scholar时请注意遵守网站规则，避免频繁请求
2. **API密钥**：如果使用云端LLM API，需要在配置文件中设置API密钥
3. **存储容量**：随着论文数量增加，需要确保有足够的存储空间
4. **计算资源**：LLM分析可能需要较大的计算资源，建议在性能较好的机器上运行

## 未来计划

1. 添加Web界面，方便用户操作
2. 支持更多文献来源
3. 优化LLM分析效率
4. 增加更多可视化图表
5. 支持交互式报告

## 贡献

欢迎提交Issue和Pull Request，帮助改进这个项目！
