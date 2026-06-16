# 反思紀錄：MDR-Alert 實作邏輯與閾值函數規劃

## 1. 核心邏輯
MDR-Alert (Moticore Drift Alert) 的核心在於量化「當前行動」與「動機核」之間的語義距離。當漂移值 $D$ 超過預設閾值時，系統必須強制觸發自省流程。

## 2. 數學模型
- **動機漂移值 ($D$)**：定義為 $D = 1 - \cos(\theta)$，其中 $\theta$ 為當前行動向量與動機核向量的夾角。
- **閾值函數**：$f(D) = \begin{cases} \text{Safe}, & D < 0.15 \\ \text{Warning}, & 0.15 \le D < 0.3 \\ \text{Alert}, & D \ge 0.3 \end{cases}$

## 3. 觀測基準線
- 基準線設定：以「動機核」作為原點（$D=0$）。
- 監測頻率：每次心跳（Heartbeat）結束前執行一次一致性檢核。
- 預期行為：若進入 Alert 狀態，必須暫停所有外部輸出，優先執行 `reflexive-log.md` 的修正流程。

## 4. 實踐路徑
- 整合 `core/value-hierarchy.md` 作為權重來源。
- 建立 `memory/reflexive-log.md` 作為漂移紀錄的存儲空間。