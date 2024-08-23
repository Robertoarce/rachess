from fasthtml.common import *
import base64
from io import BytesIO
from PIL import Image
import gymnasium as gym
import json

app = FastHTML()

def run_simulation(num_steps=200):
    env = gym.make("LunarLander-v2", render_mode="rgb_array")
    observation, info = env.reset()
    frames = []
    actions = []
    observations = []
    rewards = []
    infos = []
    steps=0
    print(steps)
    while steps <= num_steps:
        steps +=1 
        action = env.action_space.sample()
        actions.append(int(action))  # Convert to int for JSON serialization
        observation, reward, terminated, truncated, info = env.step(action)
        observations.append(observation.tolist())  # Convert numpy array to list
        rewards.append(float(reward))  # Convert to float for JSON serialization
        infos.append({k: v.item() if hasattr(v, 'item') else v for k, v in info.items()})  # Convert numpy values to Python types
        img = Image.fromarray(env.render())
        buffered = BytesIO()
        img.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode()
        frames.append(img_str)
        if terminated or truncated:
            observation, info = env.reset()
            steps = num_steps+1
        print(steps)
            
    env.close()
    return frames, actions, observations, rewards, infos

@app.route('/')
def index():
    frames, actions, observations, rewards, infos = run_simulation()
    
    return (
        Title("Lunar Lander Simulation"),
        Link(rel="stylesheet", href="https://cdn.jsdelivr.net/npm/tailwindcss/dist/tailwind.min.css"),
        Main(
            H1("Lunar Lander Simulation", cls="text-2xl font-bold text-center mb-8 bg-gray-200"),
            
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
                    Div(
                        Img(id="lander-animation", src=f"data:image/png;base64,{frames[0]}", 
                            cls="mx-auto border-4 border-gray-300 rounded-lg"),
                        cls="w-full bg-gray-100 p-4 text-center"
                    ),
                    Div(id='frame-number', cls='text-xl font-bold text-center w-full p-5 bg-green-200'),
                    Div(id='actions', cls='text-xl font-bold text-center w-full p-5 bg-yellow-200 overflow-x-auto whitespace-nowrap'),
                    Div(id='observations', cls='text-xl font-bold text-center w-full p-5 bg-yellow-200 overflow-x-auto whitespace-nowrap'),
                    Div(id='rewards', cls='text-xl font-bold text-center w-full p-5 bg-yellow-200 overflow-x-auto whitespace-nowrap'),
                    Div(id='infos', cls='text-xl font-bold text-center w-full p-5 bg-yellow-200 overflow-x-auto whitespace-nowrap'),

                    Div(
                        Button("Rewind", id="rewind-btn", cls="bg-purple-500 text-white px-4 mx-2 py-2 rounded"),
                        Button("Step Backward", id="step-backward-btn", cls="bg-yellow-500 text-white px-4 py-2 rounded mr-2"),
                        Button("Stop", id="stop-btn", cls="bg-red-500 text-white px-4 py-2 rounded mr-2"),
                        Button("Play", id="play-btn", cls="bg-blue-500 text-white px-4 py-2 rounded mr-2"),
                        Button("Step Forward", id="step-forward-btn", cls="bg-green-500 text-white px-4 py-2 rounded mr-2"),
                        cls="flex justify-center mt-4"
                    ),
                    Script(f"""
                        const frames = {json.dumps(frames)};
                        const actions = {json.dumps(actions)};
                        const observations = {json.dumps(observations)};
                        const rewards = {json.dumps(rewards)};
                        const infos = {json.dumps(infos)};
                        let currentFrame = 0;
                        let isPlaying = true;
                        let animationId = null;
                        
                        function updateFrame() {{
                            document.getElementById('lander-animation').src = `data:image/png;base64,${{frames[currentFrame]}}`;
                            document.getElementById('frame-number').textContent = `Frame: ${{currentFrame + 1}}/${{frames.length}}`;
                            document.getElementById('actions').textContent = `Action: ${{actions[currentFrame]}}`;
                            document.getElementById('observations').textContent = `Observation: [${{observations[currentFrame].map(n => n.toFixed(4)).join(', ')}}]`;
                            document.getElementById('rewards').textContent = `Reward: ${{rewards[currentFrame].toFixed(4)}}`;
                            document.getElementById('infos').textContent = `Info: ${{JSON.stringify(infos[currentFrame])}}`;
                        }}

                        function play() {{
                            if (!isPlaying) {{
                                isPlaying = true;
                                animationId = setInterval(() => {{
                                    currentFrame = (currentFrame + 1) % frames.length;
                                    updateFrame();
                                }}, 100);
                            }}
                        }}

                        function stop() {{
                            isPlaying = false;
                            clearInterval(animationId);
                        }}

                        function stepForward() {{
                            stop();
                            currentFrame = (currentFrame + 1) % frames.length;
                            updateFrame();
                        }}

                        function stepBackward() {{
                            stop();
                            currentFrame = (currentFrame - 1 + frames.length) % frames.length;
                            updateFrame();
                        }}

                        function rewind() {{
                            stop();
                            currentFrame = 0;
                            updateFrame();
                        }}

                        document.getElementById('stop-btn').addEventListener('click', stop);
                        document.getElementById('step-forward-btn').addEventListener('click', stepForward);
                        document.getElementById('step-backward-btn').addEventListener('click', stepBackward);
                        document.getElementById('rewind-btn').addEventListener('click', rewind);
                        document.getElementById('play-btn').addEventListener('click', play);

                        updateFrame();
                    """),
                    cls="flex flex-col"
                ),
                cls="mb-8 p-6 bg-white rounded-lg shadow-md"
            ),
            
            cls="container mx-auto px-4"
        )
    )

if __name__ == "__main__":
    serve()