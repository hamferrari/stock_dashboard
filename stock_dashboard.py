import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import io

# 페이지 설정
st.set_page_config(
    page_title="나의 주식 대시보드",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Toss 스타일 CSS 적용
st.markdown("""
<style>
    /* 전체 배경 및 기본 스타일 */
    .stApp {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    }
    
    /* 메인 컨테이너 */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 1200px;
    }
    
    /* 카드 스타일 */
    .stock-card {
        background: white;
        border-radius: 16px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
        border: 1px solid rgba(0, 0, 0, 0.06);
        transition: all 0.3s ease;
    }
    
    .stock-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
    }
    
    /* 제목 스타일 */
    .main-title {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1a1a1a;
        text-align: center;
        margin-bottom: 2rem;
        background: linear-gradient(45deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    /* 메트릭 카드 */
    .metric-card {
        background: white;
        border-radius: 12px;
        padding: 1.2rem;
        text-align: center;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
        border: 1px solid rgba(0, 0, 0, 0.04);
    }
    
    .metric-card h3, .metric-card h2, .metric-card h4 {
        color: #333333 !important;
        margin: 0.5rem 0;
    }
    
    .metric-card h3 {
        font-size: 1.5rem;
        font-weight: 700;
    }
    
    .metric-card h4 {
        font-size: 0.9rem;
        font-weight: 500;
        color: #666666 !important;
    }
    
    /* 가격 표시 스타일 */
    .price-up {
        color: #ef4444 !important;
        font-weight: 600;
    }
    
    .price-down {
        color: #3b82f6 !important;
        font-weight: 600;
    }
    
    .price-neutral {
        color: #6b7280 !important;
        font-weight: 600;
    }
    
    /* 회사명 링크 스타일 */
    .company-link {
        color: #1a1a1a !important;
        text-decoration: none;
        font-weight: 600;
        font-size: 1.1rem;
    }
    
    .company-link:hover {
        color: #667eea !important;
        text-decoration: underline;
    }
    
    /* 섹션 제목 */
    .section-title {
        font-size: 1.5rem;
        font-weight: 600;
        color: #1a1a1a !important;
        margin-bottom: 1.5rem;
        border-left: 4px solid #667eea;
        padding-left: 1rem;
    }
    
    /* Streamlit 기본 스타일 수정 */
    .stDataFrame {
        border-radius: 12px;
        overflow: hidden;
    }
    
    .stTabs [data-baseweb="tab-list"] {
        background-color: white;
        border-radius: 12px;
        padding: 0.5rem;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
    }
    
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px;
        padding: 0.75rem 1.5rem;
        font-weight: 500;
        color: #333333 !important;
    }
    
    /* 새로고침 버튼 스타일 */
    .stButton > button[kind="primary"] {
        background: transparent !important;
        border: 2px solid #667eea !important;
        color: #667eea !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        transition: all 0.3s ease !important;
    }
    
    .stButton > button[kind="primary"]:hover {
        background: #667eea !important;
        color: white !important;
    }
    
    /* 차트 배경색 수정 */
    .stElementChart {
        background-color: white !important;
        border-radius: 12px !important;
        padding: 1rem !important;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06) !important;
    }
    
    /* 텍스트 가독성 강제 설정 */
    p, span, div, h1, h2, h3, h4, h5, h6 {
        color: #333333 !important;
    }
    
    /* 예외: 가격 색상 */
    .price-up, .price-down, .price-neutral {
        color: inherit !important;
    }
</style>
""", unsafe_allow_html=True)

# 페이지 제목
st.markdown('<h1 class="main-title">📈 나의 주식 대시보드</h1>', unsafe_allow_html=True)

# 주식 티커 목록
TICKERS = ["GOOGL", "MSFT", "V", "LLY", "PLTR", "MSCI", "SMH", "AXON"]

def get_historical_data(tickers, period="1y"):
    """1년간의 주가 히스토리 데이터를 가져오는 함수"""
    historical_data = {}
    
    for ticker in tickers:
        try:
            stock = yf.Ticker(ticker)
            hist = stock.history(period=period)
            if not hist.empty:
                historical_data[ticker] = hist['Close']
        except Exception as e:
            st.error(f"{ticker} 히스토리 데이터를 가져오는 중 오류 발생: {e}")
    
    return historical_data

def format_market_cap(market_cap):
    """시가총액을 포맷팅하는 함수"""
    if pd.isna(market_cap) or market_cap == 0:
        return "N/A"
    
    if market_cap >= 1e12:  # 1조 이상
        return f"${market_cap/1e12:.1f}T"
    elif market_cap >= 1e9:  # 10억 이상
        return f"${market_cap/1e9:.1f}B"
    elif market_cap >= 1e6:  # 100만 이상
        return f"${market_cap/1e6:.1f}M"
    else:
        return f"${market_cap:,.0f}"

def get_stock_data(tickers):
    """주식 데이터를 가져오는 함수"""
    data = []
    
    for ticker in tickers:
        try:
            stock = yf.Ticker(ticker)
            hist = stock.history(period="2d")
            
            if len(hist) >= 2:
                current_price = hist['Close'].iloc[-1]
                previous_price = hist['Close'].iloc[-2]
                change = current_price - previous_price
                change_percent = (change / previous_price) * 100
                
                # 회사 정보 가져오기
                info = stock.info
                company_name = info.get('longName', ticker)
                
                # 시가총액 정보
                market_cap = info.get('marketCap', 0)
                formatted_market_cap = format_market_cap(market_cap)
                
                # 52주 최고점 및 하락률 계산
                hist_52w = stock.history(period="1y")
                if not hist_52w.empty:
                    week_52_high = hist_52w['High'].max()
                    mdd = ((current_price - week_52_high) / week_52_high) * 100
                else:
                    mdd = 0
                
                # 야후 파이낸스 링크 생성
                yahoo_url = f"https://finance.yahoo.com/quote/{ticker}"
                
                data.append({
                    '종목코드': ticker,
                    '회사명': company_name,
                    '회사링크': yahoo_url,
                    '현재가': f"${current_price:.2f}",
                    '전일대비': f"${change:.2f}",
                    '등락률': f"{change_percent:.2f}%",
                    '변화': change_percent,
                    '시가총액': formatted_market_cap,
                    '시가총액_원본': market_cap,
                    '고점대비하락률': f"{mdd:.2f}%",
                    '고점대비하락률_원본': mdd
                })
        except Exception as e:
            st.error(f"{ticker} 데이터를 가져오는 중 오류 발생: {e}")
            data.append({
                '종목코드': ticker,
                '회사명': ticker,
                '회사링크': f"https://finance.yahoo.com/quote/{ticker}",
                '현재가': "N/A",
                '전일대비': "N/A",
                '등락률': "N/A",
                '변화': 0,
                '시가총액': "N/A",
                '시가총액_원본': 0,
                '고점대비하락률': "N/A",
                '고점대비하락률_원본': 0
            })
    
    return pd.DataFrame(data)

def main():
    # 새로고침 버튼과 업데이트 시간
    col1, col2 = st.columns([1, 3])
    with col1:
        if st.button("🔄 새로고침", type="primary"):
            st.rerun()
    
    with col2:
        st.caption(f"마지막 업데이트: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 데이터 가져오기
    with st.spinner("주식 데이터를 불러오는 중..."):
        df = get_stock_data(TICKERS)
        historical_data = get_historical_data(TICKERS)
    
    if not df.empty:
        # 메트릭 카드 표시
        st.markdown('<h2 class="section-title">📊 포트폴리오 요약</h2>', unsafe_allow_html=True)
        
        # 전체 등락률 계산
        total_stocks = len(df[df['변화'] != 0])
        positive_stocks = len(df[df['변화'] > 0])
        negative_stocks = len(df[df['변화'] < 0])
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.markdown(f'<div class="metric-card"><h3>총 종목 수</h3><h2>{total_stocks}</h2></div>', unsafe_allow_html=True)
        with col2:
            st.markdown(f'<div class="metric-card"><h3>상승 종목</h3><h2 class="price-up">{positive_stocks}</h2></div>', unsafe_allow_html=True)
        with col3:
            st.markdown(f'<div class="metric-card"><h3>하락 종목</h3><h2 class="price-down">{negative_stocks}</h2></div>', unsafe_allow_html=True)
        with col4:
            avg_change = df[df['변화'] != 0]['변화'].mean()
            change_class = "price-up" if avg_change > 0 else "price-down" if avg_change < 0 else "price-neutral"
            st.markdown(f'<div class="metric-card"><h3>평균 등락률</h3><h2 class="{change_class}">{avg_change:.2f}%</h2></div>', unsafe_allow_html=True)
        
        # 상세 표 표시
        st.markdown('<h2 class="section-title">📈 종목별 상세 정보</h2>', unsafe_allow_html=True)
        
        # 카드 형태로 종목 정보 표시
        for _, row in df.iterrows():
            change_class = "price-up" if row['변화'] > 0 else "price-down" if row['변화'] < 0 else "price-neutral"
            mdd_class = "price-up" if row['고점대비하락률_원본'] > 0 else "price-neutral" if row['고점대비하락률_원본'] == 0 else "price-down"
            
            st.markdown(f'''
            <div class="stock-card">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem; gap: 1rem;">
                    <div style="flex: 0 0 auto; min-width: 200px;">
                        <a href="{row['회사링크']}" target="_blank" class="company-link">
                            {row['회사명']} ({row['종목코드']})
                        </a>
                        <div style="font-size: 0.9rem; color: #666666; margin-top: 0.25rem;">시가총액: {row['시가총액']}</div>
                    </div>
                    <div style="flex: 0 0 auto; text-align: right; min-width: 200px;">
                        <div style="font-size: 1.5rem; font-weight: 700; color: #333333;">{row['현재가']}</div>
                        <div class="{change_class}">{row['전일대비']} ({row['등락률']})</div>
                        <div class="{mdd_class}" style="font-size: 0.85rem; margin-top: 0.25rem;">52주 고점 대비: {row['고점대비하락률']}</div>
                    </div>
                </div>
            </div>
            ''', unsafe_allow_html=True)
        
        # 1년 주가 변동 추이 차트
        st.markdown('<h2 class="section-title">📈 최근 1년 주가 변동 추이</h2>', unsafe_allow_html=True)
        
        if historical_data:
            # 탭을 사용하여 종목별 차트 정리
            tab_names = [ticker for ticker in TICKERS if ticker in historical_data]
            
            # 한 줄에 4개씩만 배치하여 공간 확보
            for i in range(0, len(tab_names), 4):
                cols = st.columns(4)
                for j in range(4):
                    if i + j < len(tab_names):
                        ticker = tab_names[i + j]
                        try:
                            hist_data = historical_data[ticker]
                            company_name = df[df['종목코드'] == ticker]['회사명'].iloc[0] if not df[df['종목코드'] == ticker].empty else ticker
                            
                            with cols[j]:
                                st.markdown(f'<div style="color: #1a1a1a; font-weight: 600; margin-bottom: 1rem;">{company_name} ({ticker})</div>', unsafe_allow_html=True)
                                
                                # 날짜 포맷 변경
                                chart_data = hist_data.reset_index()
                                chart_data['Date'] = chart_data['Date'].dt.strftime('%m-%d')
                                chart_data = chart_data.set_index('Date')
                                
                                # 꺾은선 차트 - 흰색 배경
                                st.line_chart(chart_data, use_container_width=True)
                                
                                # 기본 통계 정보
                                current_price = hist_data.iloc[-1]
                                start_price = hist_data.iloc[0]
                                year_change = ((current_price - start_price) / start_price) * 100
                                max_price = hist_data.max()
                                min_price = hist_data.min()
                                
                                change_class = "price-up" if year_change > 0 else "price-down" if year_change < 0 else "price-neutral"
                                st.markdown(f'''
                                <div style="display: flex; justify-content: space-between; margin-top: 1rem; font-size: 0.9rem;">
                                    <span style="color: #666666;">시작: ${start_price:.2f}</span>
                                    <span style="color: #666666;">현재: ${current_price:.2f}</span>
                                    <span class="{change_class}">{year_change:.2f}%</span>
                                </div>
                                ''', unsafe_allow_html=True)
                                
                        except Exception as e:
                            st.error(f"{ticker} 차트 표시 중 오류 발생: {e}")
        else:
            st.warning("히스토리 데이터를 가져올 수 없습니다.")
        
        # 데이터 다운로드 기능
        st.markdown('<h2 class="section-title">📊 데이터 다운로드</h2>', unsafe_allow_html=True)
        
        # 엑셀 파일용 데이터프레임 생성
        download_df = df[['종목코드', '회사명', '현재가', '전일대비', '등락률', '시가총액', '고점대비하락률']].copy()
        download_df.columns = ['종목코드', '회사명', '현재가($)', '전일대비($)', '등락률(%)', '시가총액', '52주 고점 대비 하락률(%)']
        
        # 엑셀 파일 생성
        def create_excel_file(df):
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df.to_excel(writer, index=False, sheet_name='주식 포트폴리오')
                
                # 워크시트 스타일링
                worksheet = writer.sheets['주식 포트폴리오']
                
                # 컬럼 너비 조정
                for column in worksheet.columns:
                    max_length = 0
                    column_letter = column[0].column_letter
                    for cell in column:
                        try:
                            if len(str(cell.value)) > max_length:
                                max_length = len(str(cell.value))
                        except:
                            pass
                    adjusted_width = min(max_length + 2, 20)
                    worksheet.column_dimensions[column_letter].width = adjusted_width
                
                # 헤더 스타일
                for cell in worksheet[1]:
                    cell.font = openpyxl.styles.Font(bold=True)
                    cell.fill = openpyxl.styles.PatternFill(start_color="E6E6FA", end_color="E6E6FA", fill_type="solid")
            
            output.seek(0)
            return output
        
        # 다운로드 버튼
        try:
            import openpyxl
            excel_data = create_excel_file(download_df)
            
            st.download_button(
                label="📥 엑셀 파일 다운로드 (.xlsx)",
                data=excel_data,
                file_name=f"주식_포트폴리오_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        except ImportError:
            st.error("엑셀 다운로드 기능을 위해 openpyxl 라이브러리가 필요합니다.")
            st.code("pip install openpyxl")
        except Exception as e:
            st.error(f"엑셀 파일 생성 중 오류 발생: {e}")
    
    else:
        st.error("데이터를 가져올 수 없습니다. 나중에 다시 시도해주세요.")

if __name__ == "__main__":
    main()
