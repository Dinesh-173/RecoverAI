import os
import json
from backend.app.main import app


def export_postman_and_openapi():
    """Generates OpenAPI v3 specification, Postman v2.1 Collection, and Postman Environment."""
    os.makedirs("postman/specs", exist_ok=True)
    os.makedirs("postman/collections", exist_ok=True)
    os.makedirs("postman/environments", exist_ok=True)

    # 1. Export OpenAPI v3 JSON
    openapi_schema = app.openapi()
    openapi_path = "postman/specs/openapi.json"
    with open(openapi_path, "w", encoding="utf-8") as f:
        json.dump(openapi_schema, f, indent=2)
    print(f"Exported OpenAPI spec to {openapi_path}")

    # 2. Export Postman Environment
    environment_data = {
        "id": "e8a9b2c3-d4e5-4f6a-8b9c-0d1e2f3a4b5c",
        "name": "RecoverAI Production Environment",
        "values": [
            {
                "key": "base_url",
                "value": "http://localhost:8000",
                "type": "default",
                "enabled": True,
            },
            {
                "key": "api_v1",
                "value": "http://localhost:8000/api/v1",
                "type": "default",
                "enabled": True,
            },
            {
                "key": "merchant_id",
                "value": "mer_apex_digital_01",
                "type": "default",
                "enabled": True,
            },
            {
                "key": "user_role_admin",
                "value": "MERCHANT_ADMIN",
                "type": "default",
                "enabled": True,
            },
            {
                "key": "user_role_operator",
                "value": "MERCHANT_OPERATOR",
                "type": "default",
                "enabled": True,
            },
            {
                "key": "user_role_viewer",
                "value": "VIEWER",
                "type": "default",
                "enabled": True,
            },
            {
                "key": "webhook_secret",
                "value": "mockwebhooksecret12345",
                "type": "secret",
                "enabled": True,
            },
        ],
        "_postman_variable_scope": "environment",
    }
    env_path = "postman/environments/RecoverAI.postman_environment.json"
    with open(env_path, "w", encoding="utf-8") as f:
        json.dump(environment_data, f, indent=2)
    print(f"Exported Postman environment to {env_path}")

    # 3. Export Postman v2.1 Collection
    collection_data = {
        "info": {
            "_postman_id": "c1f2e3d4-5a6b-7c8d-9e0f-1a2b3c4d5e6f",
            "name": "RecoverAI API Suite",
            "description": "Production API Collection for RecoverAI Autonomous Revenue Recovery Platform.",
            "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json",
        },
        "item": [
            {
                "name": "Health & System",
                "item": [
                    {
                        "name": "System Health Probe",
                        "request": {
                            "method": "GET",
                            "header": [],
                            "url": {
                                "raw": "{{base_url}}/health",
                                "host": ["{{base_url}}"],
                                "path": ["health"],
                            },
                            "description": "Checks system health and database ping.",
                        },
                    }
                ],
            },
            {
                "name": "Dashboard & Analytics",
                "item": [
                    {
                        "name": "Get Executive Dashboard Metrics",
                        "request": {
                            "method": "GET",
                            "header": [
                                {"key": "X-User-Role", "value": "{{user_role_admin}}"}
                            ],
                            "url": {
                                "raw": "{{api_v1}}/dashboard/metrics",
                                "host": ["{{api_v1}}"],
                                "path": ["dashboard", "metrics"],
                            },
                            "description": "Fetch live executive recovery KPIs, chart timelines, and rail distributions.",
                        },
                    },
                    {
                        "name": "Get Held-out Evaluation Results",
                        "request": {
                            "method": "GET",
                            "header": [
                                {"key": "X-User-Role", "value": "{{user_role_operator}}"}
                            ],
                            "url": {
                                "raw": "{{api_v1}}/evaluation/results",
                                "host": ["{{api_v1}}"],
                                "path": ["evaluation", "results"],
                            },
                            "description": "Fetch held-out empirical ML metrics and baseline financial recovery comparison.",
                        },
                    },
                ],
            },
            {
                "name": "Transactions Explorer",
                "item": [
                    {
                        "name": "List Transactions",
                        "request": {
                            "method": "GET",
                            "header": [
                                {"key": "X-User-Role", "value": "{{user_role_admin}}"}
                            ],
                            "url": {
                                "raw": "{{api_v1}}/transactions?skip=0&limit=20&status=FAILED",
                                "host": ["{{api_v1}}"],
                                "path": ["transactions"],
                                "query": [
                                    {"key": "skip", "value": "0"},
                                    {"key": "limit", "value": "20"},
                                    {"key": "status", "value": "FAILED"},
                                ],
                            },
                            "description": "Explore real-time transaction stream with risk scores and failure codes.",
                        },
                    },
                    {
                        "name": "Get Transaction By ID",
                        "request": {
                            "method": "GET",
                            "header": [
                                {"key": "X-User-Role", "value": "{{user_role_admin}}"}
                            ],
                            "url": {
                                "raw": "{{api_v1}}/transactions/tx_example_01",
                                "host": ["{{api_v1}}"],
                                "path": ["transactions", "tx_example_01"],
                            },
                            "description": "Fetch detailed single transaction payload.",
                        },
                    },
                ],
            },
            {
                "name": "Recovery Pipeline & Approvals",
                "item": [
                    {
                        "name": "List Recovery Cases",
                        "request": {
                            "method": "GET",
                            "header": [
                                {"key": "X-User-Role", "value": "{{user_role_admin}}"}
                            ],
                            "url": {
                                "raw": "{{api_v1}}/recovery-cases?status=WAITING_APPROVAL",
                                "host": ["{{api_v1}}"],
                                "path": ["recovery-cases"],
                                "query": [{"key": "status", "value": "WAITING_APPROVAL"}],
                            },
                            "description": "List cases in recovery pipeline.",
                        },
                    },
                    {
                        "name": "Get Pending Approvals Queue",
                        "request": {
                            "method": "GET",
                            "header": [
                                {"key": "X-User-Role", "value": "{{user_role_admin}}"}
                            ],
                            "url": {
                                "raw": "{{api_v1}}/approvals/pending",
                                "host": ["{{api_v1}}"],
                                "path": ["approvals", "pending"],
                            },
                            "description": "Fetch escalated high-value or low-confidence cases requiring human signoff.",
                        },
                    },
                    {
                        "name": "Approve Recovery Case (Admin)",
                        "request": {
                            "method": "POST",
                            "header": [
                                {"key": "X-User-Role", "value": "{{user_role_admin}}"},
                                {"key": "X-User-Id", "value": "admin_lead_1"},
                            ],
                            "url": {
                                "raw": "{{api_v1}}/recovery-cases/case_example_01/approve",
                                "host": ["{{api_v1}}"],
                                "path": ["recovery-cases", "case_example_01", "approve"],
                            },
                            "description": "Authorize high-value recovery execution.",
                        },
                    },
                    {
                        "name": "Reject Recovery Case (Admin)",
                        "request": {
                            "method": "POST",
                            "header": [
                                {"key": "X-User-Role", "value": "{{user_role_admin}}"},
                                {"key": "Content-Type", "value": "application/json"},
                            ],
                            "body": {
                                "mode": "raw",
                                "raw": json.dumps({"reason": "Manual offline resolution with merchant"}),
                            },
                            "url": {
                                "raw": "{{api_v1}}/recovery-cases/case_example_01/reject",
                                "host": ["{{api_v1}}"],
                                "path": ["recovery-cases", "case_example_01", "reject"],
                            },
                            "description": "Reject and safely terminate recovery case.",
                        },
                    },
                ],
            },
            {
                "name": "Simulation Sandbox",
                "item": [
                    {
                        "name": "Run Predefined Scenarios Simulation",
                        "request": {
                            "method": "POST",
                            "header": [
                                {"key": "X-User-Role", "value": "{{user_role_operator}}"},
                                {"key": "Content-Type", "value": "application/json"},
                            ],
                            "body": {
                                "mode": "raw",
                                "raw": json.dumps({
                                    "scenario_name": "predefined_5_scenarios",
                                    "batch_size": 10,
                                    "enable_ai_agent": True,
                                    "enable_policy_engine": True,
                                }),
                            },
                            "url": {
                                "raw": "{{api_v1}}/simulation/run",
                                "host": ["{{api_v1}}"],
                                "path": ["simulation", "run"],
                            },
                            "description": "Execute autonomous recovery simulation across 5 canonical scenarios.",
                        },
                    }
                ],
            },
            {
                "name": "Audit Logs",
                "item": [
                    {
                        "name": "Get Immutable Audit Trail Logs",
                        "request": {
                            "method": "GET",
                            "header": [
                                {"key": "X-User-Role", "value": "{{user_role_admin}}"}
                            ],
                            "url": {
                                "raw": "{{api_v1}}/audit-logs?actor_type=AI_AGENT",
                                "host": ["{{api_v1}}"],
                                "path": ["audit-logs"],
                                "query": [{"key": "actor_type", "value": "AI_AGENT"}],
                            },
                            "description": "Fetch decision trail with correlation IDs and JSON diff payloads.",
                        },
                    }
                ],
            },
            {
                "name": "Webhooks Ingestion",
                "item": [
                    {
                        "name": "Razorpay Webhook (payment.failed)",
                        "request": {
                            "method": "POST",
                            "header": [
                                {"key": "X-Razorpay-Signature", "value": "valid_test_signature_hash"},
                                {"key": "X-Razorpay-Event-Id", "value": "evt_test_webhook_001"},
                                {"key": "Content-Type", "value": "application/json"},
                            ],
                            "body": {
                                "mode": "raw",
                                "raw": json.dumps({
                                    "entity": "event",
                                    "account_id": "acc_123456",
                                    "event": "payment.failed",
                                    "contains": ["payment"],
                                    "payload": {
                                        "payment": {
                                            "entity": {
                                                "id": "pay_test_wh_1001",
                                                "amount": 149900,
                                                "currency": "INR",
                                                "status": "failed",
                                                "method": "upi",
                                                "error_code": "GATEWAY_ERROR",
                                                "error_description": "Bank server timed out",
                                            }
                                        }
                                    },
                                    "created_at": 1772310000,
                                }),
                            },
                            "url": {
                                "raw": "{{base_url}}/webhooks/razorpay",
                                "host": ["{{base_url}}"],
                                "path": ["webhooks", "razorpay"],
                            },
                            "description": "Ingest payment failure webhook signal with HMAC verification.",
                        },
                    }
                ],
            },
        ],
    }

    coll_path = "postman/collections/RecoverAI.postman_collection.json"
    with open(coll_path, "w", encoding="utf-8") as f:
        json.dump(collection_data, f, indent=2)
    print(f"Exported Postman Collection to {coll_path}\n")


if __name__ == "__main__":
    export_postman_and_openapi()
