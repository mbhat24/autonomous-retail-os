# Physical Implementation Guide

This guide covers everything needed to physically deploy an autonomous retail store — hardware, cameras, sensors, store layout, and wiring.

---

## Store Layout

### Minimum Viable Store (100-300 sq ft)

```
┌──────────────────────────────────────────────┐
│  ┌─────┐  ┌─────┐  ┌─────┐  ┌─────┐        │
│  │SHELF│  │SHELF│  │SHELF│  │SHELF│        │
│  │  1  │  │  2  │  │  3  │  │  4  │        │
│  └─────┘  └─────┘  └─────┘  └─────┘        │
│                                              │
│  ┌─────┐  ┌─────┐  ┌─────┐  ┌─────┐        │
│  │SHELF│  │SHELF│  │SHELF│  │SHELF│        │
│  │  5  │  │  6  │  │  7  │  │  8  │        │
│  └─────┘  └─────┘  └─────┘  └─────┘        │
│                                              │
│         ┌──────────────┐                     │
│  ENTRY  │              │  EXIT               │
│  ───────│  CHECKOUT    │───────              │
│         │  ZONE        │                     │
│         └──────────────┘                     │
│                                              │
│  [Raspberry Pi + UPS + Router cabinet]       │
└──────────────────────────────────────────────┘
```

### Key Zones

| Zone | Purpose | Hardware |
|---|---|---|
| Entry | Detect customer entering, start session | 1x ceiling camera |
| Shelves (8 units) | Product display with weight sensors | 8x weight sensors, 4x shelf cameras |
| Checkout | Final cart verification, UPI QR display | 1x overhead camera, 1x display screen |
| Exit | Detect customer leaving, trigger security check | 1x door camera |
| Server Cabinet | Edge compute, UPS, network | Raspberry Pi 5, router, UPS |

---

## Hardware Bill of Materials

### Core Compute

| Item | Qty | Model | Cost (₹) | Purpose |
|---|---|---|---|---|
| Edge Computer | 1 | Raspberry Pi 5 (8GB) | ~6,000 | Runs the AI agents + FastAPI server |
| SSD | 1 | 256GB NVMe SSD + HAT | ~2,500 | Database + OS storage |
| MicroSD | 1 | 64GB Samsung EVO | ~500 | Boot drive |
| UPS | 1 | APC 600VA | ~2,500 | Power backup for Pi + router |

### Cameras

| Item | Qty | Model | Cost (₹) | Purpose |
|---|---|---|---|---|
| Ceiling Camera | 4 | Raspberry Pi Camera Module 3 Wide | ~2,000 each | Entry, checkout, exit, aisle overview |
| Shelf Camera | 4 | ESP32-CAM | ~500 each | Per-shelf product detection |
| **Total cameras** | **8** | | **~10,000** | |

### Sensors

| Item | Qty | Model | Cost (₹) | Purpose |
|---|---|---|---|---|
| Weight Sensor (Load Cell) | 8 | HX711 + 5kg load cell | ~200 each | Per-shelf weight tracking |
| PIR Motion Sensor | 2 | HC-SR501 | ~100 each | Entry/exit motion detection |
| Door Sensor | 1 | Magnetic reed switch | ~150 | Exit door open/close |

### Display & Network

| Item | Qty | Model | Cost (₹) | Purpose |
|---|---|---|---|---|
| Display Screen | 1 | 7" Raspberry Pi touchscreen | ~4,000 | UPI QR display, cart summary |
| WiFi Router | 1 | TP-Link Archer C6 | ~1,500 | Local network for cameras |
| Ethernet Cables | 5 | CAT6 1m | ~500 | Wired connections |

### Shelving & Enclosures

| Item | Qty | Cost (₹) | Purpose |
|---|---|---|---|
| Metal Shelving Units | 8 | ~1,500 each | Product display |
| Camera Mounts | 8 | ~200 each | Ceiling/shelf mounting |
| Junction Box | 1 | ~500 | Cable management |
| Power Strip | 2 | ~400 each | Power distribution |

### **Total Hardware Cost: ~₹40,000-50,000**

---

## Camera Placement

### Ceiling Cameras (4x)

```
Position: Mounted 8-9 ft high, pointing down at 15° angle

Camera 1 (Entry):  Above entry door, captures full body + face
Camera 2 (Aisle):  Center of store ceiling, wide-angle aisle coverage
Camera 3 (Checkout):Above checkout zone, top-down view of products
Camera 4 (Exit):   Above exit door, captures customer leaving
```

### Shelf Cameras (4x ESP32-CAM)

```
Position: Mounted on shelf underside, facing products at 45° angle
Coverage: 1 camera per 2 shelves, captures product pick/return

Shelf Cam 1 → Shelves 1-2
Shelf Cam 2 → Shelves 3-4
Shelf Cam 3 → Shelves 5-6
Shelf Cam 4 → Shelves 7-8
```

### Wiring

```
Each ESP32-CAM: 5V power via micro-USB → powered USB hub → Pi
Each Pi Camera:  Ribbon cable → Pi CSI port (max 2 direct)
Additional Pi Cameras: USB adapter required
PIR sensors:     3.3V, GND, DATA → Pi GPIO pins
HX711:           3.3V, GND, DT, SCK → Pi GPIO pins
```

---

## Sensor Wiring (Raspberry Pi GPIO)

```
Pi 5 GPIO Pinout:

HX711 #1 (Shelf 1):  VCC→3.3V(pin1), GND→GND(pin6), DT→GPIO17(pin11), SCK→GPIO27(pin13)
HX711 #2 (Shelf 2):  VCC→3.3V(pin17), GND→GND(pin14), DT→GPIO22(pin15), SCK→GPIO23(pin16)
... (use I2C multiplexer TCA9548A for >2 HX711)

PIR Entry:  VCC→5V(pin2), GND→GND(pin9), DATA→GPIO24(pin18)
PIR Exit:   VCC→5V(pin4), GND→GND(pin25), DATA→GPIO25(pin22)

Door Sensor: VCC→3.3V, GND→GND, DATA→GPIO26(pin37)
```

---

## Software Stack on Raspberry Pi

```bash
# 1. Flash Raspberry Pi OS Lite (64-bit) to microSD
# 2. Boot Pi, connect via SSH

# Install dependencies
sudo apt update && sudo apt install -y python3-pip python3-venv git

# Clone the repo
git clone https://github.com/mbhat24/autonomous-retail-os.git
cd autonomous-retail-os

# Setup
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev,vision]"

# Configure
cp .env.example .env
nano .env  # Add your GEMINI_API_KEY

# Enable camera
sudo raspi-config  # Interface Options → Camera → Enable

# Start on boot
sudo cp docs/retail-os.service /etc/systemd/system/
sudo systemctl enable retail-os
sudo systemctl start retail-os
```

---

## Computer Vision Pipeline

```
ESP32-CAM / Pi Camera
        ↓
  Frame capture (10 FPS)
        ↓
  YOLOv8 nano model (runs on Pi 5)
  - Person detection (entry/exit)
  - Product detection (shelf cameras)
  - Hand tracking (pick/return gesture)
        ↓
  Event generation:
  - customer_entered (person crosses entry line)
  - item_picked (hand removes product + weight drops)
  - item_returned (hand places product + weight increases)
  - customer_exited (person crosses exit line)
        ↓
  POST /events/vision → AI Agents process
```

### Weight Sensor Logic

```
Weight before event:  W1
Weight after event:   W2
Delta = W2 - W1

If delta < -threshold:  item_picked  (weight decreased)
If delta > +threshold:  item_returned (weight increased)

Product identified by: which shelf sensor triggered + camera frame
```

---

## Daily Operations (Zero Human)

| Time | Automated Action |
|---|---|
| Store open | System already running 24/7 |
| Customer enters | PIR triggers → camera confirms → session created |
| Customer picks item | Weight drops + camera sees hand → cart updated |
| Customer returns item | Weight increases + camera sees hand → cart adjusted |
| Customer at checkout | Screen shows cart + total + UPI QR |
| Payment received | UPI callback → inventory deducted → sale recorded |
| Customer exits | Door sensor + camera → security check → session closed |
| Low stock detected | Replenishment agent drafts purchase order |
| Excess perishables | Pricing agent applies discount |
| End of day | All reports auto-generated, no closing procedure |

---

## Power & Internet Requirements

| Requirement | Spec |
|---|---|
| Power | 220V AC, ~50W total draw (Pi + cameras + router + screen) |
| Backup | UPS gives ~2 hours runtime during power cuts |
| Internet | 4G dongle or broadband, min 2 Mbps for Gemini API calls |
| Fallback | System caches events locally if internet drops, replays when back |

---

## Scaling Up

### Small Store (100-300 sq ft) → This Guide
- 1 Raspberry Pi 5
- 8 cameras, 8 weight sensors
- ~₹50,000 hardware

### Medium Store (500-1000 sq ft)
- 1 Intel NUC / Jetson Orin
- 16-24 cameras, 16-24 weight sensors
- Add barcode scanner at checkout
- ~₹1,50,000 hardware

### Large Store (1000+ sq ft)
- Edge server + GPU (RTX 4060)
- 32+ IP cameras (PoE)
- Multiple checkout zones
- Digital signage throughout
- ~₹5,00,000+ hardware
