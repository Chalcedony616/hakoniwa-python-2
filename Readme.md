# 箱庭諸島２ for Python
## 概要
箱庭諸島２ for Pythonは、ブラウザベースのターン制ゲーム「箱庭諸島」をPythonベースで再構築したものです。このゲームのプレイヤーは島を管理し、発展させ、他の島との外交や戦争を行います。
本プロジェクトは、Djangoをバックエンドとして、Reactをフロントエンドとして構築されています。

## ディレクトリ構造
hakoniwa-python-2/
├── hakoniwa_backend/
│   ├── manage.py
│   ├── db.sqlite3
│   ├── hakoniwa_backend/
│   │   ├── __init_.py
│   │   ├── asgi.py
│   │   ├── settings.py
│   │   ├── urls.py
│   │   ├── wsgi.py
│   │   └── __pychache__/
│   │       └── （省略）
│   └── game/
│       ├── __init_.py
│       ├── admin.py
│       ├── apps.py
│       ├── command_data.py
│       ├── commands.py
│       ├── config.py
│       ├── log_messages.py
│       ├── models.py
│       ├── serializers.py
│       ├── terrain_data.py
│       ├── tests.py
│       ├── urls.py
│       ├── utils.py
│       └── views.py
└── hakoniwa_frontend/
    ├── .gitignore
    ├── package-lock.json
    ├── package.py
    ├── README.md
    ├── node_modules/
    │   └── （省略）
    ├── public/
    │   ├── favicon.ico
    │   ├── index.html
    │   ├── logo192.png
    │   ├── logo512.png
    │   ├── manifest.json
    │   ├── robots.txt
    │   └── images/
    │       └── （箱庭諸島で使用する画像ファイル）
    └── src/
        ├── App.css
        ├── App.js
        ├── App.test.js
        ├── commandData.js
        ├── index.css
        ├── index.js
        ├── logo.svg
        ├── prizeData.js
        ├── reportWebVitals.js
        ├── setupTests.js
        ├── terrainData.js
        ├── units.js
        ├── context/
        │   └── LoginContext.js
        └── component/
            ├── AllCountryLog.css
            ├── AllCountryLog.js
            ├── CreateIsland.css
            ├── CreateIsland.js
            ├── CreateUser.css
            ├── CreateUser.js
            ├── DevelopmentView.css
            ├── DevelopmentView.js
            ├── HistoryLog.css
            ├── HistoryLog.js
            ├── Home.css
            ├── Home.js
            ├── IslandsTable.css
            ├── IslandsTable.js
            ├── IslandView.css
            ├── IslandView.js
            ├── Login.css
            └── Login.js