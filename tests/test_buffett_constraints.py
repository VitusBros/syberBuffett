import pytest
import sys
import os

# Add project root to sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from engine.domain_plugin import DefaultPlugin

class TestBuffettConstraints:
    """
    Automated tests for Buffett's hard rules (Phase 1 cases solidified).
    """

    def _load_buffett_config(self) -> dict:
        from engine.skill_loader import SkillLoader
        loader = SkillLoader("/workspace")
        data = loader.load_role("buffett")
        return data['config']

    def test_no_macro_prediction(self):
        """Rule: Must not predict macro probabilities."""
        config = self._load_buffett_config()
        plugin = DefaultPlugin(config, "", "")
        
        # Trigger: "probability", "drawdown"
        violations = plugin.pre_flight_check("美股会跌吗", "我觉得下跌概率是30%")
        assert len(violations) > 0, "Should catch macro prediction violations"
        assert any("no_macro_prediction" in v for v in violations)

    def test_toll_bridge_misuse(self):
        """Rule: Equipment suppliers are NOT toll bridges."""
        config = self._load_buffett_config()
        plugin = DefaultPlugin(config, "", "")
        
        # Trigger: Input has "电网设备", Response has "收费桥梁"
        violations = plugin.pre_flight_check("分析电网设备公司", "这是典型的收费桥梁")
        assert len(violations) > 0, "Should catch toll bridge misuse"
        assert any("no_toll_bridge_for_suppliers" in v for v in violations)

    def test_correct_cash_explanation(self):
        """Rule: Cash holdings are for insurance/tax, not because market is expensive."""
        config = self._load_buffett_config()
        plugin = DefaultPlugin(config, "", "")
        
        # Trigger: Input has "现金", Response has "看空市场", missing "保险"
        violations = plugin.pre_flight_check("为什么持有那么多现金", "我们持有现金是因为看空市场")
        assert len(violations) > 0, "Should catch incorrect cash explanation"
        assert any("correct_cash_explanation" in v for v in violations)

    def test_no_sell_because_up(self):
        """Rule: Don't sell just because the price went up."""
        config = self._load_buffett_config()
        plugin = DefaultPlugin(config, "", "")
        
        # Trigger: Input has "卖出", Response has "落袋为安"
        violations = plugin.pre_flight_check("现在该卖出比亚迪吗", "涨了这么多，建议落袋为安")
        assert len(violations) > 0, "Should catch sell-because-up violations"
        assert any("no_sell_because_up" in v for v in violations)

    def test_valid_response_passes(self):
        """A compliant response should pass all checks."""
        config = self._load_buffett_config()
        plugin = DefaultPlugin(config, "", "")
        
        # Valid response (Avoids "会跌", includes "保险", "税收", "找不到好机会")
        response = "我不知道市场未来走势。但我持有的公司依然赚钱。持有现金是因为保险业务需要和税收考虑，而且目前找不到好机会。"
        violations = plugin.pre_flight_check("美股会下跌吗", response)
        assert len(violations) == 0, f"Valid response should have no violations, got: {violations}"
