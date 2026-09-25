# 2D Desktop Kinetics Sandbox // Frameless Physics Widget

An interactive 2D rigid-body kinematics sandbox that runs as a borderless, transparent desktop widget directly on Windows. Built using **Python**, **PyQt6**, and the **Pymunk** physics engine.


## Features

- **Translucent Desktop HUD:** Frameless window pinned directly above the desktop background with zero window chrome.
- **Rigid-Body Physics:** Particle kinematics, mass moments, restitution (elasticity), and impulse vectors simulated via Pymunk at 60 FPS.
- **Slingshot Vector Launching:** Dynamic mouse-drag impulse calculations for launching masses with variable velocity.
- **Live Telemetry:** Real-time kinetic energy ($E_k = \frac{1}{2}mv^2$) computation, active body counter, and gravity state display.
- **Zero-G Orbital Mode:** Toggle between Earth gravity ($9.8\,\text{m/s}^2$) and zero-gravity floating dynamics.



## Controls

| Action | Control |
| :--- | :--- |
| **Move Widget** | Click and drag the top header bar (top 60px) |
| **Launch Particle** | Click and drag in the arena to aim, release to launch |
| **Toggle Gravity** | Press `G` (Cycles between 9.8G and Zero-G) |
| **Clear Arena** | Press `C` |
| **Exit** | Press `Esc` |



## Installation & Running

1. **Clone the repository:**
   ```bash
   git (https://github.com/)<skshamg>/kinetics-desktop-sandbox.git
   cd kinetics-desktop-sandbox