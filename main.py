from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime, timezone

import re


def analyze_password(password: str) -> dict:
    """Analyze password strength and return security requirements."""
    score = 0
    checks = {}

    checks["minimum_length"] = len(password) >= 12
    if checks["minimum_length"]:
        score += 25

    checks["uppercase"] = bool(re.search(r"[A-Z]", password))
    if checks["uppercase"]:
        score += 15

    checks["lowercase"] = bool(re.search(r"[a-z]", password))
    if checks["lowercase"]:
        score += 15

    checks["number"] = bool(re.search(r"\d", password))
    if checks["number"]:
        score += 15

    checks["special_character"] = bool(
        re.search(r"[^A-Za-z0-9]", password)
    )
    if checks["special_character"]:
        score += 15

    if len(password) >= 16:
        score += 15

    if score >= 85:
        strength = "Very Strong"
    elif score >= 70:
        strength = "Strong"
    elif score >= 50:
        strength = "Moderate"
    else:
        strength = "Weak"

    return {
        "score": min(score, 100),
        "strength": strength,
        "policy_compliant": all(checks.values()),
        "checks": checks,
    }


app = FastAPI(
    title="MineCore",
    description="Mining Operations Management Platform",
    version="2.0.0",
    docs_url=None,
    redoc_url=None,
    openapi_url=None,
)


app.mount(
    "/static",
    StaticFiles(directory=Path(__file__).parent / "static"),
    name="static"
)


class Equipment(BaseModel):
    name: str = Field(..., example="Excavator")
    status: str = Field(..., example="Operational")


class MiningStage(BaseModel):
    id: int
    name: str
    status: str
    description: str
    safety_requirements: List[str]
    equipment: Optional[List[Equipment]] = None


class MiningSite(BaseModel):
    id: int
    name: str
    location: str
    current_stage_id: int
    production_status: str
    safety_status: str
    production_today: int


class Alert(BaseModel):
    id: int
    site_id: int
    severity: str
    message: str
    status: str


class HealthResponse(BaseModel):
    status: str
    service: str
    version: str
    timestamp: str


class PasswordRequest(BaseModel):
    password: str = Field(..., min_length=1)


@app.post("/api/security/password")
def check_password_security(request: PasswordRequest):
    return analyze_password(request.password)


mining_stages = [
    {
        "id": 1,
        "name": "Exploration",
        "status": "Completed",
        "description": "Survey and assessment of the proposed mining area.",
        "safety_requirements": [
            "Conduct geological assessment",
            "Identify potential hazards",
            "Assess environmental risks"
        ]
    },
    {
        "id": 2,
        "name": "Site Planning",
        "status": "Completed",
        "description": "Planning of access routes, work areas and equipment.",
        "safety_requirements": [
            "Assess access routes",
            "Plan emergency access",
            "Identify operational hazards"
        ]
    },
    {
        "id": 3,
        "name": "Mine Development",
        "status": "Completed",
        "description": "Preparation and development of the mining site.",
        "safety_requirements": [
            "Inspect work areas",
            "Verify safety equipment",
            "Confirm emergency procedures",
            "Ensure workers are trained"
        ]
    },
    {
        "id": 4,
        "name": "Extraction",
        "status": "Active",
        "description": "Extraction of coal from the mining area.",
        "equipment": [
            {
                "name": "Excavator",
                "status": "Operational"
            },
            {
                "name": "Haul Truck",
                "status": "Operational"
            }
        ],
        "safety_requirements": [
            "Complete site inspection",
            "Inspect equipment before operation",
            "Use required PPE",
            "Allow only trained personnel",
            "Maintain safe distance from heavy equipment"
        ]
    },
    {
        "id": 5,
        "name": "Coal Processing",
        "status": "Pending",
        "description": "Processing and preparation of extracted coal.",
        "safety_requirements": [
            "Follow equipment operating procedures",
            "Report equipment faults",
            "Follow safety instructions"
        ]
    },
    {
        "id": 6,
        "name": "Transportation",
        "status": "Pending",
        "description": "Transportation of coal using approved routes and vehicles.",
        "safety_requirements": [
            "Complete vehicle inspection",
            "Follow site speed limits",
            "Use approved transportation routes",
            "Report vehicle defects"
        ]
    },
    {
        "id": 7,
        "name": "Storage / Distribution",
        "status": "Pending",
        "description": "Storage and distribution of coal.",
        "safety_requirements": [
            "Control access to storage areas",
            "Monitor storage conditions",
            "Maintain emergency arrangements"
        ]
    },
    {
        "id": 8,
        "name": "Environmental Monitoring & Reclamation",
        "status": "Pending",
        "description": "Monitoring environmental impact and restoring affected areas.",
        "safety_requirements": [
            "Monitor air quality",
            "Monitor water quality",
            "Monitor dust and noise",
            "Manage waste appropriately",
            "Assess land disturbance"
        ]
    }
]


mining_sites = [
    {
        "id": 1,
        "name": "Site A",
        "location": "Mining Zone A",
        "current_stage_id": 4,
        "production_status": "Active",
        "safety_status": "Good",
        "production_today": 1250
    },
    {
        "id": 2,
        "name": "Site B",
        "location": "Mining Zone B",
        "current_stage_id": 4,
        "production_status": "Active",
        "safety_status": "Warning",
        "production_today": 980
    },
    {
        "id": 3,
        "name": "Site C",
        "location": "Mining Zone C",
        "current_stage_id": 5,
        "production_status": "Processing",
        "safety_status": "Good",
        "production_today": 760
    },
    {
        "id": 4,
        "name": "Site D",
        "location": "Mining Zone D",
        "current_stage_id": 6,
        "production_status": "Transportation",
        "safety_status": "Good",
        "production_today": 1120
    }
]


alerts = [
    {
        "id": 1,
        "site_id": 1,
        "severity": "Medium",
        "message": "Excavator inspection is due.",
        "status": "Open"
    },
    {
        "id": 2,
        "site_id": 1,
        "severity": "Low",
        "message": "PPE compliance review is scheduled.",
        "status": "Open"
    }
]


def find_site(site_id: int):
    return next(
        (site for site in mining_sites if site["id"] == site_id),
        None
    )


def find_stage(stage_id: int):
    return next(
        (stage for stage in mining_stages if stage["id"] == stage_id),
        None
    )


@app.get(
    "/health",
    response_model=HealthResponse,
    include_in_schema=False
)
def health_check():
    return {
        "status": "healthy",
        "service": "minecore",
        "version": "2.0.0",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }


@app.get("/", response_class=HTMLResponse)
def home_page():
    total_production = sum(
        site["production_today"]
        for site in mining_sites
    )

    active_sites = sum(
        1
        for site in mining_sites
        if site["production_status"] == "Active"
    )

    open_alerts = sum(
        1
        for alert in alerts
        if alert["status"] == "Open"
    )

    total_equipment = sum(
        len(stage.get("equipment", []))
        for stage in mining_stages
    )

    operational_equipment = sum(
        1
        for stage in mining_stages
        for equipment in stage.get("equipment", [])
        if equipment["status"].lower() == "operational"
    )

    equipment_percentage = (
        round(operational_equipment / total_equipment * 100)
        if total_equipment
        else 0
    )

    site_cards = ""

    for site in mining_sites:
        stage = find_stage(site["current_stage_id"])

        safety_class = (
            "good"
            if site["safety_status"].lower() == "good"
            else "warning"
        )

        status_class = (
            "active"
            if site["production_status"].lower() == "active"
            else "processing"
        )

        progress = {
            "Active": 82,
            "Processing": 58,
            "Transportation": 72
        }.get(site["production_status"], 50)

        site_cards += f"""
        <article class="site-card">
            <div class="site-card-header">
                <div>
                    <div class="site-name">{site["name"]}</div>
                    <div class="site-location">{site["location"]}</div>
                </div>

                <span class="status-badge {safety_class}">
                    {site["safety_status"]}
                </span>
            </div>

            <div class="site-stage">
                <span class="stage-dot {status_class}"></span>
                {stage["name"] if stage else "Unknown Stage"}
            </div>

            <div class="production-row">
                <div>
                    <span class="muted">Production today</span>
                    <strong>{site["production_today"]:,} tons</strong>
                </div>

                <div class="production-status">
                    {site["production_status"]}
                </div>
            </div>

            <div class="progress-track">
                <div
                    class="progress-fill"
                    style="width:{progress}%"
                ></div>
            </div>

            <div class="progress-label">
                <span>Operational progress</span>
                <span>{progress}%</span>
            </div>

            <a
                class="site-link"
                href="/sites/{site["id"]}"
            >
                View site →
            </a>
        </article>
        """

    stage_rows = ""

    for stage in mining_stages:
        if stage["status"] == "Active":
            stage_class = "active"
        elif stage["status"] == "Completed":
            stage_class = "completed"
        else:
            stage_class = "pending"

        stage_rows += f"""
        <div class="lifecycle-item">
            <div class="lifecycle-number {stage_class}">
                {stage["id"]:02d}
            </div>

            <div class="lifecycle-content">
                <div class="lifecycle-name">
                    {stage["name"]}
                </div>

                <div class="lifecycle-status">
                    {stage["status"]}
                </div>
            </div>
        </div>
        """

    alert_rows = ""

    for alert in alerts:
        severity_class = alert["severity"].lower()

        site = find_site(alert["site_id"])
        site_name = site["name"] if site else "Unknown Site"

        alert_rows += f"""
        <div class="alert-card">
            <div class="alert-symbol {severity_class}">
                !
            </div>

            <div class="alert-content">
                <div class="alert-message">
                    {alert["message"]}
                </div>

                <div class="alert-meta">
                    {alert["severity"]} · {site_name} · {alert["status"]}
                </div>
            </div>
        </div>
        """

    return f"""
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta
    name="description"
    content="MineCore Mining Operations Management Platform"
>
<title>MineCore | Mining Operations</title>

<style>
* {{
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}}

html {{
    scroll-behavior: smooth;
}}

body {{
    font-family: Inter, ui-sans-serif, system-ui, -apple-system,
        BlinkMacSystemFont, "Segoe UI", sans-serif;
    background: #06100c;
    color: #ffffff;
    line-height: 1.5;
}}

a {{
    color: inherit;
}}

.hero {{
    min-height: 720px;
    position: relative;
    overflow: hidden;
    background:
        linear-gradient(
            90deg,
            rgba(3, 12, 9, .97) 0%,
            rgba(3, 12, 9, .90) 40%,
            rgba(3, 12, 9, .45) 100%
        ),
        linear-gradient(
            180deg,
            rgba(0, 0, 0, .05),
            rgba(0, 0, 0, .75)
        ),
        url("https://images.unsplash.com/photo-1578604667557-6b7b9c4e8b91?auto=format&fit=crop&w=2200&q=85");
    background-size: cover;
    background-position: center;
}}

.navbar {{
    height: 86px;
    padding: 0 6%;
    display: flex;
    align-items: center;
    justify-content: space-between;
    position: relative;
    z-index: 5;
    border-bottom: 1px solid rgba(255,255,255,.08);
    background: rgba(3,12,9,.18);
    backdrop-filter: blur(12px);
}}

.logo {{
    display: flex;
    align-items: center;
    gap: 12px;
    font-size: 20px;
    font-weight: 800;
    letter-spacing: -.5px;
    text-decoration: none;
}}

.logo-mark {{
    width: 40px;
    height: 40px;
    border-radius: 11px;
    display: flex;
    align-items: center;
    justify-content: center;
    background: linear-gradient(135deg, #1766ff, #0a4cd1);
    box-shadow: 0 8px 30px rgba(13,91,255,.3);
}}

.logo-name span {{
    color: #6197ff;
}}

.nav-links {{
    display: flex;
    align-items: center;
    gap: 32px;
}}

.nav-links a {{
    color: rgba(255,255,255,.72);
    text-decoration: none;
    font-size: 13px;
    transition: .2s;
}}

.nav-links a:hover {{
    color: white;
}}

.nav-cta {{
    text-decoration: none;
    border: 1px solid rgba(255,255,255,.25);
    background: rgba(255,255,255,.06);
    padding: 10px 18px;
    border-radius: 24px;
    font-size: 13px;
    transition: .2s;
}}

.nav-cta:hover {{
    background: white;
    color: #07110d;
}}

.hero-content {{
    max-width: 1240px;
    margin: auto;
    padding: 115px 6% 150px;
    position: relative;
    z-index: 2;
}}

.eyebrow {{
    display: flex;
    align-items: center;
    gap: 9px;
    color: #72a4ff;
    text-transform: uppercase;
    letter-spacing: 1.7px;
    font-size: 11px;
    font-weight: 800;
    margin-bottom: 22px;
}}

.eyebrow-dot {{
    width: 7px;
    height: 7px;
    border-radius: 50%;
    background: #4388ff;
    box-shadow: 0 0 14px #4388ff;
}}

.hero h1 {{
    max-width: 820px;
    font-size: clamp(50px, 7vw, 88px);
    line-height: .97;
    letter-spacing: -4px;
    font-weight: 780;
    margin-bottom: 28px;
}}

.hero h1 span {{
    color: #4d8cff;
}}

.hero-text {{
    max-width: 620px;
    color: rgba(255,255,255,.68);
    font-size: 17px;
    line-height: 1.75;
    margin-bottom: 36px;
}}

.hero-buttons {{
    display: flex;
    gap: 13px;
    flex-wrap: wrap;
}}

.button-primary {{
    text-decoration: none;
    background: #0c5cff;
    padding: 15px 23px;
    border-radius: 30px;
    font-size: 14px;
    font-weight: 700;
    box-shadow: 0 15px 35px rgba(12,92,255,.25);
    transition: .25s;
}}

.button-primary:hover {{
    background: #2872ff;
    transform: translateY(-2px);
}}

.button-secondary {{
    text-decoration: none;
    border: 1px solid rgba(255,255,255,.27);
    background: rgba(255,255,255,.06);
    padding: 14px 23px;
    border-radius: 30px;
    font-size: 14px;
    font-weight: 600;
    transition: .25s;
}}

.button-secondary:hover {{
    background: rgba(255,255,255,.13);
}}

.stats-wrapper {{
    padding: 0 6%;
    position: relative;
    margin-top: -72px;
    z-index: 10;
}}

.stats {{
    max-width: 1200px;
    margin: auto;
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    overflow: hidden;
    border-radius: 20px;
    background: rgba(11,29,22,.92);
    border: 1px solid rgba(255,255,255,.09);
    box-shadow: 0 30px 80px rgba(0,0,0,.3);
    backdrop-filter: blur(20px);
}}

.stat {{
    padding: 28px;
    border-right: 1px solid rgba(255,255,255,.07);
}}

.stat:last-child {{
    border-right: none;
}}

.stat-label {{
    color: #70837a;
    font-size: 10px;
    text-transform: uppercase;
    letter-spacing: 1.4px;
    font-weight: 700;
    margin-bottom: 9px;
}}

.stat-value {{
    font-size: 29px;
    font-weight: 760;
    letter-spacing: -1px;
}}

.blue {{
    color: #6098ff;
}}

.green {{
    color: #4fd99b;
}}

.orange {{
    color: #ffb653;
}}

.section {{
    max-width: 1200px;
    margin: auto;
    padding: 105px 6%;
}}

.section-header {{
    display: flex;
    justify-content: space-between;
    align-items: end;
    gap: 35px;
    margin-bottom: 38px;
}}

.section-label {{
    color: #5b96ff;
    font-size: 10px;
    font-weight: 800;
    text-transform: uppercase;
    letter-spacing: 2px;
    margin-bottom: 10px;
}}

.section-title {{
    font-size: 40px;
    line-height: 1.1;
    letter-spacing: -1.8px;
}}

.section-description {{
    max-width: 430px;
    color: #71837b;
    font-size: 13px;
    line-height: 1.7;
}}

.site-grid {{
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 17px;
}}

.site-card {{
    padding: 27px;
    border-radius: 19px;
    background: linear-gradient(145deg, #10201a, #0a1511);
    border: 1px solid rgba(255,255,255,.07);
    transition: .25s;
}}

.site-card:hover {{
    transform: translateY(-4px);
    border-color: rgba(68,133,255,.35);
    box-shadow: 0 20px 50px rgba(0,0,0,.22);
}}

.site-card-header {{
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    gap: 15px;
}}

.site-name {{
    font-size: 19px;
    font-weight: 730;
}}

.site-location {{
    color: #657770;
    font-size: 12px;
    margin-top: 4px;
}}

.status-badge {{
    padding: 5px 10px;
    border-radius: 20px;
    text-transform: uppercase;
    font-size: 9px;
    letter-spacing: .7px;
    font-weight: 800;
}}

.status-badge.good {{
    color: #4fdfa0;
    background: rgba(79,223,160,.09);
}}

.status-badge.warning {{
    color: #ffbd59;
    background: rgba(255,189,89,.09);
}}

.site-stage {{
    margin-top: 23px;
    display: flex;
    align-items: center;
    gap: 8px;
    color: #9aaba4;
    font-size: 12px;
}}

.stage-dot {{
    width: 7px;
    height: 7px;
    border-radius: 50%;
}}

.stage-dot.active {{
    background: #4d8dff;
    box-shadow: 0 0 10px #4d8dff;
}}

.stage-dot.processing {{
    background: #b18aff;
}}

.production-row {{
    margin-top: 24px;
    display: flex;
    align-items: end;
    justify-content: space-between;
}}

.muted {{
    display: block;
    color: #63746e;
    font-size: 10px;
    margin-bottom: 4px;
}}

.production-row strong {{
    font-size: 18px;
}}

.production-status {{
    color: #5e9aff;
    font-size: 11px;
    font-weight: 650;
}}

.progress-track {{
    height: 5px;
    background: #1b2a24;
    border-radius: 10px;
    margin-top: 18px;
    overflow: hidden;
}}

.progress-fill {{
    height: 100%;
    border-radius: 10px;
    background: linear-gradient(90deg, #145cff, #66a1ff);
}}

.progress-label {{
    display: flex;
    justify-content: space-between;
    margin-top: 7px;
    color: #5f7069;
    font-size: 10px;
}}

.site-link {{
    display: block;
    color: #659aff;
    font-size: 11px;
    text-decoration: none;
    margin-top: 20px;
}}

.operations {{
    background: #091510;
    border-top: 1px solid rgba(255,255,255,.05);
    border-bottom: 1px solid rgba(255,255,255,.05);
}}

.operation-grid {{
    display: grid;
    grid-template-columns: 1.25fr .75fr;
    gap: 18px;
}}

.panel {{
    padding: 27px;
    border-radius: 19px;
    background: #0e1c16;
    border: 1px solid rgba(255,255,255,.07);
}}

.panel-heading {{
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 24px;
}}

.panel-heading h3 {{
    font-size: 16px;
}}

.panel-heading a {{
    color: #6198ff;
    text-decoration: none;
    font-size: 11px;
}}

.lifecycle-item {{
    display: flex;
    align-items: center;
    gap: 13px;
    padding: 12px 0;
    border-bottom: 1px solid rgba(255,255,255,.045);
}}

.lifecycle-item:last-child {{
    border-bottom: none;
}}

.lifecycle-number {{
    width: 34px;
    height: 34px;
    flex-shrink: 0;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    background: #16261f;
    color: #75867f;
    font-size: 10px;
    font-weight: 700;
}}

.lifecycle-number.active {{
    background: #0d5cff;
    color: white;
    box-shadow: 0 0 20px rgba(13,92,255,.3);
}}

.lifecycle-number.completed {{
    color: #54d99a;
    background: rgba(84,217,154,.08);
}}

.lifecycle-content {{
    flex: 1;
}}

.lifecycle-name {{
    font-size: 13px;
    font-weight: 650;
}}

.lifecycle-status {{
    color: #63756e;
    font-size: 10px;
    margin-top: 2px;
}}

.alert-card {{
    display: flex;
    gap: 12px;
    padding: 14px;
    border-radius: 12px;
    background: rgba(255,255,255,.025);
    margin-bottom: 9px;
}}

.alert-symbol {{
    width: 33px;
    height: 33px;
    flex-shrink: 0;
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 50%;
    font-weight: 800;
}}

.alert-symbol.medium {{
    color: #ffbd59;
    background: rgba(255,189,89,.1);
}}

.alert-symbol.low {{
    color: #61a0ff;
    background: rgba(97,160,255,.1);
}}

.alert-message {{
    color: #dbe5e0;
    font-size: 12px;
    line-height: 1.4;
}}

.alert-meta {{
    color: #61736b;
    font-size: 9px;
    margin-top: 5px;
}}

.monitor-box {{
    padding: 17px;
    margin-top: 18px;
    border-radius: 13px;
    background: rgba(72,215,151,.045);
    border: 1px solid rgba(72,215,151,.1);
}}

.monitor-title {{
    color: #50d995;
    font-size: 10px;
    font-weight: 800;
    letter-spacing: 1px;
    margin-bottom: 6px;
}}

.monitor-text {{
    color: #72847c;
    font-size: 11px;
    line-height: 1.6;
}}

.equipment-section {{
    background: #06100c;
}}

.equipment-grid {{
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 17px;
}}

.equipment-card {{
    padding: 24px;
    border-radius: 17px;
    background: #0c1914;
    border: 1px solid rgba(255,255,255,.06);
}}

.equipment-icon {{
    width: 42px;
    height: 42px;
    border-radius: 12px;
    background: rgba(66,136,255,.1);
    display: flex;
    align-items: center;
    justify-content: center;
    color: #609aff;
    margin-bottom: 18px;
    font-size: 18px;
}}

.equipment-name {{
    font-size: 14px;
    font-weight: 700;
}}

.equipment-status {{
    color: #4fdda0;
    font-size: 10px;
    margin-top: 5px;
}}

footer {{
    background: #030907;
    padding: 40px 6%;
    border-top: 1px solid rgba(255,255,255,.05);
}}

.footer {{
    max-width: 1200px;
    margin: auto;
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 20px;
}}

.footer-brand {{
    font-weight: 750;
    font-size: 16px;
}}

.footer-text {{
    color: #5c6e67;
    font-size: 10px;
}}

.footer-health {{
    color: #4fd99b;
    font-size: 10px;
    display: flex;
    align-items: center;
    gap: 6px;
}}

.health-dot {{
    width: 6px;
    height: 6px;
    background: #4fd99b;
    border-radius: 50%;
    box-shadow: 0 0 10px #4fd99b;
}}

.password-section {{
    background: #08130e;
    border-top: 1px solid rgba(255,255,255,.05);
    border-bottom: 1px solid rgba(255,255,255,.05);
}}

.password-panel {{
    max-width: 780px;
    margin: 0 auto;
    padding: 30px;
    border-radius: 20px;
    background: linear-gradient(145deg, #10201a, #0a1511);
    border: 1px solid rgba(255,255,255,.07);
}}

.password-form {{
    display: flex;
    gap: 10px;
    margin-top: 24px;
}}

.password-input {{
    flex: 1;
    min-width: 0;
    padding: 14px 16px;
    border-radius: 12px;
    border: 1px solid rgba(255,255,255,.12);
    background: #07110d;
    color: white;
    outline: none;
    font-size: 14px;
}}

.password-input:focus {{
    border-color: #4388ff;
    box-shadow: 0 0 0 3px rgba(67,136,255,.1);
}}

.password-button {{
    border: none;
    cursor: pointer;
    color: white;
    background: #0c5cff;
    padding: 0 22px;
    border-radius: 12px;
    font-weight: 700;
}}

.password-button:hover {{
    background: #2872ff;
}}

.password-result {{
    display: none;
    margin-top: 22px;
}}

.password-result.show {{
    display: block;
}}

.password-score-row {{
    display: flex;
    justify-content: space-between;
    align-items: end;
    gap: 15px;
    margin-bottom: 12px;
}}

.password-score {{
    font-size: 38px;
    font-weight: 800;
    letter-spacing: -1.5px;
}}

.password-strength {{
    font-size: 12px;
    font-weight: 800;
    text-transform: uppercase;
    letter-spacing: 1px;
}}

.password-bar {{
    height: 7px;
    background: #1b2a24;
    border-radius: 20px;
    overflow: hidden;
}}

.password-bar-fill {{
    width: 0;
    height: 100%;
    border-radius: 20px;
    background: #4388ff;
    transition: width .3s ease;
}}

.password-compliance {{
    margin-top: 15px;
    padding: 12px 14px;
    border-radius: 10px;
    font-size: 12px;
}}

.password-compliance.compliant {{
    color: #4fdda0;
    background: rgba(79,223,160,.08);
}}

.password-compliance.non-compliant {{
    color: #ffbd59;
    background: rgba(255,189,89,.08);
}}

.password-checks {{
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 9px;
    margin-top: 16px;
}}

.password-check {{
    padding: 11px 13px;
    border-radius: 10px;
    background: rgba(255,255,255,.025);
    color: #899b93;
    font-size: 11px;
}}

.password-check.pass {{
    color: #4fdda0;
}}

.password-check.fail {{
    color: #ff8e8e;
}}

.password-error {{
    display: none;
    margin-top: 15px;
    color: #ff8e8e;
    font-size: 12px;
}}

.password-error.show {{
    display: block;
}}

@media (max-width: 650px) {{
    .password-form {{
        flex-direction: column;
    }}

    .password-button {{
        min-height: 46px;
    }}

    .password-checks {{
        grid-template-columns: 1fr;
    }}

    .password-panel {{
        padding: 22px;
    }}
}}

@media (max-width: 900px) {{
    .nav-links {{
        display: none;
    }}

    .stats {{
        grid-template-columns: repeat(2, 1fr);
    }}

    .stat:nth-child(2) {{
        border-right: none;
    }}

    .stat:nth-child(-n+2) {{
        border-bottom: 1px solid rgba(255,255,255,.07);
    }}

    .operation-grid {{
        grid-template-columns: 1fr;
    }}

    .equipment-grid {{
        grid-template-columns: repeat(2, 1fr);
    }}
}}

@media (max-width: 650px) {{
    .hero {{
        min-height: 680px;
    }}

    .hero-content {{
        padding: 90px 5% 130px;
    }}

    .hero h1 {{
        font-size: 50px;
        letter-spacing: -2.5px;
    }}

    .hero-text {{
        font-size: 14px;
    }}

    .section {{
        padding: 80px 5%;
    }}

    .section-header {{
        display: block;
    }}

    .section-description {{
        margin-top: 15px;
    }}

    .site-grid {{
        grid-template-columns: 1fr;
    }}

    .equipment-grid {{
        grid-template-columns: 1fr;
    }}

    .stats-wrapper {{
        padding: 0 5%;
    }}

    .stat {{
        padding: 22px;
    }}

    .footer {{
        flex-direction: column;
        align-items: flex-start;
    }}
}}

@media (max-width: 450px) {{
    .stats {{
        grid-template-columns: 1fr;
    }}

    .stat {{
        border-right: none;
        border-bottom: 1px solid rgba(255,255,255,.07);
    }}

    .stat:last-child {{
        border-bottom: none;
    }}

    .hero h1 {{
        font-size: 42px;
    }}

    .hero-buttons {{
        flex-direction: column;
        align-items: stretch;
    }}

    .button-primary,
    .button-secondary {{
        text-align: center;
    }}
}}
</style>

<link rel="stylesheet" href="/static/app.css">
</head>

<body>

<section class="hero">
    <nav class="navbar">
        <a href="/" class="logo">
            <div class="logo-mark">⛏</div>
            <div class="logo-name">MINE<span>CORE</span></div>
        </a>

        <div class="nav-links">
            <a href="#sites">Mining Sites</a>
            <a href="#operations">Operations</a>
            <a href="#equipment">Equipment</a>
            <a href="#security">Security</a>
        </div>

        <a class="nav-cta" href="#dashboard">
            Dashboard
        </a>
    </nav>

    <div class="hero-content">
        <div class="eyebrow">
            <span class="eyebrow-dot"></span>
            Mining Operations Platform
        </div>

        <h1>
            Smarter software for
            <span>mining operations.</span>
        </h1>

        <p class="hero-text">
            Monitor production, manage mining stages,
            track equipment and maintain operational
            safety across your mining sites from one
            intelligent platform.
        </p>

        <div class="hero-buttons">
            <a class="button-primary" href="#dashboard">
                Explore Operations →
            </a>

            <a class="button-secondary" href="#sites">
                View Mining Sites
            </a>
        </div>
    </div>
</section>

<div class="stats-wrapper" id="dashboard">
    <div class="stats">

        <div class="stat">
            <div class="stat-label">Today's Production</div>

            <div class="stat-value blue">
                {total_production:,}
                <span style="font-size:11px;color:#60736b;">
                    TONS
                </span>
            </div>
        </div>

        <div class="stat">
            <div class="stat-label">Active Sites</div>
            <div class="stat-value green">
                {active_sites}
            </div>
        </div>

        <div class="stat">
            <div class="stat-label">Open Alerts</div>
            <div class="stat-value orange">
                {open_alerts}
            </div>
        </div>

        <div class="stat">
            <div class="stat-label">Equipment Operational</div>
            <div class="stat-value blue">
                {operational_equipment}/{total_equipment}
            </div>
        </div>

    </div>
</div>

<section class="section" id="sites">
    <div class="section-header">
        <div>
            <div class="section-label">Live Operations</div>
            <h2 class="section-title">Mining Sites</h2>
        </div>

        <p class="section-description">
            Monitor production, operational status
            and safety conditions across every
            mining location.
        </p>
    </div>

    <div class="site-grid">
        {site_cards}
    </div>
</section>

<section class="operations" id="operations">
    <div class="section">

        <div class="section-header">
            <div>
                <div class="section-label">Control Center</div>
                <h2 class="section-title">Operations Overview</h2>
            </div>

            <p class="section-description">
                Follow the mining lifecycle from
                exploration and development through
                extraction and transportation.
            </p>
        </div>

        <div class="operation-grid">

            <div class="panel">
                <div class="panel-heading">
                    <h3>Mining Lifecycle</h3>

                    <a href="#operations">
                        View operations →
                    </a>
                </div>

                {stage_rows}
            </div>

            <div class="panel" id="safety">
                <div class="panel-heading">
                    <h3>Safety Alerts</h3>

                    <a href="/sites/1#alerts">
                        View alerts →
                    </a>
                </div>

                {alert_rows}

                <div class="monitor-box">
                    <div class="monitor-title">
                        SAFETY MONITORING
                    </div>

                    <div class="monitor-text">
                        Operational safety requirements
                        and alerts are being monitored
                        across active mining sites.
                    </div>
                </div>
            </div>

        </div>
    </div>
</section>

<section class="section password-section" id="security">
    <div class="section-header">
        <div>
            <div class="section-label">Security Module</div>
            <h2 class="section-title">Password Security Analyzer</h2>
        </div>

        <p class="section-description">
            Check password strength against MineCore's
            basic security requirements.
        </p>
    </div>

    <div class="password-panel">
        <div class="panel-heading">
            <h3>Analyze a Password</h3>

            <span style="color:#63756e;font-size:10px;">
                Your password is sent only to this API endpoint for analysis.
            </span>
        </div>

        <form class="password-form" id="passwordForm">
            <input
                class="password-input"
                id="passwordInput"
                type="password"
                placeholder="Enter a password to analyze"
                autocomplete="off"
                required
            >

            <button class="password-button" type="submit">
                Analyze
            </button>
        </form>

        <div class="password-error" id="passwordError"></div>

        <div class="password-result" id="passwordResult">

            <div class="password-score-row">
                <div>
                    <div class="muted">Security Score</div>

                    <div class="password-score">
                        <span id="passwordScore">0</span>/100
                    </div>
                </div>

                <div
                    class="password-strength"
                    id="passwordStrength"
                >
                    -
                </div>
            </div>

            <div class="password-bar">
                <div
                    class="password-bar-fill"
                    id="passwordBarFill"
                ></div>
            </div>

            <div
                class="password-compliance"
                id="passwordCompliance"
            ></div>

            <div class="password-checks">

                <div class="password-check" id="checkMinimum">
                    ○ Minimum 12 characters
                </div>

                <div class="password-check" id="checkUppercase">
                    ○ Uppercase letter
                </div>

                <div class="password-check" id="checkLowercase">
                    ○ Lowercase letter
                </div>

                <div class="password-check" id="checkNumber">
                    ○ Number
                </div>

                <div class="password-check" id="checkSpecial">
                    ○ Special character
                </div>

            </div>
        </div>
    </div>
</section>

<section class="section equipment-section" id="equipment">

    <div class="section-header">
        <div>
            <div class="section-label">Fleet Monitoring</div>
            <h2 class="section-title">Equipment</h2>
        </div>

        <p class="section-description">
            Monitor equipment assigned to active
            mining operations and track operational
            status.
        </p>
    </div>

    <div class="equipment-grid">

        <div class="equipment-card">
            <div class="equipment-icon">⚙</div>

            <div class="equipment-name">
                Excavator
            </div>

            <div class="equipment-status">
                ● Operational
            </div>
        </div>

        <div class="equipment-card">
            <div class="equipment-icon">🚚</div>

            <div class="equipment-name">
                Haul Truck
            </div>

            <div class="equipment-status">
                ● Operational
            </div>
        </div>

        <div class="equipment-card">
            <div class="equipment-icon">◉</div>

            <div class="equipment-name">
                Fleet Monitoring
            </div>

            <div class="equipment-status">
                {equipment_percentage}% Operational
            </div>
        </div>

    </div>
</section>

<footer>
    <div class="footer">

        <div class="footer-brand">
            ⛏ MINECORE
        </div>

        <div class="footer-text">
            Mining Operations Management Platform
            · Version 2.0.0
        </div>

        <div class="footer-health">
            <span class="health-dot"></span>
            System Operational
        </div>

    </div>
</footer>

<script>
const passwordForm = document.getElementById("passwordForm");

if (passwordForm) {{
    passwordForm.addEventListener("submit", async function (event) {{
        event.preventDefault();

        const input = document.getElementById("passwordInput");
        const result = document.getElementById("passwordResult");
        const error = document.getElementById("passwordError");
        const password = input.value;

        error.classList.remove("show");
        result.classList.remove("show");

        if (!password) {{
            error.textContent = "Please enter a password.";
            error.classList.add("show");
            return;
        }}

        try {{
            const response = await fetch("/api/security/password", {{
                method: "POST",
                headers: {{
                    "Content-Type": "application/json"
                }},
                body: JSON.stringify({{
                    password: password
                }})
            }});

            const data = await response.json();

            if (!response.ok) {{
                throw new Error(
                    data.detail || "Password analysis failed."
                );
            }}

            document.getElementById("passwordScore").textContent =
                data.score;

            document.getElementById("passwordStrength").textContent =
                data.strength;

            const bar = document.getElementById("passwordBarFill");
            bar.style.width = data.score + "%";

            const compliance =
                document.getElementById("passwordCompliance");

            if (data.policy_compliant) {{
                compliance.textContent =
                    "✓ Password meets all required policy checks.";

                compliance.className =
                    "password-compliance compliant";
            }} else {{
                compliance.textContent =
                    "⚠ Password does not meet all policy checks.";

                compliance.className =
                    "password-compliance non-compliant";
            }}

            const checks = [
                ["minimum_length", "checkMinimum"],
                ["uppercase", "checkUppercase"],
                ["lowercase", "checkLowercase"],
                ["number", "checkNumber"],
                ["special_character", "checkSpecial"]
            ];

            checks.forEach(function (item) {{
                const passed = data.checks[item[0]];
                const element = document.getElementById(item[1]);

                element.classList.remove("pass", "fail");

                const label = element.textContent.substring(2);

                if (passed) {{
                    element.classList.add("pass");
                    element.textContent = "✓ " + label;
                }} else {{
                    element.classList.add("fail");
                    element.textContent = "✗ " + label;
                }}
            }});

            result.classList.add("show");

        }} catch (err) {{
            error.textContent =
                err.message || "Unable to analyze the password.";

            error.classList.add("show");
        }}
    }});
}}
</script>

</body>
</html>
"""


# ============================================================
# INDIVIDUAL SITE DASHBOARD
# ============================================================

@app.get("/sites/{site_id}", response_class=HTMLResponse)
def site_dashboard(site_id: int):
    site = find_site(site_id)

    if not site:
        raise HTTPException(
            status_code=404,
            detail=f"Mining site {site_id} not found"
        )

    return f"""
<!DOCTYPE html>
<html lang="en">

<head>
    <meta charset="UTF-8">
    <meta
        name="viewport"
        content="width=device-width, initial-scale=1.0"
    >

    <title>{site["name"]} | MineCore</title>

    <style>
        * {{
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }}

        html {{
            scroll-behavior: smooth;
        }}

        body {{
            font-family:
                Inter,
                ui-sans-serif,
                system-ui,
                -apple-system,
                BlinkMacSystemFont,
                "Segoe UI",
                sans-serif;

            background: #06100c;
            color: #ffffff;
            min-height: 100vh;
        }}

        a {{
            color: inherit;
            text-decoration: none;
        }}

        .navbar {{
            height: 76px;
            padding: 0 6%;

            display: flex;
            align-items: center;
            justify-content: space-between;

            border-bottom: 1px solid rgba(255,255,255,.07);
            background: rgba(5,15,11,.95);
        }}

        .logo {{
            display: flex;
            align-items: center;
            gap: 11px;

            font-size: 18px;
            font-weight: 800;
        }}

        .logo-mark {{
            width: 38px;
            height: 38px;

            display: flex;
            align-items: center;
            justify-content: center;

            border-radius: 10px;
            background: linear-gradient(
                135deg,
                #1766ff,
                #0a4cd1
            );
        }}

        .logo-name span {{
            color: #6197ff;
        }}

        .back-link {{
            color: #79a6ff;
            font-size: 13px;
            font-weight: 600;
        }}

        .page {{
            max-width: 1200px;
            margin: auto;
            padding: 55px 6% 90px;
        }}

        .breadcrumb {{
            color: #61736b;
            font-size: 11px;
            margin-bottom: 18px;
        }}

        .breadcrumb span {{
            color: #79a6ff;
        }}

        .site-header {{
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            gap: 30px;

            margin-bottom: 35px;
        }}

        .eyebrow {{
            color: #5b96ff;
            text-transform: uppercase;
            letter-spacing: 1.8px;
            font-size: 10px;
            font-weight: 800;
            margin-bottom: 9px;
        }}

        h1 {{
            font-size: clamp(36px, 5vw, 58px);
            letter-spacing: -2.5px;
            line-height: 1;
        }}

        .location {{
            color: #71837b;
            margin-top: 10px;
            font-size: 13px;
        }}

        .status {{
            padding: 8px 14px;
            border-radius: 20px;

            font-size: 10px;
            font-weight: 800;
            text-transform: uppercase;
            letter-spacing: .8px;
        }}

        .status.good {{
            color: #4fdfa0;
            background: rgba(79,223,160,.09);
        }}

        .status.warning {{
            color: #ffbd59;
            background: rgba(255,189,89,.09);
        }}

        .dashboard-grid {{
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 14px;
            margin-bottom: 18px;
        }}

        .metric {{
            padding: 23px;
            border-radius: 17px;

            background: linear-gradient(
                145deg,
                #10201a,
                #0a1511
            );

            border: 1px solid rgba(255,255,255,.07);
        }}

        .metric-label {{
            color: #64766f;
            text-transform: uppercase;
            letter-spacing: 1px;
            font-size: 9px;
            font-weight: 800;
            margin-bottom: 9px;
        }}

        .metric-value {{
            font-size: 27px;
            font-weight: 800;
            letter-spacing: -1px;
        }}

        .blue {{
            color: #6098ff;
        }}

        .green {{
            color: #4fdfa0;
        }}

        .orange {{
            color: #ffbd59;
        }}

        .content-grid {{
            display: grid;
            grid-template-columns: 1.15fr .85fr;
            gap: 18px;
        }}

        .panel {{
            padding: 27px;
            border-radius: 19px;

            background: #0e1c16;
            border: 1px solid rgba(255,255,255,.07);
        }}

        .panel + .panel {{
            margin-top: 18px;
        }}

        .panel-title {{
            display: flex;
            align-items: center;
            justify-content: space-between;

            margin-bottom: 22px;
        }}

        .panel-title h2 {{
            font-size: 16px;
        }}

        .panel-title span {{
            color: #60736b;
            font-size: 10px;
        }}

        .stage-box {{
            padding: 19px;
            border-radius: 13px;
            background: rgba(67,136,255,.055);
            border: 1px solid rgba(67,136,255,.12);
        }}

        .stage-label {{
            color: #638fdc;
            text-transform: uppercase;
            letter-spacing: 1px;
            font-size: 9px;
            font-weight: 800;
            margin-bottom: 7px;
        }}

        .stage-name {{
            font-size: 21px;
            font-weight: 750;
        }}

        .stage-status {{
            display: inline-block;
            margin-top: 8px;

            color: #4fdfa0;
            font-size: 10px;
            font-weight: 700;
        }}

        .progress-heading {{
            display: flex;
            justify-content: space-between;

            margin-top: 25px;
            margin-bottom: 8px;

            color: #788a83;
            font-size: 11px;
        }}

        .progress-track {{
            height: 7px;
            overflow: hidden;

            border-radius: 20px;
            background: #1a2922;
        }}

        .progress-fill {{
            height: 100%;
            width: 0;

            border-radius: 20px;

            background: linear-gradient(
                90deg,
                #145cff,
                #66a1ff
            );

            transition: width .5s ease;
        }}

        .alert {{
            display: flex;
            gap: 12px;

            padding: 14px;
            margin-bottom: 9px;

            border-radius: 12px;
            background: rgba(255,255,255,.025);
        }}

        .alert-icon {{
            width: 34px;
            height: 34px;
            flex-shrink: 0;

            display: flex;
            align-items: center;
            justify-content: center;

            border-radius: 50%;

            font-weight: 800;
        }}

        .alert-icon.medium {{
            color: #ffbd59;
            background: rgba(255,189,89,.1);
        }}

        .alert-icon.low {{
            color: #61a0ff;
            background: rgba(97,160,255,.1);
        }}

        .alert-message {{
            color: #dbe5e0;
            font-size: 12px;
        }}

        .alert-meta {{
            color: #60736b;
            font-size: 9px;
            margin-top: 5px;
        }}

        .empty {{
            padding: 25px;
            text-align: center;

            color: #4fdfa0;
            font-size: 12px;

            border-radius: 12px;
            background: rgba(79,223,160,.05);
        }}

        .equipment {{
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 10px;
        }}

        .equipment-card {{
            padding: 17px;
            border-radius: 13px;

            background: rgba(255,255,255,.025);
            border: 1px solid rgba(255,255,255,.05);
        }}

        .equipment-icon {{
            font-size: 20px;
            margin-bottom: 10px;
        }}

        .equipment-name {{
            font-size: 13px;
            font-weight: 700;
        }}

        .equipment-status {{
            color: #4fdfa0;
            font-size: 9px;
            margin-top: 5px;
        }}

        .requirements {{
            list-style: none;
        }}

        .requirements li {{
            padding: 10px 0;

            border-bottom: 1px solid
                rgba(255,255,255,.045);

            color: #83948d;
            font-size: 11px;
        }}

        .requirements li:last-child {{
            border-bottom: none;
        }}

        .requirements li::before {{
            content: "✓";
            color: #4fdfa0;
            font-weight: 800;
            margin-right: 9px;
        }}

        .loading {{
            padding: 50px;
            text-align: center;
            color: #63756e;
        }}

        .error {{
            padding: 30px;
            border-radius: 15px;

            color: #ff8e8e;
            background: rgba(255,80,80,.06);
            border: 1px solid rgba(255,80,80,.12);
        }}

        @media (max-width: 900px) {{
            .dashboard-grid {{
                grid-template-columns: repeat(2, 1fr);
            }}

            .content-grid {{
                grid-template-columns: 1fr;
            }}
        }}

        @media (max-width: 600px) {{
            .site-header {{
                flex-direction: column;
            }}

            .dashboard-grid {{
                grid-template-columns: 1fr;
            }}

            .equipment {{
                grid-template-columns: 1fr;
            }}

            .page {{
                padding: 40px 5% 70px;
            }}
        }}
    </style>
</head>

<body>

<nav class="navbar">

    <a href="/" class="logo">
        <div class="logo-mark">⛏</div>
        <div class="logo-name">
            MINE<span>CORE</span>
        </div>
    </a>

    <a href="/" class="back-link">
        ← Back to Mining Sites
    </a>

</nav>

<main class="page">

    <div class="breadcrumb">
        MineCore / Mining Sites /
        <span>{site["name"]}</span>
    </div>

    <header class="site-header">

        <div>
            <div class="eyebrow">
                Site Operations Dashboard
            </div>

            <h1 id="siteName">
                {site["name"]}
            </h1>

            <div class="location">
                📍 {site["location"]}
            </div>
        </div>

        <div
            id="safetyStatus"
            class="status good"
        >
            Loading...
        </div>

    </header>

    <div id="dashboardContent">

        <div class="loading">
            Loading site operations...
        </div>

    </div>

</main>


<script>

const siteId = {site_id};


function escapeHtml(value) {{
    if (value === null || value === undefined) {{
        return "";
    }}

    return String(value)
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}}


function getProgress(status) {{

    const values = {{
        "Active": 82,
        "Processing": 58,
        "Transportation": 72
    }};

    return values[status] || 50;
}}


function renderDashboard(data) {{

    const site = data.site;
    const operation = data.operation;
    const production = data.production;
    const safety = data.safety;
    const equipment = data.equipment;
    const alerts = data.alerts || [];

    document.getElementById("siteName").textContent =
        site.name;

    const safetyStatus =
        document.getElementById("safetyStatus");

    safetyStatus.textContent =
        safety.status;

    safetyStatus.className =
        "status " +
        (
            safety.status.toLowerCase() === "good"
                ? "good"
                : "warning"
        );


    const progress =
        getProgress(production.status);


    let alertsHtml = "";

    if (alerts.length === 0) {{

        alertsHtml = `
            <div class="empty">
                ✓ No open safety alerts
            </div>
        `;

    }} else {{

        alertsHtml = alerts.map(function(alert) {{

            const severity =
                alert.severity.toLowerCase();

            return `
                <div class="alert">

                    <div class="alert-icon ${{severity}}">
                        !
                    </div>

                    <div>

                        <div class="alert-message">
                            ${{escapeHtml(alert.message)}}
                        </div>

                        <div class="alert-meta">
                            ${{escapeHtml(alert.severity)}}
                            ·
                            ${{escapeHtml(alert.status)}}
                        </div>

                    </div>

                </div>
            `;

        }}).join("");

    }}


    let equipmentHtml = "";

    if (!equipment.items || equipment.items.length === 0) {{

        equipmentHtml = `
            <div class="empty">
                No equipment currently assigned
            </div>
        `;

    }} else {{

        equipmentHtml = equipment.items.map(function(item) {{

            return `
                <div class="equipment-card">

                    <div class="equipment-icon">
                        ⛏
                    </div>

                    <div class="equipment-name">
                        ${{escapeHtml(item.name)}}
                    </div>

                    <div class="equipment-status">
                        ● ${{escapeHtml(item.status)}}
                    </div>

                </div>
            `;

        }}).join("");

    }}


    const currentStage =
        data.operation.stage_id;


    document.getElementById("dashboardContent").innerHTML = `

        <div class="dashboard-grid">

            <div class="metric">

                <div class="metric-label">
                    Production Today
                </div>

                <div class="metric-value blue">
                    ${{Number(
                        production.production_today
                    ).toLocaleString()}}

                    <span style="
                        font-size:10px;
                        color:#60736b;
                    ">
                        TONS
                    </span>
                </div>

            </div>


            <div class="metric">

                <div class="metric-label">
                    Production Status
                </div>

                <div class="metric-value green">
                    ${{escapeHtml(production.status)}}
                </div>

            </div>


            <div class="metric">

                <div class="metric-label">
                    Open Safety Alerts
                </div>

                <div class="metric-value orange">
                    ${{safety.open_alerts}}
                </div>

            </div>


            <div class="metric">

                <div class="metric-label">
                    Equipment
                </div>

                <div class="metric-value blue">
                    ${{equipment.operational}}/${{
                        equipment.total
                    }}
                </div>

            </div>

        </div>


        <div class="content-grid">

            <div>

                <div class="panel">

                    <div class="panel-title">
                        <h2>Current Operation</h2>

                        <span>
                            Stage ${{operation.stage_id}}
                        </span>
                    </div>

                    <div class="stage-box">

                        <div class="stage-label">
                            Current Mining Stage
                        </div>

                        <div class="stage-name">
                            ${{escapeHtml(
                                operation.current_stage
                            )}}
                        </div>

                        <div class="stage-status">
                            ● ${{escapeHtml(
                                operation.stage_status
                            )}}
                        </div>

                    </div>

                    <div class="progress-heading">

                        <span>
                            Operational progress
                        </span>

                        <span>
                            ${{progress}}%
                        </span>

                    </div>

                    <div class="progress-track">

                        <div
                            class="progress-fill"
                            style="width:${{progress}}%"
                        ></div>

                    </div>

                </div>


                <div class="panel">

                    <div class="panel-title">

                        <h2>Equipment</h2>

                        <span>
                            ${{equipment.operational}} /
                            ${{equipment.total}}
                            operational
                        </span>

                    </div>

                    <div class="equipment">
                        ${{equipmentHtml}}
                    </div>

                </div>

            </div>


            <div>

                <div class="panel" id="alerts">

                    <div class="panel-title">

                        <h2>Safety Alerts</h2>

                        <span>
                            ${{safety.open_alerts}} open
                        </span>

                    </div>

                    ${{alertsHtml}}

                </div>


                <div class="panel">

                    <div class="panel-title">
                        <h2>Site Information</h2>
                    </div>

                    <div style="
                        color:#758780;
                        font-size:11px;
                        line-height:1.8;
                    ">

                        <div>
                            <strong style="color:#dbe5e0;">
                                Site:
                            </strong>

                            ${{escapeHtml(site.name)}}
                        </div>

                        <div>
                            <strong style="color:#dbe5e0;">
                                Location:
                            </strong>

                            ${{escapeHtml(site.location)}}
                        </div>

                        <div>
                            <strong style="color:#dbe5e0;">
                                Stage:
                            </strong>

                            ${{escapeHtml(
                                operation.current_stage
                            )}}
                        </div>

                        <div>
                            <strong style="color:#dbe5e0;">
                                Production:
                            </strong>

                            ${{escapeHtml(
                                production.status
                            )}}
                        </div>

                    </div>

                </div>

            </div>

        </div>
    `;

    loadRequirements(currentStage);
}}


async function loadRequirements(stageId) {{

    try {{

        const response =
            await fetch(
                `/api/mining/stages/${{stageId}}/safety`
            );

        if (!response.ok) {{
            return;
        }}

        const data =
            await response.json();

        const panel =
            document.querySelector(
                ".content-grid > div:first-child"
            );

        if (!panel) {{
            return;
        }}

        const requirementsHtml =
            data.safety_requirements
                .map(function(requirement) {{

                    return `
                        <li>
                            ${{escapeHtml(requirement)}}
                        </li>
                    `;

                })
                .join("");

        panel.insertAdjacentHTML(
            "beforeend",
            `
                <div class="panel">

                    <div class="panel-title">

                        <h2>
                            Safety Requirements
                        </h2>

                        <span>
                            ${{data.requirement_count}}
                            requirements
                        </span>

                    </div>

                    <ul class="requirements">
                        ${{requirementsHtml}}
                    </ul>

                </div>
            `
        );

    }} catch (error) {{

        console.error(
            "Unable to load safety requirements:",
            error
        );

    }}
}}


async function loadDashboard() {{

    try {{

        const response =
            await fetch(
                `/api/dashboard/${{siteId}}`
            );

        if (!response.ok) {{

            throw new Error(
                "Unable to load site dashboard."
            );

        }}

        const data =
            await response.json();

        renderDashboard(data);

    }} catch (error) {{

        document.getElementById(
            "dashboardContent"
        ).innerHTML = `

            <div class="error">
                Unable to load site information.
                Please try again.
            </div>

        `;

        console.error(error);
    }}
}}


loadDashboard();

</script>

</body>
</html>
"""


# ============================================================
# API ROUTES
# ============================================================

@app.get(
    "/api/mining/stages",
    response_model=List[MiningStage]
)
def get_all_stages(
    status: Optional[str] = Query(
        None,
        description="Filter stages by status"
    )
):
    stages = mining_stages

    if status:
        stages = [
            stage
            for stage in stages
            if stage["status"].lower() == status.lower()
        ]

    return stages


@app.get(
    "/api/mining/stages/{stage_id}",
    response_model=MiningStage
)
def get_stage(stage_id: int):
    stage = find_stage(stage_id)

    if not stage:
        raise HTTPException(
            status_code=404,
            detail=f"Mining stage {stage_id} not found"
        )

    return stage


@app.get("/api/mining/stages/{stage_id}/safety")
def get_safety_requirements(stage_id: int):
    stage = find_stage(stage_id)

    if not stage:
        raise HTTPException(
            status_code=404,
            detail=f"Mining stage {stage_id} not found"
        )

    return {
        "stage_id": stage["id"],
        "stage": stage["name"],
        "status": stage["status"],
        "requirement_count": len(stage["safety_requirements"]),
        "safety_requirements": stage["safety_requirements"]
    }


@app.get(
    "/api/sites",
    response_model=List[MiningSite]
)
def get_sites():
    return mining_sites


@app.get("/api/sites/{site_id}")
def get_site(site_id: int):
    site = find_site(site_id)

    if not site:
        raise HTTPException(
            status_code=404,
            detail=f"Mining site {site_id} not found"
        )

    current_stage = find_stage(site["current_stage_id"])

    return {
        "site": site,
        "current_stage": current_stage
    }


@app.get("/api/dashboard/{site_id}")
def get_dashboard(site_id: int):
    site = find_site(site_id)

    if not site:
        raise HTTPException(
            status_code=404,
            detail=f"Mining site {site_id} not found"
        )

    current_stage = find_stage(site["current_stage_id"])

    if not current_stage:
        raise HTTPException(
            status_code=404,
            detail=f"Mining stage {site['current_stage_id']} not found"
        )

    site_alerts = [
        alert
        for alert in alerts
        if alert["site_id"] == site_id
        and alert["status"] == "Open"
    ]

    equipment = current_stage.get("equipment", [])

    operational_equipment = sum(
        1
        for item in equipment
        if item["status"].lower() == "operational"
    )

    return {
        "site": {
            "id": site["id"],
            "name": site["name"],
            "location": site["location"]
        },
        "operation": {
            "current_stage": current_stage["name"],
            "stage_id": current_stage["id"],
            "stage_status": current_stage["status"]
        },
        "production": {
            "status": site["production_status"],
            "production_today": site["production_today"],
            "unit": "tons"
        },
        "safety": {
            "status": site["safety_status"],
            "open_alerts": len(site_alerts)
        },
        "equipment": {
            "total": len(equipment),
            "operational": operational_equipment,
            "items": equipment
        },
        "alerts": site_alerts
    }


@app.get("/api/sites/{site_id}/equipment")
def get_equipment(site_id: int):
    site = find_site(site_id)

    if not site:
        raise HTTPException(
            status_code=404,
            detail=f"Mining site {site_id} not found"
        )

    stage = find_stage(site["current_stage_id"])

    equipment = (
        stage.get("equipment", [])
        if stage
        else []
    )

    return {
        "site_id": site_id,
        "site": site["name"],
        "current_stage": stage["name"] if stage else None,
        "equipment_count": len(equipment),
        "equipment": equipment
    }


@app.get("/api/sites/{site_id}/alerts")
def get_alerts(
    site_id: int,
    severity: Optional[str] = Query(
        None,
        description="Filter alerts by severity"
    ),
    status: Optional[str] = Query(
        None,
        description="Filter alerts by status"
    )
):
    site = find_site(site_id)

    if not site:
        raise HTTPException(
            status_code=404,
            detail=f"Mining site {site_id} not found"
        )

    site_alerts = [
        alert
        for alert in alerts
        if alert["site_id"] == site_id
    ]

    if severity:
        site_alerts = [
            alert
            for alert in site_alerts
            if alert["severity"].lower() == severity.lower()
        ]

    if status:
        site_alerts = [
            alert
            for alert in site_alerts
            if alert["status"].lower() == status.lower()
        ]

    return {
        "site_id": site_id,
        "total": len(site_alerts),
        "alerts": site_alerts
    }


@app.get("/api/mining/stages/{stage_id}/policy-context")
def get_policy_context(stage_id: int):
    stage = find_stage(stage_id)

    if not stage:
        raise HTTPException(
            status_code=404,
            detail=f"Mining stage {stage_id} not found"
        )

    return {
        "stage_id": stage["id"],
        "stage": stage["name"],
        "policy_query": (
            f"What safety policies and requirements "
            f"apply to the {stage['name']} stage?"
        ),
        "safety_requirements": stage["safety_requirements"],
        "rag_ready": True
    }
