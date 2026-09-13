# 验证记录

快照日期：2026-09-13。测试环境：macOS，Codex CLI 0.153.4，Node.js 20.20.0，Bun 1.3.5。

- 三个插件均通过当前 plugin-creator 的 manifest / skills 校验。
- 在临时 CODEX_HOME 中实际注册 marketplace、安装三个插件、查询 installed/enabled 状态、移除插件和 marketplace。没有复制当前用户认证文件。
- 安装后的全部分发文件与源目录逐文件一致：45 个 P-Stack skills、28 个飞书 skills、3 个阅读 skills。
- 从安装后的 P-Stack 执行可选 agent setup，写入临时项目和临时 user-home；两个模板成功展开，重复安装内容一致。真实用户 agent 配置未改动。
- 阅读验证器：纯 Markdown 测试笔记通过；不存在的附件被正确拒绝。PDF 渲染链路不在本次迁移验证范围。
- P-Stack orchestrator / watch-pr：54 个 Bun 测试通过，TypeScript strict typecheck 通过。
- P-Stack model policy / Benny state machine：17 个 Node 测试通过。
- Obsidian skill 通过 skill-creator 校验；已移除私人 vault 路径和主笔记名称。
- 对分发文件检查常见凭据格式和旧电脑路径，未发现凭据或私人路径。飞书材料中的示例 ID 和 P-Stack 测试中的 `/Users/operator` 是原分发中的示例，不是当前用户资料。

可重复执行：

```bash
python3 scripts/verify_install.py
# 发布后从 GitHub 重新安装验证：
python3 scripts/verify_install.py --source spotify2junkie/codex-skill-kit
```

没有验证公司电脑的网络、账号权限、可用模型，或新 Codex 任务中的运行时 skill 发现。飞书登录/业务 API 未调用。hooks 受信任状态、可选自动化、PDF 产出能力需目标环境按实际请求验证。

`plugins/pstack-for-codex/tests` 中其余测试和上游兼容性记录作为来源资料保留；本迁移版本并未宣称原上游整套 release suite 全部通过。根目录本记录与 `scripts/verify_install.py` 是迁移包的验证入口。
