# {{ domain }} 领域综述报告

## 报告信息

- **研究领域**: {{ domain }}
- **时间范围**: {{ start_year }}-{{ end_year }}
- **报告生成日期**: {{ generation_date }}
- **论文总数**: {{ total_papers }}

## 1. 领域概述

本报告对{{ domain }}领域的研究现状进行了全面分析，基于{{ total_papers }}篇相关论文的数据。报告涵盖了该领域的研究趋势、主流方法、关键创新点、存在的问题与挑战，以及未来研究方向。

## 2. 研究趋势分析

### 2.1 年度论文分布

{% if charts.yearly %}
![年度论文分布]({{ charts.yearly }})
{% else %}
| 年份 | 论文数量 |
|------|----------|
{% for year, count in yearly_distribution.items() %}
| {{ year }} | {{ count }} |
{% endfor %}
{% endif %}

### 2.2 来源分布

{% if charts.source %}
![来源分布]({{ charts.source }})
{% else %}
| 来源 | 论文数量 |
|------|----------|
{% for source, count in source_distribution.items() %}
| {{ source }} | {{ count }} |
{% endfor %}
{% endif %}

## 3. 主流方法与技术路线

## 4. 关键创新点

## 5. 存在的问题与挑战

## 6. 未来研究方向

## 7. 结论

## 8. 参考文献

{% for paper in papers %}
- {{ paper.title }} ({{ paper.publish_year }})
{% endfor %}
