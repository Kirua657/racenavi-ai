from app.services.history_summary import summarize_plans


def test_history_summary_calculates_profit_roi_and_hit_rate():
    plans = [
        {
            "totalStake": 3000,
            "result": {"payout": 0, "hit": False, "first": 1, "second": 3, "third": 5, "mainPickFinish": 4},
            "predictionSnapshot": {
                "valuePick": {"horseNumber": 5},
                "dangerousFavorite": {"horseNumber": 2},
            },
        },
        {
            "totalStake": 2000,
            "result": {"payout": 6200, "hit": True, "first": 4, "second": 7, "third": 1, "mainPickFinish": 2},
            "predictionSnapshot": {
                "valuePick": {"horseNumber": 8},
                "dangerousFavorite": {"horseNumber": 7},
            },
        },
        {"totalStake": 1000},
        {"totalStake": 500, "result": None},
    ]

    summary = summarize_plans(plans)

    assert summary["totalStake"] == 6500
    assert summary["totalPayout"] == 6200
    assert summary["profit"] == -300
    assert summary["roi"] == 95.4
    assert summary["hitCount"] == 1
    assert summary["resultCount"] == 2
    assert summary["hitRate"] == 50.0
    assert summary["mainPickShowCount"] == 1
    assert summary["mainPickResultCount"] == 2
    assert summary["mainPickShowRate"] == 50.0
    assert summary["valuePickGoodRunCount"] == 1
    assert summary["dangerousFavoriteMissCount"] == 1
    assert "将来の結果を保証しません" in summary["note"]


def test_history_summary_handles_empty_history():
    summary = summarize_plans([])

    assert summary["totalStake"] == 0
    assert summary["totalPayout"] == 0
    assert summary["profit"] == 0
    assert summary["roi"] == 0.0
    assert summary["hitRate"] == 0.0
    assert summary["resultCount"] == 0
    assert summary["mainPickShowRate"] == 0.0
    assert summary["valuePickGoodRunCount"] == 0
    assert summary["dangerousFavoriteMissCount"] == 0