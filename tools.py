import logging
from livekit.agents import function_tool, RunContext
import os
from dotenv import load_dotenv
import json

load_dotenv()

@function_tool()
async def get_system_status(
    context: RunContext,
    system_id: str
) -> str:
    """
    Retrieves the current status of a SkyElectric system.

    Args:
        system_id: The unique identifier of the system.
    """
    # This is mock data. In a real application, this would fetch data from a database or API.
    mock_data = {
        "SE_MV_12345": {
            "system_id": "SE_MV_12345",
            "system_type": "SE_MV",
            "cloud_connected": True,
            "alerts": [],
            "grid": {"status": "available", "voltage": 220, "tariff": "low"},
            "solar": {"available": True, "output_kw": 3.5},
            "battery": {"soc_percent": 80, "state": "charging", "minor_self_discharge": False},
            "smart_flow": {"enabled": True, "sf_limit_percent": 30, "action": "None"},
            "power": {"home_load_kw": 1.0, "grid_power_kw": 0.0, "solar_power_kw": 3.5, "battery_power_kw": -2.5},
            "inverter": {"output_on": True},
            "working_mode_jp": None
        },
        "SE_JP_67890": {
            "system_id": "SE_JP_67890",
            "system_type": "SE_JP",
            "cloud_connected": True,
            "alerts": [],
            "grid": {"status": "available", "voltage": 200, "tariff": "none"},
            "solar": {"available": True, "output_kw": 4.0},
            "battery": {"soc_percent": 90, "state": "idle", "minor_self_discharge": False},
            "smart_flow": {"enabled": False, "sf_limit_percent": 0, "action": "None"},
            "power": {"home_load_kw": 0.5, "grid_power_kw": 0.0, "solar_power_kw": 4.0, "battery_power_kw": 0.0},
            "inverter": {"output_on": True},
            "working_mode_jp": "Green Mode 1"
        },
        "disconnected_system": {
            "system_id": "disconnected_system",
            "cloud_connected": False
        },
        "overload_fault": {
            "system_id": "overload_fault",
            "system_type": "SE_MV",
            "cloud_connected": True,
            "alerts": ["FLT0401: Inverter Output OFF", "FLT5015: Backup Overload Fault"],
            "grid": {"status": "available", "voltage": 220, "tariff": "low"},
            "solar": {"available": False, "output_kw": 0.0},
            "battery": {"soc_percent": 50, "state": "idle", "minor_self_discharge": False},
            "smart_flow": {"enabled": True, "sf_limit_percent": 30, "action": "None"},
            "power": {"home_load_kw": 0.0, "grid_power_kw": 0.0, "solar_power_kw": 0.0, "battery_power_kw": 0.0},
            "inverter": {"output_on": False},
            "working_mode_jp": None
        }
    }

    status = mock_data.get(system_id, {"error": "System ID not found"})
    return json.dumps(status)

@function_tool()
async def get_system_overview(context: RunContext, system_id: str) -> str:
    """Provides a general overview of the system."""
    overview = {
        "System Location": "Rawalpindi",
        "System Type": "SE_MV (Generation 1)",
        "Deployment Date": "16 Mar 2021",
        "Live Date": "06 Apr 2021",
        "Warranty Expiry": "06 Apr 2025",
        "Premium Services Expiry": "30 Jan 2026",
        "Solar Panels": "10.465 kW",
        "Inverter": "10 kW",
        "Battery Pack": "10 kWh (Smart Energy Storage)",
        "System State": "Online and running smoothly",
        "Components": "Operating normally",
        "Smart Flow": "Enabled — Limit set at 50%",
    }
    return json.dumps(overview)


@function_tool()
async def get_current_operating_conditions(context: RunContext, system_id: str) -> str:
    """Provides the current operating conditions of the system."""
    conditions = {
        "Battery Charge": "98% (Average health)",
        "Battery Activity": "Discharging",
        "Battery Capacity": "10 kWh",
        "Battery State of Health": "Bad (SOH < 50%)",
        "Backup Time": "6 min (current load) / 2 min (max load)",
        "Battery Contribution to Load": "0%",
        "Note": "Minor self-discharge detected",
        "Solar Contribution": "Supplying 100% of home load",
        "Grid Availability": "Available",
        "Grid Tariff": "Low Tariff Time",
        "Grid Export": "Active (system exporting to grid)",
        "System Flow Summary": "The system is producing excess solar energy, exporting it to the grid. The battery is fully charged and currently undergoing minor self-discharge.",
    }
    return json.dumps(conditions)


@function_tool()
async def get_energy_performance(context: RunContext, system_id: str, period: str) -> str:
    """Provides the energy performance of the system for a given period."""
    performance = {
        "today": {
            "PV Produced": "40 kWh",
            "PV Exported": "29 kWh",
            "PV to Load": "16 kWh",
            "PV to Battery": "1 kWh",
            "Battery to Load": "1 kWh",
            "Grid Consumed": "5 kWh (Grid → Load = 4 kWh, Grid → Battery = 1 kWh)",
            "Savings": "Rs 2,417",
            "Outages Served": "0 min",
        },
        "weekly": {
            "PV Produced": "80.21 kWh",
            "PV Exported": "59.5 kWh",
            "PV to Load": "26.11 kWh",
            "Battery to Load": "3.98 kWh",
            "Grid Consumed": "22.65 kWh",
            "Savings": "Rs 2,853.59",
        },
        "monthly": {
            "PV Produced": "805.54 kWh",
            "PV Exported": "579.75 kWh",
            "PV to Load": "238.75 kWh",
            "Battery to Load": "52.47 kWh",
            "Grid Consumed": "334.9 kWh",
            "Savings": "Rs 28,707.58",
        },
    }
    return json.dumps(performance.get(period, {}))


@function_tool()
async def get_pv_forecast(context: RunContext, system_id: str) -> str:
    """Provides the PV forecast and potential."""
    forecast = {
        "Today's PV Potential": "37.22 kWh",
        "Nearby Average PV Production": "35.53 kWh (for comparison)",
        "Tomorrow’s Predicted Generation": "34.95 kWh",
        "Tomorrow’s Average Temperature": "22.82 °C",
        "Monthly PV Potential": "776.1 kWh",
    }
    return json.dumps(forecast)


@function_tool()
async def get_component_data_sheet(context: RunContext, system_id: str, component: str) -> str:
    """Provides the data sheet for a specific component."""
    data_sheets = {
        "battery": {
            "Usable Capacity": "9.2 kWh",
            "Efficiency": "97%",
            "Depth of Discharge": "90%",
            "Cycle Life": "2000–4000 cycles (depending on DoD)",
            "Voltage": "51.2 V",
            "Max Discharge Current": "180 A",
            "Continuous Power": "10 kW",
            "Weight": "142.5 kg",
        },
        "inverter": {
            "Type": "Three Phase, 10 kW",
            "PV Input Power": "Max 14.58 kW",
            "Efficiency": "96% (DC–AC)",
            "Nominal Voltage": "400 V (L-L)",
            "Battery Mode Efficiency": "91%",
            "Smart Energy Console": "Present",
        },
    }
    return json.dumps(data_sheets.get(component, {}))

