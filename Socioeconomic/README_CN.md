# NC Exposome Knowledge Graph (Triple-Based)

基于三元组（Triples）的北卡罗来纳州社会经济暴露组知识图谱，借鉴ROBOKOP的推理能力。

## 特点

- ✅ **纯三元组格式**: 所有数据存储为 (subject, predicate, object) 形式
- ✅ **真实数据**: 自动从 US Census 和 CDC PLACES API 获取数据
- ✅ **证据追踪**: 每个triple包含数据来源和置信度（ROBOKOP-inspired）
- ✅ **路径推理**: 发现社会经济因素到健康结果的机制路径
- ✅ **RDF兼容**: 可导出为 N-Triples 格式
- ✅ **100个县**: 覆盖北卡罗来纳州全部县级数据

## 快速开始

```bash
# 安装依赖
pip install -r requirements.txt

# 运行notebook
jupyter notebook nc_exposome_kg.ipynb
```

## 数据源

- **US Census Bureau**: 人口、收入、贫困、失业、教育
- **CDC PLACES**: 肥胖、糖尿病、哮喘、心理健康
- **示例环境数据**: 空气质量、PM2.5（可替换为EPA EJScreen）

## Triple结构

### 基本三元组
```
(37119, 'rdf:type', 'Location')
(37119, 'name', 'Mecklenburg')
(poverty_rate, 'rdf:type', 'Indicator')
```

### 测量（Reification）
```
(m_37119_poverty_rate, 'rdf:type', 'Measurement')
(m_37119_poverty_rate, 'location', '37119')
(m_37119_poverty_rate, 'indicator', 'poverty_rate')
(m_37119_poverty_rate, 'value', 10.57)
(m_37119_poverty_rate, 'unit', 'percent')
```

### 相关性（Reification）
```
(corr_poverty_rate_obesity_pct, 'rdf:type', 'Correlation')
(corr_poverty_rate_obesity_pct, 'indicator1', 'poverty_rate')
(corr_poverty_rate_obesity_pct, 'indicator2', 'obesity_pct')
(corr_poverty_rate_obesity_pct, 'value', 0.68)
```

## 查询示例

### 基础查询
```python
# 查询所有位置
locations = kg.query(predicate='rdf:type', obj='Location')

# 查询特定县的所有三元组
mecklenburg_triples = kg.query(subject='37119')

# 获取县的完整档案（带证据来源）
profile = kg.get_location_profile('37119')
# 返回: {'Poverty Rate': {'value': 10.57, 'unit': 'percent', 'source': 'Census', 'confidence': 0.95}}
```

### ROBOKOP风格路径推理
```python
# 找出社会经济因素到健康结果的机制路径
pathways = kg.find_mechanistic_pathway('poverty_rate', 'diabetes_pct')
# 返回所有连接poverty_rate和diabetes_pct的路径，按置信度排序

# 按置信度过滤
high_quality = kg.query(predicate='rdf:type', obj='Correlation', min_confidence=0.9)
# 只返回统计显著的相关性（p < 0.01）
```

## 导出格式

### 基础版本
- `nc_exposome_kg.nt` - N-Triples RDF格式
- `nc_exposome_triples.csv` - CSV格式三元组
- `nc_exposome_data.csv` - 原始数据表

### ✨ 增强版本 (Ontology-Enhanced)
- `nc_exposome_kg_ontology.ttl` - Turtle格式 (带完整ontology映射)
- `nc_exposome_kg_ontology.nt` - N-Triples格式 (带完整ontology映射)
- `nc_exposome_kg_ontology.rdf` - RDF/XML格式
- `SPARQL_EXAMPLES.md` - 28个示例SPARQL查询
- 查看 [`ONTOLOGY_ENHANCEMENT.md`](ONTOLOGY_ENHANCEMENT.md) 了解详情

## 统计信息

运行后包含：
- ~300个三元组（Location + Indicator定义）
- ~1500个测量三元组（带数据来源和置信度）
- ~30个相关性三元组（带p-value和统计显著性）
- 100个县 × 15个指标 = 1500个数据点

### 证据质量分布
- **高置信度** (0.9-1.0): Census官方数据 (~60%)
- **中置信度** (0.7-0.9): CDC数据、统计显著相关性 (~30%)
- **低置信度** (0.5-0.7): 示例/推断数据 (~10%)

## 技术栈

- Python 3.9+
- Pandas: 数据处理
- Matplotlib/Seaborn: 可视化
- Scikit-learn: 聚类分析

## 许可证

MIT License
