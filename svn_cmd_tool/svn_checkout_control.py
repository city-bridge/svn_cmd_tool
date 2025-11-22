"""SVNチェックアウト制御クラス"""

import logging
from pathlib import Path
from .svn_cmd import svn_checkout, svn_update, is_svn_working_copy

logger = logging.getLogger(__name__)


class SvnCheckoutControl:
    """
    SVNリポジトリとチェックアウト先の関係設定を保持し、
    設定に従ってSVNコマンドを管理するクラス
    """
    
    def __init__(self, name: str, repository_url: str, target_path: str) -> None:
        """
        SvnCheckoutControlを初期化
        
        Args:
            name (str): 制御オブジェクトの名前
            repository_url (str): SVNリポジトリのURL
            target_path (str): チェックアウト先のパス
        """
        self.name = name
        self.repository_url = repository_url
        self.target_path = target_path
        
        logger.info("SvnCheckoutControl初期化: %s (%s -> %s)", name, repository_url, target_path)
    
    def update(self) -> None:
        """
        チェックアウト状態に応じて適切な処理を実行
        - チェックアウト未実行の場合はチェックアウトを実行
        - 既存のワーキングコピーがある場合はアップデートを実行
        """
        logger.info("SvnCheckoutControl処理開始: %s", self.target_path)
        
        target_path = Path(self.target_path)
        
        if target_path.exists():
            if is_svn_working_copy(self.target_path):
                # 既存のワーキングコピーをアップデート
                logger.info("既存のワーキングコピーをアップデート: %s", self.target_path)
                svn_update(self.target_path)
            else:
                # ディレクトリは存在するがワーキングコピーではない
                raise Exception("ターゲットディレクトリが存在しますが、SVNワーキングコピーではありません: %s" % self.target_path)
        else:
            # 新規チェックアウト
            logger.info("新規チェックアウト実行: %s", self.target_path)
            # 親ディレクトリを作成
            parent_dir = target_path.parent
            if parent_dir != target_path and not parent_dir.exists():
                parent_dir.mkdir(parents=True, exist_ok=True)
                logger.info("親ディレクトリを作成: %s", parent_dir)
            
            svn_checkout(self.repository_url, self.target_path)
        
        logger.info("SvnCheckoutControl処理完了: %s", self.target_path)
    
    def __str__(self) -> str:
        """文字列表現"""
        return "SvnCheckoutControl(%s: %s -> %s)" % (self.name, self.repository_url, str(self.target_path))
    
    def __repr__(self) -> str:
        """詳細文字列表現"""
        return "SvnCheckoutControl(name='%s', repository_url='%s', target_path='%s')" % (
            self.name, self.repository_url, str(self.target_path)
        )