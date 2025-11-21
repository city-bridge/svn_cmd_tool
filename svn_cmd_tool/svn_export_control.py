"""SVNエクスポート制御クラス"""

import logging
from pathlib import Path
from .svn_cmd import svn_export, set_readonly

logger = logging.getLogger(__name__)


class SvnExportControl:
    """
    SVNリポジトリとエクスポート先の関係設定を保持し、
    設定に従ってSVNエクスポートコマンドを管理するクラス（基底クラス）
    """
    
    def __init__(self, repository_url: str, target_path: str, force_overwrite: bool = False) -> None:
        """
        SvnExportControlを初期化
        
        Args:
            repository_url (str): SVNリポジトリのURL
            target_path (str): エクスポート先のパス
            force_overwrite (bool): 既存ディレクトリを上書きするかどうか
        """
        self.repository_url = repository_url
        self.target_path = target_path
        self.force_overwrite = force_overwrite
        
        logger.info("SvnExportControl初期化: %s -> %s", repository_url, target_path)
    
    def update(self):
        """
        エクスポート処理を実行
        - 指定されたパスから直接エクスポート
        - 既存のディレクトリがある場合は上書きまたはスキップ
        - エクスポート完了後に全ファイルを読み込み専用に設定
        """
        logger.info("SvnExportControl処理開始: %s", self.target_path)
        
        target_path = Path(self.target_path)
        
        if target_path.exists():
            if self.force_overwrite:
                logger.info("既存ディレクトリを上書き: %s", self.target_path)
            else:
                logger.info("既存ディレクトリが存在するためスキップ: %s", self.target_path)
                return
        else:
            # 親ディレクトリを作成
            parent_dir = target_path.parent
            if parent_dir != target_path and not parent_dir.exists():
                parent_dir.mkdir(parents=True, exist_ok=True)
                logger.info("親ディレクトリを作成: %s", parent_dir)
        
        # エクスポート実行
        svn_export(self.repository_url, self.target_path, force=self.force_overwrite)
        
        # 読み込み専用に設定
        set_readonly(self.target_path)
        
        logger.info("SvnExportControl処理完了: %s", self.target_path)
    
    def __str__(self) -> str:
        """文字列表現"""
        return "SvnExportControl(%s -> %s)" % (self.repository_url, self.target_path)
    
    def __repr__(self) -> str:
        """詳細文字列表現"""
        return "SvnExportControl(repository_url='%s', target_path='%s', force_overwrite=%s)" % (
            self.repository_url, self.target_path, self.force_overwrite
        )