"""SVNチェックアウト・エクスポート管理クラス"""

import logging
from typing import List, Union, Any

logger = logging.getLogger(__name__)


class SvnCheckoutManager:
    """
    SvnCheckoutControl、SvnExportControlのリストを保持し、
    一斉に実行するマネージャークラス
    """
    
    def __init__(self) -> None:
        """
        SvnCheckoutManagerを初期化
        """
        self.controls = []
        logger.info("SvnCheckoutManager初期化")
    
    def appendControl(self, control: Any) -> None:
        """
        制御オブジェクトをリストに追加
        
        Args:
            control: SvnCheckoutControl または SvnExportControl のインスタンス
        """
        self.controls.append(control)
        logger.info("制御オブジェクト追加: %s", str(control))
    
    def update(self) -> None:
        """
        登録されたすべての制御オブジェクトの処理を実行
        - チェックアウトとエクスポートを混在して管理可能
        - 個別のエラーをキャッチして、他の処理を継続実行
        
        Raises:
            Exception: いずれかの処理でエラーが発生した場合、最初のエラーを再発生
        """
        logger.info("SvnCheckoutManager処理開始: %d件の制御オブジェクト", len(self.controls))
        
        if not self.controls:
            logger.warning("処理対象の制御オブジェクトがありません")
            return
        
        errors = []
        successful_count = 0
        
        for i, control in enumerate(self.controls, 1):
            try:
                logger.info("制御オブジェクト処理開始 (%d/%d): %s", i, len(self.controls), str(control))
                control.update()
                successful_count += 1
                logger.info("制御オブジェクト処理成功 (%d/%d): %s", i, len(self.controls), str(control))
                
            except Exception as e:
                error_msg = "制御オブジェクト処理失敗 (%d/%d): %s - %s" % (i, len(self.controls), str(control), str(e))
                logger.error(error_msg)
                errors.append((control, e))
        
        # 処理結果をログ出力
        logger.info("SvnCheckoutManager処理完了: 成功 %d件、失敗 %d件", successful_count, len(errors))
        
        if errors:
            # エラーの詳細をログ出力
            for control, error in errors:
                logger.error("エラー詳細: %s - %s", str(control), str(error))
            
            # 最初のエラーを再発生させて呼び出し元に通知
            first_control, first_error = errors[0]  
            error_summary = "処理中にエラーが発生しました。成功: %d件、失敗: %d件。最初のエラー: %s" % (
                successful_count, len(errors), str(first_error)
            )
            raise Exception(error_summary)
    
    def clear(self) -> None:
        """
        登録されたすべての制御オブジェクトをクリア
        """
        self.controls.clear()
        logger.info("制御オブジェクトをクリア")
    
    def count(self) -> int:
        """
        登録されている制御オブジェクトの数を取得
        
        Returns:
            int: 制御オブジェクトの数
        """
        return len(self.controls)
    
    def __str__(self) -> str:
        """文字列表現"""
        return "SvnCheckoutManager(controls=%d)" % len(self.controls)
    
    def __repr__(self) -> str:
        """詳細文字列表現"""
        return "SvnCheckoutManager(controls=%s)" % [str(control) for control in self.controls]