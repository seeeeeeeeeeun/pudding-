import os
import json
from flask import Flask, request, jsonify, render_template
from google import genai
from google.genai.errors import APIError

app = Flask(__name__)

# ----------------------------------------------------
# 1. Gemini 클라이언트 초기화 및 설정
# ----------------------------------------------------

# Render에 설정된 환경 변수 'GEMINI_API_KEY'에서 키를 가져옵니다.
API_KEY = os.environ.get("GEMINI_API_KEY")

if not API_KEY:
    print("FATAL: GEMINI_API_KEY 환경 변수가 설정되지 않았습니다. Render 환경 변수를 확인하세요.")
    client = None
else:
    # 클라이언트 초기화
    client = genai.Client(api_key=API_KEY)


# ----------------------------------------------------
# 2. 이미지 생성 프롬프트 조합 로직
# ----------------------------------------------------

def build_pudding_prompt(data):
    """
    사용자 입력 데이터를 기반으로 상세한 이미지 생성 프롬프트를 조합합니다.
    (이 로직은 10가지 질문에 대한 답변 구조에 맞춰 조정해야 합니다.)
    """
    
    # 사용자 답변 딕셔너리에서 값 추출 (예시)
    gender = data.get('gender', 'Male')
    energy = data.get('energy', 'Vibrant')
    hobby = data.get('hobby', 'Music')
    season = data.get('season', 'Spring')
    
    # 템플릿: 이미지 생성에 필요한 구체적이고 창의적인 묘사 문장
    base_description = "A stylized, highly detailed illustration of a unique dessert character that looks like pudding."
    
    traits = (
        f"The pudding is represented as a {gender} character, showing a {energy} demeanor. "
        f"Its base is creatively themed with {hobby} accessories. "
        f"The background features elements of {season}, and the character's expression is {data.get('emotion', 'confident')}. "
        f"The overall style should be whimsical digital painting."
    )
    
    return f"{base_description} The character embodies the following traits: {traits}"


# ----------------------------------------------------
# 3. 이미지 생성 API 호출 함수 (모델 이름 수정 완료)
# ----------------------------------------------------

def call_image_generation(prompt_text, client):
    """Gemini API를 호출하여 이미지를 생성하고 URL을 반환합니다."""
    if not client:
        return {"error": "API 클라이언트 오류: 키 설정 누락"}, 500
        
    try:
        # 🚨🚨🚨 이미지 생성 모델 이름으로 정확히 수정되었습니다. 🚨🚨🚨
        response = client.models.generate_content
