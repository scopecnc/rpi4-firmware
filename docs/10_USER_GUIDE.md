# User Guide - Museum Operator Manual

**Document:** 10 - User Guide  
**Version:** 1.0  
**Date:** December 23, 2025  
**Audience:** Museum Staff, Kiosk Operators

---

## 1. Introduction

Welcome to **The Mineral Microscope** - an interactive kiosk for exploring New Hampshire minerals under magnification. This guide will help you operate and maintain the system.

### What This System Does

The Mineral Microscope automatically displays 28 different mineral specimens from famous New Hampshire localities (Palermo Mine, Ruggles Mine, Fletcher Mine, etc.). Visitors can:
- Watch as the system automatically cycles through specimens
- Touch the screen to jump to specific minerals
- Use jog controls to manually explore specimens
- See live video of minerals at 20-100× magnification

---

## 2. Daily Operations

### Starting the System

**Power On Sequence:**
1. Turn on the main power strip
2. Raspberry Pi will boot automatically (30-60 seconds)
3. GUI will start automatically and show "DISCONNECTED" briefly
4. System will connect to motion controller ("CONNECTED")
5. **Homing Process (30 seconds):**
   - Message: "Homing in progress..."
   - You'll hear motors moving sequentially
   - Z-axis moves first (up), then Y, then X, then Focus
6. When complete, system shows first specimen and begins auto-cycle

**What You Should See:**
- Live microscope video filling the screen
- Title banner at top: "The Mineral Microscope"
- Green status indicator (circle) showing "IDLE"
- "AUTO" mode indicator
- List of 28 specimens on the left
- First specimen highlighted in blue

**Normal Startup Time:** 90 seconds from power-on to first specimen

---

### Shutting Down

**End of Day Procedure:**

**Option 1: Proper Shutdown (Recommended)**
1. Press ESC key on connected keyboard (if available)
2. System will close gracefully
3. Wait 10 seconds for Raspberry Pi to finish shutdown
4. Turn off power strip

**Option 2: Power Off (Acceptable)**
1. Simply turn off power strip
2. Raspberry Pi will shutdown when power is cut
3. No harm to system (designed for this)

**DO NOT:**
- Pull USB cables while system is running
- Turn off during homing (wait for completion)
- Forcibly restart during specimen moves

---

### Normal Operation

The system runs automatically and requires no intervention. Here's what happens:

**Auto-Cycle Behavior:**
- System moves to a new specimen every 10 seconds
- Displays mineral name, location, and collector
- Cycles through all 28 specimens continuously
- Loops back to start after finishing

**Visitor Interaction:**
- Visitors can touch any specimen name to jump directly to it
- Visitors can use jog buttons to manually explore
- When visitor touches anything, "AUTO" changes to "MANUAL"
- After 30 seconds of no touching, returns to "AUTO" mode

**You Should Hear:**
- Quiet motor whine when moving (this is normal with TB6600 drivers)
- Brief buzzing during acceleration/deceleration
- No grinding, clicking, or loud noises

---

## 3. Touch Interface Guide

### Screen Layout

```
┌──────────────────────────────────────────────────────────┐
│ ●IDLE  |  The Mineral Microscope  | X: 58mm Y: 21mm  │← Status Bar
│  AUTO  |     Tom Mortimer         | Z:  9mm F:  3mm  │
├────────┬─────────────────────────────────────────────────┤
│Specimen│                                                 │
│  List  │         Live Microscope Video                   │
│        │         (automatically updates)                 │
│  [1]   │                                                 │
│  [2]   │                     ┌──────────────────┐        │
│  [3]   │                     │ Golden Beryl     │← Info Card
│  ...   │                     │ Palermo Mine,    │
│  [28]  │                     │ North Groton     │
│        │                     │ Collected by:    │
│        │                     │ Sarah Johnson    │
│        │                     └──────────────────┘        │
│ HOME   │                                                 │
│        │              ┌─────Scale─Ruler──────┐          │
│  Jog   │              │  0 ──── 5mm ──── 10  │          │
│Controls│              └──────────────────────┘          │
└────────┴─────────────────────────────────────────────────┘
```

### Left Panel

**Specimen List (scrollable):**
- 28 buttons showing mineral names and locations
- Currently selected specimen is highlighted in **blue**
- Touch any specimen to jump to it immediately
- System enters MANUAL mode for 30 seconds

**HOME Button:**
- Returns all axes to home position
- Use if system seems "lost" or stuck
- Takes 30 seconds to complete
- System will pause auto-cycle during homing

**Jog Controls:**
- **Up/Down/Left/Right arrows:** Move specimen stage
  - Quick tap: Small movement (0.5mm)
  - Hold: Continuous movement until released
- **Focus ▲/▼:** Adjust microscope focus (Z-axis)
  - Moves 0.1mm per tap
  - Hold for continuous adjustment
- **Zoom ▲/▼:** Adjust magnification (objective position)
  - Moves 0.2mm per tap
  - Changes field of view (see scale ruler update)

### Right Side - Video Display

**Info Card (bottom-right):**
- **Mineral Name:** Large text (e.g., "Golden Beryl")
- **Location:** Where specimen was collected
- **Collector:** Who collected the specimen

**Scale Ruler (bottom-center):**
- Shows actual size of what's visible
- Updates automatically when you zoom
- Ranges from 20mm (zoomed out) to 5mm (zoomed in)

**Status Bar (top):**
- **Left:** Status indicator
  - Green ● = Working normally ("IDLE" or "MOVING")
  - Yellow ● = Connected but not homed
  - Red ● = Disconnected or error
- **Center:** Title and curator credit
- **Right:** Exact stage position in millimeters

---

## 4. Common Visitor Questions

### "How do I use this?"

**Answer:** "The microscope automatically shows different minerals. You can touch any mineral name on the left to see it immediately, or use the arrow buttons to look around. After 30 seconds, it goes back to automatic mode."

### "Why did it move by itself?"

**Answer:** "The system automatically cycles through all 28 specimens so everyone gets to see different minerals. You can take control anytime by touching the screen."

### "Can I take pictures?"

**Answer:** "Not directly from this system, but feel free to photograph the screen with your phone."

### "What magnification is this?"

**Answer:** "It ranges from about 20× to 100× depending on the zoom setting. The scale bar at the bottom shows the actual size."

### "Why does it make that noise?"

**Answer:** "That's the sound of the stepper motors moving the stage. It's completely normal - the motors vibrate at a specific frequency to move precisely."

---

## 5. Troubleshooting

### Problem: Black Screen

**Symptoms:** Screen is completely black, no video

**Solutions:**
1. Check power connections (both power strip and Raspberry Pi)
2. Wait 60 seconds - system might still be booting
3. Check HDMI cable connection
4. Try power-cycling: turn off, wait 10 seconds, turn on

**If Persistent:** USB camera may be disconnected - check cable

---

### Problem: "DISCONNECTED" Status

**Symptoms:** Red circle, says "DISCONNECTED" at top

**Cause:** Raspberry Pi cannot communicate with Teensy motion controller

**Solutions:**
1. Check USB cable between Raspberry Pi and Teensy
2. Check that Teensy has power (LED should be lit)
3. Try unplugging and reconnecting Teensy USB cable
4. Restart system (turn off/on power strip)

**If Persistent:** Contact technician - may be Teensy hardware issue

---

### Problem: Stage Won't Move

**Symptoms:** Clicking specimens or jog buttons does nothing

**Check:**
1. Status should show "IDLE" (not "MOVING" or "DISCONNECTED")
2. System must be homed first (happens automatically at startup)
3. May have hit a limit switch

**Solutions:**
1. Touch HOME button and wait 30 seconds
2. Check for obstructions blocking stage movement
3. Listen for motor noise - if silent, may be power issue
4. Restart system

---

### Problem: Video is Frozen

**Symptoms:** Video doesn't update, stage moves but video stays same

**Cause:** Video capture thread crashed

**Solutions:**
1. Touch any specimen to see if system responds
2. If system moves but video frozen, restart required
3. Power cycle system

**Prevention:** Don't unplug USB camera while system running

---

### Problem: Wrong Specimen Highlighted

**Symptoms:** Blue highlighting doesn't match current specimen

**Cause:** Minor GUI sync issue (rare)

**Solution:**
1. Touch any specimen in list
2. Highlighting should update correctly
3. No harm, purely cosmetic

---

### Problem: Stage Makes Grinding Noise

**Symptoms:** Loud grinding, clicking, or scraping sounds

**⚠️ THIS IS SERIOUS:**
1. **Immediately press HOME button** or turn off system
2. **DO NOT continue operation**
3. **Contact technician before restarting**

**Possible Causes:**
- Limit switch failure
- Mechanical obstruction
- Belt/screw jam
- Motor driver malfunction

---

### Problem: Specimen Out of Focus

**Symptoms:** Image is blurry, hard to see details

**Normal Behavior:**
- Each specimen is pre-programmed with focus settings
- Some specimens may look softer than others (natural variation)
- Lighting affects perceived sharpness

**Solutions:**
1. Use Focus jog buttons (▲/▼) to adjust manually
2. System will return to preset focus after timeout
3. Some minerals are naturally less distinct

**Not a Problem:**
- Different minerals have different textures
- Some are transparent, some opaque
- Crystal structure affects how they look under microscope

---

## 6. Maintenance

### Daily Checks (Start of Day)

**Before Opening:**
1. ✓ Power on system
2. ✓ Wait for automatic homing (30 seconds)
3. ✓ Verify first specimen displays correctly
4. ✓ Touch one specimen to verify visitor interaction works
5. ✓ Check that video is live (moves when you touch jog buttons)
6. ✓ Listen for abnormal noises

**End of Day:**
1. Power off system using ESC key or power strip
2. Clean touchscreen with microfiber cloth (screen cleaner OK)
3. **DO NOT CLEAN NEAR STAGE** - specimen tray is delicate

---

### Weekly Maintenance

**Every Week:**
1. Inspect specimen tray for dust buildup
   - Use compressed air from a distance
   - DO NOT touch specimens with hands or cloth
2. Check all cable connections
3. Verify HOME button still works correctly
4. Test random specimens to ensure full grid accessibility

---

### Monthly Maintenance

**Every Month:**
1. Clean stage rails with dry cloth
2. Check for loose screws on frame
3. Verify camera lens is clean
4. Check belt tension (should not be too loose or too tight)

**DO NOT:**
- Lubricate without consulting technician
- Adjust motor drivers (TB6600 settings)
- Move stage manually (always use controls)
- Remove specimen tray while powered on

---

## 7. Safety and Care

### Safe Operating Practices

**DO:**
- ✓ Let system complete homing before interaction
- ✓ Use HOME button if system seems stuck
- ✓ Power off if abnormal noises occur
- ✓ Keep area around kiosk clean and clear

**DON'T:**
- ✗ Force stage to move manually
- ✗ Disconnect cables while system running
- ✗ Touch or move specimens by hand
- ✗ Spray cleaner near electronics or specimens
- ✗ Allow food or drinks near system

### Visitor Safety

The system is safe for public use:
- No exposed moving parts
- Low voltage (12V) to motors
- Touchscreen-only interface (no keyboards/mice for visitors)
- Automatic limits prevent stage collisions

**If Visitor Reports Pain/Injury:**
- Unlikely with this system (no pinch points)
- Most common: accidentally touching their own finger to screen too hard
- No sharp edges or hazardous materials

---

## 8. Understanding System Behavior

### AUTO Mode

**Characteristics:**
- "AUTO" shown at top left
- System moves every 10 seconds
- Cycles through all 28 specimens
- Ignores invalid/missing specimens automatically

**What's Normal:**
- May skip some positions (if specimen data invalid)
- Always returns to same starting position
- Timing is consistent (10s ± 1s)

### MANUAL Mode

**Triggers:**
- Visitor touches any specimen
- Visitor touches any jog button
- Visitor presses HOME

**Behavior:**
- "MANUAL" shown at top left
- Auto-cycle pauses
- System waits 30 seconds of no touching
- Then returns to AUTO mode

**What's Normal:**
- May resume mid-list (not from beginning)
- Doesn't reset when exiting MANUAL mode
- Multiple visitors can interact sequentially

---

## 9. Technical Support

### When to Call for Help

**Call Immediately If:**
- ❌ Stage makes grinding/clicking noises
- ❌ Stage moves beyond visible limits
- ❌ Smell of burning electronics
- ❌ System won't boot after multiple attempts
- ❌ Screen shows error messages

**Can Wait Until Convenient:**
- ℹ️ Single specimen won't display
- ℹ️ Video occasionally freezes
- ℹ️ Auto-cycle timing seems off
- ℹ️ Highlighting doesn't match specimen
- ℹ️ Motors seem louder than usual (but no grinding)

### Information to Provide

When reporting issues:
1. What were you doing when problem occurred?
2. What did you see/hear? (exact error messages)
3. Does it happen every time or intermittently?
4. When did it start? (after power cycle, during operation?)
5. Have you tried restarting?

### Contact Information

**System Developer:** [Your contact info here]  
**Technical Support:** [Your support contact]  
**Museum IT:** [Museum IT contact]

---

## 10. Advanced Operations (Staff Only)

### Restarting a Specific Specimen

If a visitor wants to see a specific specimen again:
1. Touch that specimen's name in the list
2. System jumps immediately
3. No need to wait for auto-cycle

### Pausing Auto-Cycle Temporarily

If you need system to stay on one specimen:
1. Touch jog buttons periodically (every 25 seconds)
2. Keeps system in MANUAL mode
3. Use any jog button (even tiny movements)

### Accessing CLI Diagnostic Mode (Advanced)

**Only if instructed by technician:**
1. Connect keyboard to Raspberry Pi
2. Press ESC to exit GUI
3. Run: `python3 cli_menu.py`
4. Follow technician instructions

**⚠️ Caution:** CLI mode provides full motion control. Incorrect use can damage system.

---

## 11. Quick Reference Card

**Print this section and post near kiosk:**

```
┌─────────────────────────────────────────────┐
│   THE MINERAL MICROSCOPE - QUICK START     │
├─────────────────────────────────────────────┤
│ STARTUP:                                    │
│  1. Turn on power strip                     │
│  2. Wait 90 seconds                         │
│  3. System starts automatically             │
│                                             │
│ NORMAL OPERATION:                           │
│  • System cycles automatically              │
│  • Visitors can touch to explore            │
│  • Returns to auto after 30 seconds         │
│                                             │
│ SHUTDOWN:                                   │
│  • Press ESC or turn off power strip        │
│                                             │
│ EMERGENCY:                                  │
│  • Grinding noise: Press HOME or power off  │
│  • Frozen: Restart system                   │
│  • Disconnected: Check USB cables           │
│                                             │
│ DAILY CHECKS:                               │
│  ✓ System boots and homes correctly         │
│  ✓ Touch interaction works                  │
│  ✓ Video is live                            │
│  ✓ No abnormal noises                       │
│                                             │
│ CONTACT: [Your phone/email here]           │
└─────────────────────────────────────────────┘
```

---

## 12. Appendix: Specimen List

Current configuration shows **28 New Hampshire Minerals**:

1. Smoky Quartz - Ruggles Mine, Grafton
2. Golden Beryl - Palermo Mine, North Groton
3. Black Tourmaline - Fletcher Mine, North Groton
4. Fluorapatite - Palermo Mine, North Groton
5. Amblygonite - Palermo Mine, North Groton
6. Muscovite - Ruggles Mine, Grafton
7. Almandine Garnet - Littleton area
8. Aquamarine - Royalston Quarry, Cheshire Co.
9. Elbaite Tourmaline - Mount Mica, Paris
10. Columbite - Palermo Mine, North Groton
11. Triphylite - Palermo Mine, North Groton
12. Pollucite - Fletcher Mine, North Groton
13. Microcline - Pikes Peak, Grafton Co.
14. Spodumene - Fletcher Mine, North Groton
15. Autunite - Ruggles Mine, Grafton (⚠️ radioactive)
16. Uraninite - Ruggles Mine, Grafton (⚠️ radioactive)
17. Rose Quartz - Keene area, Cheshire Co.
18. Lepidolite - Palermo Mine, North Groton
19. Cassiterite - Lost River Mine, North Woodstock
20. Euxenite - Palermo Mine, North Groton
21. Lithiophilite - Palermo Mine, North Groton
22. Beryllonite - Palermo Mine, North Groton
23. Herderite - Palermo Mine, North Groton
24. Blue Apatite - Palermo Mine, North Groton
25. Orthoclase Feldspar - Ruggles Mine, Grafton
26. Albite - Fletcher Mine, North Groton
27. Bismuthinite - Grafton area
28. Monazite - Palermo Mine, North Groton

**Note:** Specimens #15 (Autunite) and #16 (Uraninite) are mildly radioactive but safe for display. No special handling required.

---

**Previous Section:** [09 - GUI Architecture](09_GUI_ARCHITECTURE.md)  
**Next Section:** [11 - Installation Guide](11_INSTALLATION.md)
