请帮我把这个公开仓库里的 skills 安装到这台电脑的 Codex：
https://github.com/spotify2junkie/codex-skill-kit

先读取 README.md 和 BOOTSTRAP.md，再完成安装与验证，不要只给我教程。

1. 安装 pstack-for-codex、lark-work 和 reading-notes，保留已有 Codex 配置、skills、插件与公司规则。检查同名 marketplace/skills 冲突，不直接覆盖。
2. reading-notes 的全部 4 个 skills 及其脚本、features、references 一并安装，包括 verify-obsidian-notes。不要迁移或寻找旧笔记、创建 vault；笔记的承载形式和目标位置等我确定后再适配。
3. 检查 Codex plugin 命令、Node.js、Bun、gh、lark-cli，以及阅读流程的 Python 3.10+、Poppler、ImageMagick、浏览器和 PDF 能力。沿用公司现有工具；缺少的依赖按仓库文档和公司规则处理，说明哪些功能需要它们。
4. 不复制旧电脑登录态，不读取或展示密钥。飞书首次使用时再引导我配置公司身份；需要我登录或授权的步骤明确告诉我。
5. 不固定 agent 模型，不创建或启动自动化，不替换全局 AGENTS.md。
6. 安装后用 codex plugin list --json 核对插件、检查包内 skills 和依赖资源，并告诉我哪些已验证、哪些尚待登录或新任务验证。提醒我新建任务刷新 skills。
