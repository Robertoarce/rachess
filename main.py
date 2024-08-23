from fasthtml.common import *
import base64
from io import BytesIO
from PIL import Image
import gymnasium as gym
import json
import numpy as np

app = FastHTML()

def run_simulation(num_steps=100, custom_actions=None):
    env = gym.make("LunarLander-v2", render_mode="rgb_array")
    observation, info = env.reset()
    frames = []
    actions = []
    observations = []
    rewards = []
    infos = []
    for i in range(num_steps):
        if custom_actions and i < len(custom_actions):
            action = custom_actions[i]
        else:
            action = env.action_space.sample()
        actions.append(int(action))
        observation, reward, terminated, truncated, info = env.step(action)
        observations.append(observation.tolist())
        rewards.append(float(reward))
        infos.append({k: v.item() if hasattr(v, 'item') else v for k, v in info.items()})
        img = Image.fromarray(env.render())
        buffered = BytesIO()
        img.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode()
        frames.append(img_str)
        if terminated or truncated:
            observation, info = env.reset()
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
            
            Div(
                Div(
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
                            cls="flex flex-col"
                        ),
                        cls="mb-8 p-6 bg-white rounded-lg shadow-md"
                    ),
                    cls="w-2/3 pr-4"
                ),
                Div(
                    Card(
                        H2("Custom Actions", cls="text-2xl font-semibold mb-4"),
                        P("Enter custom actions (0-3) separated by commas. Leave blank for random actions.", cls="mb-2"),
                        Textarea(id="custom-actions", cls="w-full p-2 border rounded", rows="10"),
                        Button("Run Simulation", id="run-simulation-btn", cls="mt-4 bg-blue-500 text-white px-4 py-2 rounded"),
                        cls="p-6 bg-white rounded-lg shadow-md"
                    ),
                    cls="w-1/3 pl-4"
                ),
                cls="flex"
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

                document.getElementById('run-simulation-btn').addEventListener('click', async () => {{
                    const customActionsInput = document.getElementById('custom-actions').value;
                    const customActions = customActionsInput ? customActionsInput.split(',').map(Number) : [];
                    
                    const response = await fetch('/run_simulation', {{
                        method: 'POST',
                        headers: {{
                            'Content-Type': 'application/json',
                        }},
                        body: JSON.stringify({{ custom_actions: customActions }}),
                    }});
                    
                    const data = await response.json();
                    frames.length = 0;
                    frames.push(...data.frames);
                    actions.length = 0;
                    actions.push(...data.actions);
                    observations.length = 0;
                    observations.push(...data.observations);
                    rewards.length = 0;
                    rewards.push(...data.rewards);
                    infos.length = 0;
                    infos.push(...data.infos);
                    
                    currentFrame = 0;
                    updateFrame();
                }});

                updateFrame();
            """),
            cls="container mx-auto px-4"
        )
    )

@app.route('/run_simulation', methods=['POST'])
async def run_custom_simulation(request):
    data = await request.json()
    custom_actions = data.get('custom_actions', [])
    frames, actions, observations, rewards, infos = run_simulation(custom_actions=custom_actions)
    return JSONResponse({
        'frames': frames,
        'actions': actions,
        'observations': observations,
        'rewards': rewards,
        'infos': infos
    })

if __name__ == "__main__":
    serve()