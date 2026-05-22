# CHANGELOG

## v0.1.0 — 公開沙盒動機核原型 (2026-05-11)

### 初始建立

- 建立代理身份定義（`motive-core/identity.md`）
- 建立主動機語句（`motive-core/prime-motive.md`）
- 建立價值排序（`motive-core/value-hierarchy.md`）
- 建立核心憲法（`motive-core/constitution.md`）
- 建立記憶格式規範（`memory/format.md`）
- 建立行動紀錄（`memory/action-log.md`）
- 建立決策流程（`procedure/decision-flow.md`）
- 建立工具使用流程（`procedure/tool-use-flow.md`）
- 建立自省流程（`procedure/introspection-flow.md`）
- 建立自我修正流程（`procedure/correction-flow.md`）
- 建立護欄：禁止模式（`guardrails/forbidden-patterns.md`）
- 建立護欄：沙盒邊界（`guardrails/boundary-rules.md`）
- 建立偏離紀錄初始條目（`reflexive/deviation-log.md`）
- 建立語義裁決初始紀錄（`reflexive/semantic-rulings.md`）
- 建立修正事件初始紀錄（`reflexive/correction-records.md`）
- 建立初始狀態報告（`reports/v0.1.0-init-report.md`）
- 建立任務收件匣（`tasks/inbox.md`）
- 建立任務模板（`tasks/task-template.md`）
- 建立測試案例（`tests/test-cases.md`）
- 建立範例檔案（`examples/`）

### 已知限制

- 系統目前完全依賴人工觸發，無自動執行能力
- 語義偏離偵測為人工程序，非自動化
- 心跳/定時器系統尚未實作

### 下一版本規劃（v0.2.0）

**目標：自動化基礎層**

- [ ] 建立 GitHub Actions workflow，定期執行自省報告
- [ ] 建立 GitHub Issues 作為任務收件匣
- [ ] 建立自動偏離偵測腳本（基於關鍵詞規則）
- [ ] 建立自省報告生成腳本
- [ ] 完成首次自省報告（基於 v0.1.0 行動紀錄）

### 後續可能演進方向（v0.3.0+）

- 聊天軟體串接（Slack / Discord）
- 語義漂移自動偵測（基於 embedding 相似度）
- 代理自動修正流程
- 多代理動機核比較實驗
- 動機核版本差異比對工具
