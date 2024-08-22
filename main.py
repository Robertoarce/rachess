import base64
from io import BytesIO
from PIL import Image
import gymnasium as gym
from fasthtml.common import *

app = FastHTML(
    ftrs=(
        StyleX('tailwind.css'),
    )
)

def run_simulation(num_steps=100):
    env = gym.make("LunarLander-v2", render_mode="rgb_array")
    observation, info = env.reset()
    frames = []
    for _ in range(num_steps):
        action = env.action_space.sample()
        observation, reward, terminated, truncated, info = env.step(action)
        
        img = Image.fromarray(env.render())
        buffered = BytesIO()
        img.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode()
        frames.append(img_str)
        if terminated or truncated:
            observation, info = env.reset()
    env.close()
    return frames

@app.route('/')
def index():
    frames = run_simulation()
    
    return (
        Title("Lunar Lander Simulation"),
        Main(
            H1("Lunar Lander Simulation", cls="text-2xl font-bold text-center mb-8"),
            
            Card(
                H2("About Lunar Lander", cls="text-2xl font-semibold mb-4"),
                P("Lunar Lander is a classic control problem in reinforcement learning. "
                  "The goal is to land a spacecraft on the moon's surface. The agent "
                  "must control the spacecraft's thrusters to navigate it safely to the landing pad.",
                  cls="text-gray-700"),
                cls="mb-8 p-6 bg-white rounded-lg shadow-md"
            ),
            
            Card(
                H2("Simulation Viewer", cls="text-2xl font-semibold mb-4"),
                Div(
                    Img(id="lander-animation", src=f"data:image/png;base64,{frames[0]}", 
                        cls="mx-auto border-4 border-gray-300 rounded-lg"),
                    cls="bg-gray-100 p-4 text-center"
                ),
                Script(f"""
                    const frames = {frames};
                    let currentFrame = 0;
                    function updateFrame() {{
                        document.getElementById('lander-animation').src = `data:image/png;base64,${{frames[currentFrame]}}`;
                        currentFrame = (currentFrame + 1) % frames.length;
                        requestAnimationFrame(updateFrame);
                    }}
                    requestAnimationFrame(updateFrame);
                """),
                cls="mb-8 p-6 bg-white rounded-lg shadow-md"
            ),
            
            Card(
                H2("Simulation Code", cls="text-2xl font-semibold mb-4"),
                Pre(Code("""
import gymnasium as gym
env = gym.make("LunarLander-v2", render_mode="rgb_array")
observation, info = env.reset()
for _ in range(100):
    action = env.action_space.sample()  # agent policy that uses the observation and info
    observation, reward, terminated, truncated, info = env.step(action)
    if terminated or truncated:
        observation, info = env.reset()
env.close()
                """.strip(), cls="language-python")),
                cls="p-6 bg-white rounded-lg shadow-md"
            ),
            cls="container mx-auto px-4"
        )
    )

if __name__ == "__main__":
    serve()