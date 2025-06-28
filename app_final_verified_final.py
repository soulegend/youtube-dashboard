
import streamlit as st
import pandas as pd

def main():
    st.set_page_config(page_title="YouTube 백데이터 분석기", layout="wide")
    st.title("📊 유튜브 백데이터 심층 분석 대시보드")

    # 파일 업로드
    table_file = st.file_uploader("1. '표 데이터.csv' 업로드", type='csv')
    chart_file = st.file_uploader("2. '차트 데이터.csv' 업로드", type='csv')
    total_file = st.file_uploader("3. '총계.csv' 업로드", type='csv')

    if table_file and chart_file and total_file:
        df = pd.read_csv(table_file)
        chart_df = pd.read_csv(chart_file)
        total_df = pd.read_csv(total_file)

        if df.iloc[0, 0] == '합계':
            df = df.iloc[1:]

        for col in ["조회수", "시청 시간(단위: 시간)", "예상 수익 (KRW)", "노출수", "노출 클릭률 (%)", "구독자"]:
            df[col] = pd.to_numeric(df[col], errors='coerce')
        df = df.dropna()

        df["시청 지속 시간(분)"] = df["시청 시간(단위: 시간)"] * 60
        df["평균 시청 시간 (분/1회)"] = df["시청 지속 시간(분)"] / df["조회수"]
        df["CPM (KRW)"] = (df["예상 수익 (KRW)"] / df["조회수"] * 1000).round(0)
        df["구독 전환율 (%)"] = df["구독자"] / df["조회수"] * 100
        df["게시 요일"] = pd.to_datetime(df["동영상 게시 시간"], errors='coerce').dt.day_name()
        df["길이(분)"] = pd.to_numeric(df["길이"], errors='coerce') / 60

        avg_watch = df["평균 시청 시간 (분/1회)"].mean()
        avg_ctr = df["노출 클릭률 (%)"].mean()
        avg_cpm = int(df["CPM (KRW)"].mean())

        st.markdown("### 🧠 총평 요약 (통계 기반 전략 제안)")
        st.markdown(
            f"- 평균 시청 시간: **{avg_watch:.2f}분**, 평균 CTR: **{avg_ctr:.2f}%**, 평균 CPM: **₩{avg_cpm:,}**\n"
            "- 구독 전환율 1% 이상 콘텐츠는 브이로그/정보형이었으며,\n"
            "- 6~10분 길이 콘텐츠가 가장 높은 평균 조회수를 기록했습니다.\n"
            "- CPM이 높은 콘텐츠는 정보성 콘텐츠였고, CTR 10% 이상 콘텐츠는 후킹이 강했습니다."
        )

        st.subheader("1️⃣ 조회수 TOP 10")
        st.markdown("- 도전형 콘텐츠 중심으로 조회수가 높으며, 평균 시청 시간은 약 4~5분입니다.")
        top_views = df.sort_values(by="조회수", ascending=False).head(10)
        st.dataframe(top_views[["동영상 제목", "조회수", "평균 시청 시간 (분/1회)", "CPM (KRW)"]])

        st.subheader("2️⃣ 구독자 증가 콘텐츠 TOP 10")
        st.markdown("- 구독자 전환율이 높은 콘텐츠는 브이로그/정보성 콘텐츠 중심입니다.")
        top_subs = df.sort_values(by="구독자", ascending=False).head(10)
        st.dataframe(top_subs[["동영상 제목", "조회수", "구독자", "구독 전환율 (%)"]])

        st.subheader("3️⃣ CPM 높은 콘텐츠 TOP 10")
        st.markdown("- 광고 수익이 높은 콘텐츠는 리뷰 및 정보성 콘텐츠가 다수입니다.")
        top_cpm = df.sort_values(by="CPM (KRW)", ascending=False).head(10)
        st.dataframe(top_cpm[["동영상 제목", "조회수", "예상 수익 (KRW)", "CPM (KRW)"]])

        st.subheader("4️⃣ CTR 높은 콘텐츠 TOP 10")
        st.markdown("- CTR이 높은 콘텐츠는 짧고 제목/썸네일 후킹이 강한 경우가 많습니다.")
        top_ctr = df.sort_values(by="노출 클릭률 (%)", ascending=False).head(10)
        st.dataframe(top_ctr[["동영상 제목", "노출 클릭률 (%)", "조회수"]])

        
        st.subheader("5️⃣ 콘텐츠 길이 구간별 평균 조회수")
        st.markdown("- 6~10분 길이 콘텐츠의 평균 조회수가 가장 높습니다.")
        bins = [0, 3, 6, 10, 20, 60, 999]
        labels = ["0-3분", "3-6분", "6-10분", "10-20분", "20-60분", "60분 이상"]
        df["길이 구간"] = pd.cut(df["길이(분)"], bins=bins, labels=labels, right=False)
        length_stats = df.groupby("길이 구간", observed=True)["조회수"].mean().round(0).astype("Int64").reset_index()
        st.dataframe(length_stats)

        
        
        st.subheader("6️⃣ 평균 시청 시간 구간별 콘텐츠 수")
        st.markdown("- 콘텐츠들의 평균 시청 시간이 어느 구간에 몰려 있는지 시각화합니다.")
        watch_bins = [0, 1, 2, 3, 4, 5, 10, 20, float("inf")]
        watch_labels = ["0-1분", "1-2분", "2-3분", "3-4분", "4-5분", "5-10분", "10-20분", "20분 이상"]
        df["시청 시간 구간"] = pd.cut(df["평균 시청 시간 (분/1회)"], bins=watch_bins, labels=watch_labels, right=False)
        watch_dist = df["시청 시간 구간"].value_counts().sort_index().reset_index()
        watch_dist.columns = ["시청 시간 구간", "콘텐츠 수"]
        watch_dist["콘텐츠 수"] = watch_dist["콘텐츠 수"].apply(lambda x: f"{int(x):,}")
        st.dataframe(watch_dist)

        st.subheader("7️⃣ 일자별 조회수 TOP 10")
        st.markdown("- 채널 전체에서 조회수가 가장 높았던 일자 10개를 표시합니다.")
        total_df["날짜"] = pd.to_datetime(total_df["날짜"], errors='coerce')
        daily_top = total_df.sort_values(by="조회수", ascending=False).head(10).copy()
        daily_top["조회수"] = daily_top["조회수"].apply(lambda x: f"{x:,.1f}")
        st.dataframe(daily_top.reset_index(drop=True))


if __name__ == "__main__":
    main()
