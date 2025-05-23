# Extract-data

## 概要
このリポジトリは、ロボカップのようなロボットサッカーの試合データを抽出・可視化するためのツールセットです。Pythonとシェルスクリプトを活用し、試合ログの再生やデータ収集、可視化作業を自動化します。RoboCup Small Size League（SSL）エコシステムのツールと連携し、研究やチーム開発に貢献します。

## セットアップ

1. リポジトリをクローン  
   `git clone git@github.com:RoboDragons/Extract-data.git`
2. セットアップスクリプトを実行  
   `sh setup.sh`

## 使い方

1. `prepare.sh` 内で AutoRef と logtool を起動  
   - logtoolのログ保存パスに注意  
   - `prepare.sh` を実行
2. ログを再生しながらPythonファイルを実行してデータを取得

### 参考ツール

- 試合再生: [ssl-logtools](https://github.com/RoboCup-SSL/ssl-logtools)
- データ可視化:  
  - [ssl-vision](https://github.com/RoboCup-SSL/ssl-vision)  
  - [AutoReferee (TIGERs-Mannheim)](https://github.com/TIGERs-Mannheim/AutoReferee)

## 特徴・技術

- PythonとShellによる自動化スクリプト
- RoboCup-SSL公式ツールとの連携
- データ抽出・解析・可視化の効率化

---

ご質問や改善提案はIssueまたはPull Requestでお知らせください。