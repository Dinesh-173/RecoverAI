from typing import Dict, Any, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from backend.app.models.transaction import Transaction
from backend.app.models.recovery_case import RecoveryCase
from backend.app.models.recovery_action import RecoveryAction
from backend.app.models.risk_assessment import RevenueRiskAssessment
from backend.app.schemas.schemas import DashboardMetrics


class MetricsService:
    @staticmethod
    async def get_dashboard_metrics(db: AsyncSession) -> DashboardMetrics:
        """
        Calculates live dashboard metrics across transactions, recovery cases, and actions.
        Never fabricates results; computes directly from database state.
        """
        # Total Evaluated Transactions (Phase 4: Count distinct evaluated live transactions)
        tx_count_res = await db.execute(
            select(func.count(func.distinct(RevenueRiskAssessment.transaction_id))).where(
                RevenueRiskAssessment.is_simulation == False
            )
        )
        total_evaluated = tx_count_res.scalar() or 0

        # Revenue at Risk (Phase 3: Total live transactions that originated as FAILED)
        failed_sum_res = await db.execute(
            select(func.coalesce(func.sum(Transaction.amount), 0.0)).where(
                Transaction.is_simulation == False,
                func.coalesce(Transaction.initial_status, Transaction.status) == "FAILED",
            )
        )
        total_risk_amount = float(failed_sum_res.scalar() or 0.0)

        # Expected Recoverable Revenue from ML assessments (Phase 6: total potential live recoverable revenue)
        exp_sum_res = await db.execute(
            select(func.coalesce(func.sum(RevenueRiskAssessment.expected_recoverable_amount), 0.0)).where(
                RevenueRiskAssessment.is_simulation == False
            )
        )
        expected_recoverable = float(exp_sum_res.scalar() or 0.0)

        # Expected Recoverable Revenue for currently open/active cases
        exp_open_res = await db.execute(
            select(func.coalesce(func.sum(RevenueRiskAssessment.expected_recoverable_amount), 0.0))
            .join(RecoveryCase, RecoveryCase.transaction_id == RevenueRiskAssessment.transaction_id)
            .where(
                RevenueRiskAssessment.is_simulation == False,
                RecoveryCase.is_simulation == False,
                RecoveryCase.status.in_(["OPEN", "ANALYZING", "SCHEDULED", "EXECUTING", "WAITING_APPROVAL"]),
            )
        )
        expected_recoverable_open = float(exp_open_res.scalar() or 0.0)

        # Recovered Revenue (Phase 5: Unique live transaction principal successfully recovered via SUCCESS action)
        rec_sum_res = await db.execute(
            select(func.coalesce(func.sum(Transaction.amount), 0.0)).where(
                Transaction.is_simulation == False,
                func.coalesce(Transaction.initial_status, Transaction.status) == "FAILED",
                Transaction.status == "CAPTURED",
                Transaction.id.in_(
                    select(RecoveryAction.transaction_id).where(
                        RecoveryAction.status == "SUCCESS",
                        RecoveryAction.is_simulation == False,
                    )
                ),
            )
        )
        recovered_revenue = float(rec_sum_res.scalar() or 0.0)

        # Case Status Counts (live non-simulation)
        open_cases_res = await db.execute(
            select(func.count(RecoveryCase.id)).where(
                RecoveryCase.is_simulation == False,
                RecoveryCase.status.in_(["OPEN", "ANALYZING", "SCHEDULED", "EXECUTING"]),
            )
        )
        open_cases = open_cases_res.scalar() or 0

        pending_app_res = await db.execute(
            select(func.count(RecoveryCase.id)).where(
                RecoveryCase.is_simulation == False,
                RecoveryCase.status == "WAITING_APPROVAL",
            )
        )
        pending_approvals = pending_app_res.scalar() or 0

        stopped_res = await db.execute(
            select(func.count(RecoveryCase.id)).where(
                RecoveryCase.is_simulation == False,
                RecoveryCase.status == "STOPPED",
            )
        )
        stopped_cases = stopped_res.scalar() or 0

        success_cases_res = await db.execute(
            select(func.count(RecoveryCase.id)).where(
                RecoveryCase.is_simulation == False,
                RecoveryCase.status == "RECOVERED",
            )
        )
        successful_recoveries = success_cases_res.scalar() or 0

        # Rates & Averages (Phase 7: Live population consistency)
        recovery_rate = (recovered_revenue / total_risk_amount * 100.0) if total_risk_amount > 0 else 0.0
        avg_recovery = (recovered_revenue / successful_recoveries) if successful_recoveries > 0 else 0.0

        # Baseline Comparison (Phase 8: Population-aligned 32.78% empirical benchmark)
        # Baseline population is identical to RecoverAI live revenue at risk population
        baseline_rate = 32.78
        baseline_recovered = total_risk_amount * (baseline_rate / 100.0)
        # Delta revenue gain MUST NOT be clamped to zero with max(0.0, ...) to preserve negative delta
        delta_gain = recovered_revenue - baseline_recovered

        # Chart: Recovery by Payment Method (live non-simulation)
        method_stmt = (
            select(Transaction.payment_method, func.count(Transaction.id), func.sum(Transaction.amount))
            .where(Transaction.is_simulation == False)
            .group_by(Transaction.payment_method)
        )
        method_res = await db.execute(method_stmt)
        chart_by_method = [
            {"method": row[0], "count": row[1], "volume": float(row[2] or 0.0)}
            for row in method_res.all()
        ]

        # Chart: Recovery by Failure Reason (live non-simulation)
        reason_stmt = (
            select(Transaction.failure_code, func.count(Transaction.id), func.sum(Transaction.amount))
            .where(Transaction.is_simulation == False, Transaction.failure_code.isnot(None))
            .group_by(Transaction.failure_code)
        )
        reason_res = await db.execute(reason_stmt)
        chart_by_reason = [
            {"failure_code": row[0] or "OTHER", "count": row[1], "volume": float(row[2] or 0.0)}
            for row in reason_res.all()
        ]

        # Chart: Strategy distribution (live non-simulation)
        strategy_stmt = (
            select(RecoveryAction.action_type, func.count(RecoveryAction.id))
            .where(RecoveryAction.is_simulation == False)
            .group_by(RecoveryAction.action_type)
        )
        strat_res = await db.execute(strategy_stmt)
        chart_strategy = [
            {"strategy": row[0], "executions": row[1]}
            for row in strat_res.all()
        ]

        # Chart: Dynamic timeline aggregation derived from independent live database timestamps
        # 1. Fetch live at-risk transactions for risk timeline (grouped by Transaction.created_at)
        tx_timeline_stmt = select(
            Transaction.created_at,
            Transaction.amount,
        ).where(
            Transaction.is_simulation == False,
            func.coalesce(Transaction.initial_status, Transaction.status) == "FAILED",
        )
        tx_timeline_res = await db.execute(tx_timeline_stmt)
        tx_rows = tx_timeline_res.all()

        # 2. Fetch live successful recovery actions for recovered timeline (grouped by RecoveryAction.executed_at)
        act_timeline_stmt = (
            select(
                RecoveryAction.executed_at,
                RecoveryAction.created_at,
                Transaction.amount,
                RecoveryAction.transaction_id,
            )
            .join(Transaction, RecoveryAction.transaction_id == Transaction.id)
            .where(
                RecoveryAction.is_simulation == False,
                RecoveryAction.status == "SUCCESS",
                Transaction.is_simulation == False,
            )
            .order_by(RecoveryAction.executed_at.asc())
        )
        act_timeline_res = await db.execute(act_timeline_stmt)
        act_rows = act_timeline_res.all()

        # Deduplicate recovery actions by transaction_id to prevent double counting
        unique_act_rows = []
        seen_act_tx_ids = set()
        for a_row in act_rows:
            tx_id = a_row[3]
            if tx_id not in seen_act_tx_ids:
                seen_act_tx_ids.add(tx_id)
                unique_act_rows.append(a_row)

        # 3. Determine global chronological span across Transaction.created_at and RecoveryAction.executed_at
        all_timestamps = []
        for r in tx_rows:
            if r[0]:
                all_timestamps.append(r[0])
        for a in unique_act_rows:
            exec_t = a[0] or a[1]
            if exec_t:
                all_timestamps.append(exec_t)

        if all_timestamps:
            min_t = min(all_timestamps)
            max_t = max(all_timestamps)
            span = (max_t - min_t).total_seconds() if max_t > min_t else 1.0

            buckets = [
                {"period": "Week 1", "risk": 0.0, "recovered": 0.0},
                {"period": "Week 2", "risk": 0.0, "recovered": 0.0},
                {"period": "Week 3", "risk": 0.0, "recovered": 0.0},
                {"period": "Week 4", "risk": 0.0, "recovered": 0.0},
            ]

            # Bucket risk by Transaction.created_at
            for r in tx_rows:
                t = r[0]
                if t:
                    offset = (t - min_t).total_seconds()
                    idx = min(3, int((offset / span) * 4)) if span > 0 else 0
                    buckets[idx]["risk"] += float(r[1] or 0.0)

            # Bucket recovered by RecoveryAction.executed_at
            for a in unique_act_rows:
                t = a[0] or a[1]
                if t:
                    offset = (t - min_t).total_seconds()
                    idx = min(3, int((offset / span) * 4)) if span > 0 else 0
                    buckets[idx]["recovered"] += float(a[2] or 0.0)

            chart_timeline = [
                {"period": b["period"], "risk": round(b["risk"], 2), "recovered": round(b["recovered"], 2)}
                for b in buckets
            ]
        else:
            chart_timeline = [
                {"period": "Week 1", "risk": 0.0, "recovered": 0.0},
                {"period": "Week 2", "risk": 0.0, "recovered": 0.0},
                {"period": "Week 3", "risk": 0.0, "recovered": 0.0},
                {"period": "Week 4", "risk": 0.0, "recovered": 0.0},
            ]

        return DashboardMetrics(
            revenue_at_risk=round(total_risk_amount, 2),
            recovered_revenue=round(recovered_revenue, 2),
            expected_recoverable_revenue=round(expected_recoverable, 2),
            expected_recoverable_revenue_open=round(expected_recoverable_open, 2),
            recovery_rate=round(recovery_rate, 2),
            open_cases=open_cases,
            pending_approvals=pending_approvals,
            stopped_cases=stopped_cases,
            successful_recoveries=successful_recoveries,
            total_evaluated_transactions=total_evaluated,
            average_recovery_amount=round(avg_recovery, 2),
            baseline_recovered_revenue=round(baseline_recovered, 2),
            baseline_recovery_rate=baseline_rate,
            delta_revenue_gain=round(delta_gain, 2),
            chart_revenue_timeline=chart_timeline,
            chart_recovery_by_method=chart_by_method,
            chart_recovery_by_reason=chart_by_reason,
            chart_strategy_success=chart_strategy,
        )
