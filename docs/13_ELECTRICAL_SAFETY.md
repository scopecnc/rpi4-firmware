# Electrical Safety Analysis

**Document ID:** 13_ELECTRICAL_SAFETY  
**Analysis Date:** December 30, 2025  
**System:** 4-Axis CNC Robotic Microscope  
**Revision:** 1.0  
**Reviewer:** System Safety Assessment

---

## Executive Summary

This document provides a comprehensive electrical safety assessment of the robotic microscope system, covering power supply design, enclosure materials, fault protection, and compliance considerations.

**Overall Safety Rating:** **LOW-MODERATE RISK** ✓

**Key Safety Features:**
- SELV (Safety Extra-Low Voltage) 24V system
- Properly rated fusing and overcurrent protection
- Non-conductive PLA enclosure (good insulator)
- Low current levels (1A per motor driver)
- Isolated control circuits

---

## System Power Architecture

### Primary Power Supply

**Specification:**
- **Manufacturer:** Liteon
- **Model:** Industry-standard 24V DC supply
- **Output:** 24V, 5A (120W max)
- **Input:** 120/240V AC (depending on region)
- **Safety Certifications:** UL/CE listed (assumed for Liteon industrial unit)

**Power Distribution:**
```
AC Mains (120/240V)
    │
    ├─→ Liteon PSU (24V, 5A) ───┬─→ 4× TB6600 Drivers (96W)
    │                            ├─→ 60mm Fan (2.4W)
    │                            └─→ Buck Converter (5V) ──┬─→ Raspberry Pi 4 (6.5W)
    │                                                       ├─→ Teensy 4.1 (0.8W)
    │                                                       ├─→ USB Camera (1.0W)
    │                                                       └─→ 24× WS2812B LEDs (0.6W)
    │
    └─→ Monitor/Display (if applicable)
```

### Power Budget Analysis

| Load | Voltage | Current | Power | % of Supply |
|------|---------|---------|-------|-------------|
| 4× TB6600 (1A each) | 24V | 4.0A | 96W | 80% |
| 60mm Fan | 24V | 0.1A | 2.4W | 2% |
| Buck Converter Load | 5V | 3.16A | 15.8W | 13% |
| **Total System** | — | — | **114.2W** | **95%** |
| **Supply Rating** | 24V | 5A | **120W** | **100%** |
| **Design Margin** | — | — | **5.8W** | **5%** |

**Assessment:** Adequate margin for steady-state operation. Peak transients are brief (9% duty cycle).

---

## Voltage Safety Classification

### 24V DC System (SELV)

**Classification:** Safety Extra-Low Voltage (SELV)  
**Definition:** DC voltage ≤ 50V under normal conditions, ≤ 120V under fault conditions

**Safety Implications:**
- **No risk of electrocution** from direct contact with 24V rails
- **No arc flash hazard** at this voltage level
- **Touch-safe** for operators and maintenance personnel
- **Suitable for public installations** (museum kiosk environment)

**Compliance Note:** 24V DC systems are widely accepted as inherently safe for human contact in dry conditions. No additional insulation barriers required between user and internal electronics.

---

## Enclosure Material Analysis

### PLA (Polylactic Acid) Thermoplastic

**Material Properties:**
- **Dielectric Strength:** 20-50 kV/mm (excellent insulator)
- **Volume Resistivity:** ~10¹⁶ Ω·cm (very high resistance)
- **Flammability:** V-0 to HB rating (depending on formulation)
- **Thermal Stability:** Softens at 60°C, melts at 150-160°C

**Safety Assessment:**

✓ **Electrical Insulation: EXCELLENT**
- PLA is an excellent electrical insulator
- Prevents accidental contact with live 24V rails
- No conductive paths through enclosure material
- Comparable to ABS/polycarbonate for electrical safety

✓ **Thermal Considerations: ACCEPTABLE**
- System operating temperature: 30-50°C typical (see Thermal Analysis)
- PLA safe up to 60°C continuous
- **Margin:** 10-30°C above typical operating temperature
- TB6600 drivers (hottest components) reach 55-80°C peak but are thermally isolated

⚠ **Fire Safety: MODERATE CONCERN**
- PLA is combustible (organic polymer)
- Ignition temperature: ~350-400°C
- No credible ignition source in system (all components <150°C)
- **Risk level: LOW** given temperature margins

**Recommendation:** Current PLA enclosure is **electrically safe** and **thermally adequate** for this application. For enhanced fire safety in commercial deployment, consider:
- Fire-retardant PLA formulations (FR-PLA)
- UL94 V-0 rated plastics (polycarbonate, ABS-FR)
- External smoke detector if required by venue

---

## Circuit Protection Analysis

### Overcurrent Protection

**Primary Fusing (AC Input):**
- **Location:** Inside Liteon PSU
- **Type:** Internal fuse or circuit breaker
- **Rating:** Matched to 120W output (typically 2A @ 120V AC or 1A @ 240V AC)

**Secondary Fusing (24V Rails):**
- **Recommended:** Inline fuse on 24V output from PSU
- **Rating:** 5A fast-blow or 6A slow-blow
- **Purpose:** Protects wiring and drivers from short circuits

**Load-Level Protection:**
- **TB6600 Drivers:** Built-in overcurrent shutdown (1.0A setting)
- **Buck Converter:** Typically includes current limiting
- **Raspberry Pi:** Protected by USB power management

### Fault Scenarios

**Short Circuit Analysis:**

| Fault Location | Protection Mechanism | Trip Time | Consequence |
|----------------|---------------------|-----------|-------------|
| 24V rail short | PSU current limit + fuse | <1 second | PSU shutdown, no damage |
| Motor winding short | TB6600 overcurrent | <100ms | Driver shutdown, motor safe |
| 5V rail short | Buck converter foldback | <10ms | Logic system resets |
| LED array short | Current limiting resistors | N/A | Single LED failure only |

**Assessment:** Multi-layer protection provides adequate fault isolation.

---

## Grounding and EMI Considerations

### Ground Architecture

**Safety Ground (Earth):**
- **AC Input:** Liteon PSU has 3-prong AC input with safety ground
- **Chassis Ground:** PSU ground bonded to metal chassis/ground plane
- **Purpose:** Fault protection, prevents chassis from becoming energized

**Signal Ground (0V Reference):**
- **24V System:** Common negative rail for motors, drivers, fan
- **5V System:** Isolated negative rail for logic circuits
- **Ground Isolation:** Buck converter provides galvanic isolation between 24V and 5V systems

**Grounding Assessment:**
- **Safety ground: REQUIRED** for AC-powered system
- **Ground loops: NOT A CONCERN** (low-frequency DC system, no audio/video signals)
- **ESD protection: ADEQUATE** (touchscreen provides some isolation)

### Electromagnetic Compatibility (EMC)

**Emission Sources:**
- Stepper motor drivers (PWM at ~20-40 kHz)
- Buck converter (switching at ~500 kHz)
- Digital circuits (Teensy, RPi - low levels)

**Mitigation Measures:**
- Shielded motor cables (recommended for long runs)
- Bypass capacitors on power rails
- Ground plane in enclosure

**Assessment:** System operates in benign EMI environment (museum kiosk). No radio/wireless interference expected. Commercial EMC testing not required for single-unit prototype but recommended for production.

---

## Potential Hazards and Mitigation

### Hazard #1: Electrical Shock

**Voltage Level:** 24V DC (SELV)  
**Risk Level:** **VERY LOW**

**Analysis:**
- 24V DC is below threshold for human sensation (~50V)
- Dry skin resistance: 100kΩ typical → 0.24mA current (imperceptible)
- Even in wet conditions, 24V poses minimal shock hazard

**Mitigation:**
- PLA enclosure prevents casual contact with live parts
- Touchscreen interface isolates user from internal electronics
- Maintenance personnel should still use standard precautions

**Residual Risk:** Effectively zero for normal operation and maintenance.

---

### Hazard #2: Fire Risk

**Heat Sources:**
- TB6600 drivers: 55-80°C peak
- Motors: 40-60°C during operation
- Raspberry Pi: 35-50°C

**Risk Level:** **LOW**

**Analysis:**
- All component temperatures well below autoignition point of PLA (350-400°C)
- No open flames or arcing (24V DC, no switching at high voltage)
- Thermal shutdown protects drivers at 150°C (before PLA softening point of 160°C)

**Mitigation:**
- Adequate ventilation (see Thermal Analysis)
- Component thermal protection (TB6600 shutdown at 150°C)
- Keep flammable materials away from enclosure

**Residual Risk:** Very low. No credible fire initiation mechanism.

---

### Hazard #3: Mechanical Hazards from Motors

**Moving Parts:**
- 4× stepper motors with lead screws
- Specimen stage (X-Y motion)
- Objective focus (Z-axis)
- Camera positioning

**Risk Level:** **LOW-MODERATE** (pinch points, not electrical)

**Analysis:**
- Motor torque: Moderate (1A current, NEMA 17 typical)
- Speed: Slow (controlled motion, museum environment)
- Access: Enclosed in PLA housing

**Mitigation:**
- Limit switches prevent overtravel
- Software limits enforce workspace boundaries
- Touchscreen interface prevents direct access during operation
- Emergency stop (if implemented)

**Residual Risk:** Low for pinch injuries. Enclosure prevents direct contact during operation.

---

### Hazard #4: Supply Overcurrent / Overload

**Scenario:** All four motors + accessories simultaneously drawing peak current

**Peak Load:** 114W (95% of supply capacity)

**Risk Level:** **LOW**

**Analysis:**
- 5.8W margin under steady-state peak load
- Duty cycle: 9% (motors active only 3 seconds per 33-second cycle)
- Liteon PSU has built-in overcurrent protection

**Mitigation:**
- Software sequencing (motors don't start simultaneously)
- PSU current limiting prevents damage
- External fuse provides secondary protection

**Residual Risk:** PSU will shut down cleanly if overloaded. No damage expected.

---

## Compliance and Standards

### Applicable Standards (if seeking certification)

**Low Voltage Directive (LVD) - EU:**
- EN 60950-1: Safety of IT equipment
- EN 62368-1: Audio/video equipment safety
- **Status:** 24V SELV system is inherently compliant

**UL Standards - USA:**
- UL 61010-1: Electrical equipment for measurement, control, laboratory use
- UL 60950-1: IT equipment safety
- **Status:** Prototype exempt; production units should use UL-listed PSU

**IEC 60335-1 - Household Appliances:**
- Not applicable (not a household appliance)

### FCC/EMC Compliance

**Part 15 (USA) / CE (EU):**
- Class A (industrial) or Class B (residential) emission limits
- **Status:** Prototype exempt; production units may require EMC testing
- **Recommendation:** Use shielded motor cables, ferrite beads on power supply

### Museum/Public Installation Requirements

**Venue-Specific Considerations:**
- Fire marshal approval (varies by jurisdiction)
- Electrical inspection (if hardwired to building power)
- ADA compliance (if applicable)
- Liability insurance requirements

**Recommendation:** Consult with venue management for specific electrical safety requirements.

---

## Safety Checklist for Deployment

### Pre-Installation

- [ ] Verify PSU is UL/CE listed and properly rated
- [ ] Inspect all wiring for damage, proper gauge (minimum 18 AWG for 24V)
- [ ] Confirm TB6600 current setting: 1.0A (DIP switches SW5=ON, SW6=OFF)
- [ ] Test emergency stop functionality (if implemented)
- [ ] Verify limit switches are functional
- [ ] Check enclosure integrity (no cracks, loose parts)

### Installation

- [ ] Connect AC power through GFCI outlet (recommended for public installations)
- [ ] Verify 3-prong grounded AC connection
- [ ] Install external fuse on 24V rail (5A recommended)
- [ ] Confirm fan is operational (13.8 CFM, 24V)
- [ ] Label high-current components (drivers, PSU) with "Service Only" warnings
- [ ] Ensure ventilation slots are unobstructed

### Operational Testing

- [ ] Measure 24V rail voltage under load (should be 23.5-24.5V)
- [ ] Measure 5V rail voltage under load (should be 4.9-5.1V)
- [ ] Verify motor current draw: ≤1A per driver
- [ ] Check TB6600 heatsink temperatures: <100°C after extended run
- [ ] Test overcurrent protection by simulating motor stall
- [ ] Run 100-cycle auto-cycle test to verify thermal stability

### Maintenance Schedule

**Monthly:**
- Inspect AC power cord for damage
- Check cooling fan operation
- Clean ventilation slots

**Quarterly:**
- Verify limit switch functionality
- Test emergency stop (if present)
- Inspect motor wiring for wear

**Annually:**
- Professional electrical inspection (if required by venue)
- Thermal imaging of drivers/PSU to detect hot spots
- Replace cooling fan if bearing noise develops

---

## Risk Assessment Summary

| Hazard | Severity | Probability | Risk Level | Mitigation |
|--------|----------|-------------|------------|------------|
| Electrical shock (24V) | Minor | Very Low | **LOW** | SELV voltage, PLA enclosure |
| Fire (component failure) | Moderate | Very Low | **LOW** | Thermal protection, ventilation |
| Fire (PLA enclosure) | Moderate | Very Low | **LOW** | Component temps <150°C, FR-PLA option |
| Overcurrent/PSU failure | Minor | Low | **LOW** | Fused supply, current limiting |
| Mechanical pinch | Minor | Low | **LOW** | Enclosure, limit switches |
| EMI interference | Negligible | Low | **VERY LOW** | DC motors, low-frequency system |

**Overall System Risk:** **LOW-MODERATE**

**Justification:** The 24V SELV design, non-conductive enclosure, and multiple layers of overcurrent protection result in a system with inherently low electrical hazards. Fire risk is minimal given the large temperature margins between operating conditions and material limits. Mechanical hazards are the primary concern but are well-controlled by enclosure and software limits.

---

## Recommendations for Production Units

### Required Improvements

1. **Fusing:**
   - Add external 5A fuse on 24V rail (between PSU and drivers)
   - Use automotive blade fuse holder for easy replacement

2. **Wiring:**
   - Minimum 18 AWG wire for 24V distribution (current: 16 AWG for margin)
   - Ferrules on all screw terminal connections
   - Cable management to prevent chafing

3. **Labeling:**
   - "CAUTION: 24V DC" labels on PSU and driver area
   - "SERVICE ONLY - DO NOT OPEN" on enclosure panels
   - Wiring diagram inside access panel

### Optional Enhancements

1. **Fire Safety:**
   - Upgrade to FR-PLA or UL94 V-0 rated plastic
   - Thermal fuse on TB6600 heatsinks (150°C cutoff)
   - Smoke detector integration

2. **Electrical Protection:**
   - GFCI-protected AC outlet (for wet environments)
   - Surge protection on AC input
   - Reverse polarity protection on 24V rail

3. **Monitoring:**
   - Voltage monitoring (24V and 5V rails)
   - Current monitoring (detect motor stall, verify operation)
   - Temperature sensor (DS18B20) for thermal dashboard

---

## Conclusions

The robotic microscope system demonstrates **sound electrical safety design** appropriate for a prototype or limited-production museum kiosk. The use of 24V SELV, non-conductive enclosure, and multiple protection layers results in a **low-risk electrical system**.

**Key Strengths:**
- Inherently safe 24V operating voltage
- PLA enclosure provides excellent electrical insulation
- Multi-layer overcurrent protection
- Low thermal stress on components
- Suitable for public installation with minimal risk

**Recommended Actions:**
- Add external fusing on 24V rail (quick win)
- Use UL/CE-listed PSU for production (compliance)
- Consider FR-PLA for enhanced fire safety (optional)
- Label high-voltage areas clearly (best practice)

**Safety Sign-Off:** System approved for continued prototype operation and limited deployment. For commercial production, implement recommended fusing and labeling enhancements.

---

## Appendix: Safety References

### Standards and Guidelines

- **IEC 60950-1:** Information Technology Equipment - Safety
- **IEC 61010-1:** Safety Requirements for Electrical Equipment for Measurement, Control, and Laboratory Use
- **UL 61010-1:** Standard for Electrical Equipment for Laboratory Use
- **NFPA 70 (NEC):** National Electrical Code (USA)
- **IEC 60529:** IP Rating System (dust/water ingress)

### Voltage Classification

| Voltage Range | Classification | Safety Requirements |
|---------------|----------------|---------------------|
| < 50V DC | SELV (Safety Extra-Low Voltage) | Touch-safe, minimal protection |
| 50-120V DC | Low Voltage | Insulation required, not inherently safe |
| > 120V DC | High Voltage | Strict insulation, interlocks, labeling |

### Useful Contacts

- **Underwriters Laboratories (UL):** www.ul.com
- **CE Marking / EU Compliance:** Local Notified Body
- **Electrical Safety Foundation International:** www.esfi.org

---

**End of Electrical Safety Analysis**
