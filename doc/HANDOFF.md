# GeoVigil Analytics — Handoff Note

> 次スレッド（コンテキスト引き継ぎ用）の作業開始ガイド。
> 背景・理由は [CONCEPT_NOTE.md](CONCEPT_NOTE.md)、仕様は [ARCHITECTURE.md](ARCHITECTURE.md) を参照。
> この3点セットを「コアドキュメント」と呼ぶ。

最終更新: 2026-06-30

---

## 直近の決定事項（このスレッドで確定）

1. 前任者モデル（Faster R-CNN、ブラジル178枚）は出発点として使うが、そのままでは実運用不可と評価済み
2. データセット拡充は **Active Learning方式**：既存モデル検出500枚＋NDVI変化検出500枚をスタッフ確認 → 元178枚と合わせて再学習
3. **Sentinel-2の独立YOLOモデルは作らない**。Sentinel-2は変化検出による早期警戒のみ、NICFIが本検出（YOLO、形状判定）を担う
4. ステータス遷移ロジック確定（`active`/`unconfirmed`/`inactive`、優先順位つき）— 詳細は ARCHITECTURE.md の Detection Record Lifecycle
5. **WBF（Weighted Boxes Fusion）はほぼ不要の方向。** Sentinel-2変化検出の出力形式が座標点＋スコアに確定したため、近接マッチングのみで足りる見込み（最終確定は未）
6. Sentinel-2変化検出の候補フィルタ・パラメータ調整方式・学習データ構築フロー（日付例つき）が確定。詳細はCONCEPT_NOTE.md「Sentinel-2変化検出の出力形式と候補フィルタ」参照
7. Sentinel単独検出の信頼度は固定値ではなく**検出ごとの可変信頼度**（較正曲線）に変更
8. **ARCHITECTURE.mdの反映待ち：** Pipeline Execution節・Overview図・Output Format（`source`フィールド）がまだWBF前提の記述のまま。上記5,6,7の確定を受けて更新が必要（次スレッドのタスク1）

---

## 次スレッドでやること（優先順）

### 1. ARCHITECTURE.mdをこのスレッドの決定に合わせて更新
- Overview図の「Ensemble via WBF」、Pipeline Executionのディレクトリ構成（`ensemble.py`）と実行ステップ（「Merge results with WBF」）を、WBFほぼ不要の方針に合わせて修正
- Output Formatの`source`フィールド値（`"Ensemble (Sentinel-2 + Planet)"`）の要否を再検討
- `confidence`フィールドの意味（NICFI検出のモデル信頼度 と Sentinel単独検出の可変信頼度で性質が異なる点）を明記するか検討

### 2. NDVI変化検出ロジックの実装
- 出力形式・候補フィルタ条件・構築フロー（日付例つき）は確定済み（CONCEPT_NOTE.md「Sentinel-2変化検出の出力形式と候補フィルタ」参照）
- 残タスク：対象範囲（ペルー全土 or 試験的に一部地域）、各フィルタの初期パラメータ（NDVI閾値、アスペクト比閾値、直線性の許容残差、最小長さ）
- 直線性・最小長さ・アスペクト比の実装（`skimage.measure.regionprops`, `skimage.morphology.skeletonize`等を想定）

### 3. 既存Faster-RCNNモデルでの推論バッチ実行（構築フロー3a）
- `data/original_files/illegal_runway_detection_training.py` のモデル構造を参照
- 信頼度閾値なしで全検出を出力 → NICFI画像（構築フロー例：2025-06-15）に対して候補500件を抽出
- 学習済み重みファイル（.pth）の所在を確認（前任者から未受領の可能性、ARCHITECTURE.md Pending Items参照）

### 4. スタッフ確認フローの準備
- 1178枚（既存モデル500＋変化検出500＋元178枚）の正誤チェックシート/ツールの用意
- 確認結果フォーマット：画像ID、ソース（NICFI検出/Sentinelトリガー由来）、正誤、必要なら理由メモ
- 変化検出候補500枚（構築フロー2.）の正誤結果は、TP変化量分布から99.9%信頼度で閾値を外挿決定するために使う
- NICFIトリガー確認500枚（構築フロー3b）の正誤結果は、2.の500枚とプール（計1000枚）して99.9%信頼度を再計算し、かつ可変信頼度の較正曲線を作るために使う（CONCEPT_NOTE.md「構築フロー」参照）。パラメータ再調整は1回で打ち切り、反復しない

### 5. YOLO再学習
- 178枚＋確認済み陽性・陰性（既存モデル500＋NICFIトリガー確認500）を合わせてYOLOデータセットを構築（計1178枚）
- 3b由来サンプルには「Sentinelトリガー由来」タグを付与（信頼度算出用ではなく将来のトレーサビリティ目的）
- COCO→YOLO形式変換が必要（`labelme2coco_ada.py` がCOCO変換部分の参考になる）
- NIRバンド込みで学習するかどうか要検討（CONCEPT_NOTE.md「データセット拡充の方針」参照、4バンド画像を活かす案）

---

## 読むべきファイル（前任者データ）

`data/original_files/` 配下：

| ファイル | 内容 | 読了状況 |
|---|---|---|
| `illegal_runway_detection_training.py` | Faster R-CNN訓練コード | 読了 |
| `Faster-RCNN illegal runway detection_model_training_report.pdf` | 訓練レポート（epoch/lr等、コードと一部不一致あり） | 読了 |
| `ReadMe_Illegal_Runway_Dataset.pdf` | データソース・COCOフォーマット・信頼性評価の説明 | 読了 |
| `labelme2coco_ada.py` | Labelme→COCO変換スクリプト | 未読 |
| `shp to tif.pdf` | シェープファイル→TIFF変換手順 | 未読 |
| `dataset.json` | COCOアノテーション本体 | 未読（重いため） |

---

## 確認が必要な未解決事項

- 前任者の学習済みモデル重みファイル（`FRN_30epochs_CompleteDataset_2ndround.pth` 等）を受領しているか
- コード（30 epoch, lr=0.001）とレポート（100 epoch, lr=0.005）のどちらが最終モデルの実際の設定か、前任者に確認できるか
- Planet NICFI GEE APIアクセス、Copernicus Data Space APIの取得状況
