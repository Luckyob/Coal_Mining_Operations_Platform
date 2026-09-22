from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime, timezone
import re


# Password Security Analyzer

def analyze_password(password: str) -> dict:
    score = 0

    checks = {
        "minimum_length": len(password) >= 12,
        "uppercase": bool(re.search(r"[A-Z]", password)),
        "lowercase": bool(re.search(r"[a-z]", password)),
        "number": bool(re.search(r"[0-9]", password)),
        "special_character": bool(re.search(r"[^A-Za-z0-9]", password)),
    }

    if checks["minimum_length"]:
        score += 25

    if checks["uppercase"]:
        score += 15

    if checks["lowercase"]:
        score += 15

    if checks["number"]:
        score += 15

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

    recommendations = []

    if not checks["minimum_length"]:
        recommendations.append("Use at least 12 characters.")

    if not checks["uppercase"]:
        recommendations.append("Add at least one uppercase letter.")

    if not checks["lowercase"]:
        recommendations.append("Add at least one lowercase letter.")

    if not checks["number"]:
        recommendations.append("Add at least one number.")

    if not checks["special_character"]:
        recommendations.append("Add at least one special character.")

    if len(password) < 16:
        recommendations.append(
            "Consider using 16 or more characters for stronger security."
        )

    return {
        "score": score,
        "strength": strength,
        "checks": checks,
        "policy_compliant": all(checks.values()),
        "recommendations": recommendations,
    }


# FastAPI Application

app = FastAPI(
    title="MineCore",
    description="Coal Mining Operations Platform",
    version="2.0.0",
    docs_url=None,
    redoc_url=None,
    openapi_url=None,
)


# Static Files

BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"

if STATIC_DIR.exists():
    app.mount(
        "/static",
        StaticFiles(directory=str(STATIC_DIR)),
        name="static",
    )


# Data Models

class Equipment(BaseModel):
    name: str
    type: str
    status: str
    site_id: Optional[int] = None


class MiningStage(BaseModel):
    id: int
    name: str
    status: str
    description: str
    equipment: List[str] = Field(default_factory=list)


class MiningSite(BaseModel):
    id: int
    name: str
    location: str
    current_stage: int
    status: str
    safety_status: str
    production: int


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
    password: str


# Mining Stages

mining_stages = [
    MiningStage(
        id=1,
        name="Exploration",
        status="Completed",
        description="Geological exploration and coal reserve identification.",
        equipment=[],
    ),
    MiningStage(
        id=2,
        name="Site Planning",
        status="Completed",
        description="Mine planning, surveying and operational preparation.",
        equipment=[],
    ),
    MiningStage(
        id=3,
        name="Mine Development",
        status="Completed",
        description="Development of mine infrastructure and access routes.",
        equipment=[],
    ),
    MiningStage(
        id=4,
        name="Extraction",
        status="Active",
        description="Coal extraction using mining equipment.",
        equipment=["Excavator", "Haul Truck"],
    ),
    MiningStage(
        id=5,
        name="Coal Processing",
        status="Pending",
        description="Processing and preparation of extracted coal.",
        equipment=[],
    ),
    MiningStage(
        id=6,
        name="Transportation",
        status="Pending",
        description="Transportation of processed coal.",
        equipment=[],
    ),
    MiningStage(
        id=7,
        name="Storage / Distribution",
        status="Pending",
        description="Storage and distribution of coal products.",
        equipment=[],
    ),
    MiningStage(
        id=8,
        name="Environmental Monitoring & Reclamation",
        status="Pending",
        description="Environmental monitoring and reclamation activities.",
        equipment=[],
    ),
]


# Mining Sites

mining_sites = [
    MiningSite(
        id=1,
        name="Site A",
        location="Mining Zone A",
        current_stage=4,
        status="Active",
        safety_status="Good",
        production=1250,
    ),
    MiningSite(
        id=2,
        name="Site B",
        location="Mining Zone B",
        current_stage=4,
        status="Active",
        safety_status="Warning",
        production=980,
    ),
    MiningSite(
        id=3,
        name="Site C",
        location="Mining Zone C",
        current_stage=5,
        status="Processing",
        safety_status="Good",
        production=760,
    ),
    MiningSite(
        id=4,
        name="Site D",
        location="Mining Zone D",
        current_stage=6,
        status="Transportation",
        safety_status="Good",
        production=1120,
    ),
]


# Safety Alerts

alerts = [
    Alert(
        id=1,
        site_id=1,
        severity="Medium",
        message="Excavator inspection is due.",
        status="Open",
    ),
    Alert(
        id=2,
        site_id=1,
        severity="Low",
        message="PPE compliance review is scheduled.",
        status="Open",
    ),
]


# Helper Functions

def find_site(site_id: int) -> MiningSite:
    for site in mining_sites:
        if site.id == site_id:
            return site

    raise HTTPException(
        status_code=404,
        detail="Mining site not found",
    )


def find_stage(stage_id: int) -> MiningStage:
    for stage in mining_stages:
        if stage.id == stage_id:
            return stage

    raise HTTPException(
        status_code=404,
        detail="Mining stage not found",
    )


def escape_html(value) -> str:
    if value is None:
        return ""

    return (
        str(value)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("'", "&#039;")
    )


# Health Check

@app.get("/health", response_model=HealthResponse)
def health_check():
    return HealthResponse(
        status="healthy",
        service="MineCore",
        version="2.0.0",
        timestamp=datetime.now(timezone.utc).isoformat(),
    )


# Password Security API

@app.post("/api/security/password")
def password_security(request: PasswordRequest):
    return analyze_password(request.password)


# Mining Stage API

@app.get("/api/mining/stages")
def get_mining_stages(
    status: Optional[str] = Query(default=None),
):
    if status:
        return [
            stage
            for stage in mining_stages
            if stage.status.lower() == status.lower()
        ]

    return mining_stages


@app.get("/api/mining/stages/{stage_id}")
def get_mining_stage(stage_id: int):
    return find_stage(stage_id)


@app.get("/api/mining/stages/{stage_id}/safety")
def get_stage_safety(stage_id: int):
    stage = find_stage(stage_id)

    related_alerts = [
        alert
        for alert in alerts
        if alert.status.lower() == "open"
    ]

    return {
        "stage_id": stage.id,
        "stage": stage.name,
        "safety_status": "Good",
        "checks": [
            {
                "name": "PPE compliance",
                "status": "Required",
            },
            {
                "name": "Equipment inspection",
                "status": "Required",
            },
            {
                "name": "Emergency procedures",
                "status": "Ready",
            },
            {
                "name": "Environmental controls",
                "status": "Monitored",
            },
        ],
        "open_alerts": len(related_alerts),
        "equipment": stage.equipment,
    }


@app.get("/api/mining/stages/{stage_id}/policy-context")
def get_policy_context(stage_id: int):
    stage = find_stage(stage_id)

    return {
        "stage_id": stage.id,
        "stage": stage.name,
        "status": stage.status,
        "description": stage.description,
        "equipment": stage.equipment,
        "policy_context": (
            f"MineCore policy context for the {stage.name} stage. "
            f"Current status: {stage.status}. "
            f"{stage.description}"
        ),
    }


# Sites API

@app.get("/api/sites")
def get_sites():
    return mining_sites


@app.get("/api/sites/{site_id}")
def get_site(site_id: int):
    return find_site(site_id)


@app.get("/api/dashboard/{site_id}")
def get_dashboard(site_id: int):
    site = find_site(site_id)
    stage = find_stage(site.current_stage)

    site_alerts = [
        alert
        for alert in alerts
        if alert.site_id == site.id
    ]

    return {
        "site": site,
        "stage": stage,
        "alerts": site_alerts,
        "equipment": stage.equipment,
        "production": site.production,
    }


@app.get("/api/sites/{site_id}/equipment")
def get_site_equipment(site_id: int):
    site = find_site(site_id)
    stage = find_stage(site.current_stage)

    equipment = []

    for item in stage.equipment:
        equipment.append(
            Equipment(
                name=item,
                type="Mining Equipment",
                status="Operational",
                site_id=site.id,
            )
        )

    return equipment


@app.get("/api/sites/{site_id}/alerts")
def get_site_alerts(
    site_id: int,
    severity: Optional[str] = Query(default=None),
    status: Optional[str] = Query(default=None),
):
    find_site(site_id)

    results = [
        alert
        for alert in alerts
        if alert.site_id == site_id
    ]

    if severity:
        results = [
            alert
            for alert in results
            if alert.severity.lower() == severity.lower()
        ]

    if status:
        results = [
            alert
            for alert in results
            if alert.status.lower() == status.lower()
        ]

    return results


# Homepage Calculations

total_production = sum(
    site.production
    for site in mining_sites
)

active_sites = sum(
    1
    for site in mining_sites
    if site.status.lower() == "active"
)

open_alerts = sum(
    1
    for alert in alerts
    if alert.status.lower() == "open"
)

all_equipment = []

for stage in mining_stages:
    for item in stage.equipment:
        all_equipment.append(item)

total_equipment = len(all_equipment)
operational_equipment = total_equipment

equipment_percentage = (
    int((operational_equipment / total_equipment) * 100)
    if total_equipment
    else 0
)


# Homepage

@app.get("/", response_class=HTMLResponse)
def homepage():

    site_cards = ""

    for site in mining_sites:
        site_cards += f"""
        <a class="site-card" href="/sites/{site.id}">
            <div class="site-card-top">
                <div>
                    <span class="site-label">MINING SITE</span>
                    <h3>{escape_html(site.name)}</h3>
                </div>

                <span class="status-badge">
                    {escape_html(site.status)}
                </span>
            </div>

            <p class="location">
                {escape_html(site.location)}
            </p>

            <div class="site-card-bottom">
                <span>
                    Safety:
                    <strong>{escape_html(site.safety_status)}</strong>
                </span>

                <span>
                    {site.production:,} tons
                </span>
            </div>
        </a>
        """

    stage_rows = ""

    for stage in mining_stages:
        status_class = stage.status.lower().replace(" ", "-")

        stage_rows += f"""
        <div class="stage-row">
            <div class="stage-number">
                {stage.id}
            </div>

            <div class="stage-info">
                <strong>{escape_html(stage.name)}</strong>

                <span>
                    {escape_html(stage.description)}
                </span>
            </div>

            <span class="stage-status {status_class}">
                {escape_html(stage.status)}
            </span>
        </div>
        """

    alert_rows = ""

    for alert in alerts:
        alert_rows += f"""
        <div class="alert-row">
            <div class="alert-severity {alert.severity.lower()}">
                {escape_html(alert.severity)}
            </div>

            <div class="alert-message">
                <strong>{escape_html(alert.message)}</strong>
                <span>Site {alert.site_id}</span>
            </div>

            <span class="alert-status">
                {escape_html(alert.status)}
            </span>
        </div>
        """

    html = """
<!DOCTYPE html>
<html lang="en">

<head>

    <meta charset="UTF-8">

    <meta
        name="viewport"
        content="width=device-width, initial-scale=1.0"
    >

    <title>MineCore | Coal Mining Operations Platform</title>

    <style>

        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }

        html {
            scroll-behavior: smooth;
        }

        body {
            font-family: Arial, Helvetica, sans-serif;
            background: #020b07;
            color: #f5f7f6;
            line-height: 1.5;
        }

        a {
            color: inherit;
            text-decoration: none;
        }

        nav {
            background: #030b08;
            border-bottom: 1px solid rgba(255,255,255,.05);
            padding: 22px max(6%, calc((100vw - 1080px) / 2));
            display: flex;
            align-items: center;
            justify-content: space-between;
        }

        .logo {
            font-size: 19px;
            font-weight: 800;
            color: #fff;
        }

        .logo span {
            color: #4f8cff;
        }

        .nav-links {
            display: flex;
            gap: 26px;
            list-style: none;
        }

        .nav-links a {
            color: #aeb9b4;
            font-size: 12px;
        }

        .nav-links a:hover {
            color: #fff;
        }

        .hero {
            background:
                radial-gradient(
                    circle at 75% 35%,
                    rgba(24, 80, 55, .12),
                    transparent 35%
                ),
                #020b07;

            color: white;

            padding:
                70px
                max(6%, calc((100vw - 1080px) / 2))
                105px;
        }

        .hero-content {
            max-width: 850px;
        }

        .eyebrow {
            color: #4f8cff;
            font-size: 10px;
            font-weight: 800;
            letter-spacing: 1.8px;
            margin-bottom: 18px;
        }

        .hero h1 {
            font-size: clamp(48px, 7vw, 76px);
            line-height: .98;
            letter-spacing: -3px;
            margin-bottom: 25px;
        }

        .hero h1 .blue {
            color: #4f8cff;
        }

        .hero p {
            max-width: 700px;
            color: #a8b5ae;
            font-size: 15px;
            line-height: 1.7;
        }

        .hero-buttons {
            margin-top: 30px;
            display: flex;
            gap: 12px;
        }

        .button {
            display: inline-flex;
            align-items: center;
            padding: 12px 20px;
            border-radius: 24px;
            font-size: 12px;
            font-weight: 800;
        }

        .button-primary {
            background: #1769ff;
            color: white;
            box-shadow: 0 8px 25px rgba(23,105,255,.25);
        }

        .button-secondary {
            border: 1px solid #3d4944;
            color: #d8dfdb;
        }

        main {
            background: #020b07;
        }

        .container {
            width: min(1080px, 88%);
            margin: 0 auto;
        }

        .stats {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            background: #061812;
            border: 1px solid #17352a;
            border-radius: 15px;
            overflow: hidden;
            margin-top: -48px;
            position: relative;
            z-index: 2;
        }

        .stat-card {
            background: transparent;
            padding: 25px 20px;
            border-right: 1px solid #17352a;
            box-shadow: none;
        }

        .stat-card:last-child {
            border-right: 0;
        }

        .stat-label {
            color: #65766e;
            font-size: 9px;
            font-weight: 700;
            letter-spacing: .5px;
        }

        .stat-value {
            color: #fff;
            font-size: 23px;
            font-weight: 800;
            margin-top: 7px;
        }

        .stat-card:nth-child(1) .stat-value,
        .stat-card:nth-child(4) .stat-value {
            color: #4f8cff;
        }

        .stat-card:nth-child(2) .stat-value {
            color: #45d48a;
        }

        .stat-card:nth-child(3) .stat-value {
            color: #ffb340;
        }

        section {
            padding: 75px 0;
        }

        .section-heading {
            margin-bottom: 30px;
        }

        .section-heading h2 {
            color: #fff;
            font-size: 30px;
            letter-spacing: -1px;
        }

        .section-heading p {
            color: #687870;
            font-size: 12px;
        }

        .sites-grid {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 14px;
        }

        .site-card {
            background: #061812;
            border: 1px solid #17352a;
            padding: 24px;
            border-radius: 14px;
            transition: .2s ease;
        }

        .site-card:hover {
            border-color: #275440;
            transform: translateY(-2px);
        }

        .site-card-top {
            display: flex;
            justify-content: space-between;
        }

        .site-label {
            color: #527065;
            font-size: 9px;
            font-weight: 700;
            letter-spacing: 1px;
        }

        .site-card h3 {
            color: #fff;
            font-size: 20px;
            margin-top: 4px;
        }

        .status-badge {
            background: rgba(69,212,138,.1);
            color: #45d48a;
            border: 1px solid rgba(69,212,138,.15);
            padding: 4px 9px;
            border-radius: 20px;
            font-size: 9px;
        }

        .location {
            color: #718078;
            font-size: 12px;
            margin: 15px 0;
        }

        .site-card-bottom {
            border-top: 1px solid #17352a;
            padding-top: 14px;
            display: flex;
            justify-content: space-between;
            color: #718078;
            font-size: 11px;
        }

        .site-card-bottom strong {
            color: #45d48a;
        }

        .dashboard-grid {
            display: grid;
            grid-template-columns: 1.3fr 1fr;
            gap: 15px;
        }

        .panel {
            background: #061812;
            border: 1px solid #17352a;
            border-radius: 14px;
            padding: 24px;
        }

        .panel h3 {
            color: #fff;
            margin-bottom: 18px;
        }

        .stage-row {
            display: flex;
            align-items: center;
            gap: 14px;
            padding: 14px 0;
            border-bottom: 1px solid #17352a;
        }

        .stage-row:last-child {
            border-bottom: 0;
        }

        .stage-number {
            width: 30px;
            height: 30px;
            min-width: 30px;
            display: grid;
            place-items: center;
            border-radius: 50%;
            background: rgba(79,140,255,.1);
            color: #4f8cff;
            font-size: 11px;
            font-weight: 800;
        }

        .stage-info {
            flex: 1;
        }

        .stage-info strong {
            display: block;
            color: #fff;
            font-size: 13px;
        }

        .stage-info span {
            display: block;
            color: #718078;
            font-size: 10px;
            margin-top: 2px;
        }

        .stage-status {
            font-size: 9px;
            font-weight: 700;
            padding: 5px 8px;
            border-radius: 15px;
            background: #11221b;
            color: #829189;
        }

        .stage-status.active {
            background: rgba(69,212,138,.1);
            color: #45d48a;
        }

        .stage-status.completed {
            background: rgba(79,140,255,.1);
            color: #4f8cff;
        }

        .stage-status.pending {
            background: rgba(255,179,64,.1);
            color: #ffb340;
        }

        .alert-row {
            display: flex;
            align-items: center;
            gap: 12px;
            padding: 14px 0;
            border-bottom: 1px solid #17352a;
        }

        .alert-row:last-child {
            border-bottom: 0;
        }

        .alert-severity {
            min-width: 50px;
            text-align: center;
            font-size: 8px;
            font-weight: 800;
            padding: 5px;
            border-radius: 12px;
        }

        .alert-severity.medium {
            background: rgba(255,179,64,.1);
            color: #ffb340;
        }

        .alert-severity.low {
            background: rgba(79,140,255,.1);
            color: #4f8cff;
        }

        .alert-message {
            flex: 1;
        }

        .alert-message strong {
            display: block;
            color: #dce4df;
            font-size: 11px;
        }

        .alert-message span {
            display: block;
            color: #65766e;
            font-size: 9px;
        }

        .alert-status {
            color: #65766e;
            font-size: 9px;
        }

        .security {
            background: #030d08;
            border-top: 1px solid #10281e;
        }

        .security-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 35px;
            align-items: start;
        }

        .security h2 {
            color: #fff;
            font-size: 30px;
            letter-spacing: -1px;
        }

        .security p {
            color: #829189;
            font-size: 13px;
            line-height: 1.7;
        }

        .password-box {
            background: #061812;
            border: 1px solid #17352a;
            border-radius: 14px;
            padding: 24px;
            color: #fff;
        }

        .password-box input {
            width: 100%;
            padding: 13px 14px;
            border: 1px solid #274439;
            background: #030d08;
            color: white;
            border-radius: 8px;
            margin-bottom: 12px;
            font-size: 13px;
            outline: none;
        }

        .password-box input:focus {
            border-color: #4f8cff;
        }

        .password-box button {
            width: 100%;
            padding: 13px;
            border: 0;
            border-radius: 8px;
            background: #1769ff;
            color: white;
            font-weight: 800;
            cursor: pointer;
        }

        #passwordResult {
            margin-top: 18px;
            display: none;
        }

        .result-score {
            font-size: 30px;
            font-weight: 800;
            color: #4f8cff;
        }

        .result-strength {
            color: #45d48a;
            font-weight: 700;
            margin: 5px 0 10px;
        }

        .result-list {
            padding-left: 18px;
            color: #829189;
            font-size: 11px;
        }

        footer {
            background: #010604;
            color: #52615a;
            border-top: 1px solid #10241b;
            text-align: center;
            padding: 30px;
            font-size: 11px;
        }

        @media (max-width: 850px) {

            .stats {
                grid-template-columns: repeat(2, 1fr);
            }

            .stat-card:nth-child(2) {
                border-right: 0;
            }

            .sites-grid,
            .dashboard-grid,
            .security-grid {
                grid-template-columns: 1fr;
            }
        }

        @media (max-width: 600px) {

            .nav-links {
                display: none;
            }

            .hero {
                padding-top: 55px;
                padding-bottom: 90px;
            }

            .hero h1 {
                font-size: 46px;
            }

            .hero-buttons {
                flex-direction: column;
                align-items: flex-start;
            }

            .stats {
                grid-template-columns: 1fr;
            }

            .stat-card {
                border-right: 0;
                border-bottom: 1px solid #17352a;
            }

            .stat-card:last-child {
                border-bottom: 0;
            }
        }

    </style>

</head>

<body>

<nav>

    <div class="logo">
        Mine<span>Core</span>
    </div>

    <ul class="nav-links">
        <li>
            <a href="#sites">Sites</a>
        </li>

        <li>
            <a href="#operations">Operations</a>
        </li>

        <li>
            <a href="#security">Security</a>
        </li>
    </ul>

</nav>

<header class="hero">

    <div class="hero-content">

        <div class="eyebrow">
            MINING OPERATIONS PLATFORM
        </div>

        <h1>
            Smarter software for<br>
            <span class="blue">mining operations.</span>
        </h1>

        <p>
            Monitor production, manage mining stages, track equipment and
            maintain operational safety across your mining sites from one
            intelligent platform.
        </p>

        <div class="hero-buttons">

            <a
                class="button button-primary"
                href="#operations"
            >
                Explore Operations →
            </a>

            <a
                class="button button-secondary"
                href="#sites"
            >
                View Mining Sites
            </a>

        </div>

    </div>

</header>

<main>

    <div class="container">

        <div class="stats">

            <div class="stat-card">

                <div class="stat-label">
                    TODAY'S PRODUCTION
                </div>

                <div class="stat-value">
                    __TOTAL_PRODUCTION__ TONS
                </div>

            </div>

            <div class="stat-card">

                <div class="stat-label">
                    ACTIVE SITES
                </div>

                <div class="stat-value">
                    __ACTIVE_SITES__
                </div>

            </div>

            <div class="stat-card">

                <div class="stat-label">
                    OPEN ALERTS
                </div>

                <div class="stat-value">
                    __OPEN_ALERTS__
                </div>

            </div>

            <div class="stat-card">

                <div class="stat-label">
                    EQUIPMENT OPERATIONAL
                </div>

                <div class="stat-value">
                    __OPERATIONAL_EQUIPMENT__/__TOTAL_EQUIPMENT__
                </div>

            </div>

        </div>

    </div>

    <section id="sites">

        <div class="container">

            <div class="section-heading">

                <h2>
                    Mining Sites
                </h2>

                <p>
                    Live overview of your active mining operations.
                </p>

            </div>

            <div class="sites-grid">

                __SITE_CARDS__

            </div>

        </div>

    </section>

    <section id="operations">

        <div class="container">

            <div class="section-heading">

                <h2>
                    Live Operations
                </h2>

                <p>
                    Track the mining lifecycle and current safety status.
                </p>

            </div>

            <div class="dashboard-grid">

                <div class="panel">

                    <h3>
                        Mining Lifecycle
                    </h3>

                    __STAGE_ROWS__

                </div>

                <div class="panel">

                    <h3>
                        Safety Alerts
                    </h3>

                    __ALERT_ROWS__

                    <div style="margin-top: 20px;">

                        <a
                            href="/sites/1#alerts"
                            style="
                                color:#4f8cff;
                                font-size:10px;
                                font-weight:700;
                            "
                        >
                            View site alerts →
                        </a>

                    </div>

                </div>

            </div>

        </div>

    </section>

    <section
        id="security"
        class="security"
    >

        <div class="container">

            <div class="security-grid">

                <div>

                    <div class="eyebrow">
                        SECURITY MODULE
                    </div>

                    <h2>
                        Password Security Analyzer
                    </h2>

                    <p style="margin-top: 14px;">
                        Analyze password strength against common security
                        requirements and receive recommendations for
                        improving password security.
                    </p>

                </div>

                <div class="password-box">

                    <input
                        id="passwordInput"
                        type="password"
                        placeholder="Enter a password to analyze"
                    >

                    <button onclick="analyzePassword()">
                        Analyze Password
                    </button>

                    <div id="passwordResult">

                        <div
                            class="result-score"
                            id="passwordScore"
                        >
                            0/100
                        </div>

                        <div
                            class="result-strength"
                            id="passwordStrength"
                        ></div>

                        <ul
                            class="result-list"
                            id="passwordRecommendations"
                        ></ul>

                    </div>

                </div>

            </div>

        </div>

    </section>

</main>

<footer>
    MineCore — Coal Mining Operations Platform
</footer>

<script>

async function analyzePassword() {

    const passwordInput =
        document.getElementById("passwordInput");

    const result =
        document.getElementById("passwordResult");

    const score =
        document.getElementById("passwordScore");

    const strength =
        document.getElementById("passwordStrength");

    const recommendations =
        document.getElementById("passwordRecommendations");

    const password = passwordInput.value;

    if (!password) {

        result.style.display = "block";

        score.textContent = "0/100";

        strength.textContent =
            "Please enter a password.";

        recommendations.innerHTML = "";

        return;
    }

    try {

        const response = await fetch(
            "/api/security/password",
            {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    password: password
                })
            }
        );

        if (!response.ok) {
            throw new Error(
                "Password analysis failed."
            );
        }

        const data = await response.json();

        result.style.display = "block";

        score.textContent =
            data.score + "/100";

        strength.textContent =
            data.strength;

        recommendations.innerHTML = "";

        if (data.recommendations.length === 0) {

            const item =
                document.createElement("li");

            item.textContent =
                "Password satisfies the required policy.";

            recommendations.appendChild(item);

        } else {

            data.recommendations.forEach(
                function(itemText) {

                    const item =
                        document.createElement("li");

                    item.textContent =
                        itemText;

                    recommendations.appendChild(item);
                }
            );
        }

    } catch (error) {

        result.style.display = "block";

        score.textContent = "Error";

        strength.textContent =
            error.message;

        recommendations.innerHTML = "";
    }
}

</script>

</body>

</html>
"""

    html = (
        html
        .replace(
            "__TOTAL_PRODUCTION__",
            f"{total_production:,}",
        )
        .replace(
            "__ACTIVE_SITES__",
            str(active_sites),
        )
        .replace(
            "__OPEN_ALERTS__",
            str(open_alerts),
        )
        .replace(
            "__OPERATIONAL_EQUIPMENT__",
            str(operational_equipment),
        )
        .replace(
            "__TOTAL_EQUIPMENT__",
            str(total_equipment),
        )
        .replace(
            "__EQUIPMENT_PERCENTAGE__",
            str(equipment_percentage),
        )
        .replace(
            "__SITE_CARDS__",
            site_cards,
        )
        .replace(
            "__STAGE_ROWS__",
            stage_rows,
        )
        .replace(
            "__ALERT_ROWS__",
            alert_rows,
        )
    )

    return HTMLResponse(content=html)


# Individual Site Dashboard

@app.get("/sites/{site_id}", response_class=HTMLResponse)
def site_dashboard(site_id: int):

    site = find_site(site_id)
    stage = find_stage(site.current_stage)

    html = """
<!DOCTYPE html>
<html lang="en">

<head>

    <meta charset="UTF-8">

    <meta
        name="viewport"
        content="width=device-width, initial-scale=1.0"
    >

    <title>__SITE_NAME__ | MineCore</title>

    <style>

        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }

        html {
            scroll-behavior: smooth;
        }

        body {
            font-family: Arial, Helvetica, sans-serif;
            background: #020b07;
            color: #f5f7f6;
            line-height: 1.5;
        }

        a {
            color: inherit;
            text-decoration: none;
        }

        nav {
            background: #030b08;
            border-bottom: 1px solid rgba(255,255,255,.05);
            padding: 22px max(6%, calc((100vw - 1080px) / 2));
            display: flex;
            align-items: center;
            justify-content: space-between;
        }

        .logo {
            font-size: 19px;
            font-weight: 800;
            color: #fff;
        }

        .logo span {
            color: #4f8cff;
        }

        .back {
            color: #aeb9b4;
            font-size: 12px;
        }

        .back:hover {
            color: #fff;
        }

        .hero {
            background:
                radial-gradient(
                    circle at 75% 35%,
                    rgba(24, 80, 55, .12),
                    transparent 35%
                ),
                #020b07;

            padding:
                60px
                max(6%, calc((100vw - 1080px) / 2))
                85px;
        }

        .container {
            width: min(1080px, 88%);
            margin: 0 auto;
        }

        .eyebrow {
            color: #4f8cff;
            font-size: 10px;
            font-weight: 800;
            letter-spacing: 1.8px;
            margin-bottom: 14px;
        }

        .hero h1 {
            color: #fff;
            font-size: clamp(45px, 6vw, 70px);
            line-height: .98;
            letter-spacing: -3px;
            margin-bottom: 16px;
        }

        .hero p {
            color: #a8b5ae;
            font-size: 14px;
        }

        .content {
            padding: 0 0 75px;
        }

        .stats {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            background: #061812;
            border: 1px solid #17352a;
            border-radius: 15px;
            overflow: hidden;
            margin-top: -45px;
            position: relative;
            z-index: 2;
        }

        .stat {
            padding: 23px 20px;
            border-right: 1px solid #17352a;
        }

        .stat:last-child {
            border-right: 0;
        }

        .stat-label {
            color: #65766e;
            font-size: 9px;
            font-weight: 700;
            letter-spacing: .5px;
        }

        .stat-value {
            color: #fff;
            font-size: 20px;
            font-weight: 800;
            margin-top: 7px;
        }

        .stat:nth-child(1) .stat-value {
            color: #45d48a;
        }

        .stat:nth-child(2) .stat-value {
            color: #45d48a;
        }

        .stat:nth-child(3) .stat-value {
            color: #4f8cff;
        }

        .grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 15px;
            margin-top: 22px;
        }

        .panel {
            background: #061812;
            border: 1px solid #17352a;
            border-radius: 14px;
            padding: 24px;
        }

        .panel h2 {
            color: #fff;
            font-size: 20px;
            margin-bottom: 18px;
        }

        .stage-box {
            background: rgba(79,140,255,.06);
            border: 1px solid #17352a;
            border-radius: 10px;
            padding: 18px;
            margin-bottom: 25px;
        }

        .stage-box strong {
            display: block;
            color: #4f8cff;
            font-size: 17px;
            margin-bottom: 5px;
        }

        .stage-box span {
            color: #829189;
            font-size: 12px;
        }

        .check {
            display: flex;
            justify-content: space-between;
            align-items: center;
            gap: 12px;
            padding: 13px 0;
            border-bottom: 1px solid #17352a;
            color: #cbd5cf;
            font-size: 12px;
        }

        .check:last-child {
            border-bottom: 0;
        }

        .check label {
            display: flex;
            align-items: center;
            gap: 8px;
        }

        .check input {
            accent-color: #4f8cff;
        }

        .check-status {
            font-size: 9px;
            font-weight: 700;
            background: rgba(69,212,138,.1);
            color: #45d48a;
            padding: 5px 8px;
            border-radius: 15px;
        }

        .alert {
            border: 1px solid #17352a;
            border-left: 3px solid #ffb340;
            background: rgba(255,179,64,.04);
            padding: 14px;
            margin-bottom: 10px;
            border-radius: 7px;
        }

        .alert strong {
            display: block;
            color: #dce4df;
            font-size: 12px;
        }

        .alert span {
            color: #829189;
            font-size: 10px;
        }

        .empty {
            color: #65766e;
            font-size: 12px;
        }

        .policy-button {
            display: inline-block;
            margin-top: 18px;
            padding: 11px 17px;
            border-radius: 22px;
            background: #1769ff;
            color: white;
            font-weight: 800;
            font-size: 11px;
            border: 0;
            cursor: pointer;
            box-shadow: 0 8px 25px rgba(23,105,255,.2);
        }

        #policyResult {
            margin-top: 15px;
            background: #030d08;
            border: 1px solid #17352a;
            border-radius: 8px;
            padding: 15px;
            display: none;
            color: #829189;
            font-size: 11px;
        }

        #policyResult strong {
            color: #4f8cff;
        }

        footer {
            background: #010604;
            color: #52615a;
            border-top: 1px solid #10241b;
            text-align: center;
            padding: 30px;
            font-size: 11px;
        }

        @media (max-width: 850px) {

            .stats,
            .grid {
                grid-template-columns: 1fr 1fr;
            }

        }

        @media (max-width: 600px) {

            .stats,
            .grid {
                grid-template-columns: 1fr;
            }

            .stat {
                border-right: 0;
                border-bottom: 1px solid #17352a;
            }

            .stat:last-child {
                border-bottom: 0;
            }

            .hero h1 {
                font-size: 45px;
            }

        }

    </style>

</head>

<body>

<nav>

    <div class="logo">
        Mine<span>Core</span>
    </div>

    <a
        class="back"
        href="/"
    >
        ← Back to Dashboard
    </a>

</nav>

<header class="hero">

    <div class="container">

        <div class="eyebrow">
            MINING SITE
        </div>

        <h1>
            __SITE_NAME__
        </h1>

        <p>
            __SITE_LOCATION__
        </p>

    </div>

</header>

<main class="content">

    <div class="container">

        <div class="stats">

            <div class="stat">

                <div class="stat-label">
                    STATUS
                </div>

                <div
                    class="stat-value"
                    id="siteStatus"
                >
                    __SITE_STATUS__
                </div>

            </div>

            <div class="stat">

                <div class="stat-label">
                    SAFETY
                </div>

                <div
                    class="stat-value"
                    id="safetyStatus"
                >
                    __SAFETY_STATUS__
                </div>

            </div>

            <div class="stat">

                <div class="stat-label">
                    PRODUCTION
                </div>

                <div class="stat-value">
                    __PRODUCTION__ tons
                </div>

            </div>

            <div class="stat">

                <div class="stat-label">
                    CURRENT STAGE
                </div>

                <div class="stat-value">
                    __STAGE_NAME__
                </div>

            </div>

        </div>

        <div class="grid">

            <div class="panel">

                <h2>
                    Current Operation
                </h2>

                <div class="stage-box">

                    <strong>
                        __STAGE_NAME__
                    </strong>

                    <span>
                        __STAGE_DESCRIPTION__
                    </span>

                </div>

                <h2>
                    Equipment
                </h2>

                <div id="equipmentList">

                    <div class="empty">
                        Loading equipment...
                    </div>

                </div>

            </div>

            <div
                class="panel"
                id="alerts"
            >

                <h2>
                    Safety Alerts
                </h2>

                <div id="alertsList">

                    <div class="empty">
                        Loading alerts...
                    </div>

                </div>

            </div>

        </div>

        <div
            class="panel"
            style="margin-top: 15px;"
        >

            <h2>
                Safety Checklist
            </h2>

            <div id="safetyChecklist">

                <div class="empty">
                    Loading safety information...
                </div>

            </div>

        </div>

        <div
            class="panel"
            style="margin-top: 15px;"
        >

            <h2>
                Policy Context
            </h2>

            <p class="empty">
                Use the policy context to connect this mining stage
                with relevant operational and safety requirements.
            </p>

            <button
                class="policy-button"
                onclick="loadPolicyContext()"
            >
                Load Policy Context
            </button>

            <div id="policyResult"></div>

        </div>

    </div>

</main>

<footer>
    MineCore — Coal Mining Operations Platform
</footer>

<script>

const siteId = __SITE_ID__;

const stageId = __STAGE_ID__;


function escapeHtml(value) {

    const div = document.createElement("div");

    div.textContent =
        value == null ? "" : value;

    return div.innerHTML;
}


async function loadDashboard() {

    try {

        const response = await fetch(
            "/api/dashboard/" + siteId
        );

        if (!response.ok) {
            throw new Error(
                "Dashboard request failed."
            );
        }

        const data = await response.json();

        const equipmentList =
            document.getElementById(
                "equipmentList"
            );

        if (
            data.equipment &&
            data.equipment.length > 0
        ) {

            equipmentList.innerHTML =
                data.equipment
                    .map(function(item) {

                        return `
                            <div class="check">

                                <span>
                                    ${escapeHtml(item)}
                                </span>

                                <span class="check-status">
                                    Operational
                                </span>

                            </div>
                        `;

                    })
                    .join("");

        } else {

            equipmentList.innerHTML =
                '<div class="empty">No equipment assigned.</div>';

        }


        const alertsList =
            document.getElementById(
                "alertsList"
            );

        if (
            data.alerts &&
            data.alerts.length > 0
        ) {

            alertsList.innerHTML =
                data.alerts
                    .map(function(alert) {

                        return `
                            <div class="alert">

                                <strong>
                                    ${escapeHtml(
                                        alert.message
                                    )}
                                </strong>

                                <span>
                                    Severity:
                                    ${escapeHtml(
                                        alert.severity
                                    )}
                                    · Status:
                                    ${escapeHtml(
                                        alert.status
                                    )}
                                </span>

                            </div>
                        `;

                    })
                    .join("");

        } else {

            alertsList.innerHTML =
                '<div class="empty">No active alerts.</div>';

        }

    } catch (error) {

        document.getElementById(
            "equipmentList"
        ).innerHTML =
            '<div class="empty">Unable to load equipment.</div>';

        document.getElementById(
            "alertsList"
        ).innerHTML =
            '<div class="empty">Unable to load alerts.</div>';

        console.error(error);
    }
}


async function loadSafety() {

    try {

        const response = await fetch(
            "/api/mining/stages/" +
            stageId +
            "/safety"
        );

        if (!response.ok) {
            throw new Error(
                "Safety request failed."
            );
        }

        const data = await response.json();

        const checklist =
            document.getElementById(
                "safetyChecklist"
            );

        if (
            data.checks &&
            data.checks.length > 0
        ) {

            checklist.innerHTML =
                data.checks
                    .map(function(item, index) {

                        return `
                            <div class="check">

                                <label>

                                    <input
                                        type="checkbox"
                                        data-check-index="${index}"
                                    >

                                    ${escapeHtml(
                                        item.name
                                    )}

                                </label>

                                <span class="check-status">
                                    ${escapeHtml(
                                        item.status
                                    )}
                                </span>

                            </div>
                        `;

                    })
                    .join("");


            document
                .querySelectorAll(
                    "#safetyChecklist input[type='checkbox']"
                )
                .forEach(function(checkbox) {

                    const key =
                        "minecore-site-" +
                        siteId +
                        "-check-" +
                        checkbox.dataset.checkIndex;

                    checkbox.checked =
                        localStorage.getItem(key) === "true";

                    checkbox.addEventListener(
                        "change",
                        function() {

                            localStorage.setItem(
                                key,
                                checkbox.checked
                            );

                        }
                    );

                });

        } else {

            checklist.innerHTML =
                '<div class="empty">No safety checks available.</div>';

        }

    } catch (error) {

        document.getElementById(
            "safetyChecklist"
        ).innerHTML =
            '<div class="empty">Unable to load safety information.</div>';

        console.error(error);
    }
}


async function loadPolicyContext() {

    const result =
        document.getElementById(
            "policyResult"
        );

    result.style.display = "block";

    result.textContent =
        "Loading policy context...";

    try {

        const response = await fetch(
            "/api/mining/stages/" +
            stageId +
            "/policy-context"
        );

        if (!response.ok) {
            throw new Error(
                "Policy request failed."
            );
        }

        const data = await response.json();

        result.innerHTML = `
            <strong>
                ${escapeHtml(data.stage)}
            </strong>

            <p style="margin-top: 8px;">
                ${escapeHtml(
                    data.policy_context
                )}
            </p>
        `;

        if (
            window.MineCore &&
            typeof window.MineCore.askPolicy === "function"
        ) {

            window.MineCore.askPolicy(data);

        }

    } catch (error) {

        result.textContent =
            "Unable to load policy context.";

        console.error(error);
    }
}


window.addEventListener(
    "DOMContentLoaded",
    function() {

        loadDashboard();
        loadSafety();

    }
);

</script>

</body>

</html>
"""

    html = (
        html
        .replace(
            "__SITE_ID__",
            str(site.id),
        )
        .replace(
            "__SITE_NAME__",
            escape_html(site.name),
        )
        .replace(
            "__SITE_LOCATION__",
            escape_html(site.location),
        )
        .replace(
            "__SITE_STATUS__",
            escape_html(site.status),
        )
        .replace(
            "__SAFETY_STATUS__",
            escape_html(site.safety_status),
        )
        .replace(
            "__PRODUCTION__",
            f"{site.production:,}",
        )
        .replace(
            "__STAGE_NAME__",
            escape_html(stage.name),
        )
        .replace(
            "__STAGE_DESCRIPTION__",
            escape_html(stage.description),
        )
        .replace(
            "__STAGE_ID__",
            str(stage.id),
        )
    )

    return HTMLResponse(content=html)

