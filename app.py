import gradio as gr
import os
from io import BytesIO
from PIL import Image

# -------------------------
# 1. Gemini API 초기화
# -------------------------
try:
    from google import genai
    from google.genai.types import GenerateImagesConfig
    
    client = genai.Client()
    IMAGE_MODEL = "models/image-generation-003"
    API_STATUS = "Gemini API 초기화 성공"

except Exception as e:
    print(f"Gemini 초기화 실패: {e}")
    client = None
    IMAGE_MODEL = "Dummy Mode"
    API_STATUS = f"Gemini API 오류: {e}"


# -------------------------
# 2. 프롬프트 스타일 설정
# -------------------------
BASE_STYLE = (
    "cute anthropomorphic pudding character, thick black outline, "
    "2D soft pastel sticker style, clean white background"
)

FLAVOR_MAP = {
    "외향": "bright strawberry red pudding",
    "내향": "calming blueberry indigo pudding",
}

BEHAVIOR_MAP = {
    "잔잔함": "sitting peacefully by a window, reading softly",
    "활발함": "jumping with energy, cheerful expression",
    "탐험·액티비티": "climbing a tiny mountain, adventurous look",
    "예술적": "painting on a small easel, artistic expression",
    "감성적": "watching a sunset with emotional gaze",
}

VALUE_MAP = {
    "안정감": "wearing a cozy scarf, stable and reliable",
    "설렘": "sparkling eyes full of excitement",
    "성장": "holding a sprout of growth",
    "유머": "winking with a tiny comic hat",
    "배려": "offering a flower gently",
}


# -------------------------
# 3. 프롬프트 생성
# -------------------------
def make_prompt(energy, mood, value):
    flavor = FLAVOR_MAP.get(energy, "caramel pudding")
    behavior = BEHAVIOR_MAP.get(mood, "smiling softly")
    value_adj = VALUE_MAP.get(value, "gentle personality")
    
    prompt = f"{flavor}, {value_adj}, {behavior}, {BASE_STYLE}"

    description = (
        f"### 🍮 성향 분석 결과\n"
        f"- **에너지 유형:** {energy}\n"
        f"- **데이트 분위기:** {mood}\n"
        f"- **중요 가치:** {value}\n\n"
        f"➡ 이 성향을 바탕으로 푸딩 캐릭터가 생성되었습니다!"
    )

    return prompt, description


# -------------------------
# 4. 이미지 생성
# -------------------------
def generate_image(prompt):
    if client is None:
        return Image.new("RGB", (512, 512), "gray"), API_STATUS

    try:
        result = client.models.generate_images(
            model=IMAGE_MODEL,
            prompt=prompt,
            config=GenerateImagesConfig(
                number_of_images=1,
                aspect_ratio="1:1"
            )
        )

        img_bytes = result.generated_images[0].image.image_bytes
        img = Image.open(BytesIO(img_bytes))
        return img, "이미지 생성 성공!"

    except Exception as e:
        print("[Gemini ERROR]", e)
        return Image.new("RGB", (512, 512), "red"), f"API 오류: {e}"


# -------------------------
# 5. Gradio UI
# -------------------------
with gr.Blocks() as demo:   # ← theme 제거한 버전
    gr.Markdown("# 🍮 AI 소개팅 푸딩 캐릭터 생성기")
    gr.Markdown("세 가지 질문만 선택하면 AI가 나만의 **성향 푸딩 캐릭터**를 만들어줍니다!")

    with gr.Row():
        with gr.Column(scale=1):
            q1 = gr.Radio(list(FLAVOR_MAP.keys()), label="① 에너지 유형", value="외향")
            q5 = gr.Radio(list(BEHAVIOR_MAP.keys()), label="② 데이트 분위기", value="잔잔함")
            q10 = gr.Radio(list(VALUE_MAP.keys()), label="③ 가치관", value="안정감")

            btn = gr.Button("💖 생성하기")

        with gr.Column(scale=2):
            output_img = gr.Image(label="✨ 생성된 푸딩 캐릭터")
            output_desc = gr.Markdown("---")
            output_status = gr.Textbox(label="상태", interactive=False)
            output_prompt = gr.Textbox(label="AI 프롬프트 (개발용)", interactive=False, visible=False)

    def run(energy, mood, value):
        prompt, desc = make_prompt(energy, mood, value)
        image, status = generate_image(prompt)
        return image, desc, status, prompt

    btn.click(
        fn=run,
        inputs=[q1, q5, q10],
        outputs=[output_img, output_desc, output_status, output_prompt]
    )


# -------------------------
# 6. Render 배포용 서버 실행 설정
# -------------------------
if __name__ == "__main__":
    demo.launch(
        server_name="0.0.0.0",
        server_port=int(os.environ.get("PORT", 7860))
    )
