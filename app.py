import gradio as gr
import os
from io import BytesIO
from PIL import Image

try:
    from google import genai
    from google.genai.types import GenerateImagesConfig
    
    client = genai.Client()

    # ⭐ v1beta에서 실제 사용 가능한 이미지 생성 모델
    IMAGE_MODEL = "models/gemini-2.0-image-001"

    API_STATUS = "Gemini API 초기화 성공"

except Exception as e:
    print(f"Gemini 초기화 실패: {e}")
    client = None
    IMAGE_MODEL = "Dummy Mode"
    API_STATUS = f"Gemini API 오류: {e}"


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
    "예술적": "painting at a small easel",
    "감성적": "watching a sunset emotionally",
}

VALUE_MAP = {
    "안정감": "wearing a cozy scarf, reliable",
    "설렘": "sparkling excited eyes",
    "성장": "holding a sprout",
    "유머": "winking with a playful hat",
    "배려": "offering a flower kindly",
}


def make_prompt(energy, mood, value):
    flavor = FLAVOR_MAP.get(energy, "caramel pudding")
    behavior = BEHAVIOR_MAP.get(mood, "smiling softly")
    value_adj = VALUE_MAP.get(value, "gentle personality")

    prompt = f"{flavor}, {value_adj}, {behavior}, {BASE_STYLE}"

    desc = (
        f"### 🍮 성향 분석 결과\n"
        f"- **에너지 유형:** {energy}\n"
        f"- **데이트 분위기:** {mood}\n"
        f"- **가치관:** {value}\n\n"
    )

    return prompt, desc


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
        image = Image.open(BytesIO(img_bytes))
        return image, "생성 성공!"

    except Exception as e:
        print("IMAGE ERROR:", e)
        return Image.new("RGB", (512, 512), "red"), f"API 오류: {e}"


with gr.Blocks() as demo:
    gr.Markdown("# 🍮 AI 소개팅 푸딩 캐릭터 생성기")

    with gr.Row():
        with gr.Column(scale=1):
            q1 = gr.Radio(list(FLAVOR_MAP.keys()), label="① 에너지 유형", value="외향")
            q5 = gr.Radio(list(BEHAVIOR_MAP.keys()), label="② 데이트 분위기", value="잔잔함")
            q10 = gr.Radio(list(VALUE_MAP.keys()), label="③ 가치관", value="안정감")

            btn = gr.Button("💖 생성하기")

        with gr.Column(scale=2):
            out_img = gr.Image(label="✨ 생성된 푸딩")
            out_desc = gr.Markdown("---")
            out_status = gr.Textbox(label="상태", interactive=False)
            out_prompt = gr.Textbox(label="프롬프트", visible=False)

    def run_all(a, b, c):
        prompt, desc = make_prompt(a, b, c)
        image, status = generate_image(prompt)
        return image, desc, status, prompt

    btn.click(run_all, [q1, q5, q10], [out_img, out_desc, out_status, out_prompt])


if __name__ == "__main__":
    demo.launch(
        server_name="0.0.0.0",
        server_port=int(os.environ.get("PORT", 7860))
    )

