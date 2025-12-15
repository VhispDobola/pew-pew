# Testing Plan — 3D Shooter Game (Ursina)

## 1. Overview

This document defines the testing strategy for a single-player 3D shooter game built using the Ursina engine. It connects gameplay requirements to concrete test cases, expected behaviors, boundary conditions, and automation opportunities. The goal is to ensure core gameplay systems (player controls, combat, enemies, UI, and progression) behave reliably, handle edge cases correctly, and remain stable as new features are added.

---

## 2. User Stories and Acceptance Criteria

### User Story 1:

As a player, I want responsive movement and camera controls so I can navigate the world and aim accurately.

* **Acceptance Criterion 1**

  * **Requirement(s):** WASD movement, mouse-look camera
  * **Purpose:** Ensure basic navigation works at all times
  * **Test Case:**
    a) Feature: Player movement
    b) Test: Hold each movement key individually and in combinations
    c) Expected Result / Behavior: Player moves smoothly in the correct direction without jitter or delay
    d) Automation Candidate: Yes (rule-based)

* **Acceptance Criterion 2**

  * **Requirement(s):** Mouse sensitivity and camera rotation
  * **Purpose:** Ensure aiming feels accurate and consistent
  * **Test Case:**
    a) Feature: Camera rotation
    b) Test: Move mouse slowly and rapidly in all directions
    c) Expected Result / Behavior: Camera rotates proportionally with no snapping or inversion
    d) Automation Candidate: Partial (manual feel validation required)

---

### User Story 2:

As a player, I want weapons to fire correctly and damage enemies so combat feels fair and predictable.

* **Acceptance Criterion 1**

  * **Requirement(s):** Weapon firing, projectile spawning
  * **Purpose:** Confirm weapons activate on input
  * **Test Case:**
    a) Feature: Weapon firing
    b) Test: Press fire button with ammo available
    c) Expected Result / Behavior: Projectile spawns, sound plays, ammo decreases by one
    d) Automation Candidate: Yes (rule-based)

* **Acceptance Criterion 2**

  * **Requirement(s):** Damage calculation, enemy health
  * **Purpose:** Ensure enemies take correct damage
  * **Setup:** Spawn enemy with known health value
  * **Test Case:**
    a) Feature: Enemy hit detection
    b) Test: Hit enemy with weapon multiple times
    c) Expected Result / Behavior: Enemy health decreases correctly and enemy is destroyed at zero health
    d) Automation Candidate: Yes (repetitive)

---

### User Story 3:

As a player, I want clear UI feedback so I always know my health, ammo, and game state.

* **Acceptance Criterion 1**

  * **Requirement(s):** Health and ammo UI
  * **Purpose:** Prevent player confusion during combat
  * **Test Case:**
    a) Feature: HUD updates
    b) Test: Take damage and fire weapon repeatedly
    c) Expected Result / Behavior: Health and ammo values update immediately and accurately
    d) Automation Candidate: Yes (rule-based)

* **Acceptance Criterion 2**

  * **Requirement(s):** Death and game-over handling
  * **Purpose:** Ensure clear failure state
  * **Setup:** Reduce player health to near zero
  * **Test Case:**
    a) Feature: Player death
    b) Test: Take final point of damage
    c) Expected Result / Behavior: Player input disabled and game-over screen appears
    d) Automation Candidate: Yes (repetitive)

---

## 3. Boundary and Edge Testing

### Boundary / Edge 1: Player Health Limits

```
- **Requirement(s):** Health cannot drop below 0 or exceed max
- **Purpose:** Prevent UI bugs and logic errors

- **Test Case 1:**
    a) Upper Boundary: Max health
    b) Testing data used: < max-1, max, max+1 >
    c) Expected Result / Behavior: Health caps at max value
    d) Automation Candidate: Yes

- **Test Case 2:**
    a) Lower Boundary: Zero health
    b) Testing data used: < 1, 0, -1 >
    c) Expected Result / Behavior: Health stays at 0 and triggers death state
    d) Automation Candidate: Yes
```

---

### Boundary / Edge 2: Ammo Count

```
- **Requirement(s):** Weapons cannot fire with zero ammo
- **Purpose:** Prevent infinite firing bugs

- **Test Case 1:**
    a) Upper Boundary: Max ammo
    b) Testing data used: < max-1, max, max+1 >
    c) Expected Result / Behavior: Ammo does not exceed max
    d) Automation Candidate: Yes

- **Test Case 2:**
    a) Lower Boundary: Zero ammo
    b) Testing data used: < 1, 0, -1 >
    c) Expected Result / Behavior: Weapon does not fire and empty sound/UI feedback occurs
    d) Automation Candidate: Yes
```

---

### Boundary / Edge 3: Enemy Spawning

```
- **Requirement(s):** Enemy count limits
- **Purpose:** Maintain performance and stability

- **Test Case 1:**
    a) Upper Boundary: Max enemies allowed
    b) Testing data used: < max-1, max, max+1 >
    c) Expected Result / Behavior: No more than max enemies exist at once
    d) Automation Candidate: Yes (high-volume)

- **Test Case 2:**
    a) Lower Boundary: Zero enemies
    b) Testing data used: < 1, 0, -1 >
    c) Expected Result / Behavior: Game continues without errors and spawner logic remains stable
    d) Automation Candidate: Yes
```

---

## 4. Automated Test List

| Test Area                        | Automation Type |
| -------------------------------- | --------------- |
| Player movement input validation | Rule-based      |
| Weapon firing and ammo reduction | Repetitive      |
| Enemy damage and death           | Repetitive      |
| Health and ammo boundary checks  | Rule-based      |
| Enemy spawn limits               | High-volume     |

These automated tests reduce regression risk as new weapons, enemies, and levels are added.
