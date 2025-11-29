import gradio as gr
import os
from io import BytesIO
from PIL import Image

# ⚠️ Gemini API 클라이언트 초기화 ⚠️
# API 키는 환경 변수(GEMINI_API_KEY)에서 자동으로 가져옵니다. 
try:
    from google import genai
    from google.genai.types import GenerateImagesConfig
    # 클라이언트 초기화 (API 키는 환경 변수에서 자동 로드됨)
    client = genai.Client()
    IMAGE_MODEL = 'imagen-3.0-generate-002'
    API_STATUS = "Gemini 클라이언트 초기화 성공"
except Exception as e:
    # API 키 오류나 라이브러리 초기화 실패 시 더미 모드로 전환
    print(f"Gemini 클라이언트 초기화 실패: {e}")
    client = None
    IMAGE_MODEL = "Dummy Mode"
    API_STATUS = f"Gemini API 키 오류 또는 라이브러리 문제: {e}"


# --- 1. 프롬프트 생성에 사용될 데이터 및 맵핑 ---
# 모든 캐릭터에 일관성을 부여하는 핵심 키워드 (푸딩 스타일 고정)
BASE_STYLE = "cute anthropomorphic pudding character, thick black outline, 2D minimalist sticker style, no frosting or cream, clean white background, digital art"

# Q1: 에너지 유형 -> 푸딩 맛(색깔) 결정
FLAVOR_MAP = {
    "외향": "vibrant strawberry red pudding",
    "내향": "calm indigo blueberry pudding",
}

# Q5: 데이트 선호 분위기 -> 행동/배경 결정
BEHAVIOR_MAP = {
    "잔잔함": "sitting by a window, reading a book calmly, small smile",
    "활발함": "jumping energetically, wearing running shoes",
    "탐험·액티비티": "climbing a small mountain peak, looking adventurous",
    "예술적": "holding a small paintbrush, standing next to an easel",
    "감성적": "looking up at the sunset with a thoughtful expression",
}

# Q10: 가치관 우선순위 -> 성격 강조
VALUE_ADJECTIVE_MAP = {
    "안정감": "wearing a cozy scarf, looking secure and reliable",
    "설렘": "with sparkling eyes, looking excited and enthusiastic",
    "성장": "holding a small sprout, looking determined and hopeful",
    "유머": "winking, wearing a funny tiny hat, looking playful",
    "배려": "offering a flower to the viewer, looking gentle and kind",
}

def generate_character_prompt(energy_type, date_mood, priority_value):
    """
    사용자의 답변을 기반으로 Gemini용 이미지 생성 프롬프트를 생성하고, 설명을 반환합니다.
    """
    flavor = FLAVOR_MAP.get(energy_type, "classic caramel brown pudding")
    behavior = BEHAVIOR_MAP.get(date_mood, "smiling happily")
    value_adjective = VALUE_ADJECTIVE_MAP.get(priority_value, "happy")
    
    # 최종 프롬프트 조합
    final_prompt = f"{flavor}, {value_adjective}, {behavior}. {BASE_STYLE}"

    # 키워드 설명 생성 (Gradio 출력용)
    description = (
        f"**에너지 유형:** `{energy_type}`\n"
        f"**데이트 분위기:** `{date_mood}`\n"
        f"**중요 가치:** `{priority_value}`\n\n"
        f"이 푸딩은 {flavor.split()[0].capitalize()}색처럼 **{energy_type}** 에너지를 가지며, **{priority_value}**를 중요하게 생각하는 **{date_mood}** 스타일의 성향입니다!"
    )
    
    return final_prompt, description

def generate_image_from_gemini(prompt):
    """
    Gemini API를 호출하여 이미지를 생성하고 PIL Image 객체를 반환합니다.
    """
    if client is None:
        return Image.new('RGB', (512, 512), color='lightgray'), API_STATUS

    try:
        full_prompt = f"{prompt}" 
        
        # 이미지 생성 요청
        result = client.models.generate_images(
            model=IMAGE_MODEL,
            prompt=full_prompt,
            config=GenerateImagesConfig(
                number_of_images=1,
                aspect_ratio="1:1"
            )
        )

        image_bytes = result.generated_images[0].image.image_bytes
        image = Image.open(BytesIO(image_bytes))
        
        return image, "성공적으로 생성됨"

    except Exception as e:
        error_msg = f"API 호출 중 오류 발생. 키 설정 또는 권한 확인 필요: {e}"
        # Render 로그 확인을 위해 에러 출력
        print(f"--- FATAL GEMINI ERROR ---: {error_msg}")
        return Image.new('RGB', (512, 512), color='red'), error_msg


# --- 2. Gradio 인터페이스 구축 ---
with gr.Blocks() as demo:
    gr.Markdown("# 🍮 AI 푸딩 캐릭터 소개팅 타입 테스트 (Gemini Image Generation)")
    gr.Markdown("**10가지 핵심 질문 중 3가지**에 답하여 나만의 성향 푸딩 캐릭터를 실시간으로 만들어보세요!")

    with gr.Row():
        with gr.Column(scale=1):
            q1 = gr.Radio(list(FLAVOR_MAP.keys()), label="Q1. 에너지 유형: 사람들과 시간을 보내는 것과 혼자 보내는 것 중 어느 쪽에서 에너지를 얻나요?", value=list(FLAVOR_MAP.keys())[0])
            q5 = gr.Radio(list(BEHAVIOR_MAP.keys()), label="Q5. 데이트 분위기: 데이트를 할 때 어떤 분위기를 가장 좋아하나요?", value=list(BEHAVIOR_MAP.keys())[0])
            q10 = gr.Radio(list(VALUE_ADJECTIVE_MAP.keys()), label="Q10. 가치관: 연인에게 가장 중요한 가치는 무엇인가요?", value=list(VALUE_ADJECTIVE_MAP.keys())[0])
            
            generate_btn = gr.Button("💖 내 푸딩 캐릭터 생성하기!")
        
        with gr.Column(scale=2):
            output_image = gr.Image(label="나의 성향 푸딩 캐릭터", type="pil")
            output_description = gr.Markdown("---")
            output_status = gr.Textbox(label="상태", interactive=False)
            output_prompt = gr.Textbox(label="AI 전달 프롬프트 (개발자 확인용)", interactive=False, visible=True) 

    def process_all_questions(energy, mood, value):
        prompt, description = generate_character_prompt(energy, mood, value)
        
        image, status = generate_image_from_gemini(prompt) 
        
        return image, description, status, prompt

    generate_btn.click(
        fn=process_all_questions, 
        inputs=[q1, q5, q10], 
        outputs=[output_image, output_description, output_status, output_prompt]
    )

if __name__ == "__main__":
    # Render와 같은 환경에서 포트 설정이 중요합니다.
    demo.launch(server_name="0.0.0.0", server_port=int(os.environ.get("PORT", 7860)))
