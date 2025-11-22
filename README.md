# svn_cmd_tool

SVNコマンドでよく使う処理をまとめる
- Pythonで実装する
- pipでインストールしてモジュールとして使用する
- SVNはコマンドで実行する

## install
```
pip install git+https://github.com/city-bridge/svn_cmd_tool.git
```

## 使用方法

### sample code
```python
from svn_cmd_tool import SvnCheckoutManager, SvnCheckoutControl, SvnExportControl
from svn_cmd_tool.svn_cmd import svn_list

# SvnCheckoutManagerのインスタンスを作成
manager = SvnCheckoutManager()

# 1. 直接的な制御オブジェクト作成と追加
checkout_control = SvnCheckoutControl("main_trunk", "https://svn.example.com/repo/trunk", "/workspace/project1")
export_control = SvnExportControl("stable_release", "https://svn.example.com/repo/tags/v1.0", "/release/project1-v1.0", True)

manager.appendControl(checkout_control)
manager.appendControl(export_control)

# 2. SVNサーバから子ディレクトリのリストを取得して、最後のディレクトリをエクスポート
parent_url = "https://svn.example.com/repo/tags/"
try:
    directories = svn_list(parent_url)
    if directories:
        last_directory = directories[-1].rstrip('/')
        export_url = parent_url + last_directory
        print(f"最後のディレクトリを発見: {last_directory}")
        
        manager.appendControl(SvnExportControl(
            f"latest_{last_directory}",
            export_url,
            f"/release/project1-{last_directory}"
        ))
    else:
        print("子ディレクトリが見つかりませんでした")
except Exception as e:
    print(f"ディレクトリリスト取得エラー: {e}")

# 3. JSON設定ファイルからの読み込み
try:
    json_manager = SvnCheckoutManager()
    json_manager.load_from_json("config.json")
    print(f"JSON設定から{json_manager.count()}個の制御オブジェクトを読み込み")
except Exception as e:
    print(f"JSON読み込みエラー: {e}")

# 4. 辞書データからの直接読み込み
config_dict = {
    "controls": [
        {
            "name": "dynamic_checkout",
            "type": "checkout",
            "repository_url": "https://svn.example.com/dynamic",
            "target_path": "/workspace/dynamic"
        },
        {
            "name": "dynamic_export",
            "type": "export",
            "repository_url": "https://svn.example.com/dynamic/tags/latest",
            "target_path": "/release/dynamic-latest",
            "force_overwrite": True
        }
    ]
}

dict_manager = SvnCheckoutManager()
dict_manager.load_from_dict(config_dict)
print(f"辞書設定から{dict_manager.count()}個の制御オブジェクトを読み込み")

# 5. 名前による制御オブジェクトの管理
print(f"登録された制御オブジェクト名: {manager.get_control_names()}")
print(f"総制御オブジェクト数: {manager.count()}")

# 名前で制御オブジェクトを取得
control = manager.get_control_by_name("main_trunk")
if control:
    print(f"'main_trunk'制御オブジェクト: {control}")

# 名前の存在確認
exists = manager.has_control_name("main_trunk")
print(f"'main_trunk'の存在: {exists}")

# 6. 実行方法の選択
try:
    # 特定の名前のみ実行
    manager.update_by_name("main_trunk")
    print("メインプロジェクトのチェックアウトが完了")
    
    # 全ての制御オブジェクトを一括実行
    manager.update()
    print("すべてのリポジトリの処理が完了")
    
except Exception as e:
    print(f"実行エラー: {e}")
```

### JSON設定ファイル例
```json
{
  "controls": [
    {
      "name": "main_project",
      "type": "checkout",
      "repository_url": "https://svn.example.com/repo/trunk",
      "target_path": "/workspace/project1"
    },
    {
      "name": "stable_release",
      "type": "export",
      "repository_url": "https://svn.example.com/repo/tags/v1.0",
      "target_path": "/release/project1-v1.0",
      "force_overwrite": true
    },
    {
      "name": "latest_release",
      "type": "export", 
      "parent_url": "https://svn.example.com/repo/tags/",
      "target_path": "/release/project1-latest",
      "force_overwrite": false
    }
  ]
}
```

## 機能

### svn_cmd_tool/svn_cmd.py
- subprocessを使ってSVNコマンドをラップした関数
  - SVNチェックアウト
  - SVNエクスポート
  - SVNアップデート

### svn_cmd_tool/svn_checkout_control.py
- SvnCheckoutControlクラスを作成
  - SVNリポジトリとチェックアウト先の関係設定を保持
  - 設定に従ってSVNコマンドを管理する
  - 機能
    - チェックアウト未実行の場合はチェックアウトを実行する
    - 既存のワーキングコピーがある場合はアップデートを実行する

### svn_cmd_tool/svn_export_control.py
- SvnExportControlクラスを作成（基底クラス）
  - SVNリポジトリとエクスポート先の関係設定を保持
  - 設定に従ってSVNエクスポートコマンドを管理する
  - 機能
    - .svnディレクトリを含まない純粋なソースコードのコピーを作成
    - 指定されたパスから直接エクスポート
    - 既存のディレクトリがある場合は上書きまたはスキップ
    - エクスポート完了後に全ファイルを読み込み専用に設定
    - 読み込み専用設定により意図しない編集を防止

### svn_cmd_tool/svn_checkout_manager.py
- SvnCheckoutManagerクラスの作成
  - SvnCheckoutControl、SvnExportControlのリストを保持し、一斉に実行する
  - チェックアウトとエクスポートを混在して管理可能
  - JSON設定ファイルからの一括設定読み込み
  - 辞書データからの直接設定読み込み
  - 名前付き設定による個別制御オブジェクト管理
  - 特定の名前を指定した個別実行機能

### 共通
- 結果の出力はloggingモジュールのloggerを使用する
- 例外はraiseを使用する

