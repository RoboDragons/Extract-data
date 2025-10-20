# Extract-data
説明書：
https://docs.google.com/presentation/d/1mYKmMry_S_inGERtIFB3dyAUrgqKzL2KXuPlgpXNPPI/edit?usp=sharing
## 概要
このリポジトリは、ロボカップのようなロボットサッカーの試合データを抽出・（可視化）するためのツールセットです。Pythonとシェルスクリプトを活用し、試合ログの再生やデータ収集、（可視化作業）を自動化します。RoboCup Small Size League（SSL）のツールと連携し、研究やチーム開発に貢献します。

## セットアップ

1. リポジトリをクローン  
   `git clone git@github.com:RoboDragons/Extract-data.git`
2. セットアップスクリプトを実行  
   `sh setup.sh`

## 使い方
1. `prepare.sh` を実行しAutoRef と logtool を起動  
   ※logtoolのログ保存パスに注意  
2. logtoolでログを再生しながら，Pythonファイルを実行してデータを取得

### 参考ツール
- 試合再生: [ssl-logtools](https://github.com/RoboCup-SSL/ssl-logtools)
- 可視化:  
　- [AutoReferee (TIGERs-Mannheim)](https://github.com/TIGERs-Mannheim/AutoReferee)
  - [ssl-vision](https://github.com/RoboCup-SSL/ssl-vision)  
  
## 特徴・技術

- PythonとShellによる自動化スクリプト
- RoboCup-SSL公式ツールとの連携
- データ抽出・解析・（可視化)の効率化

---

ご質問や改善提案はIssueまたはPull Requestでお知らせください。
