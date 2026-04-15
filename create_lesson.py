import os
import subprocess
import shutil
from pathlib import Path
import ollama # <-- NEW: The library to talk to your local AI
import json   # <-- NEW: To decode the AI's response
import wave # To measure audio duration

def setup_project_folders(topic_name):
    base_dir = Path("Media Storage") / topic_name
    paths = {"text": base_dir / "text", "image": base_dir / "image", 
             "videos": base_dir / "videos", "manim_cache": base_dir / "manim_cache"}
    for folder in paths.values():
        folder.mkdir(parents=True, exist_ok=True)
    return paths, base_dir / f"{topic_name}_video.mp4"

def get_audio_duration(audio_path):
    with wave.open(str(audio_path), 'rb') as f:
        return f.getnframes() / float(f.getframerate())

def phase_1_brain(user_topic):
    """Two-Agent AI Pipeline: 1. Scriptwriter -> 2. Manim Coder"""
    print(f"\n--- Phase 1A: Scripting '{user_topic}' ---")
    
    # AGENT 1: The Scriptwriter
    script_prompt = f"Write a 1-minute (150 word) script for a beginner about {user_topic} using a real-world analogy. Return ONLY JSON: {{\"spoken_text\": \"...\"}}"
    res1 = ollama.chat(model='gemma4:e4b', messages=[{'role': 'user', 'content': script_prompt}], format='json', options={'keep_alive': 0})
    script_data = json.loads(res1['message']['content'])
    
    print(f"--- Phase 1B: Coding Animation ---")
    # AGENT 2: The Manim Coder (reads the ai_reference.txt)
    with open("ai_reference.txt", "r") as f:
        reference = f.read()

    coder_prompt = f"""
    Based on this script: "{script_data['spoken_text']}"
    Write ONLY the Python code for the 'construct(self)' method of a Manim Scene.
    Use these components: {reference}
    Return ONLY JSON: {{"manim_code": "self.play(...); self.wait(...)"}}
    """
    res2 = ollama.chat(model='gemma4:e4b', messages=[{'role': 'user', 'content': coder_prompt}], format='json', options={'keep_alive': 0})
    coder_data = json.loads(res2['message']['content'])
    
    script_data.update(coder_data)
    script_data["topic_name"] = user_topic.replace(" ", "_")
    return script_data

def generate_manim_file(topic_name, ai_code):
    """Combines a master template with the AI's generated code."""
    template = f"""
from manim import *
from templates.visual_lib import * # Imports your Lego bricks

class AI_Generated_Scene(Scene):
    def construct(self):
        self.camera.background_color = "#050505"
        # AI GENERATED CODE BELOW
        {ai_code}
    """
    file_path = Path("templates") / f"gen_{topic_name}.py"
    with open(file_path, "w") as f:
        f.write(template)
    return file_path

def phase_2_generate_audio(text, output_path):
    """Uses Piper TTS and saves directly to the videos folder."""
    print("--- Phase 2: Generating Voice ---")
    
    output_str = str(output_path)
    command = f'echo "{text}" | piper --model en_US-lessac-medium.onnx --output_file "{output_str}"'
    subprocess.run(command, shell=True)
    
    print(f"Audio saved to: {output_str}")
    return output_str

def phase_3_generate_video(template_file, scene_name, video_path, cache_dir, duration):
    print(f"--- Phase 3: Rendering Animation ({duration:.2f}s) ---")
    # We pass the duration into the environment variables for Manim to read
    env_vars = os.environ.copy()
    env_vars["VIDEO_DURATION"] = str(duration)
    
    command = f'manim --media_dir "{cache_dir}" "{template_file}" {scene_name}'
    subprocess.run(command, shell=True, env=env_vars)
    
    found_videos = list(cache_dir.glob(f"**/{scene_name}.mp4"))
    if found_videos:
        shutil.copy(found_videos[0], video_path)
        shutil.rmtree(cache_dir)

def phase_4_assemble_video(video_path, audio_path, final_output_path):
    """Stitches audio and video, standardizing to a universal wide format."""
    print("--- Phase 4: Final Assembly (FFmpeg) ---")
    
    command = (
        f'ffmpeg -stream_loop -1 -i "{video_path}" -i "{audio_path}" '
        f'-c:v libx264 -pix_fmt yuv420p '
        f'-c:a aac -ar 44100 -ac 2 -b:a 128k '
        f'-shortest -y "{final_output_path}"'
    )
    
    subprocess.run(command, shell=True)
    print(f"SUCCESS! Your video is ready: {final_output_path}")

# ==========================================
# MASTER EXECUTION
# ==========================================
if __name__ == "__main__":
    topic = input("What are we teaching? > ")
    
    # 1. Two-Agent Planning
    lesson_data = phase_1_brain(topic)
    
    # 2. Setup & File Creation
    folders, final_path = setup_project_folders(lesson_data["topic_name"])
    manim_file = generate_manim_file(lesson_data["topic_name"], lesson_data["manim_code"])
    
    # 3. Audio & Rendering
    audio_path = folders["videos"] / "raw_audio.wav"
    phase_2_generate_audio(lesson_data["spoken_text"], audio_path)
    
    # 4. Final Video
    phase_3_generate_video(str(manim_file), "AI_Generated_Scene", folders["videos"] / "raw_animation.mp4", folders["manim_cache"])
    phase_4_assemble_video(str(folders["videos"] / "raw_animation.mp4"), str(audio_path), final_path)