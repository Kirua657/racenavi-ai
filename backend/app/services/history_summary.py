def _top_three(result: dict) -> set[int]:
    return {
        horse_number
        for horse_number in (result.get("first"), result.get("second"), result.get("third"))
        if isinstance(horse_number, int)
    }


def _pick_in_top_three(pick: dict | None, result: dict) -> bool:
    return bool(pick and pick.get("horseNumber") in _top_three(result))


def summarize_plans(plans: list[dict]) -> dict:
    total_stake = sum(plan.get("totalStake", 0) for plan in plans)
    result_plans = [plan for plan in plans if plan.get("result") is not None]
    reviewed_stake = sum(plan.get("totalStake", 0) for plan in result_plans)
    total_payout = sum(plan["result"].get("payout", 0) for plan in result_plans)
    profit = total_payout - reviewed_stake
    roi = round((total_payout / reviewed_stake) * 100, 1) if reviewed_stake else 0.0
    hit_count = sum(1 for plan in result_plans if plan["result"].get("hit") is True)
    result_count = len(result_plans)
    hit_rate = round((hit_count / result_count) * 100, 1) if result_count else 0.0

    main_pick_results = [
        plan
        for plan in result_plans
        if isinstance(plan["result"].get("mainPickFinish"), int)
    ]
    main_pick_show_count = sum(
        1 for plan in main_pick_results if plan["result"]["mainPickFinish"] <= 3
    )
    main_pick_show_rate = (
        round((main_pick_show_count / len(main_pick_results)) * 100, 1)
        if main_pick_results
        else 0.0
    )

    value_pick_good_run_count = sum(
        1
        for plan in result_plans
        if _pick_in_top_three(plan.get("predictionSnapshot", {}).get("valuePick"), plan["result"])
    )
    dangerous_favorite_miss_count = sum(
        1
        for plan in result_plans
        if plan.get("predictionSnapshot", {}).get("dangerousFavorite")
        and _top_three(plan["result"])
        and not _pick_in_top_three(
            plan.get("predictionSnapshot", {}).get("dangerousFavorite"),
            plan["result"],
        )
    )

    return {
        "totalStake": total_stake,
        "reviewedStake": reviewed_stake,
        "totalPayout": total_payout,
        "profit": profit,
        "roi": roi,
        "hitCount": hit_count,
        "resultCount": result_count,
        "hitRate": hit_rate,
        "mainPickShowCount": main_pick_show_count,
        "mainPickResultCount": len(main_pick_results),
        "mainPickShowRate": main_pick_show_rate,
        "valuePickGoodRunCount": value_pick_good_run_count,
        "dangerousFavoriteMissCount": dangerous_favorite_miss_count,
        "note": "回収率や収支はレース後に入力した振り返り記録だけから計算します。将来の結果を保証するものではありません。",
    }