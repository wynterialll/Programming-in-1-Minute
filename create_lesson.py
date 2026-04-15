import os
import subprocess
import shutil
from pathlib import Path
import ollama # <-- NEW: The library to talk to your local AI
import json   # <-- NEW: To decode the AI's response

def setup_project_folders(topic_name):
    """Automatically generates the strict Media Storage root structure."""
    print(f"--- Setting up folders for: {topic_name} ---")
    
    base_dir = Path("Media Storage") / topic_name
    
    paths = {
        "text": base_dir / "text",
        "image": base_dir / "image",
        "videos": base_dir / "videos",
        "manim_cache": base_dir / "manim_cache" # Temporary holding cell for Manim junk
    }
    
    # Create the subfolders
    for folder in paths.values():
        folder.mkdir(parents=True, exist_ok=True)
        
    # Define the final video as a .mp4 FILE inside the topic root
    final_video_file = base_dir / f"{topic_name}_video.mp4"
        
    return paths, final_video_file

def phase_1_planning(user_topic):
    """Uses your local Gemma AI to write the lesson script."""
    print(f"\n--- Phase 1: Asking AI to plan '{user_topic}' ---")
    
    # We use Prompt Engineering to force the AI to return computer-readable JSON
    prompt = f"""
    You are an expert programming teacher making 1-minute TikToks.
    Write a 1-sentence educational script explaining the concept of: {user_topic}.
    
    You MUST respond ONLY with a valid JSON object in this exact format. Do not include markdown formatting or extra text:
    {{
        "topic_name": "OneWordTopic",
        "spoken_text": "The 1-sentence script to be spoken."
    }}
    """
    
    # Ping the local AI
    response = ollama.chat(model='gemma4:e4b', messages=[
        {'role': 'user', 'content': prompt}
    ], format='json')
    
    # Extract the AI's text and combine it with our Manim template data
    try:
        ai_data = json.loads(response['message']['content'])
        ai_data["template_file"] = "templates/concept_lesson.py"
        ai_data["scene_name"] = "SplitScreenConcept"
        
        print(f"AI Approved Script: {ai_data['spoken_text']}\n")
        return ai_data
    except Exception as e:
        print(f"ERROR: The AI didn't format the text correctly. {e}")
        exit()

def phase_2_generate_audio(text, output_path):
    """Uses Piper TTS and saves directly to the videos folder."""
    print("--- Phase 2: Generating Voice ---")
    
    output_str = str(output_path)
    command = f'echo "{text}" | piper --model en_US-lessac-medium.onnx --output_file "{output_str}"'
    subprocess.run(command, shell=True)
    
    print(f"Audio saved to: {output_str}")
    return output_str

def phase_3_generate_video(template_file, scene_name, organized_video_path, cache_dir):
    """Renders 16:9 wide animation and traps the raw files in a cache folder."""
    print("--- Phase 3: Rendering Animation ---")
    
    # FIX: Removed the -r 1080,1920 flag. Manim will now default to standard wide resolution.
    command = f'manim --media_dir "{cache_dir}" "{template_file}" {scene_name}'
    subprocess.run(command, shell=True)
    
    # Dynamically search the cache folder to find the rendered .mp4
    found_videos = list(cache_dir.glob(f"**/{scene_name}.mp4"))
    
    if found_videos:
        # Move it to our clean videos folder
        shutil.copy(found_videos[0], organized_video_path)
        print(f"Raw video moved to: {organized_video_path}")
        
        # Delete the messy Manim cache folder so your root stays perfectly clean
        shutil.rmtree(cache_dir)
    else:
        print("ERROR: Manim failed to output the video.")
    
    return str(organized_video_path)

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
    # NEW: Chat with your terminal!
    print("Welcome to the TikTok Automator!")
    target_concept = input("What programming concept should we teach today? > ")
    
    # 1. Pass your input to the AI
    lesson_data = phase_1_planning(target_concept)
    
    # 2. Build the folder structure and get paths
    folders, final_save_path = setup_project_folders(lesson_data["topic_name"])
    audio_save_path = folders["videos"] / "raw_audio.wav"
    video_save_path = folders["videos"] / "raw_animation.mp4"
    
    # 3. Run the pipeline
    phase_2_generate_audio(lesson_data["spoken_text"], audio_save_path)
    phase_3_generate_video(lesson_data["template_file"], lesson_data["scene_name"], video_save_path, folders["manim_cache"])
    phase_4_assemble_video(str(video_save_path), str(audio_save_path), final_save_path)