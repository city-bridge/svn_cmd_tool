"""SVNコマンドをラップした関数群"""

import logging
import subprocess
from pathlib import Path
from typing import List

logger = logging.getLogger(__name__)


def svn_checkout(repository_url: str, target_path: str) -> subprocess.CompletedProcess:
    """
    SVNリポジトリからチェックアウトを実行
    
    Args:
        repository_url (str): SVNリポジトリのURL
        target_path (str): チェックアウト先のパス
        
    Raises:
        subprocess.CalledProcessError: SVNコマンドが失敗した場合
    """
    logger.info("SVNチェックアウト開始: %s -> %s", repository_url, target_path)
    
    cmd = ["svn", "checkout", repository_url, target_path]
    
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        check=True
    )
    
    logger.info("SVNチェックアウト完了: %s", target_path)
    return result


def svn_export(repository_url: str, target_path: str, force: bool = False) -> subprocess.CompletedProcess:
    """
    SVNリポジトリからエクスポートを実行
    
    Args:
        repository_url (str): SVNリポジトリのURL
        target_path (str): エクスポート先のパス
        force (bool): 上書きするかどうか
        
    Raises:
        subprocess.CalledProcessError: SVNコマンドが失敗した場合
    """
    logger.info("SVNエクスポート開始: %s -> %s", repository_url, target_path)
    
    cmd = ["svn", "export", repository_url, target_path]
    if force:
        cmd.append("--force")
    
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        check=True
    )
    
    logger.info("SVNエクスポート完了: %s", target_path)
    return result


def svn_update(working_copy_path: str) -> subprocess.CompletedProcess:
    """
    SVNワーキングコピーを更新
    
    Args:
        working_copy_path (str): ワーキングコピーのパス
        
    Raises:
        subprocess.CalledProcessError: SVNコマンドが失敗した場合
    """
    logger.info("SVNアップデート開始: %s", working_copy_path)
    
    cmd = ["svn", "update", working_copy_path]
    
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        check=True
    )
    
    logger.info("SVNアップデート完了: %s", working_copy_path)
    return result


def svn_list(repository_url: str) -> List[str]:
    """
    SVNリポジトリのファイル・ディレクトリ一覧を取得
    
    Args:
        repository_url (str): SVNリポジトリのURL
        
    Returns:
        list: ディレクトリ・ファイル名のリスト
        
    Raises:
        subprocess.CalledProcessError: SVNコマンドが失敗した場合
    """
    logger.info("SVNリスト取得開始: %s", repository_url)
    
    cmd = ["svn", "list", repository_url]
    
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        check=True
    )
    
    # 出力を行ごとに分割し、空行を除去
    items = [line.strip() for line in result.stdout.split('\n') if line.strip()]
    
    logger.info("SVNリスト取得完了: %s件", len(items))
    return items


def is_svn_working_copy(path: str) -> bool:
    """
    指定されたパスがSVNワーキングコピーかどうかを判定
    
    Args:
        path (str): 判定するパス
        
    Returns:
        bool: SVNワーキングコピーの場合True
    """
    svn_dir = Path(path) / '.svn'
    return svn_dir.exists() and svn_dir.is_dir()


def set_readonly(path: str) -> None:
    """
    指定されたパス以下のすべてのファイルを読み込み専用に設定
    
    Args:
        path (str): 読み込み専用にするディレクトリのパス
    """
    logger.info("読み込み専用設定開始: %s", path)
    
    path_obj = Path(path)
    for file_path in path_obj.rglob('*'):
        if file_path.is_file():
            try:
                # ファイルを読み込み専用に設定
                file_path.chmod(0o444)
            except OSError as e:
                logger.warning("読み込み専用設定に失敗: %s - %s", file_path, str(e))
    
    logger.info("読み込み専用設定完了: %s", path)