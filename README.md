# FPS Game with Multiplayer Support

A first-person shooter game built with Ursina Engine that supports both single-player and multiplayer modes.

## Features

- Single-player mode with enemy AI
- Multiplayer mode with host/client architecture
- Custom weapon models and sound effects
- Health and ammo systems
- Score tracking and wave-based gameplay
- Basic physics (sliding, grappling hook)

## Installation

1. Make sure you have Python 3.7+ installed
2. Install the required packages:
   ```
   pip install ursina numpy
   ```

## How to Play

### Single Player
1. Run the game:
   ```
   python main.py
   ```
2. Click "SINGLE PLAYER" to start a single-player game
3. Use WASD to move, SPACE to jump, and MOUSE to look around
4. Left-click to shoot, R to reload
5. Left SHIFT to slide, Right-click to grapple

### Multiplayer

#### Hosting a Game
1. Click "MULTIPLAYER" then "HOST GAME"
2. Enter a port number (default is 5555)
3. Click "START HOSTING"
4. Share your IP address and port with other players

#### Joining a Game
1. Click "MULTIPLAYER" then "JOIN GAME"
2. Enter the host's IP address and port
3. Click "CONNECT"

## Controls

- **WASD**: Move
- **SPACE**: Jump
- **Left Mouse Button**: Shoot
- **Right Mouse Button**: Grapple
- **R**: Reload
- **Left SHIFT**: Slide
- **1-3**: Switch weapons
- **ESC**: Pause menu

## Multiplayer Networking

The game uses UDP for networking with a simple protocol for syncing player positions, shooting, and damage. The network code is in `network.py`.

## Known Issues

- Multiplayer mode is still in development and may have synchronization issues
- Some sound effects may not play correctly
- Performance may vary depending on network conditions

## Future Improvements

- Add more maps and game modes
- Improve enemy AI
- Add more weapons and power-ups
- Implement voice chat
- Add player customization options
