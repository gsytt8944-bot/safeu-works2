import streamlit as st
import pandas as pd
from datetime import datetime
import os
from fpdf import FPDF

st.set_page_config(page_title="🦺 세이프유 웍스 - 서울특별시", layout="wide")

DATA_FILE = "accident_data.csv"

if not os.path.exists(DATA_FILE):
    pd.DataFrame(columns=["날짜", "지역", "지역코드", "사고유형", "내용", "사진경로", "보고서"]).to_csv(DATA_FILE, index=False)

SEOUL_REGION_CODES = {
    "서울특별시 종로구": "11110",
    "서울특별시 중구": "11140",
    "서울특별시 용산구": "11170",
    "서울특별시 성동구": "11200",
    "서울특별시 광진구": "11215",
    "서울특별시 동대문구": "11230",
    "서울특별시 중랑구": "11260",
    "서울특별시 성북구": "11290",
    "서울특별시 강북구": "11305",
    "서울특별시 도봉구": "11320",
    "서울특별시 노원구": "11350",
    "서울특별시 은평구": "11380",
    "서울특별시 서대문구": "11410",
    "서울특별시 마포구": "11440",
    "서울특별시 양천구": "11470",
    "서울특별시 강서구": "11500",
    "서울특별시 구로구": "11530",
    "서울특별시 금천구": "11545",
    "서울특별시 영등포구": "11560",
    "서울특별시 동작구": "11590",
    "서울특별시 관악구": "11620",
    "서울특별시 서초구": "11650",
    "서울특별시 강남구": "11680",
    "서울특별시 송파구": "11710",
    "서울특별시 강동구": "11740"
}

st.title("🦺 세이프유 웍스 - 서울특별시 안전관리 자동화 시스템")

tab1, tab2, tab3 = st.tabs(["📋 사고기록", "📊 사고현황", "⚙️ 설정"])

with tab1:
    st.subheader("사고기록 등록")

    date = st.date_input("사고 날짜", datetime.now())
    region = st.text_input("지역 (예: 서울특별시 강남구)")
    region_code = SEOUL_REGION_CODES.get(region, "미등록 지역")

    if region_code != "미등록 지역":
        st.success(f"자동검색된 지역코드: {region_code}")
    else:
        st.warning("⚠️ 서울특별시 내에서 지역명을 정확히 입력해주세요.")
        region_code = st.text_input("직접 지역코드 입력", "")

    accident_type = st.selectbox("사고 유형", ["추락", "낙하", "전도", "끼임", "감전", "기타"])
    description = st.text_area("사고 내용")
    photo = st.file_uploader("사고 현장 사진 업로드", type=["jpg", "jpeg", "png"])

    if st.button("기록 저장 및 보고서 자동생성"):
        if not description or not region:
            st.error("❌ 지역명과 사고 내용을 입력해주세요.")
        else:
            os.makedirs("photos", exist_ok=True)
            photo_path = None
            if photo:
                photo_path = os.path.join("photos", photo.name)
                with open(photo_path, "wb") as f:
                    f.write(photo.getbuffer())

            pdf_dir = "reports"
            os.makedirs(pdf_dir, exist_ok=True)
            pdf_path = os.path.join(pdf_dir, f"{date.strftime('%Y%m%d')}_{region}_사고보고서.pdf")

            # ✅ 한글 폰트 등록 (Streamlit Cloud 환경에서도 작동)
            pdf = FPDF()
            pdf.add_page()
            font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
            pdf.add_font("DejaVu", "", font_path, uni=True)
            pdf.set_font("DejaVu", "", 16)

            pdf.cell(200, 10, txt="사고 보고서 (SafeU Works)", ln=True, align="C")
            pdf.set_font("DejaVu", "", 12)
            pdf.cell(200, 10, txt=f"날짜: {date}", ln=True)
            pdf.cell(200, 10, txt=f"지역: {region} ({region_code})", ln=True)
            pdf.cell(200, 10, txt=f"사고유형: {accident_type}", ln=True)
            pdf.multi_cell(0, 10, txt=f"사고 내용:\n{description}")

            if photo_path:
                try:
                    pdf.image(photo_path, x=30, y=90, w=150)
                except:
                    pdf.cell(200, 10, txt="⚠️ 이미지를 추가하지 못했습니다.", ln=True)

            pdf.output(pdf_path)

            df = pd.read_csv(DATA_FILE)
            new_row = {
                "날짜": date,
                "지역": region,
                "지역코드": region_code,
                "사고유형": accident_type,
                "내용": description,
                "사진경로": photo_path,
                "보고서": pdf_path
            }
            df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
            df.to_csv(DATA_FILE, index=False)

            st.success("✅ 사고기록이 저장되고 보고서가 자동 생성되었습니다.")
            st.download_button("📄 보고서 다운로드", open(pdf_path, "rb"), file_name=os.path.basename(pdf_path))

with tab2:
    st.subheader("사고현황 통계")
    df = pd.read_csv(DATA_FILE)

    if len(df) == 0:
        st.warning("등록된 사고 데이터가 없습니다.")
    else:
        st.dataframe(df)
        chart_data = df["사고유형"].value_counts(normalize=True) * 100
        st.bar_chart(chart_data)
        st.write("사고유형별 비율(%)")
        st.dataframe(chart_data)

with tab3:
    if st.button("데이터 초기화"):
        pd.DataFrame(columns=["날짜", "지역", "지역코드", "사고유형", "내용", "사진경로", "보고서"]).to_csv(DATA_FILE, index=False)
        st.success("데이터가 초기화되었습니다.")
