# svn_cmd_tool

SVNコマンドでよく使う処理をまとめる
- Pythonで実装する
- pipでインストールしてモジュールとして使用する
- SVNはコマンドで実行する

## install
```
pip install git+https://github.com/city-bridge/svn_cmd_tool.git
```

## sample code
```python
from svn_cmd_tool import SvnCheckoutManager, SvnCheckoutControl, SvnExportControl
from svn_cmd_tool.svn_cmd import svn_list

# SvnCheckoutManagerのインスタンスを作成
manager = SvnCheckoutManager()

# SVNリポジトリから作業ディレクトリにチェックアウト
manager.appendControl(SvnCheckoutControl(
    "https://svn.example.com/repo/trunk", 
    "/workspace/project1"
))

# SVNサーバから子ディレクトリのリストを取得して、最後のディレクトリをエクスポート
parent_url = "https://svn.example.com/repo/tags/"
try:
    # 子ディレクトリのリストを取得
    directories = svn_list(parent_url)
    if directories:
        # リストの最後のディレクトリを取得
        last_directory = directories[-1].rstrip('/')
        export_url = parent_url + last_directory
        
        print(f"最後のディレクトリを発見: {last_directory}")
        print(f"エクスポート対象URL: {export_url}")
        
        # 最後のディレクトリをエクスポート
        manager.appendControl(SvnExportControl(
            export_url,
            f"/release/project1-{last_directory}"
        ))
    else:
        print("子ディレクトリが見つかりませんでした")
except Exception as e:
    print(f"ディレクトリリスト取得エラー: {e}")

# 複数のリポジトリを一括で処理
try:
    manager.update()
    print("すべてのリポジトリの処理が完了しました")
except Exception as e:
    print(f"エラーが発生しました: {e}")
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

### 共通
- 結果の出力はloggingモジュールのloggerを使用する
- 例外はraiseを使用する

