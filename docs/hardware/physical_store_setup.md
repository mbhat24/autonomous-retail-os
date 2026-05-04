# Physical Store Setup Guide

## Store Types

### Tier 1: Assisted Small Vendor

Best for vegetable vendors and tiny shops.

Required:

- Android phone
- UPI QR printout
- Bluetooth weighing scale
- Mobile data connection
- Optional barcode scanner

Automation level:

- Voice/manual billing
- UPI payment
- Inventory tracking
- Agent recommendations

### Tier 2: Smart Kirana

Best for normal kirana/general stores.

Required:

- 2-4 IP cameras
- Edge mini PC or NVIDIA Jetson
- Router with 4G/5G backup
- Barcode scanner fallback
- Weighing scale for loose items
- UPS backup
- UPI QR/payment terminal

Automation level:

- Camera-assisted cart detection
- Auto inventory update
- UPI checkout
- Agentic replenishment

### Tier 3: Autonomous Mini Market

Best for apartments, offices, hostels, campuses, and unmanned convenience stores.

Required:

- 6-20 ceiling/shelf cameras
- Edge AI computer
- Smart entry gate or QR entry kiosk
- Smart weighing scales
- Optional smart shelf/load cells
- Optional RFID for high-value items
- UPS/inverter
- Secure network router
- Remote monitoring dashboard
- Signage for privacy and consent

Automation level:

- Autonomous entry
- Product pick/return tracking
- Auto cart
- Auto payment request
- Inventory and stockout automation
- Security alerts

## Camera Recommendations

Minimum camera specifications:

- 1080p or higher
- 25/30 FPS
- RTSP stream support
- Wide dynamic range
- Good low-light performance
- PoE preferred for reliability

Placement:

- Ceiling cameras for aisle coverage
- Shelf-facing cameras for product interaction
- Entry/exit camera for session start/end
- Billing/exception camera for audit
- Avoid blind spots near corners and high-value shelves

## Edge Compute Options

### Premium

- NVIDIA Jetson Orin Nano / Orin NX
- Best for real-time computer vision

### Mid-Tier

- Intel NUC / mini PC with GPU acceleration
- Good for small supermarkets

### Low-Cost

- Android device or CPU-only mini PC
- Use for event capture, not heavy multi-camera inference

## Sensor Fusion

Camera-only automation is risky. Production stores should combine:

- Camera events
- Shelf weight changes
- Product barcode/RFID
- Weighing scale readings
- Payment events
- Entry/exit events

## Network

Required:

- Primary broadband
- 4G/5G failover
- Static LAN IPs for cameras
- Secure Wi-Fi for devices
- VPN/tunnel for remote support

## Power

Required:

- UPS for router, edge box, cameras
- Surge protection
- Backup power for unmanned stores

## Physical Security

Required:

- Locked edge device cabinet
- Camera tamper detection
- Emergency manual unlock
- Fire safety equipment
- Clear customer privacy notice
