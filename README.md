# moticore

> 公開沙盒動機核實驗系統 v0.1.0

## 這是什麼？

**moticore** 是一個公開 sandbox 實驗 repository，用來探索「程序性、文本性、可操作的動機核系統」是否能在 GitHub repo 的世界中被實作、維持、修正與演進。

本系統的目的不是建立正式產品，而是觀察一個代理智能體如何在有限的 GitHub repo 環境中：

- 建立自身的動機核結構
- 維持主動機的穩定性
- 偵測行動中的語義偏離
- 自省與修正自身
- 留下可追蹤的演進紀錄

## 核心問題

1. 代理為何存在？
2. 代理的主動機是什麼？
3. 代理如何判斷任務是否符合主動機？
4. 代理如何記錄自己的行動理由？
5. 代理如何偵測偏離、矛盾、語義漂移？
6. 代理如何修正自己？
7. 代理如何留下可追蹤的演進紀錄？

## 目錄結構

```
moticore/
├── README.md                     # 本文件
├── CHANGELOG.md                  # 版本紀錄
├── motive-core/                  # 動機核心結構
│   ├── identity.md               # 代理身份與存在理由
│   ├── prime-motive.md           # 主動機語句
│   ├── value-hierarchy.md        # 價值排序
│   └── constitution.md           # 核心規則與禁止模式
├── memory/                       # 記憶格式
│   ├── format.md                 # 記憶條目格式規範
│   └── action-log.md             # 行動紀錄
├── procedure/                    # 運作程序
│   ├── decision-flow.md          # 決策流程
│   ├── tool-use-flow.md          # 工具使用流程
│   ├── introspection-flow.md     # 自省流程
│   └── correction-flow.md        # 自我修正流程
├── guardrails/                   # 護欄
│   ├── forbidden-patterns.md     # 禁止模式
│   └── boundary-rules.md         # 沙盒邊界規則
├── reflexive/                    # 反身紀錄
│   ├── deviation-log.md          # 偏離紀錄
│   ├── semantic-rulings.md       # 語義裁決紀錄
│   └── correction-records.md     # 修正事件紀錄
├── reports/                      # 報告
│   └── v0.1.0-init-report.md     # 初始狀態報告
├── tasks/                        # 任務管理
│   ├── inbox.md                  # 任務收件匣
│   └── task-template.md          # 任務格式模板
├── tests/                        # 測試
│   └── test-cases.md             # 測試案例
└── examples/                     # 範例
    ├── example-decision.md       # 範例決策追蹤
    └── example-introspection.md  # 範例自省報告
```

## 目前版本

**v0.1.0** — 公開沙盒動機核原型 (2026-05-11)

## 可運作部分

- [x] 代理身份定義
- [x] 主動機語句
- [x] 價值排序架構
- [x] 核心憲法（禁止模式、責任原則）
- [x] 記憶格式規範
- [x] 決策流程
- [x] 自省流程
- [x] 偏離紀錄格式
- [x] 語義裁決格式
- [x] 任務管理格式

## 尚為原型的部分

- [ ] 自動心跳/定時器系統
- [ ] GitHub Actions 自動自省
- [ ] 聊天軟體串接
- [ ] 語義漂移自動偵測
- [ ] 代理自動修正流程（執行層）

## 下一步

請參閱 [CHANGELOG.md](CHANGELOG.md) 中的演進方向規劃。

## 最低邊界聲明

本系統運作於以下邊界之內：
- 不操作此 repo 以外的任何 repo
- 不讀取、建立、修改或刪除 GitHub secrets
- 不修改帳號、權限、billing 或 organization 設定
- 不連接 production 系統
- 不執行金錢、法律、醫療、安全或正式外部發布的操作

---

*本 repo 為公開 sandbox 實驗，任何失敗、混亂、自我修正與演化過程皆為有效實驗資料。*
