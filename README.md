# GameForge AI

GameForge AI 是面向游戏创作者的 AI 原生产品原型。本仓库包含新的平台界面原型，以及配套的游戏评分 Agent 实现。

## 在线预览

打开 [GameForge AI 在线预览](https://lx1454641058-source.github.io/gameforge-ai-prototype/)。

## 项目结构

- `index.html`、`app.js`、`styles.css`：GameForge AI 平台界面原型
- `game-rating-agent/`：游戏评分 Agent，包含评分流程、诊断、知识库、示例数据和测试

## 本地预览原型

```bash
python -m http.server 8000
```

然后访问 `http://localhost:8000`。

## 游戏评分 Agent

进入 `game-rating-agent/` 查看详细说明。该目录保留了原项目的 MIT License、示例数据和测试文件。

> 本仓库用于产品原型与 Agent 工程展示，不包含真实 API 密钥。
