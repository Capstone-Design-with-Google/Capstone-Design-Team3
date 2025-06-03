import os
import time
import config # config 모듈 import
from config import initialize_project_folders # config에서 함수 직접 import
from core.data_collector import setup_image_collection, collect_product_details, download_images_from_urls
from core.image_processor import extract_texts_from_images_in_folder
from core.scenario_generator import generate_initial_narration, generate_scene_by_scene_script # 수정
from core.voice_generator import generate_audio_clips_from_scenario
from core.video_editor import create_video_from_scenario

def run_ai_shorts_generator(target_url):
    start_time = time.time()
    print("🚀 AI 쇼츠 영상 자동 생성 시작 🚀")
    initialize_project_folders()

    print("\n--- [Step 1] 데이터 수집 시작 ---")
    setup_image_collection()
    product_data = collect_product_details(target_url)
    if not product_data or not product_data.get("name") or product_data.get("name") == "정보 없음": # 상품명 확인
        print("상품 정보를 제대로 수집하지 못했습니다. 프로세스를 중단합니다.")
        return
    product_name = product_data["name"]
    print(f"수집된 상품명: {product_name}")
    product_data["downloaded_image_paths"] = download_images_from_urls(
        product_data.get("image_urls", []), target_url
    )

    print("\n--- [Step 2] 이미지 내 OCR 텍스트 추출 시작 ---")
    all_ocr_texts = extract_texts_from_images_in_folder(config.IMAGES_RAW_FOLDER) # config 사용
    if not all_ocr_texts:
        print("이미지에서 OCR 텍스트를 추출하지 못했습니다. 나레이션 품질에 영향이 있을 수 있습니다.")

    print("\n--- [Step 3.1] 초기 전체 나레이션 생성 시작 ---")
    initial_narration = generate_initial_narration(product_name, all_ocr_texts)
    if not initial_narration:
        print("초기 전체 나레이션을 생성하지 못했습니다. 프로세스를 중단합니다.")
        return

    print("\n--- [Step 3.2] 씬별 JSON 스크립트 생성 시작 ---")
    scene_script_data = generate_scene_by_scene_script(product_name, initial_narration)
    if not scene_script_data:
        print("씬별 JSON 스크립트를 생성하지 못했습니다. 프로세스를 중단합니다.")
        return

    print("\n--- [Step 4] 음성 클립 생성 시작 ---")
    scenario_data_with_audio = generate_audio_clips_from_scenario(scene_script_data, product_name)
    if not scenario_data_with_audio: # 오류가 나도 원본 scene_script_data를 사용하도록 voice_generator에서 처리
        print("음성 클립 생성에 일부 문제가 있었을 수 있습니다. 원본 시나리오 데이터로 진행합니다.")
        scenario_data_with_audio = scene_script_data 

    print("\n--- [Step 5] 영상 조합 시작 ---")
    final_video_path = create_video_from_scenario(
        scenario_data_with_audio,
        product_name,
        product_data.get("downloaded_image_paths", []) # downloaded_image_paths가 없을 수도 있으므로 .get 사용
    )

    if final_video_path: print(f"\n🎉 모든 작업 완료! 생성된 영상: {final_video_path}")
    else: print("\n😥 영상 생성에 실패했습니다.")
    end_time = time.time()
    print(f"총 실행 시간: {end_time - start_time:.2f} 초")
    return final_video_path

if __name__ == "__main__":
    # target_product_url = "https://prod.danawa.com/info/?pcode=41499608&cate=10253217"
    target_product_url = "https://commerceh.cafe24.com/product/%ED%85%8C%EC%98%A4%ED%91%B8%EB%93%9C-%EC%95%84%EB%A1%B1%EC%82%AC%ED%83%9C-%EC%8A%A4%EC%A7%80%EC%A0%84%EA%B3%A8/830/category/1/display/3/"
    # target_product_url = "https://commerceh.cafe24.com/product/%EB%82%AD%EB%A7%8C%ED%91%B8%EB%93%9C-%EC%88%AF%EB%B6%88%EC%96%91%EB%85%90%EC%B9%98%ED%82%A8-%EC%B9%98%EC%A6%88%EB%B6%88%EB%8B%AD-%EC%96%91%EB%85%90%EC%82%BC%EA%B2%B9%EB%B0%94%EB%B2%A0%ED%81%90/841/category/1/display/3/"
    # API 키 및 GCP 인증 파일 경로 확인 (config.py에서 수행되지만, 여기서 한 번 더 명시적으로 알림)
    if not config.GOOGLE_API_KEY_GEMINI:
        print("🚨 중요: Gemini API 키가 config.py 또는 .env 파일에 설정되지 않았습니다.")
    if not os.path.exists(config.GCP_SERVICE_ACCOUNT_KEY_PATH):
         print(f"🚨 중요: GCP 서비스 계정 키 파일({config.GCP_SERVICE_ACCOUNT_KEY_PATH})을 찾을 수 없습니다.")
    
    # 로컬에서 ChromeDriver 자동 설치 (선택 사항)
    # try:
    #     from webdriver_manager.chrome import ChromeDriverManager
    #     from selenium.webdriver.chrome.service import Service as ChromeService
    #     # driver_path = ChromeDriverManager().install() # 이것만으로도 PATH에 잡히거나, 서비스 객체에 경로 전달
    #     print("WebDriver Manager를 통해 ChromeDriver 준비 완료 또는 확인됨.")
    # except ImportError:
    #     print("webdriver-manager가 설치되지 않았습니다. `pip install webdriver-manager`를 고려해보세요.")
    #     print("또는 ChromeDriver를 수동으로 설치하고 PATH에 추가해야 합니다.")
    # except Exception as e_wdm:
    #     print(f"webdriver-manager 실행 중 오류: {e_wdm}. ChromeDriver 수동 설정 필요.")


    run_ai_shorts_generator(target_product_url)