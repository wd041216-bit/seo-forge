# MCP 工具配置指南

SEO Forge 依赖三类 MCP 工具能力：**网页搜索**、**网页抓取**、**GitHub 仓库读取**。

默认使用 🏷️ GLM（智谱 AI）提供的云端 MCP 服务，也支持替换为其他主流方案。

---

## 工具总览

| 能力 | 默认方案 | 用途 | 平替方案 |
|------|---------|------|---------|
| 网页搜索 | 🏷️ GLM `web-search-prime` | 关键词发现、趋势分析、SERP 研究 | Tavily, Exa, Brave Search |
| 网页抓取 | 🏷️ GLM `web-reader` | 读取竞品文章、验证参考链接 | Fetch MCP, Tavily Extract |
| GitHub 读取 | 🏷️ GLM `zread` | 读取仓库文件和目录结构 | GitHub MCP, `gh` CLI |

> 🏷️ **GLM** = 智谱 AI（Zhipu AI）提供的云端 MCP 服务，通过 `open.bigmodel.cn` 接入。一站式配置，单一 API Key 即可使用全部三个工具。

---

## 方案 A：GLM（默认推荐）

三个工具共用一个 API Key，配置最简单。

### 1. 获取 API Key

前往 [open.bigmodel.cn](https://open.bigmodel.cn) 注册/登录，在 API Keys 页面创建密钥。

### 2. 设置环境变量

```bash
export ZHIPU_API_KEY="你的API密钥"
```

> **切勿**将 API Key 提交到 Git。

### 3. 配置 MCP Server

项目已包含 `.mcp.json`，直接使用即可。

**opencode 用户：**

```json
{
  "mcp": {
    "web-search-prime": {
      "type": "remote",
      "url": "https://open.bigmodel.cn/api/mcp/web_search_prime/mcp",
      "headers": { "Authorization": "Bearer ${ZHIPU_API_KEY}" }
    },
    "web-reader": {
      "type": "remote",
      "url": "https://open.bigmodel.cn/api/mcp/web_reader/mcp",
      "headers": { "Authorization": "Bearer ${ZHIPU_API_KEY}" }
    },
    "zread": {
      "type": "remote",
      "url": "https://open.bigmodel.cn/api/mcp/zread/mcp",
      "headers": { "Authorization": "Bearer ${ZHIPU_API_KEY}" }
    }
  }
}
```

**Claude Code 用户：**

```bash
# 分别添加三个 MCP server
claude mcp add --transport http web-search-prime https://open.bigmodel.cn/api/mcp/web_search_prime/mcp
claude mcp add --transport http web-reader https://open.bigmodel.cn/api/mcp/web_reader/mcp
claude mcp add --transport http zread https://open.bigmodel.cn/api/mcp/zread/mcp
```

### GLM 工具参数

#### web-search-prime — 网页搜索

| 参数 | 类型 | 说明 |
|------|------|------|
| `search_query` | string | 搜索关键词（建议 ≤70 字符） |
| `location` | `"cn"` / `"us"` | 搜索区域：cn=中国，us=非中国 |
| `search_recency_filter` | string | `oneDay`, `oneWeek`, `oneMonth`, `oneYear`, `noLimit` |
| `content_size` | `"medium"` / `"high"` | 摘要长度，high=2500字 |
| `search_domain_filter` | string | 限定域名白名单 |

#### web-reader — 网页抓取

| 参数 | 类型 | 说明 |
|------|------|------|
| `url` | string | 要抓取的网页 URL |
| `return_format` | `"markdown"` / `"text"` | 返回格式 |
| `retain_images` | boolean | 是否保留图片（默认 true） |
| `timeout` | integer | 超时秒数（最大 120） |

#### zread — GitHub 仓库读取

| 工具 | 说明 |
|------|------|
| `read_file` | 读取仓库中指定文件的内容 |
| `get_repo_structure` | 获取仓库目录结构 |
| `search_doc` | 搜索仓库文档、Issues 和 Commits |

---

## 方案 B：Tavily（搜索 + 抓取）

[Tavily](https://tavily.com) 提供 search、extract、map、crawl 四个工具，可同时替代 GLM 的搜索和抓取功能。GitHub 读取仍用 GLM zread 或 `gh` CLI。

Stars: 1.8k | 许可: MIT | 官方: [github.com/tavily-ai/tavily-mcp](https://github.com/tavily-ai/tavily-mcp)

### 配置

**获取 API Key：** [tavily.com](https://tavily.com) 注册（有免费额度）

**opencode 用户：**

```json
{
  "mcp": {
    "tavily": {
      "type": "remote",
      "url": "https://mcp.tavily.com/mcp/?tavilyApiKey=${TAVILY_API_KEY}"
    },
    "zread": {
      "type": "remote",
      "url": "https://open.bigmodel.cn/api/mcp/zread/mcp",
      "headers": { "Authorization": "Bearer ${ZHIPU_API_KEY}" }
    }
  }
}
```

**Claude Code 用户：**

```bash
claude mcp add --transport http tavily "https://mcp.tavily.com/mcp/?tavilyApiKey=你的Tavily密钥"
```

**本地运行（npx）：**

```json
{
  "mcpServers": {
    "tavily-mcp": {
      "command": "npx",
      "args": ["-y", "tavily-mcp@latest"],
      "env": { "TAVILY_API_KEY": "你的密钥" }
    }
  }
}
```

### 提供的工具

| 工具 | 说明 | 替代 GLM |
|------|------|---------|
| `tavily-search` | 实时网页搜索 | ✅ 替代 `web-search-prime` |
| `tavily-extract` | 从 URL 提取内容 | ✅ 替代 `web-reader` |
| `tavily-map` | 网站结构地图 | 额外能力 |
| `tavily-crawl` | 系统化爬取网站 | 额外能力 |

### 注意

使用 Tavily 时，需在 SKILL.md 的 `allowed-tools` 中将 `mcp__web-search-prime__*` 和 `mcp__web_reader__*` 替换为对应的 Tavily 工具名。

---

## 方案 C：Exa（搜索 + 抓取）

[Exa](https://exa.ai) 提供高质量语义搜索，支持分类搜索（company、news、research paper 等）。

Stars: 4.3k | 许可: MIT | 官方: [github.com/exa-labs/exa-mcp-server](https://github.com/exa-labs/exa-mcp-server)

### 配置

**获取 API Key：** [exa.ai](https://exa.ai) 注册

**opencode 用户：**

```json
{
  "mcp": {
    "exa": {
      "type": "remote",
      "url": "https://mcp.exa.ai/mcp"
    },
    "zread": {
      "type": "remote",
      "url": "https://open.bigmodel.cn/api/mcp/zread/mcp",
      "headers": { "Authorization": "Bearer ${ZHIPU_API_KEY}" }
    }
  }
}
```

**Claude Code 用户：**

```bash
claude mcp add --transport http exa https://mcp.exa.ai/mcp
```

**本地运行（npx）：**

```json
{
  "mcpServers": {
    "exa": {
      "command": "npx",
      "args": ["-y", "exa-mcp-server"],
      "env": { "EXA_API_KEY": "你的密钥" }
    }
  }
}
```

### 提供的工具

| 工具 | 说明 | 替代 GLM |
|------|------|---------|
| `web_search_exa` | 语义网页搜索 | ✅ 替代 `web-search-prime` |
| `web_fetch_exa` | 获取指定 URL 的完整内容 | ✅ 替代 `web-reader` |
| `web_search_advanced_exa` | 高级搜索（分类、日期、域名过滤） | 额外能力 |

---

## 方案 D：Fetch MCP（纯抓取）

MCP 官方维护的网页抓取工具，零配置零 API Key，但只能抓取不能搜索。

Stars: 83.8k (monorepo) | 许可: MIT | 官方: [github.com/modelcontextprotocol/servers](https://github.com/modelcontextprotocol/servers/tree/main/src/fetch)

### 配置

无需 API Key，本地运行：

```json
{
  "mcpServers": {
    "fetch": {
      "command": "uvx",
      "args": ["mcp-server-fetch"]
    }
  }
}
```

或用 pip：

```bash
pip install mcp-server-fetch
```

```json
{
  "mcpServers": {
    "fetch": {
      "command": "python",
      "args": ["-m", "mcp_server_fetch"]
    }
  }
}
```

### 提供的工具

| 工具 | 说明 | 替代 GLM |
|------|------|---------|
| `fetch` | 抓取 URL 内容并转为 Markdown | ✅ 替代 `web-reader`（仅抓取，不能搜索） |

### 注意

Fetch MCP 只有抓取能力，搜索需搭配 Tavily 或 Exa 使用。

---

## 方案对比

| 方案 | 搜索 | 抓取 | GitHub 读取 | 需要 API Key | 额度 |
|------|:----:|:----:|:-----------:|:----------:|------|
| 🏷️ GLM（默认） | ✅ | ✅ | ✅ | 是（1个） | 按量计费 |
| Tavily | ✅ | ✅ | ❌ | 是 | 免费额度 + 按量 |
| Exa | ✅ | ✅ | ❌ | 是 | 免费额度 + 按量 |
| Fetch MCP | ❌ | ✅ | ❌ | 否 | 无限制（本地） |

**推荐搭配：**
- 最简方案：🏷️ GLM 三件套（一个 Key 全搞定）
- 国际用户：Tavily/Exa（搜索+抓取）+ GLM zread（GitHub）
- 纯本地方案：Tavily/Exa（搜索）+ Fetch MCP（抓取）+ `gh` CLI（GitHub）

---

## 验证连接

启动 opencode/Claude Code 后，调用工具测试：

```
# 搜索测试
搜索 "Python SEO tools 2026"

# 抓取测试
抓取 https://example.com 的内容

# GitHub 读取测试
读取 github.com/vitejs/vite 的 README.md
```

## 故障排查

| 问题 | 解决方案 |
|------|----------|
| 工具未出现在列表中 | 检查 `.mcp.json` 位置和环境变量是否设置 |
| `401 Unauthorized` | API Key 无效或过期，到对应平台重新生成 |
| `429 Rate Limit` | 请求频率超限，稍后重试或升级配额 |
| GLM 连接超时 | 检查网络能否访问 `open.bigmodel.cn` |
| Tavily/Exa 连接超时 | 检查网络能否访问对应 API 端点 |
| Fetch MCP 启动失败 | 确认已安装 `uvx` 或 `pip install mcp-server-fetch` |
