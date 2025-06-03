import os
import platform

import numpy as np
from moviepy.editor import (ImageClip, AudioFileClip, TextClip, CompositeVideoClip,
                            concatenate_videoclips, vfx, CompositeAudioClip, afx) # CompositeAudioClip, afx 추가
from PIL import Image, ImageOps

# config에서 BGM 관련 설정도 가져오도록 수정
from config import (VIDEOS_FOLDER, IMAGES_RAW_FOLDER, DEFAULT_FONT_PATH_WIN,
                    DEFAULT_FONT_PATH_MAC, DEFAULT_FONT_PATH_LINUX,
                    VIDEO_RESOLUTION, VIDEO_FPS, MAX_VIDEO_LENGTH,
                    SINGLE_BGM_FILE_PATH, DEFAULT_BGM_VOLUME,
                    TTS_SAMPLE_RATE_HERTZ) # TTS_SAMPLE_RATE_HERTZ 추가
from utils.file_utils import ensure_folder_exists
from core.scenario_generator import recommend_image_for_scene

# --- ImageMagick 경로 설정 (기존과 동일) ---
imagemagick_binary_path = r"C:\Program Files\ImageMagick-7.1.1-Q16-HDRI\magick.exe"

if os.path.isfile(imagemagick_binary_path):
    if "IMAGEMAGICK_BINARY" not in os.environ:
         os.environ["IMAGEMAGICK_BINARY"] = imagemagick_binary_path
    print(f"ImageMagick 바이너리 경로 확인/설정됨: {os.environ.get('IMAGEMAGICK_BINARY')}")
else:
    print(f"Warning: ImageMagick 바이너리 파일을 찾을 수 없습니다: {imagemagick_binary_path}")
    print("자막 생성에 문제가 발생할 수 있습니다. ImageMagick을 설치하고 경로를 정확히 지정하거나, 시스템 PATH에 추가해주세요.")

# --- get_system_font 함수 (기존과 거의 동일, macOS 경로 수정됨) ---
def get_system_font():
    system = platform.system()

    if system == 'Windows':
        nanum_gothic_bold = r"C:/Windows/Fonts/NanumGothicBold.ttf"
        if os.path.exists(nanum_gothic_bold):
            print(f"Using font: {nanum_gothic_bold} (NanumGothic Bold)")
            return nanum_gothic_bold
        nanum_gothic = r"C:/Windows/Fonts/NanumGothic.ttf"
        if os.path.exists(nanum_gothic):
            print(f"Using font: {nanum_gothic} (NanumGothic)")
            return nanum_gothic
        specific = os.path.join(os.environ.get("SystemRoot", "C:/Windows"), "Fonts", DEFAULT_FONT_PATH_WIN)
        if os.path.exists(specific):
            print(f"Using font: {specific} (From config)")
            return specific
        print(f"Warning: Windows font not found, falling back to '{DEFAULT_FONT_PATH_WIN.split('.')[0]}'")
        return DEFAULT_FONT_PATH_WIN.split('.')[0]
    elif system == 'Darwin':
        mac_font_dir = "/Users/kimyihyeon/Desktop/Capstone-Design-Team3/Nanum_Gothic"
        font_path_candidate = os.path.join(mac_font_dir, "NanumGothic-Bold.ttf")
        if os.path.exists(font_path_candidate):
            print(f"Using font: {font_path_candidate} (NanumGothic-Bold from project)")
            return font_path_candidate
        fallback = "Apple SD Gothic Neo"
        print(f"Warning: NanumGothic not found in {mac_font_dir}, falling back to system font '{fallback}'")
        return fallback
    else:
        font_path = DEFAULT_FONT_PATH_LINUX
        font_full = os.path.join("/usr/share/fonts/truetype", font_path)
        if os.path.exists(font_full):
            print(f"Using font: {font_full}")
            return font_full
        print(f"Warning: 지정된 폰트({font_full})를 찾을 수 없습니다. '{font_path.split('.')[0]}'로 시도합니다.")
        return font_path.split('.')[0]


def create_video_from_scenario(scenario_data_with_audio, product_name, downloaded_image_paths):
    if not scenario_data_with_audio:
        print("시나리오 데이터가 없어 영상 생성을 건너뜁니다.")
        return None

    font_for_subtitle = get_system_font()
    print(f"자막 생성에 사용될 폰트: {font_for_subtitle}")

    print("\n=== MoviePy 영상 조합 시작 ===")
    ensure_folder_exists(VIDEOS_FOLDER)

    scene_clips = []
    narration_audio_clips_for_scenes = []

    if downloaded_image_paths:
        available_images = [img_path for img_path in downloaded_image_paths if os.path.exists(img_path)]
    else:
        available_images = []

    placeholder_path_temp = os.path.join(IMAGES_RAW_FOLDER, "placeholder_temp.png")
    if not available_images:
        print("사용 가능한 이미지가 없습니다. 플레이스홀더 이미지를 사용합니다.")
        if not os.path.exists(placeholder_path_temp):
            try:
                Image.new('RGB', VIDEO_RESOLUTION, color='lightgrey').save(placeholder_path_temp)
            except Exception as e_placeholder:
                print(f"플레이스홀더 이미지 생성 실패: {e_placeholder}.")

    total_video_duration_calculated = 0
    used_image_filenames_in_video = []

    for scene_info in scenario_data_with_audio:
        scene_num = scene_info.get("scene_number", "N/A")
        narration = scene_info.get("narration", "")
        subtitle_text = scene_info.get("subtitle", "")
        audio_file_path = scene_info.get("audio_file_path")

        scene_duration = 0
        audio_clip_for_this_scene = None

        if audio_file_path and os.path.exists(audio_file_path):
            try:
                # ++++++++++ AudioFileClip 로드 시 FPS 명시적 지정 ++++++++++
                audio_clip_for_this_scene = AudioFileClip(audio_file_path, fps=TTS_SAMPLE_RATE_HERTZ)
                # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++
                narration_audio_clips_for_scenes.append(audio_clip_for_this_scene)
                scene_duration = audio_clip_for_this_scene.duration

                ##### DEBUG PRINT START #####
                if audio_clip_for_this_scene:
                    print(f"    DEBUG: Scene {scene_num} TTS audio loaded. Duration: {audio_clip_for_this_scene.duration:.2f}s, FPS: {getattr(audio_clip_for_this_scene, 'fps', 'N/A')}, Channels: {getattr(audio_clip_for_this_scene, 'nchannels', 'N/A')}")
                ##### DEBUG PRINT END #####

                if "actual_audio_duration_seconds" in scene_info and scene_info["actual_audio_duration_seconds"] > 0:
                    scene_duration = scene_info["actual_audio_duration_seconds"]
                json_duration = scene_info.get("duration_seconds", scene_duration)
                if abs(scene_duration - json_duration) > 1.5 :
                    print(f"  Warning: Scene {scene_num} - 실제 오디오 길이({scene_duration:.2f}s)와 JSON 명시 길이({json_duration}s) 차이 발생.")
            except Exception as e:
                print(f"  Warning: Scene {scene_num} 오디오 파일 로드 실패 ({audio_file_path}): {e}.")
                scene_duration = scene_info.get("duration_seconds", 3)
                audio_clip_for_this_scene = None # 실패 시 None으로 설정
        else:
            print(f"  Scene {scene_num}: 오디오 파일 경로가 없거나 파일이 존재하지 않음. JSON의 duration_seconds 사용.")
            scene_duration = scene_info.get("duration_seconds", 3)

        if scene_duration <= 0.1:
            print(f"  Warning: Scene {scene_num}의 유효한 재생 시간이 너무 짧습니다({scene_duration:.2f}s). 0.5초로 강제 설정.")
            scene_duration = 0.5
        total_video_duration_calculated += scene_duration

        scene_image_description = scene_info.get("recommended_image_description", "")
        selected_image_path = recommend_image_for_scene(
            scene_description=scene_image_description,
            scene_narration=narration,
            scene_subtitle=subtitle_text,
            available_image_paths=available_images,
            product_name=product_name,
            scene_number=str(scene_num),
            previously_used_filenames=used_image_filenames_in_video
        )
        if not selected_image_path or not os.path.exists(selected_image_path):
            print(f"  Scene {scene_num}: 적합한 이미지 찾지 못함/경로 유효하지 않음. 플레이스홀더 사용.")
            if not os.path.exists(placeholder_path_temp):
                 Image.new('RGB', VIDEO_RESOLUTION, color='grey').save(placeholder_path_temp)
            selected_image_path = placeholder_path_temp
        else:
            used_image_filenames_in_video.append(os.path.basename(selected_image_path))
        print(f"  Scene {scene_num}: 최종 선택 이미지 '{os.path.basename(selected_image_path)}', 길이: {scene_duration:.2f}s")
        try:
            pil_image = Image.open(selected_image_path)
            pil_image = pil_image.convert("RGB")
            resized_pil_image = ImageOps.pad(pil_image, VIDEO_RESOLUTION, method=Image.Resampling.LANCZOS, color=(0,0,0))
            numpy_image = np.array(resized_pil_image)
            img_clip = ImageClip(numpy_image)
            img_clip = img_clip.set_duration(scene_duration)
        except Exception as e:
            print(f"  Error creating image clip for Scene {scene_num} ({selected_image_path}): {e}. Using placeholder.")
            if not os.path.exists(placeholder_path_temp): Image.new('RGB', VIDEO_RESOLUTION, color='darkgrey').save(placeholder_path_temp)
            pil_placeholder = Image.open(placeholder_path_temp).convert("RGB")
            resized_placeholder = ImageOps.pad(pil_placeholder, VIDEO_RESOLUTION, method=Image.Resampling.LANCZOS, color=(0,0,0))
            numpy_placeholder = np.array(resized_placeholder)
            img_clip = ImageClip(numpy_placeholder).set_duration(scene_duration)

        txt_clip = None
        if subtitle_text:
            try:
                txt_clip = TextClip(subtitle_text, fontsize=50, color='white', font=font_for_subtitle,
                                    stroke_color='black', stroke_width=2.5, method='caption',
                                    size=(VIDEO_RESOLUTION[0]*0.9, None), align='South', kerning=-1)
                txt_clip = txt_clip.set_position(('center', VIDEO_RESOLUTION[1] * 0.8)).set_duration(scene_duration)
            except Exception as e:
                print(f"  Error creating text clip for Scene {scene_num} ('{subtitle_text}') using font '{font_for_subtitle}': {e}")

        compositing_list = [img_clip]
        if txt_clip: compositing_list.append(txt_clip)

        scene_video_clip = CompositeVideoClip(compositing_list, size=VIDEO_RESOLUTION, bg_color=(0,0,0))
        if audio_clip_for_this_scene: # audio_clip_for_this_scene이 유효할 때만 set_audio
            scene_video_clip = scene_video_clip.set_audio(audio_clip_for_this_scene)
        scene_clips.append(scene_video_clip)

    if not scene_clips:
        print("생성된 씬 클립이 없어 영상을 만들 수 없습니다.")
        if os.path.exists(placeholder_path_temp):
            try: os.remove(placeholder_path_temp)
            except: pass
        return None

    base_video_clip_with_narration = concatenate_videoclips(scene_clips, method="compose")
    print(f"\n조합된 영상의 총 길이 (씬 기반 계산): {total_video_duration_calculated:.2f} 초")
    print(f"MoviePy 기본 클립 길이 (나레이션 포함): {base_video_clip_with_narration.duration:.2f} 초")

    # ================== BGM 추가 로직 시작 ==================
    final_clip_for_render = base_video_clip_with_narration
    bgm_audio_clip_object = None

    bgm_file_to_use = SINGLE_BGM_FILE_PATH
    bgm_volume_to_use = DEFAULT_BGM_VOLUME

    if os.path.exists(bgm_file_to_use):
        print(f"BGM 파일 로드 시도: {bgm_file_to_use}")
        try:
            bgm_audio_clip_object = AudioFileClip(bgm_file_to_use)

            ##### DEBUG PRINT START #####
            if bgm_audio_clip_object:
                print(f"  DEBUG: Initial BGM audio loaded. Duration: {bgm_audio_clip_object.duration:.2f}s, FPS: {getattr(bgm_audio_clip_object, 'fps', 'N/A')}, Channels: {getattr(bgm_audio_clip_object, 'nchannels', 'N/A')}")
            else:
                print("  DEBUG: BGM audio clip object is None after loading attempt.")
            ##### DEBUG PRINT END #####

            video_duration = base_video_clip_with_narration.duration
            if bgm_audio_clip_object and bgm_audio_clip_object.duration < video_duration:
                try:
                    bgm_audio_clip_object = afx.audio_loop(bgm_audio_clip_object, duration=video_duration)
                    print(f"BGM을 영상 길이에 맞춰 반복 설정 (총 {video_duration:.2f}초)")
                except AttributeError:
                    print(f"Warning: afx.audio_loop 사용 불가. BGM이 영상보다 짧으면 앞부분만 재생됩니다. (BGM 길이: {bgm_audio_clip_object.duration:.2f}초)")
                    bgm_audio_clip_object = bgm_audio_clip_object.subclip(0, min(bgm_audio_clip_object.duration, video_duration))
            elif bgm_audio_clip_object:
                bgm_audio_clip_object = bgm_audio_clip_object.subclip(0, video_duration)
                print(f"BGM을 영상 길이에 맞춰 자르기 (총 {video_duration:.2f}초)")

            ##### DEBUG PRINT START #####
            if bgm_audio_clip_object:
                print(f"  DEBUG: BGM audio after length adjustment. Duration: {bgm_audio_clip_object.duration:.2f}s, FPS: {getattr(bgm_audio_clip_object, 'fps', 'N/A')}, Channels: {getattr(bgm_audio_clip_object, 'nchannels', 'N/A')}")
            ##### DEBUG PRINT END #####

            if bgm_audio_clip_object:
                bgm_audio_clip_object = bgm_audio_clip_object.volumex(bgm_volume_to_use)
                print(f"BGM 볼륨 설정: {bgm_volume_to_use}")

                ##### DEBUG PRINT START #####
                print(f"  DEBUG: BGM audio after volume adjustment. Duration: {bgm_audio_clip_object.duration:.2f}s, FPS: {getattr(bgm_audio_clip_object, 'fps', 'N/A')}, Channels: {getattr(bgm_audio_clip_object, 'nchannels', 'N/A')}")
                ##### DEBUG PRINT END #####

            narration_audio = base_video_clip_with_narration.audio

            ##### DEBUG PRINT START #####
            if narration_audio:
                print(f"  DEBUG: Narration audio from base_video_clip. Duration: {narration_audio.duration:.2f}s, FPS: {getattr(narration_audio, 'fps', 'N/A')}, Channels: {getattr(narration_audio, 'nchannels', 'N/A')}")
            else:
                print("  DEBUG: No narration audio found in base_video_clip_with_narration (base_video_clip_with_narration.audio is None).")
            ##### DEBUG PRINT END #####

            if narration_audio and bgm_audio_clip_object:
                combined_audio = CompositeAudioClip([narration_audio, bgm_audio_clip_object])
                final_clip_for_render = base_video_clip_with_narration.set_audio(combined_audio)

                ##### DEBUG PRINT START #####
                if final_clip_for_render.audio:
                    print(f"  DEBUG: Combined audio in final_clip_for_render. Duration: {final_clip_for_render.audio.duration:.2f}s, FPS: {getattr(final_clip_for_render.audio, 'fps', 'N/A')}, Channels: {getattr(final_clip_for_render.audio, 'nchannels', 'N/A')}")
                else:
                    print("  DEBUG: final_clip_for_render.audio is None after attempting to set combined audio.")
                ##### DEBUG PRINT END #####

            elif bgm_audio_clip_object:
                final_clip_for_render = base_video_clip_with_narration.set_audio(bgm_audio_clip_object)
                ##### DEBUG PRINT START #####
                if final_clip_for_render.audio:
                    print(f"  DEBUG: BGM-only audio in final_clip_for_render. Duration: {final_clip_for_render.audio.duration:.2f}s, FPS: {getattr(final_clip_for_render.audio, 'fps', 'N/A')}, Channels: {getattr(final_clip_for_render.audio, 'nchannels', 'N/A')}")
                else:
                    print("  DEBUG: final_clip_for_render.audio is None after attempting to set BGM-only audio.")
                ##### DEBUG PRINT END #####
            else:
                 print("  DEBUG: No narration and no valid BGM to set for the final clip.")

            if narration_audio or bgm_audio_clip_object:
                 print("BGM (또는 나레이션만)이 성공적으로 오디오 트랙에 설정/합성되었습니다.")

        except Exception as e_bgm:
            print(f"BGM 추가 중 오류 발생 ({bgm_file_to_use}): {e_bgm}. BGM 없이 영상을 생성합니다.")
            if bgm_audio_clip_object:
                if hasattr(bgm_audio_clip_object, 'close') and callable(bgm_audio_clip_object.close):
                    try: bgm_audio_clip_object.close()
                    except: pass
                bgm_audio_clip_object = None
    else:
        print(f"BGM 파일을 찾을 수 없습니다: {bgm_file_to_use}. BGM 없이 영상을 생성합니다.")
    # ================== BGM 추가 로직 끝 ==================

    if final_clip_for_render.duration > MAX_VIDEO_LENGTH:
        print(f"⚠️ 경고: 최종 영상 길이({final_clip_for_render.duration:.2f}초)가 목표({MAX_VIDEO_LENGTH}초)를 초과했습니다.")

    safe_product_name = "".join(c if c.isalnum() else "_" for c in product_name[:30])
    output_video_filename = f"{safe_product_name}_shorts_video_bgm.mp4"
    output_video_path = os.path.join(VIDEOS_FOLDER, output_video_filename)

    try:
        print(f"\n최종 영상 저장 중... ({output_video_path})")
        final_clip_for_render.write_videofile(output_video_path,
                                   fps=VIDEO_FPS, # 영상의 FPS
                                   codec="libx264",
                                   audio_codec="aac",
                                   # ++++++++++ audio_fps 추가 시도 ++++++++++
                                   audio_fps=TTS_SAMPLE_RATE_HERTZ, # 나레이션 오디오의 샘플링 속도를 명시
                                   # +++++++++++++++++++++++++++++++++++++
                                   threads=os.cpu_count(),
                                   preset="medium",
                                   ffmpeg_params=['-crf', '23'],
                                   verbose=True,
                                   logger='bar'
                                  )
        print(f"🎉 최종 영상 저장 완료: {output_video_path}")
        return output_video_path
    except Exception as e:
        print(f"최종 영상 저장 중 오류 발생: {e}")
        return None
    finally:
        # 리소스 해제
        if 'final_clip_for_render' in locals() and final_clip_for_render:
            if hasattr(final_clip_for_render, 'close') and callable(final_clip_for_render.close):
                try: final_clip_for_render.close()
                except: pass
        for audio_clip in narration_audio_clips_for_scenes:
            if audio_clip:
                if hasattr(audio_clip, 'close') and callable(audio_clip.close):
                    try: audio_clip.close()
                    except: pass
        # bgm_audio_clip_object는 final_clip_for_render에 포함되거나 위에서 닫힐 수 있음
        if 'bgm_audio_clip_object' in locals() and bgm_audio_clip_object:
             if hasattr(bgm_audio_clip_object, 'close') and callable(bgm_audio_clip_object.close):
                try: bgm_audio_clip_object.close() # 명시적으로 다시 닫아도 안전
                except: pass
        for sc_clip_obj in scene_clips:
            if sc_clip_obj:
                if hasattr(sc_clip_obj, 'reader') and hasattr(sc_clip_obj.reader, 'close_proc'):
                    try: sc_clip_obj.reader.close_proc()
                    except: pass
                if hasattr(sc_clip_obj, 'close') and callable(sc_clip_obj.close):
                    try: sc_clip_obj.close()
                    except: pass
        if os.path.exists(placeholder_path_temp):
            try: os.remove(placeholder_path_temp)
            except: pass