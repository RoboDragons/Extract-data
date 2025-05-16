---
name: Feature request
about: Suggest an idea for this project
title: ''
labels: ''
assignees: ''

---

name: 💡 機能リクエスト
description: 新機能のアイデアを提案する
labels: ["enhancement"]
body:
  - type: markdown
    attributes:
      value: |
        機能の提案ありがとうございます。以下の情報を記入してください。

  - type: textarea
    id: problem
    attributes:
      label: 関連する問題
      description: この機能リクエストに関連する問題を説明してください
      placeholder: 例）〜の操作が面倒です
    validations:
      required: true

  - type: textarea
    id: solution
    attributes:
      label: 提案する解決策
      description: 考えられる解決策を説明してください
    validations:
      required: true

  - type: textarea
    id: alternatives
    attributes:
      label: 代替案
      description: 検討した他の解決策があれば記述してください
    validations:
      required: false

  - type: textarea
    id: additional
    attributes:
      label: その他の情報
      description: スクリーンショットや参考資料などがあれば追加してください
    validations:
      required: false
