from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
from multiplayer_menu import MultiplayerMenu
from network import NetworkManager
import random
import time
import math
import os
import sys

# Global variables
player = None
ground = None
walls = []
enemies = []
bullets = []
powerups = []
wave = 1  # Start from wave 1
enemies_per_wave = 3
game_over = False

def safe_load_model(model_name):
    """Safely load a model by name, falling back to basic shapes if needed."""
    # List of built-in models that don't require file loading
    builtin_models = ['cube', 'sphere', 'plane', 'quad', 'circle', 'arrow', 'cube_uv_top']
    
    if model_name in builtin_models:
        return model_name
        
    # If not a built-in model, try to load it with error handling
    try:
        # Try with a direct path first
        model_path = os.path.join('assets', 'models', f"{model_name}.obj")
        if os.path.exists(model_path):
            return loader.loadModel(model_path)
            
        # Try with just the model name
        return loader.loadModel(model_name)
    except Exception as e:
        print(f"Warning: Could not load model '{model_name}': {str(e)}. Using cube as fallback.")
        return 'cube'  # Fallback to a basic cube

class StartMenu(Entity):
    def __init__(self, **kwargs):
        super().__init__(parent=camera.ui, **kwargs)
        self.is_menu = True  # Flag to identify this as the main menu
        self.player_id = str(id(self))[-4:]  # Generate a simple player ID
        self.is_multiplayer = False
        self.network_manager = None
        
        # Main menu
        self.menu = Entity(parent=self, enabled=True)
        self.background = Entity(model='quad', color=color.black90, scale=(2, 1.5), parent=self.menu)
        self.title = Text(text='FPS GAME', origin=(0, 0), y=0.3, scale=2.5, parent=self.menu)
        
        # Singleplayer button
        self.singleplayer_button = Button(
            text='SINGLE PLAYER', 
            color=color.green, 
            scale=(0.25, 0.1), 
            y=0.1, 
            parent=self.menu
        )
        self.singleplayer_button.on_click = self.start_singleplayer
        
        # Multiplayer button
        self.multiplayer_button = Button(
            text='MULTIPLAYER', 
            color=color.blue, 
            scale=(0.25, 0.1), 
            y=-0.05, 
            parent=self.menu
        )
        self.multiplayer_button.on_click = self.show_multiplayer_menu
        
        # Quit button
        self.quit_button = Button(
            text='QUIT', 
            color=color.red, 
            scale=(0.2, 0.08), 
            y=-0.5, 
            parent=self.menu
        )
        self.quit_button.on_click = application.quit
        
        # Multiplayer menu (initially hidden)
        self.multiplayer_menu = MultiplayerMenu(parent=self, enabled=False)
        self.multiplayer_menu.on_back = self.back_to_main
        
        # Game UI (initially hidden)
        self.game_ui = Entity(parent=self, enabled=False)
        self.health_bar = Entity(model='quad', color=color.red, scale=(0.4, 0.05), x=-0.7, y=-0.4, parent=self.game_ui)
        self.health_text = Text(text='100/100', x=-0.7, y=-0.4, origin=(0, 0), parent=self.game_ui)
        self.ammo_text = Text(text='30/90', x=0.7, y=-0.4, origin=(0, 0), parent=self.game_ui)
        self.score_text = Text(text='Score: 0', x=0, y=0.45, origin=(0, 0), parent=self.game_ui)
        self.wave_text = Text(text='Wave: 1', x=0, y=0.4, origin=(0, 0), parent=self.game_ui)
        
        # Game over UI (initially hidden)
        self.game_over_ui = Entity(parent=self, enabled=False)
        self.game_over_text = Text(text='GAME OVER', origin=(0, 0), scale=3, color=color.red, parent=self.game_over_ui)
        self.restart_button = Button(text='RESTART', color=color.green, scale=(0.2, 0.1), y=-0.1, parent=self.game_over_ui)
        self.restart_button.on_click = self.restart_game
        self.menu_button = Button(text='MAIN MENU', color=color.blue, scale=(0.2, 0.08), y=-0.25, parent=self.game_over_ui)
        self.menu_button.on_click = self.return_to_menu
        
        # Network manager
        self.network_manager = None
        self.is_multiplayer = False
        self.score_text = Text(
            parent=self.game_ui,
            text='SCORE: 0',
            position=(-0.8, 0.2),
            scale=1.5,
            color=color.white
        )
        
        self.wave_text = Text(
            parent=self.game_ui,
            text='WAVE: 1',
            position=(-0.8, 0.1),
            scale=1.5,
            color=color.white
        )
    
    def start_game(self):
        """Start the game in single-player mode"""
        self.menu.enabled = False
        self.game_ui.enabled = True
        self.is_multiplayer = False
        self.network_manager = None
        start_game()
    
    def start_multiplayer(self, is_host, host='localhost', port=5555):
        """Start a multiplayer game as either host or client"""
        self.menu.enabled = False
        self.game_ui.enabled = True
        self.is_multiplayer = True
        
        try:
            # Initialize network manager
            self.network_manager = NetworkManager(is_host=is_host, host=host, port=port)
            self.network_manager.start()
            
            # Set up network callbacks
            self.network_manager.on_player_update = self.on_player_update
            self.network_manager.on_shoot = self.on_remote_shoot
            self.network_manager.on_damage = self.on_remote_damage
            
            # Connect to the server
            self.network_manager.send_connect()
            
            # Start the game
            start_game()
            
            # Set the network manager for the player
            if player:
                player.network_manager = self.network_manager
                
        except Exception as e:
            print(f"Error starting multiplayer: {e}")
            self.status_text = f"Error: {str(e)}"
            self.status_text.color = color.red
            self.back_to_main()
    
    def on_player_update(self, player_id, position, rotation):
        """Handle player position/rotation updates from the network"""
        # This would be called when receiving updates for other players
        # You would update the corresponding player entity in the game
        pass
    
    def on_remote_shoot(self, message):
        """Handle shoot events from other players"""
        # Create a bullet at the specified position and direction
        position = Vec3(*message['position'])
        direction = Vec3(*message['direction'])
        bullet = Bullet(
            position=position,
            direction=direction,
            enemies_list=enemies,
            speed=50,
            damage=10,
            owner_id=message['player_id']
        )
        bullets.append(bullet)
    
    def on_remote_damage(self, message):
        """Handle damage events from other players"""
        # Apply damage to the local player if they were hit
        if player and message['target_id'] == player.player_id:
            player.take_damage(message['amount'], message['from_player'])
    
    def back_to_main(self):
        """Return to the main menu"""
        self.menu.enabled = True
        self.game_ui.enabled = False
        self.game_over_ui.enabled = False
        
        # Clean up network connection if it exists
        if self.network_manager:
            self.network_manager.stop()
            self.network_manager = None

# Create the Ursina application
app = Ursina()

# Game settings
window.title = 'FPS Game'
window.borderless = False
window.fullscreen = False  # Start in windowed mode
window.fps_counter.enabled = True
window.exit_button.visible = False  # Hide the default exit button

# Add fullscreen toggle function
def toggle_fullscreen():
    window.fullscreen = not window.fullscreen
    if window.fullscreen:
        window.borderless = True  # Go borderless in fullscreen
    else:
        window.borderless = False  # Show borders when windowed

# Set asset paths
application.asset_folder = os.path.dirname(os.path.abspath(__file__))
models_folder = os.path.join('assets', 'models')
sounds_folder = os.path.join('assets', 'sounds')

# Create assets directory if it doesn't exist
if not os.path.exists('assets'):
    os.makedirs('assets')
    os.makedirs(models_folder, exist_ok=True)
    os.makedirs(sounds_folder, exist_ok=True)
sounds_folder = os.path.join('assets', 'sounds')

# Game state
game_over = False
player = None
enemies = []
bullets = []
powerups = []
wave = 1
enemies_per_wave = 3
score = 0

# Weapon classes
class Weapon(Entity):
    def __init__(self, name, damage, fire_rate, ammo, max_ammo, reload_time, model_scale, model_pos, model_color):
        super().__init__()
        self.name = name
        self.damage = damage
        self.fire_rate = fire_rate
        self.ammo = ammo
        self.max_ammo = max_ammo
        self.reload_time = reload_time
        self.last_shot = 0
        self.reloading = False
        self.reload_start = 0
        self.model_scale = model_scale
        self.model_pos = model_pos
        self.model_color = model_color
        self.muzzle_flash = None
        self.bullet_spawn_point = None
        
        # Create weapon model
        self.model = 'models/gun.obj'  # Use our custom gun model
        self.scale = model_scale
        self.position = model_pos
        self.color = model_color
        self.enabled = False  # Start disabled until equipped
        self.rotation = (0, 90, 0)  # Rotate gun to point forward
        
        # Set bullet spawn point at the end of the barrel
        self.bullet_spawn_point = Entity(
            parent=self,
            position=(0, 0, 0.8),  # At the end of the barrel
            scale=0.1
        )
        
    def create_model(self, parent):
        # Create weapon model with direct property setting
        self.model = Entity(parent=parent)
        self.model.model = 'cube'  # Using basic cube for weapon
        self.model.color = self.model_color
        self.model.position = self.model_pos
        self.model.scale = self.model_scale
        
        # Create muzzle flash effect (initially hidden)
        self.muzzle_flash = Entity(parent=self.model)
        self.muzzle_flash.model = 'cube'
        self.muzzle_flash.color = (1, 1, 0, 1)  # Yellow
        self.muzzle_flash.position = (0, 0, -0.5)
        self.muzzle_flash.scale = (0.1, 0.1, 0.1)
        self.muzzle_flash.enabled = False
    
    def show_muzzle_flash(self):
        if self.muzzle_flash:
            self.muzzle_flash.enabled = True
            invoke(setattr, self.muzzle_flash, 'enabled', False, delay=0.05)
    
    def can_shoot(self, current_time):
        return (not self.reloading and 
                self.ammo > 0 and 
                current_time - self.last_shot > 1/self.fire_rate)
    
    def shoot(self, current_time):
        if self.can_shoot(current_time):
            self.ammo -= 1
            self.last_shot = current_time
            self.show_muzzle_flash()
            
            # Create bullet from the bullet spawn point
            if hasattr(self, 'bullet_spawn_point'):
                bullet_pos = self.bullet_spawn_point.world_position
                bullet_dir = self.bullet_spawn_point.forward
            else:
                bullet_pos = self.position + self.forward
                bullet_dir = self.forward
                
            # Create bullet with the weapon's damage
            bullet = Bullet(
                position=bullet_pos,
                direction=bullet_dir,
                enemies_list=enemies,
                damage=self.damage
            )
            bullets.append(bullet)
            
            # Play shoot sound
            try:
                Audio('assets/sounds/shoot.wav', autoplay=False, volume=0.5).play()
            except:
                pass
                
            return True
        return False
    
    def start_reload(self, current_time):
        if not self.reloading and self.ammo < self.max_ammo:
            self.reloading = True
            self.reload_start = current_time
            invoke(self.finish_reload, delay=self.reload_time)
    
    def finish_reload(self):
        self.ammo = self.max_ammo
        self.reloading = False

class Player(FirstPersonController):
    def __init__(self, is_local=True, player_id=None, **kwargs):
        # Initialize FirstPersonController with movement settings
        super().__init__(
            speed=7,
            jump_height=2,
            gravity=1.5,  # Increased gravity for better feel with grappling
            **kwargs
        )
        
        # Multiplayer properties
        self.is_local = is_local
        self.player_id = player_id or str(id(self))[-4:]  # Last 4 digits of object id as player ID
        self.network_manager = None
        self.last_network_update = 0
        self.network_update_interval = 0.1  # Update 10 times per second
        self.network_position = Vec3(0, 0, 0)
        self.network_rotation = Vec3(0, 0, 0)
        self.network_lerp_factor = 10.0  # How quickly to interpolate to network position
        
        # Player state
        self.health = 100
        self.max_health = 100
        self.score = 0
        
        # Movement states
        self.is_sliding = False
        self.slide_timer = 0
        self.slide_cooldown = 0
        self.slide_speed = 15
        self.slide_duration = 0.8
        self.slide_cooldown_duration = 1.5
        
        # Grapple mechanics
{{ ... }}
        
        # Initialize grapple properties
        self.grappling = False
        self.grapple_point = None
        self.grapple_speed = 30
        self.grapple_range = 30
        self.grapple_overswing = 1.5  # Multiplier for overswing effect
        self.grapple_line = None
        
        # Initialize weapons list
        self.weapons = []
        self.current_weapon_index = 0
        
        # Initialize weapons and UI if this is the local player
        if self.is_local:
            self.init_weapons()
            self.setup_ui()
        
        # Create UI elements with text labels
        # Health bar
        self.health_bar = Entity(
            parent=camera.ui,
            model=Quad(),
            color=(1, 0, 0, 1),  # Red
            scale=(0.2, 0.05),
            position=(-0.8, 0.4)
        )
        self.health_text = Text(
            text='HEALTH',
            parent=camera.ui,
            position=(-0.9, 0.4),
            scale=1.5,
            color=color.white
        )
        
        # Ammo display
        self.ammo_display = Entity(
            parent=camera.ui,
            model=Quad(),
            color=(0, 0, 1, 1),  # Blue
            scale=(0.2, 0.05),
            position=(-0.8, 0.3)
        )
        self.ammo_text = Text(
            text='AMMO',
            parent=camera.ui,
            position=(-0.9, 0.3),
            scale=1.5,
            color=color.white
        )
        
        # Score display
        self.score_display = Entity(
            parent=camera.ui,
            model=Quad(),
            color=(0, 1, 0, 1),  # Green
            scale=(0.2, 0.05),
            position=(-0.8, 0.2)
        )
        self.score_text = Text(
            text='SCORE',
            parent=camera.ui,
            position=(-0.9, 0.2),
            scale=1.5,
            color=color.white
        )
        
        # Wave display
        self.wave_display = Entity(
            parent=camera.ui,
            model=Quad(),
            color=(1, 1, 0, 1),  # Yellow
            scale=(0.2, 0.05),
            position=(-0.8, 0.1)
        )
        self.wave_text = Text(
            text='WAVE',
            parent=camera.ui,
            position=(-0.9, 0.1),
            scale=1.5,
            color=color.white
        )
        
    def take_damage(self, amount):
        """Reduce player health by the specified amount and check for game over."""
        self.health -= amount
        self.health = max(0, self.health)  # Ensure health doesn't go below 0
        
        # Update health bar
        health_percent = self.health / self.max_health
        self.health_bar.scale_x = 0.2 * health_percent
        
        # Flash red when taking damage
        self.health_bar.color = color.red
        invoke(setattr, self.health_bar, 'color', color.red, delay=0.1)
        
        if self.health <= 0:
            self.die()
    
    def die(self):
        """Handle player death."""
        print("Player died!")
        # Add game over logic here
        from ursina import Text
        Text(
            text="GAME OVER",
            origin=(0, 0),
            scale=2,
            color=color.red,
            background=True
        )
        # Pause the game
        from ursina import application
        application.pause()
        # Grapple UI indicator
        self.grapple_indicator = Entity(
            parent=camera.ui,
            model=Circle(16),  # 16 segments for smooth circle
            color=color.white,
            scale=0.02,
            position=(0, 0.1, 0),
            enabled=False
        )
        self.grapple_text = Text(
            text='GRAPPLE',
            parent=camera.ui,
            position=(0.02, 0.1),
            scale=1.5,
            color=color.white,
            enabled=False
        )
        
        # Set initial UI state
        try:
            self.update_ui()
        except Exception as e:
            print(f"Error initializing UI: {e}")
            # Set default values if UI update fails
            self.health = 100
            self.max_health = 100
            self.score = 0
    
    def init_weapons(self):
        # Pistol
        pistol = Weapon(
            name='Pistol',
            damage=15,
            fire_rate=2,
            ammo=12,
            max_ammo=48,
            reload_time=1.5,
            model_scale=(0.2, 0.1, 0.5),
            model_pos=(0.5, -0.25, 0.5),
            model_color=color.dark_gray
        )
        
        # SMG
        smg = Weapon(
            name='SMG',
            damage=8,
            fire_rate=10,
            ammo=30,
            max_ammo=90,
            reload_time=2.0,
            model_scale=(0.3, 0.15, 0.7),
            model_pos=(0.6, -0.3, 0.4),
            model_color=color.blue
        )
        
        # Shotgun
        shotgun = Weapon(
            name='Shotgun',
            damage=40,
            fire_rate=1,
            ammo=8,
            max_ammo=24,
            reload_time=3.0,
            model_scale=(0.4, 0.2, 0.8),
            model_pos=(0.7, -0.35, 0.3),
            model_color=color.red
        )
        
        self.weapons = [pistol, smg, shotgun]
        for weapon in self.weapons:
            weapon.create_model(camera)
            weapon.model.enabled = False
        
        # Enable first weapon
        self.weapons[0].model.enabled = True
    
    def switch_weapon(self, index):
        if 0 <= index < len(self.weapons):
            self.weapons[self.current_weapon_index].model.enabled = False
            self.current_weapon_index = index
            self.weapons[self.current_weapon_index].model.enabled = True
            self.update_ammo_display()
    
    def next_weapon(self):
        next_index = (self.current_weapon_index + 1) % len(self.weapons)
        self.switch_weapon(next_index)
    
    def prev_weapon(self):
        prev_index = (self.current_weapon_index - 1) % len(self.weapons)
        self.switch_weapon(prev_index)
    
    def get_current_weapon(self):
        return self.weapons[self.current_weapon_index]
    
    def update_ammo_display(self):
        weapon = self.get_current_weapon()
        reload_text = " (Reloading...)" if weapon.reloading else ""
        # Update ammo display width based on ammo percentage
        ammo_pct = weapon.ammo / weapon.max_ammo
        self.ammo_display.scale_x = 0.2 * ammo_pct
    
    def update_ui(self):
        try:
            # Update health bar and text
            health_ratio = self.health / max(1, self.max_health)
            self.health_bar.scale_x = 0.2 * max(0, min(1, health_ratio))
            if hasattr(self, 'health_text'):
                self.health_text.text = f'HEALTH: {int(self.health)}/{self.max_health}'
            
            # Update ammo display and text
            weapon = self.get_current_weapon()
            if weapon:
                ammo_ratio = weapon.ammo / max(1, weapon.max_ammo)
                self.ammo_display.scale_x = 0.2 * max(0, min(1, ammo_ratio))
                if hasattr(self, 'ammo_text'):
                    self.ammo_text.text = f'AMMO: {weapon.ammo}/{weapon.max_ammo}'
            
            # Update score display and text
            score_ratio = min(1, self.score / 1000)
            self.score_display.scale_x = 0.2 * score_ratio
            if hasattr(self, 'score_text'):
                self.score_text.text = f'SCORE: {self.score}'
                
            # Update wave display (simple indicator for now)
            wave_pulse = 0.1 + (time.time() % 3) * 0.05
            self.wave_display.scale_x = 0.2 * wave_pulse
            
            # Update wave text if wave system is implemented
            if hasattr(globals(), 'current_wave') and hasattr(self, 'wave_text'):
                self.wave_text.text = f'WAVE: {current_wave}'
                
            # Update grapple indicator
            if hasattr(self, 'grapple_text'):
                self.grapple_text.enabled = self.grappling
                
        except Exception as e:
            print(f"Error in update_ui: {e}")
        
        # Update grapple indicator if grappling
        if self.grappling and self.grapple_line:
            self.grapple_line.start = self.position + (0, 1.8, 0)  # Slightly above player
            self.grapple_line.end = self.grapple_point
    
    def input(self, key):
        super().input(key)
        
        # Shooting with left mouse button
        if key == 'left mouse down' and not self.grappling:
            weapon = self.get_current_weapon()
            if weapon:
                weapon.shoot(time.time())
        
        # Reload with R key
        if key == 'r':
            weapon = self.get_current_weapon()
            if weapon and not weapon.reloading and weapon.ammo < weapon.max_ammo:
                weapon.start_reload(time.time())
        
        # Toggle slide on left shift
        if key == 'left shift' and not self.is_sliding and self.slide_cooldown <= 0 and self.grounded:
            self.start_slide()
        
        # Start grapple on right mouse button
        if key == 'right mouse down' and not self.grappling and not held_keys['left mouse']:
            self.start_grapple()
        
        # Release grapple
        if key == 'right mouse up' and self.grappling:
            self.release_grapple()
            
        # Switch weapons with number keys
        if key == '1' and len(self.weapons) > 0:
            self.switch_weapon(0)
        elif key == '2' and len(self.weapons) > 1:
            self.switch_weapon(1)
        elif key == '3' and len(self.weapons) > 2:
            self.switch_weapon(2)
    
    def start_slide(self):
        try:
            if not hasattr(self, 'grounded') or not self.grounded or self.is_sliding or (hasattr(self, 'slide_cooldown') and self.slide_cooldown > 0):
                return
                
            self.is_sliding = True
            self.slide_timer = self.slide_duration
            self.original_speed = self.speed if hasattr(self, 'speed') else 7
            self.speed = self.slide_speed if hasattr(self, 'slide_speed') else 15
            
            # Apply downward force for slide
            if hasattr(self, 'y_velocity'):
                self.y_velocity = -5  # Push player down slightly
                
            # Change player height for slide
            self.scale_y = 0.5
            self.y -= 0.5  # Lower the player
            
            # Play slide sound
            try:
                Audio('assets/sounds/slide.wav', autoplay=False, volume=0.3).play()
            except:
                pass
                
        except Exception as e:
            print(f"Error in start_slide: {e}")
    
    def end_slide(self):
        try:
            if not hasattr(self, 'is_sliding') or not self.is_sliding:
                return
                
            self.is_sliding = False
            if hasattr(self, 'original_speed'):
                self.speed = self.original_speed
            if hasattr(self, 'slide_cooldown_duration'):
                self.slide_cooldown = self.slide_cooldown_duration
            
            # Reset player height
            self.scale_y = 1
            self.y += 0.5  # Raise the player back up
            
        except Exception as e:
            print(f"Error in end_slide: {e}")
    
    def start_grapple(self):
        try:
            if not hasattr(self, 'grappling'):
                self.grappling = False
            if not hasattr(self, 'grapple_range'):
                self.grapple_range = 30
                
            if not hasattr(camera, 'world_position') or not hasattr(camera, 'forward'):
                print("Error: Camera not properly initialized")
                return
                
            # Cast a ray to find grapple point
            hit_info = raycast(
                camera.world_position,
                camera.forward,
                distance=self.grapple_range,
                ignore=[self],
                debug=False
            )
            
            if hit_info and hasattr(hit_info, 'hit') and hit_info.hit and hasattr(hit_info, 'point'):
                self.grappling = True
                self.grapple_point = hit_info.point
                
                # Initialize grapple line if it doesn't exist
                if not hasattr(self, 'grapple_line'):
                    self.grapple_line = Entity(
                        parent=camera.ui,
                        model=Line(
                            (0, 0, 0),
                            (0, 0, 0),
                            thickness=2,
                            mode='line'
                        ),
                        color=color.white,
                        scale=1,
                        position=(0, 0, 0)
                    )
                
                # Update grapple line visibility
                if hasattr(self, 'grapple_line'):
                    self.grapple_line.enabled = True
                    
                if hasattr(self, 'grapple_indicator'):
                    self.grapple_indicator.enabled = True
                
                # Apply force towards grapple point
                direction = (self.grapple_point - self.position).normalized()
                if hasattr(self, 'velocity'):
                    self.velocity = direction * self.grapple_speed
                    
                    # Add overswing effect
                    overswing_direction = direction + Vec3(0, self.grapple_overswing, 0)
                    self.velocity += overswing_direction * (self.grapple_speed * 0.5)
                
                # Play sound
                play_sound('grapple.wav', volume=0.3)
                
            else:
                # Show failed grapple indicator
                if hasattr(self, 'grapple_indicator'):
                    self.grapple_indicator.color = color.red
                    invoke(setattr, self.grapple_indicator, 'color', color.white, delay=0.2)
                    
        except Exception as e:
            print(f"Error in start_grapple: {e}")
            self.grappling = False
            if hasattr(self, 'grapple_line') and self.grapple_line:
                try:
                    if hasattr(self.grapple_line, 'model'):
                        destroy(self.grapple_line.model)
                    destroy(self.grapple_line)
                except Exception as e:
                    print(f"Error destroying grapple line: {e}")
                finally:
                    self.grapple_line = None
    
    def release_grapple(self):
        try:
            if not self.grappling:
                return
                
            self.grappling = False
            
            # Safely destroy the grapple line if it exists
            if hasattr(self, 'grapple_line') and self.grapple_line:
                try:
                    if hasattr(self.grapple_line, 'model'):
                        destroy(self.grapple_line.model)
                    destroy(self.grapple_line)
                except Exception as e:
                    print(f"Error destroying grapple line: {e}")
                finally:
                    self.grapple_line = None
            
            # Disable the indicator if it exists
            if hasattr(self, 'grapple_indicator'):
                self.grapple_indicator.enabled = False
                
        except Exception as e:
            print(f"Error in release_grapple: {e}")
    
    def update_grapple(self):
        try:
            if not self.grappling or not hasattr(self, 'grapple_point') or not self.grapple_point:
                return
                
            # Calculate direction to grapple point
            try:
                direction = (self.grapple_point - self.position).normalized()
                distance = (self.grapple_point - self.position).length()
            except Exception as e:
                print(f"Error calculating grapple direction/distance: {e}")
                self.release_grapple()
                return
            
            # Apply force towards grapple point with overswing
            if hasattr(self, 'velocity'):
                self.velocity += direction * self.grapple_speed * time.dt
            
            # Update grapple line position if it exists
            if hasattr(self, 'grapple_line') and self.grapple_line and hasattr(self.grapple_line, 'model'):
                try:
                    self.grapple_line.model.start = self.position + (0, 1.8, 0)
                    self.grapple_line.model.end = self.grapple_point
                    self.grapple_line.model.generate()
                except Exception as e:
                    print(f"Error updating grapple line: {e}")
                    self.release_grapple()
                    return
            
            # Add overswing effect when close to the grapple point
            if distance < 5:
                overshoot_force = (5 - distance) * self.grapple_overswing
                if hasattr(self, 'velocity'):
                    self.velocity += direction * overshoot_force
            
            # Release if we've passed the grapple point or are too far
            if distance < 1 or distance > self.grapple_range * 1.5:
                self.release_grapple()
                
        except Exception as e:
            print(f"Error in update_grapple: {e}")
            self.release_grapple()
    
    def update_slide(self):
        if not self.is_sliding:
            return
            
        self.slide_timer -= time.dt
        if self.slide_timer <= 0 or not self.grounded:
            self.end_slide()
    
    def update(self):
        # Only process input and send updates for local player
        if self.is_local:
            super().update()
            
            # Update slide cooldown
            if self.slide_cooldown > 0:
                self.slide_cooldown -= time.dt
            
            # Update slide state
            self.update_slide()
            
            # Update grapple physics
            self.update_grapple()
            
            # Update UI
            self.update_ui()
            
            # Send network updates at regular intervals
            current_time = time.time()
            if (current_time - self.last_network_update) > self.network_update_interval:
                self.send_network_update()
                self.last_network_update = current_time
        
        # For remote players, update position/rotation based on network data
        else:
            # This would be updated by network messages
            pass
        
        wave_color = (1, 1, 0, 1)  # Yellow
        self.wave_display.color = wave_color
    
    def send_network_update(self):
        """Send player's current state to the network"""
        if not self.is_local or not self.network_manager:
            return
            
        self.network_manager.send_player_update(
            position=tuple(self.position),
            rotation=tuple(self.rotation)
        )
    
    def take_damage(self, amount, attacker_id=None):
        """Handle taking damage, with optional attacker ID for multiplayer"""
        if not hasattr(self, 'health'):
            self.health = 100
            self.max_health = 100
            
        self.health = max(0, self.health - amount)
        
        # Update UI for local player
        if self.is_local:
            self.update_ui()
            
            # Flash red when taking damage
            if hasattr(self, 'health_bar'):
                self.health_bar.color = color.red
                invoke(setattr, self.health_bar, 'color', (0, 1, 0, 1), delay=0.1)
            
            # Notify network about damage
            if self.network_manager and attacker_id and attacker_id != self.player_id:
                self.network_manager.send_damage(attacker_id, amount)
        
        if self.health <= 0:
            self.die()
    
    def shoot(self, target_pos=None):
        """Shoot a bullet, with optional target position for remote players"""
        if not self.is_local:
            # For remote players, use the provided target position
            if target_pos:
                direction = (target_pos - self.position).normalized()
                bullet = Bullet(
                    position=self.position + (0, 1.5, 0),  # Shoot from player's head
                    direction=direction,
                    enemies_list=enemies,
                    damage=10,
                    owner_id=self.player_id
                )
                bullets.append(bullet)
            return
            
        # For local player, use the standard shooting logic
        weapon = self.get_current_weapon()
        if weapon and weapon.shoot(time.time()):
            # Notify network about the shot
            if self.network_manager:
                self.network_manager.send_shoot(
                    position=tuple(weapon.bullet_spawn_point.world_position),
                    direction=tuple(weapon.bullet_spawn_point.forward)
                )
        
    def take_damage(self, amount):
        """Reduce player health by the specified amount and update UI."""
        if not hasattr(self, 'health'):
            self.health = 100
            self.max_health = 100
            
        self.health = max(0, self.health - amount)
        self.update_ui()
        
        # Flash red when taking damage
        if hasattr(self, 'health_bar'):
            self.health_bar.color = color.red
            invoke(setattr, self.health_bar, 'color', (0, 1, 0, 1), delay=0.1)  # Flash back to green
        
        if self.health <= 0:
            self.die()
    
    def die(self):
        global game_over
        game_over = True
        Text(text='GAME OVER', origin=(0,0), scale=3, background=True)

class Enemy(Entity):
    def __init__(self, position, health=30, speed=2, damage=10, color=color.red, scale=(1, 2, 1), is_boss=False):
        # First create a basic entity
        super().__init__()
        
        self.is_boss = is_boss
        self.position = position
        self.scale = scale
        
        # Set model and color based on enemy type
        if is_boss:
            # Boss enemies are larger and purple
            self.model = Sphere()  # Use Sphere() for bosses
            self.color = (0.5, 0, 0.5, 1)  # Purple
            self.scale = (2, 3, 2)  # Make the sphere bigger for bosses
        else:
            # Regular enemies are smaller and red
            self.model = Cube()  # Use Cube() for regular enemies
            self.color = (1, 0, 0, 1)  # Red
            
        # Set collider after model
        self.collider = 'box'
        self.health = health
        self.max_health = health
        self.speed = speed
        self.damage = damage
        self.last_attack = 0
        self.attack_cooldown = 1.0
        
        # Health bar
        self.health_bar = Entity(
            parent=self,
            model='cube',
            color=(0, 1, 0, 1),  # Green color
            position=(0, 1.5, 0),
            scale=(0.5, 0.1, 0.1)
        )
        self.update_health_bar()
    
    def update_health_bar(self):
        health_percent = self.health / self.max_health
        self.health_bar.scale_x = 0.5 * health_percent
        # Interpolate between red and green based on health percentage
        r = 1.0 - health_percent
        g = health_percent
        b = 0.0
        self.health_bar.color = (r, g, b, 1.0)  # RGBA format
    
    def take_damage(self, amount):
        self.health -= amount
        self.update_health_bar()
        
        if self.health <= 0:
            self.die()
            return True
        return False
    
    def die(self):
        player.score += 10
        player.score_text.text = f'Score: {player.score}'
        destroy(self.health_bar)
        destroy(self)
    
    def update(self):
        if game_over:
            return
            
        # Move towards player
        direction = (player.position - self.position).normalized()
        self.look_at(player.position)
        self.rotation_x = 0
        self.rotation_z = 0
        
        # Move forward
        self.position += self.forward * time.dt * self.speed
        
        # Check for attack
        distance = (player.position - self.position).length()
        if distance < 2 and time.time() - self.last_attack > self.attack_cooldown:
            player.take_damage(self.damage)
            self.last_attack = time.time()

class Boss(Enemy):
    def __init__(self, position):
        super().__init__(
            position=position,
            health=200,
            speed=1.5,
            damage=20,
            color=color.purple,
            scale=(2, 3, 2),
            is_boss=True
        )
        self.attack_cooldown = 2.0
        
        # Make boss face the player
        if player:
            self.look_at_2d(player.position, 'y')
        
    def die(self):
        player.score += 100
        player.score_text.text = f'Score: {player.score}'
        destroy(self.health_bar)
        destroy(self)

class Bullet(Entity):
    def __init__(self, position, direction, enemies_list, speed=50, damage=10, bullet_color=(1, 1, 0, 1), owner_id=None):
        try:
            # First create a basic entity with no model
            super().__init__()
            
            # Set properties directly
            self.position = position if hasattr(position, '__len__') and len(position) >= 3 else (0, 0, 0)
            self.scale = 0.2
            self.color = bullet_color if hasattr(bullet_color, '__len__') and len(bullet_color) >= 3 else (1, 1, 0, 1)  # Default to yellow
            
            # Add a sphere model directly
            try:
                self.model = Sphere(segments=8)  # Using Sphere() with reduced segments for better performance
            except:
                self.model = 'sphere'  # Fallback to string model
            
            # Set collider after model
            self.collider = 'sphere'
            
            # Set other properties
            self.direction = Vec3(*direction) if hasattr(direction, '__len__') and len(direction) >= 3 else Vec3(1, 0, 0)
            self.speed = max(1, min(1000, speed))  # Clamp speed to reasonable values
            self.damage = max(1, damage)  # Ensure at least 1 damage
            self.birth_time = time.time()
            self.max_lifetime = 5.0  # seconds
            self.enemies_list = enemies_list if enemies_list is not None else []
            self.owner_id = owner_id  # ID of the player who shot this bullet
            self.has_collided = False  # Track if bullet has already hit something
            
            # Make the bullet face the direction it's moving
            self.look_at(self.position + self.direction)
            
            # Play shoot sound for local player's bullets
            if owner_id == getattr(player, 'player_id', None):
                try:
                    Audio('assets/sounds/shoot.wav', autoplay=False, volume=0.3).play()
                except:
                    pass
            self.enabled = True  # Enable the bullet
        
        except Exception as e:
            print(f"Error initializing bullet: {e}")
            self.enabled = False  # Disable if there's an error
    
    def update(self):
        try:
            if not hasattr(self, 'enabled') or not self.enabled:
                destroy(self)
                return
                
            # Move the bullet
            if hasattr(self, 'position') and hasattr(self, 'direction') and hasattr(self, 'speed'):
                self.position += self.direction * self.speed * time.dt
            
            # Check if bullet has been alive too long
            if time.time() - self.birth_time > self.max_lifetime:
                destroy(self)
                return
                
            # Check for collisions with enemies
            if hasattr(self, 'enemies_list') and self.enemies_list is not None:
                for enemy in list(self.enemies_list):  # Create a copy of the list to avoid modification during iteration
                    if enemy and hasattr(enemy, 'enabled') and enemy.enabled and distance(enemy, self) < 1.5:
                        if hasattr(enemy, 'take_damage'):
                            enemy.take_damage(self.damage)
                        destroy(self)
                        return
                        
        except Exception as e:
            print(f"Error in bullet update: {e}")
            destroy(self)

class Powerup(Entity):
    def __init__(self, position, powerup_type):
        # First create a basic entity
        super().__init__()
        
        self.powerup_type = powerup_type
        self.position = position
        self.scale = 0.5
        
        # Set model and color based on powerup type
        self.model = Cube()  # Using Cube() for better compatibility
        
        if powerup_type == 'health':
            self.color = (0, 1, 0, 1)  # Green
        elif powerup_type == 'ammo':
            self.color = (0, 0, 1, 1)  # Blue
            
        # Set collider after model
        self.collider = 'box'  # Using 'box' collider to match cube model
        
        # Add rotation animation
        self.animate_rotation((0, 360, 0), duration=3, loop=True)
        self.animate_y(self.y + 0.5, duration=1, loop=True, curve=curve.in_out_sine)
    
    def collect(self):
        if self.powerup_type == 'health':
            player.health = min(player.max_health, player.health + 25)
            player.health_text.text = f'Health: {player.health}'
        elif self.powerup_type == 'ammo':
            for weapon in player.weapons:
                weapon.ammo = weapon.max_ammo
            player.update_ammo_display()
        
        destroy(self)

def spawn_enemy(is_boss=False):
    # Find a random position around the player
    angle = random.uniform(0, 6.28)  # Random angle in radians
    distance = random.uniform(15, 30)  # Random distance from player
    x = player.x + math.cos(angle) * distance
    z = player.z + math.sin(angle) * distance
    
    # Make sure position is within bounds
    x = max(-45, min(45, x))
    z = max(-45, min(45, z))
    
    # Create enemy
    try:
        if is_boss:
            enemy = Boss(position=(x, 0, z))
        else:
            enemy = Enemy(position=(x, 0, z))
        
        enemies.append(enemy)
        return enemy
    except Exception as e:
        print(f"Error spawning enemy: {e}")
        # Fallback to basic cube if model loading fails
        enemy = Enemy(position=(x, 0, z))
        if is_boss:
            enemy.scale = (2, 3, 2)
            enemy.color = color.purple
        enemies.append(enemy)
        return enemy

def spawn_wave():
    global wave, enemies_per_wave
    for _ in range(enemies_per_wave):
        spawn_enemy()
    if wave > 0 and wave % 3 == 0:
        spawn_enemy(is_boss=True)
    wave += 1
    enemies_per_wave += 1
    
    # Update wave display color based on wave number
    if hasattr(player, 'wave_display'):
        # Make the wave display flash when a new wave starts
        player.wave_display.color = (1, 1, 0, 1)  # Yellow flash
        invoke(setattr, player.wave_display, 'color', (1, 1, 0, 0.5), delay=0.5)  # Fade back to semi-transparent

def play_sound(sound_name, volume=0.5, loop=False):
    """Play a sound effect from the sounds folder."""
    try:
        sound_path = os.path.join(sounds_folder, sound_name)
        if os.path.exists(sound_path):
            Audio(sound_path, volume=volume, loop=loop)
    except Exception as e:
        print(f"Error playing sound {sound_name}: {e}")

def shoot():
    try:
        if not hasattr(globals(), 'game_over') or game_over:
            return
            
        if not hasattr(globals(), 'player') or not hasattr(globals(), 'camera'):
            print("Error: Player or camera not initialized")
            return
            
        weapon = player.get_current_weapon()
        if not weapon:
            print("Error: No weapon equipped")
            return
            
        current_time = time.time()
        
        if weapon.shoot(current_time):
            try:
                # Ensure enemies list exists
                if 'enemies' not in globals():
                    globals()['enemies'] = []
                
                # Create bullet
                bullet = Bullet(
                    position=camera.world_position,
                    direction=camera.forward,
                    enemies_list=enemies,
                    damage=weapon.damage,
                    bullet_color=weapon.model_color if hasattr(weapon, 'model_color') else color.yellow
                )
                
                # Ensure bullets list exists
                if 'bullets' not in globals():
                    globals()['bullets'] = []
                bullets.append(bullet)
                
                # Update ammo display
                if hasattr(player, 'update_ammo_display'):
                    player.update_ammo_display()
                
                # Play shoot sound (skip if sound file doesn't exist)
                play_sound('shoot.wav', volume=0.2)
                
            except Exception as e:
                print(f"Error creating bullet: {e}")
        
        # Auto-reload when out of ammo
        elif weapon.ammo <= 0 and not weapon.reloading:
            reload_weapon()
            
    except Exception as e:
        print(f"Error in shoot function: {e}")

def reload_weapon():
    if game_over:
        return
        
    weapon = player.get_current_weapon()
    if not weapon.reloading and weapon.ammo < weapon.max_ammo:
        weapon.start_reload(time.time())
        player.update_ammo_display()
        # Play reload sound (if available)
        # play_sound('reload.wav')

def start_game():
    global player, ground, enemies, bullets, powerups, wave, enemies_per_wave, game_over, score
    
    # Get reference to the menu
    menu = None
    for e in scene.entities:
        if hasattr(e, 'is_menu') and e.is_menu:
            menu = e
            break
    
    # Reset game state
    game_over = False
    score = 0
    wave = 1
    enemies_per_wave = 5
    
    # Clear existing entities
    for enemy in enemies[:]:
        if enemy and hasattr(enemy, 'enabled'):
            enemy.disable()
    enemies.clear()
    
    for bullet in bullets[:]:
        if bullet and hasattr(bullet, 'enabled'):
            bullet.disable()
    bullets.clear()
    
    for powerup in powerups[:]:
        if powerup and hasattr(powerup, 'enabled'):
            powerup.disable()
    powerups.clear()
    
    # Create ground
    ground = Entity(
        model='plane',
        scale=100,
        texture='white_cube',
        texture_scale=(10, 10),
        collider='box'
    )
    
    # Create walls
    wall_positions = [
        (0, 5, -50), (0, 5, 50),  # Front and back walls
        (-50, 5, 0), (50, 5, 0),   # Left and right walls
    ]
    
    for pos in wall_positions:
        wall = Entity(
            model='cube',
            scale=(100, 10, 1) if abs(pos[2]) > 0 else (1, 10, 100),
            position=pos,
            color=color.gray,
            collider='box',
            texture='white_cube'
        )
    
    # Create player
    is_multiplayer = hasattr(menu, 'is_multiplayer') and menu.is_multiplayer
    player = Player(
        position=(0, 2, 0),
        is_local=True,  # The local player is always controlled by this client
        player_id=menu.player_id if hasattr(menu, 'player_id') else None
    )
    
    # Set up network manager if in multiplayer
    if is_multiplayer and hasattr(menu, 'network_manager') and menu.network_manager:
        player.network_manager = menu.network_manager
    
    camera.parent = player
    
    # Only spawn enemies for single-player or host
    if not is_multiplayer or (hasattr(menu, 'network_manager') and menu.network_manager and menu.network_manager.is_host):
        spawn_wave()
    

def update():
    # This function is called every frame
    if game_over or not hasattr(player, 'enabled') or not player.enabled:
        return
    
    try:
        # Update player
        if player.health <= 0:
            global game_over
            game_over = True
            return
            
        # Update bullets
        for bullet in bullets[:]:
            if bullet and hasattr(bullet, 'update'):
                bullet.update()
                
        # Update enemies
        for enemy in enemies[:]:
            if enemy and hasattr(enemy, 'update'):
                enemy.update()
                
        # Update powerups
        for powerup in powerups[:]:
            if powerup and hasattr(powerup, 'update'):
                powerup.update()
                
    except Exception as e:
        print(f"Error in update: {e}")

# Create start menu
menu = StartMenu()

# Start the game
if __name__ == '__main__':
    print("Starting game...")
    try:
        # Initialize the game
        init_game()
        
        # Set up error handling for the main loop
        def safe_update():
            try:
                update()
            except Exception as e:
                print(f"Error in game loop: {e}")
                # Try to keep the game running
                try:
                    if 'player' in globals() and player and hasattr(player, 'update'):
                        player.update()
                except Exception as e:
                    print(f"Error in player update: {e}")
        
        # Set the update function
        app.update = safe_update
        
        # Start the game
        print("Starting Ursina application...")
        app.run()
        
    except Exception as e:
        print(f"Fatal error: {e}")
        import traceback
        traceback.print_exc()
        input("Press Enter to exit...")
