# 配置说明

## 1. CSV列标签

生成的CSV文件包含55个英文列标签。如果需要中文列标签，可以在导出时使用列名映射。

**主要列标签**:
- `name` - 商家名称
- `address` - 地址
- `google_rating` - Google评分
- `google_reviews_total` - Google评论总数
- `linkedin_employee_count` - LinkedIn员工数
- `ai_employees_estimate` - AI估算员工数
- `ai_status` - AI分析状态 (Active/Inactive/Uncertain)
- `overall_confidence` - 总体置信度 (High/Medium/Low)

## 2. Outscraper 配置

根据官方文档 (https://github.com/outscraper/outscraper-python)：

**需要API Key**:
```python
from outscraper import ApiClient
client = ApiClient(api_key='SECRET_API_KEY')
```

**获取API Key**:
1. 访问 https://outscraper.com/
2. 注册账号
3. 在Profile页面创建API key
4. 添加到 `.env` 文件:
   ```
   OUTSCRAPER_API_KEY=your_api_key_here
   ```

**定价**: 约$1/1000次查询 (比Google Maps API便宜97%)

**功能**:
- 完整的Google Maps评论历史（不限于5条）
- Popular times数据
- 更详细的商家属性

## 3. LinkedIn Scraper v3.0+ 配置

已更新到Playwright异步版本。

**安装**:
```bash
pip install linkedin-scraper>=3.1.0 playwright
playwright install chromium
```

**配置 .env**:
```
LINKEDIN_EMAIL=your_email@example.com
LINKEDIN_PASSWORD=your_password
```

**首次使用**:
- 自动创建会话文件 `.linkedin_session.json`
- 之后可重复使用会话，无需每次登录

**注意**: LinkedIn自动化可能违反ToS，仅用于学术研究。

## 4. 完整配置步骤

1. **复制环境变量模板**:
   ```bash
   cp .env.example .env
   ```

2. **编辑 .env 文件，填入API密钥**:
   ```
   OPENAI_API_KEY=sk-your_key_here          # 必需
   GOOGLE_MAPS_API_KEY=AIza_your_key_here  # 必需
   OUTSCRAPER_API_KEY=your_key_here         # 可选（增强功能）
   LINKEDIN_EMAIL=your_email@example.com    # 可选（员工验证）
   LINKEDIN_PASSWORD=your_password          # 可选（员工验证）
   ```

3. **运行测试**:
   ```bash
   python scripts/03_complete_pipeline.py --limit 10
   ```

## 5. 功能状态

| 功能 | 状态 | 依赖 |
|------|------|------|
| Google Maps搜索 | OK | GOOGLE_MAPS_API_KEY (必需) |
| GPT分析 | OK | OPENAI_API_KEY (必需) |
| Wayback验证 | PARTIAL | 无需配置（API格式问题） |
| Outscraper增强 | NEEDS_CONFIG | OUTSCRAPER_API_KEY |
| LinkedIn员工验证 | NEEDS_CONFIG | LINKEDIN_EMAIL + PASSWORD |

## 6. 运行命令

```bash
# 标准运行（所有商家）
python scripts/03_complete_pipeline.py

# 限制数量测试
python scripts/03_complete_pipeline.py --limit 10

# 跳过Wayback（更快）
python scripts/03_complete_pipeline.py --skip-wayback

# 跳过GPT分析（省钱）
python scripts/03_complete_pipeline.py --skip-gpt

# 查看所有选项
python scripts/03_complete_pipeline.py --help
```
