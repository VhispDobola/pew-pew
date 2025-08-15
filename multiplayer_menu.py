from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
from network import NetworkManager

class MultiplayerMenu(Entity):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background = Entity(
            model='quad',
            scale=(2, 1.5),
            color=color.black90,
            parent=self
        )
        
        self.title = Text(
            text="MULTIPLAYER",
            origin=(0, 0),
            y=0.3,
            scale=2,
            color=color.white,
            parent=self
        )
        
        self.host_button = Button(
            text='HOST GAME',
            color=color.blue,
            scale=(0.25, 0.1),
            y=0.1,
            parent=self
        )
        self.host_button.on_click = self.host_game
        
        self.join_button = Button(
            text='JOIN GAME',
            color=color.green,
            scale=(0.25, 0.1),
            y=-0.05,
            parent=self
        )
        self.join_button.on_click = self.show_join_menu
        
        self.back_button = Button(
            text='BACK',
            color=color.gray,
            scale=(0.2, 0.08),
            y=-0.5,
            parent=self
        )
        self.back_button.on_click = self.back_to_main
        
        # Join game elements (initially hidden)
        self.join_menu = Entity(parent=self, enabled=False)
        
        self.ip_input = InputField(
            default_value='localhost',
            label='Host IP:',
            scale=(0.3, 0.05),
            y=0.1,
            parent=self.join_menu
        )
        
        self.port_input = InputField(
            default_value='5555',
            label='Port:',
            scale=(0.2, 0.05),
            y=0,
            parent=self.join_menu
        )
        
        self.connect_button = Button(
            text='CONNECT',
            color=color.green,
            scale=(0.2, 0.08),
            y=-0.15,
            parent=self.join_menu
        )
        self.connect_button.on_click = self.join_game
        
        self.status_text = Text(
            text='',
            origin=(0, 0),
            y=-0.3,
            color=color.yellow,
            parent=self.join_menu
        )
        
        # Host game elements (initially hidden)
        self.host_menu = Entity(parent=self, enabled=False)
        
        self.port_input_host = InputField(
            default_value='5555',
            label='Port:',
            scale=(0.2, 0.05),
            y=0.1,
            parent=self.host_menu
        )
        
        self.start_hosting_button = Button(
            text='START HOSTING',
            color=color.blue,
            scale=(0.25, 0.1),
            y=-0.1,
            parent=self.host_menu
        )
        self.start_hosting_button.on_click = self.start_hosting
        
        self.host_status = Text(
            text='',
            origin=(0, 0),
            y=-0.3,
            color=color.yellow,
            parent=self.host_menu
        )
    
    def show_join_menu(self):
        self.join_menu.enabled = True
        self.host_menu.enabled = False
        self.host_button.enabled = False
        self.join_button.enabled = False
        self.title.enabled = False
    
    def show_host_menu(self):
        self.host_menu.enabled = True
        self.join_menu.enabled = False
        self.host_button.enabled = False
        self.join_button.enabled = False
        self.title.enabled = False
    
    def back_to_menu(self):
        self.join_menu.enabled = False
        self.host_menu.enabled = False
        self.host_button.enabled = True
        self.join_button.enabled = True
        self.title.enabled = True
        self.status_text.text = ''
        self.host_status.text = ''
    
    def host_game(self):
        self.show_host_menu()
    
    def join_game(self):
        host = self.ip_input.text
        try:
            port = int(self.port_input.text)
            self.status_text.text = f"Connecting to {host}:{port}..."
            self.status_text.color = color.yellow
            
            # Start the game in client mode
            if hasattr(self.parent, 'start_multiplayer'):
                self.parent.start_multiplayer(is_host=False, host=host, port=port)
            
        except ValueError:
            self.status_text.text = "Invalid port number"
            self.status_text.color = color.red
    
    def start_hosting(self):
        try:
            port = int(self.port_input_host.text)
            self.host_status.text = f"Hosting on port {port}..."
            self.host_status.color = color.yellow
            
            # Start the game in host mode
            if hasattr(self.parent, 'start_multiplayer'):
                self.parent.start_multiplayer(is_host=True, port=port)
            
        except ValueError:
            self.host_status.text = "Invalid port number"
            self.host_status.color = color.red
    
    def back_to_main(self):
        # This will be connected to the main menu's back functionality
        if hasattr(self, 'on_back'):
            self.on_back()
