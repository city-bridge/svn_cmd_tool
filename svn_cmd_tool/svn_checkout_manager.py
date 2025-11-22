"""SVNチェックアウト・エクスポート管理クラス"""

import json
import logging
from pathlib import Path
from typing import List, Union, Any, Dict

from .svn_checkout_control import SvnCheckoutControl
from .svn_export_control import SvnExportControl
from .svn_cmd import svn_list

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
            control: SvnCheckoutControl または SvnExportControl のインスタンス（名前付き）
        """
        self.controls.append(control)
        logger.info("制御オブジェクト追加: %s", str(control))
    
    def load_from_json(self, json_path: str) -> None:
        """
        JSON設定ファイルから制御オブジェクトを読み込み
        
        Args:
            json_path (str): JSON設定ファイルのパス
            
        Raises:
            FileNotFoundError: JSONファイルが見つからない場合
            ValueError: JSONフォーマットが不正な場合
            Exception: 設定内容が不正な場合
        """
        logger.info("JSON設定ファイル読み込み開始: %s", json_path)
        
        config_path = Path(json_path)
        if not config_path.exists():
            raise FileNotFoundError(f"JSON設定ファイルが見つかりません: {json_path}")
        
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
        except json.JSONDecodeError as e:
            raise ValueError(f"JSONフォーマットエラー: {e}")
        
        # 読み込んだ辞書を処理
        self.load_from_dict(config)
        
        logger.info("JSON設定ファイル読み込み完了: %s", json_path)
    
    def load_from_dict(self, config: Dict) -> None:
        """
        辞書設定から制御オブジェクトを読み込み
        
        Args:
            config (Dict): 設定辞書
            
        Raises:
            Exception: 設定内容が不正な場合
        """
        logger.info("辞書設定読み込み開始")
        
        if not isinstance(config, dict) or 'controls' not in config:
            raise Exception("設定に'controls'キーが必要です")
        
        controls_config = config['controls']
        if not isinstance(controls_config, list):
            raise Exception("'controls'は配列である必要があります")
        
        for i, control_config in enumerate(controls_config):
            try:
                self._create_control_from_config(control_config)
            except Exception as e:
                logger.error("制御オブジェクト作成エラー (%d番目): %s", i + 1, str(e))
                raise Exception(f"制御オブジェクト作成エラー ({i + 1}番目): {e}")
        
        logger.info("辞書設定読み込み完了: %d個の制御オブジェクトを追加", len(controls_config))
    
    def _create_control_from_config(self, config: Dict) -> None:
        """
        設定辞書から制御オブジェクトを作成
        
        Args:
            config (Dict): 制御オブジェクトの設定
        """
        
        if not isinstance(config, dict):
            raise Exception("制御オブジェクト設定は辞書である必要があります")
        
        control_type = config.get('type')
        if not control_type:
            raise Exception("'type'キーが必要です")
        
        name = config.get('name')
        if not name:
            raise Exception("'name'キーが必要です")
        
        target_path = config.get('target_path')
        if not target_path:
            raise Exception("'target_path'キーが必要です")
        
        if control_type == 'checkout':
            repository_url = config.get('repository_url')
            if not repository_url:
                raise Exception("checkoutタイプには'repository_url'キーが必要です")
            
            control = SvnCheckoutControl(name, repository_url, target_path)
            self.appendControl(control)
            
        elif control_type == 'export':
            repository_url = config.get('repository_url')
            force_overwrite = config.get('force_overwrite', False)
            
            if repository_url:
                # 直接URL指定
                control = SvnExportControl(name, repository_url, target_path, force_overwrite)
                self.appendControl(control)
                
            elif 'parent_url' in config:
                # 親ディレクトリから最後のディレクトリを選択
                parent_url = config['parent_url']
                directories = svn_list(parent_url)
                
                if directories:
                    last_directory = directories[-1].rstrip('/')
                    if parent_url.endswith('/'):
                        export_url = parent_url + last_directory
                    else:
                        export_url = parent_url + '/' + last_directory
                    
                    logger.info("最後のディレクトリを発見: %s -> %s", last_directory, export_url)
                    
                    control = SvnExportControl(name, export_url, target_path, force_overwrite)
                    self.appendControl(control)
                else:
                    raise Exception(f"親ディレクトリに子ディレクトリが見つかりません: {parent_url}")
            else:
                raise Exception("exportタイプには'repository_url'または'parent_url'キーが必要です")
                
        else:
            raise Exception(f"サポートされていないタイプ: {control_type}")
    
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
    
    def get_control_by_name(self, name: str) -> Union[Any, None]:
        """
        名前で制御オブジェクトを取得
        
        Args:
            name (str): 制御オブジェクトの名前
            
        Returns:
            Union[Any, None]: 指定された名前の制御オブジェクト、見つからない場合はNone
        """
        for control in self.controls:
            if hasattr(control, 'name') and control.name == name:
                return control
        return None
    
    def get_control_names(self) -> List[str]:
        """
        登録されている制御オブジェクトの名前一覧を取得
        
        Returns:
            List[str]: 制御オブジェクトの名前一覧
        """
        names = []
        for control in self.controls:
            if hasattr(control, 'name'):
                names.append(control.name)
        return names
    
    def has_control_name(self, name: str) -> bool:
        """
        指定された名前の制御オブジェクトが存在するかチェック
        
        Args:
            name (str): 制御オブジェクトの名前
            
        Returns:
            bool: 存在する場合True、しない場合False
        """
        return self.get_control_by_name(name) is not None
    
    def update_by_name(self, name: str) -> None:
        """
        指定された名前の制御オブジェクトのみ処理を実行
        
        Args:
            name (str): 処理する制御オブジェクトの名前
            
        Raises:
            Exception: 指定された名前の制御オブジェクトが見つからない場合
            Exception: 処理中にエラーが発生した場合
        """
        control = self.get_control_by_name(name)
        if control is None:
            raise Exception(f"指定された名前の制御オブジェクトが見つかりません: {name}")
        
        logger.info("名前指定制御オブジェクト処理開始: %s -> %s", name, str(control))
        
        try:
            control.update()
            logger.info("名前指定制御オブジェクト処理成功: %s -> %s", name, str(control))
        except Exception as e:
            error_msg = f"名前指定制御オブジェクト処理失敗: {name} -> {str(control)} - {str(e)}"
            logger.error(error_msg)
            raise Exception(error_msg)
    
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