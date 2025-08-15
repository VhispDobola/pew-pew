from ursina import *

app = Ursina()

# Test basic shape
cube = Entity(model='cube', color=color.blue, scale=1)

# Test camera
camera.position = (0, 0, -5)

app.run()
