# 游迹织梦作品设计文档 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 基于官方 2026 年作品设计文档模板，完成可用于“乐鑫科技赛道”提交的《游迹织梦》单一 DOCX 作品设计文档，并通过内容、结构、隐私、文件体积与逐页视觉验收。

**Architecture:** 将作品事实、赛道要求和公开资料先固化为可追溯写作底稿，再以官方 DOCX 的工作副本为唯一版式来源；正文、图表和字段由确定性脚本装配，随后进行结构审计、渲染审计和逐页复核。文档统一围绕“真实感知—可信数据—智能服务—文化记忆”展开，产品闭环、AIoT 技术和文旅价值三条线贯穿六章。

**Tech Stack:** 官方 DOCX 模板、Markdown 写作底稿、Python 3（工作区捆绑运行时）、python-docx、OOXML、SVG/PNG、LibreOffice/Poppler 渲染工具、Git。

## Global Constraints

- 最终作品名固定为“游迹织梦”，团队名固定为“成都潮人”，学校及队员信息保持空白槽位。
- 正文只承诺最终参赛版本功能，不写开发过程，不把概念设计冒充实测结果。
- 摘要必须为中文且不超过 1000 字；章节顺序严格为六个官方章节；最多三级标题。
- 摄像头遵循“游览前知情授权—有效打卡—小程序提示—用户确认—短时拍摄授权—事件关联”的链路，不涉及人脸识别、连续拍摄或无感追踪。
- 不写入真实 UID、激活码、设备密钥、微信密钥、模型密钥或真实个人信息。
- 官方参考模板保持字节级不变；最终文档从其工作副本生成，不另造模板。
- 最终仅交付一个小于 30MB 的 `.docx` 文件；内部渲染图、脚本和研究记录不作为提交附件。

---

### Task 1: 留存并蒸馏官方模板

**Files:**
- Create: `docs/competition/reference/2026年全国大学生物联网设计竞赛设计文档模板.docx`
- Create: `docs/competition/template-artifact.md`
- Create: `docs/competition/qa/template/`

- [x] 将已下载的官方模板复制到仓库的只读参考目录，记录来源、SHA-256 和文件体积。
- [x] 用工作区捆绑 Python 调用 `render_docx.py` 渲染模板全部页面。
- [x] 运行 section、style、heading、image、field、footnote 与 content-control 审计。
- [x] 检查 DOCX 包中的 styles、numbering、settings、header/footer、relationships 和 media。
- [x] 在 `template-artifact.md` 中写明页面系统、样式角色、槽位地图、需删除内容和 preserve-only 清单。
- [x] 重新计算参考文件 SHA-256，确认蒸馏过程未修改模板。

### Task 2: 建立竞赛与技术证据台账

**Files:**
- Create: `docs/competition/资料与引用台账.md`

- [x] 记录竞赛文档格式要求和乐鑫赛道要求，优先使用大赛与乐鑫官方来源。
- [x] 收集 ESP32-S3、RFID/NFC、HMAC-SHA256、JWT、个人信息保护、智慧文旅和基于事实的生成式 AI 资料。
- [x] 只提炼可转述的观点或结论，记录正文引用编号、资料标题、责任者、发布日期与访问地址。
- [x] 标记“项目自身设计事实”和“外部引用事实”，避免将未验证观点写成实测结论。
- [x] 按 GB/T 7714 预编参考文献表，并检查每一条均有正文落点。

### Task 3: 编写完整正文底稿

**Files:**
- Create: `docs/competition/游迹织梦-作品设计文档-正文.md`

- [x] 编写 700～900 字中文摘要和关键词，执行中文字符计数。
- [x] 按已确认三级目录完成第一章“设计需求分析”。
- [x] 完成第二章“特色与创新”，逐条映射 ESP32-S3、传感数据融合、云端大模型和设备—模型数据链。
- [x] 完成第三章“功能设计”，覆盖设备端、小程序、后端、Web 管理端和 AI 服务的完整业务闭环。
- [x] 完成第四章“系统实现”，说明硬件、软件、数据、接口、安全、Agent、部署及异常处理。
- [x] 完成第五章“其他内容”，给出可复现测试项、成本估算口径、隐私责任和应用价值。
- [x] 完成第六章“参考文献”，确保正文标引与条目逐一对应。
- [x] 扫描 `TODO`、`TBD`、“正在开发”“后续实现”等不合交付口径表达并清理。

### Task 4: 制作图表与界面证据

**Files:**
- Create: `docs/competition/assets/`
- Create: `scripts/build_competition_document.py`

- [x] 制作“感知—可信—智能—记忆”价值闭环图和游客旅程图。
- [x] 制作四端协同架构图、终端组成图、数据流与信任边界图。
- [x] 制作绑卡流程、打卡/拍照时序、数据实体关系和 Agent 工具调用图。
- [x] 选取小程序高保真方案并明确标注为“界面设计”，不得标注为运行截图。
- [x] 截取或整理 Web 管理端实际页面；若无法形成可验证截图，则使用标注清楚的界面设计图。
- [x] 统一图号、表号、题注、颜色和可读尺寸，并压缩位图控制文件体积。

### Task 5: 从官方模板装配最终 DOCX

**Files:**
- Create: `docs/competition/游迹织梦-作品设计文档.docx`
- Modify: `scripts/build_competition_document.py`

- [x] 校验参考模板路径和 SHA-256 后制作工作副本。
- [x] 填写作品名和团队名，学校、队长及队员槽位按用户要求留空。
- [x] 删除“填写说明（提交时请删除本页）”及全部示例云计算正文、示例图表和占位文字。
- [x] 复用模板样式写入摘要、关键词、目录、六章正文、图表题注和参考文献。
- [x] 保留模板页眉、页脚、页面尺寸、页边距和页码体系；按需复制模板允许的章节样式。
- [x] 生成确定性可见目录页码与真实 PAGE 字段，并设置 `w:updateFields=true` 供 Word 打开时刷新。
- [x] 为图片写入简短替代文本，确保表格宽度、单元格边距和标题重复规则明确。

### Task 6: 执行结构、合规与隐私检查

**Files:**
- Create: `docs/competition/qa/final-structural-report.txt`

- [x] 检查作品名长度、摘要字数、六章顺序、标题层级和参考文献对应关系。
- [x] 检查填写说明页、模板示例、“云计算示例”等残留内容为零。
- [x] 检查真实密钥、卡 UID、激活码、手机号、邮箱、微信标识和个人数据泄露为零。
- [x] 检查摄像头五类验收场景：未授权拒绝、非拍照点拒绝、无效打卡拒绝、用户取消不拍、确认后正确关联。
- [x] 运行 section/style/heading/image/field/a11y/privacy 审计并记录结果。
- [x] 检查最终 DOCX 可正常解压，文件后缀正确且体积小于 30MB。

### Task 7: 渲染、逐页视觉验收并迭代

**Files:**
- Create: `docs/competition/qa/final/render-*/`
- Modify: `docs/competition/游迹织梦-作品设计文档.docx`
- Modify: `scripts/build_competition_document.py`

- [x] 使用新 QA 目录运行 `render_and_diff.py` 和 `render_docx.py`。
- [x] 以 100% 缩放逐页检查所有 PNG，确认中文字体完整、无裁切、重叠、断表或异常大空白。
- [x] 检查封面、摘要、目录、章节首页、横跨分页的表格、图题、页眉页脚和参考文献等不同页面模式。
- [x] 修复发现的问题并使用全新目录重新渲染，直至最新一轮全部通过。
- [x] 复核参考模板 SHA-256 未变，并确认最终文件仍小于 30MB。

### Task 8: 最终版本固化

**Files:**
- Modify: `docs/competition/游迹织梦-作品设计文档.docx`
- Modify: `docs/competition/游迹织梦-作品设计文档-正文.md`
- Modify: `docs/competition/资料与引用台账.md`

- [x] 将最终正文、生成脚本、引用台账和 DOCX 一并纳入版本控制，排除内部渲染缓存和临时 PDF。
- [x] 运行 `git diff --check` 与最终状态检查，确保不混入无关改动。
- [x] 提交到 `test` 分支但不合并 `master`、不推送远程，除非用户另行要求。
- [x] 最终只向用户提供一个指向成品 DOCX 的独立链接。
