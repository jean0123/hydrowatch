"""AI-powered data summarization using the Anthropic Claude API."""

import os
import statistics

import anthropic


def generate_summary(station, readings):
    """Generate a natural-language summary of water level data using Claude."""
    api_key = os.environ.get("ANTHROPIC_API_KEY", "")
    if not api_key:
        return _generate_fallback_summary(station, readings)

    if not readings:
        return f"No data available for station {station.name} in the requested period."

    data_context = _build_data_context(station, readings)

    client = anthropic.Anthropic(api_key=api_key)
    message = client.messages.create(
        model="claude-3-haiku-20240307",
        max_tokens=512,
        messages=[
            {
                "role": "user",
                "content": (
                    "You are a hydrological analyst. Analyze the following water "
                    "monitoring data and provide a concise 2-3 paragraph summary "
                    "suitable for a client report. Include trends, anomalies, and "
                    "any concerns. Be professional and data-driven.\n\n"
                    f"{data_context}"
                ),
            }
        ],
    )
    return message.content[0].text


def _build_data_context(station, readings):
    """Build a text summary of the data for the LLM prompt."""
    levels = [r.water_level_m for r in readings]
    flows = [r.flow_rate_cms for r in readings if r.flow_rate_cms is not None]

    context = (
        f"Station: {station.name} ({station.station_id})\n"
        f"Location: {station.latitude:.4f}°N, {station.longitude:.4f}°W\n"
        f"Period: {readings[0].timestamp:%Y-%m-%d %H:%M} to "
        f"{readings[-1].timestamp:%Y-%m-%d %H:%M}\n"
        f"Total readings: {len(readings)}\n\n"
        f"Water Level (m):\n"
        f"  Min: {min(levels):.2f}\n"
        f"  Max: {max(levels):.2f}\n"
        f"  Mean: {statistics.mean(levels):.2f}\n"
        f"  Std Dev: {statistics.stdev(levels):.3f}\n"
    )

    if flows:
        context += (
            f"\nFlow Rate (m³/s):\n"
            f"  Min: {min(flows):.2f}\n"
            f"  Max: {max(flows):.2f}\n"
            f"  Mean: {statistics.mean(flows):.2f}\n"
        )

    recent = levels[-10:]
    if len(recent) >= 2:
        trend = "rising" if recent[-1] > recent[0] else "falling"
        change = abs(recent[-1] - recent[0])
        context += f"\nRecent trend: {trend} ({change:.2f}m change over last {len(recent)} readings)\n"

    return context


def _generate_fallback_summary(station, readings):
    """Generate a basic statistical summary when the API key is not available."""
    if not readings:
        return f"No data available for station {station.name}."

    levels = [r.water_level_m for r in readings]
    return (
        f"Station {station.name} recorded {len(readings)} readings. "
        f"Water levels ranged from {min(levels):.2f}m to {max(levels):.2f}m "
        f"with a mean of {statistics.mean(levels):.2f}m. "
        f"(AI-enhanced summary unavailable — set ANTHROPIC_API_KEY for detailed analysis.)"
    )
