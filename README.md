# 🔥 Battery Telemetry Heatmap Viewer

This interactive Dash application visualizes 3D heatmaps of battery module temperature data over time, using sensor logs and STL geometry overlays. It is designed for analyzing cooling performance and thermal hotspots in high-voltage packs during race events.

## 🚀 Features

- Interpolated 3D temperature maps using sensor data
- Time slider with play/pause functionality
- STL-based geometry rendering of the battery layout
- Adjustable z-slice, opacity, and module range filters
- Optional visualization of casing temperature and thermal losses

## 📁 Structure

- `app.py` – Main Dash application
- `data/endurance.csv` – Input telemetry file (CAN + temperature logs)
- `assets/` – Custom CSS and UI icons
- `models/pack_geometry.stl` – STL geometry of battery modules (optional)

## 🛠 Requirements

- Python 3.8+
- `dash`, `plotly`, `pandas`, `numpy`, `trimesh`, `scipy`

```bash
pip install -r requirements.txt
