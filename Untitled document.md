# Boundary Test Data

## Overview

This document identifies three critical logic points in the game and defines boundary cases, concrete test inputs, and expected behavior. These tests ensure stable behavior across movement controls, enemy spawning, and health/armor systems.

---

# Logic Point A: Player Movement & Collision Boundaries

Movement is a core system that instantly breaks gameplay if mishandled. Boundary cases include world edges, restricted areas, and invalid movement states.

### Boundary Table

| Boundary Input | Why It’s a Boundary |
| ----- | ----- |
| Player moves to world coordinate below minimum bounds | Tests clamping and grid limits |
| Player moves to world coordinate above maximum bounds | Ensures max map limits aren’t bypassed |
| Player attempts to move through a wall/obstacle | Verifies collision blocking |

### Test Data Table

| Boundary Input | Test Data Example |
| ----- | ----- |
| Below minimum | Position attempt: `(-1, 0, 5)` |
| Above maximum | Position attempt: `(101, 0, 40)` in a 100×40 map |
| Through a wall | Player moving forward into `collider=True` object |

### Expected Outcomes

| Boundary Input | Test Data | Expected Outcome |
| ----- | ----- | ----- |
| Below minimum | `(-1,0,5)` | Player remains at `(0,0,5)`; movement clamped |
| Above maximum | `(101,0,40)` | Player clamped to `(100,0,40)`; no crash |
| Into wall | Forward movement into wall mesh | Movement should stop; no clipping or phasing |

---

# Logic Point B: Enemy Spawning Rules

Enemy spawning uses lists, random generation, and limits. Boundary cases often break array indexing or overload performance.

### Boundary Table

| Boundary Input | Why It’s a Boundary |
| ----- | ----- |
| Spawn count \= 0 | Tests minimum enemy value |
| Spawn count \= max limit | Ensures cap enforcement |
| Spawn count exceeds list/limit | Ensures no invalid list access or infinite loops |

### Test Data Table

| Boundary Input | Test Data Example |
| ----- | ----- |
| Zero enemies | Level set to `enemy_count = 0` |
| Max enemies | `enemy_count = 20` (game-defined cap) |
| Exceeds limit | `enemy_count = 25` on a system limited to 20 |

### Expected Outcomes

| Boundary Input | Test Data | Expected Outcome |
| ----- | ----- | ----- |
| Zero enemies | 0 | Level loads with no enemies; no errors |
| Max enemies | 20 | Exactly 20 enemies spawn; system stable |
| Exceeds limit | 25 | Only 20 spawn; excess ignored or clamped |

---

# Logic Point C: Health & Armor Calculations

Health interacts with damage, healing, and armor reductions. Boundary conditions often cause negative health or improper death triggers.

### Boundary Table

| Boundary Input | Why It’s a Boundary |
| ----- | ----- |
| Health drops below zero | Prevents negative HP bugs |
| Health exactly zero | Valid death threshold |
| Health increased above max | Prevents exceeding cap values |

### Test Data Table

| Boundary Input | Test Data Example |
| ----- | ----- |
| Below zero | Apply 200 damage when HP \= 150 |
| Exactly zero | Apply 50 damage when HP \= 50 |
| Above max | Heal player with \+50 when HP \= max (100) |

### 

### 

### Expected Outcomes

| Boundary Input | Test Data | Expected Outcome |
| ----- | ----- | ----- |
| Below zero | HP becomes \-50 | Game clamps to 0; triggers death event |
| Exactly zero | HP becomes 0 | Player death animation and respawn/lose state triggers |
| Above max | HP becomes 150 | HP capped to 100; armor unchanged |

---

# Reflection

Most fragile logic point: Movement and collision; a single missing collider check can break gameplay.

What to watch out for:

* Off-grid positions

* Missing colliders on level geometry

* Array bounds on enemy spawn functions

Most surprising boundary case:

* Allowing health to go above max can silently cause difficulty inconsistencies later.

