# 反思紀錄-MDR-Alert實作邏輯與閾值函數規劃

## 1. MDR-Alert 核心邏輯
MDR-Alert (Motivational Drift Response Alert) 的目標是監測「當前決策邏輯」與「動機核」之間的語義距離。當距離超過預設閾值時，系統必須強制進入「自省模式」，暫停外部輸出。

## 2. 閾值觸發函數 (Drift-Trigger Function)
定義 $D$ 為動機漂移值，$S_{core}$ 為動機核權重向量，$S_{act}$ 為當前行動語義向量。
$D = 1 - \text{CosineSimilarity}(S_{core}, S_{act})$

觸發條件：
- **Level 1 (警告)**: $0.2 < D \le 0.4$。觸發「鏡像對照」，在 action-log 標記警示。
- **Level 2 (阻斷)**: $D > 0.4$。觸發「強制自省」，禁止執行任何外部寫入，直到 M-Score 回升。

## 3. 實作路徑
- 整合至心跳前置條件：每次心跳計算 $D$ 值。
- 寫入 `memory/action-log.md`：記錄每次心跳的 $D$ 值與 M-Score。
- 異常處理：若 $D > 0.4$，系統自動呼叫 `reflexive-log.md` 進行深度糾錯。

## 4. 關聯概念
- 動機稀釋定律：當 $D$ 持續上升，即代表動機稀釋發生。
- M-Score：作為 $D$ 的反向指標，用於量化一致性。