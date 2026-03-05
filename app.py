import streamlit as st
from datetime import date, timedelta

# ===== 核心配置 =====
start_date = date(2026, 3, 9)

# 放假日期
holiday_dates = {
    date(2026, 4, 4): "清明",
    date(2026, 4, 5): "清明",
    date(2026, 4, 6): "清明",
    date(2026, 5, 1): "劳动节",
    date(2026, 5, 2): "劳动节",
    date(2026, 5, 3): "劳动节",
    date(2026, 5, 4): "劳动节",
    date(2026, 5, 5): "劳动节",
    date(2026, 6, 19): "端午",
    date(2026, 6, 20): "端午",
    date(2026, 6, 21): "端午"
}

# 调休上班日
rest_work_dates = {
    date(2026, 5, 9): date(2026, 5, 4)
}

# ===== 核心函数 =====
def is_single_week(d: date) -> bool:
    delta = (d - start_date).days
    if delta < 0:
        return False
    return (delta // 7) % 2 == 0

def is_morning_shift(d: date) -> bool:
    if d in rest_work_dates:
        original_date = rest_work_dates[d]
        single = is_single_week(original_date)
        if single and original_date.weekday() in [0, 2, 4]:
            return True
        if (not single) and original_date.weekday() in [1, 3]:
            return True
        return False

    if d.weekday() >= 5 or d in holiday_dates:
        return False

    single = is_single_week(d)
    if single and d.weekday() in [0, 2, 4]:
        return True
    if (not single) and d.weekday() in [1, 3]:
        return True
    return False

def get_holiday_label(d: date) -> str:
    if d in holiday_dates:
        return holiday_dates[d]
    elif d in rest_work_dates:
        return "调休（补5.4）"
    else:
        return ""

# ===== Streamlit 页面（强制横屏网格布局）=====
st.set_page_config(
    page_title="早班日历",
    page_icon="📅",
    layout="wide"  # 改为宽布局，强制手机横屏显示网格
)

# 自定义样式（修复手机竖排问题）
st.markdown("""
<style>
    /* 强制日历网格布局，防止竖排 */
    .stColumns > div {
        min-width: 40px !important;
        flex: 1 1 calc(100% / 7) !important;
    }
    .main {
        background-color: #FFF9F2;
        padding: 10px;
    }
    .shift-card {
        padding: 20px;
        border-radius: 16px;
        text-align: center;
        font-size: 24px;
        font-weight: bold;
        color: white;
        margin: 10px 0;
    }
    .shift-yes {
        background-color: #E67E22;
    }
    .shift-no {
        background-color: #4CAF50;
    }
    .holiday-label {
        font-size: 14px;
        color: #947764;
        text-align: center;
        margin-top: 5px;
    }
    .calendar-day {
        text-align: center;
        padding: 8px 2px;
        border-radius: 8px;
        font-weight: bold;
        font-size: 14px;
        min-height: 50px;
        display: flex;
        flex-direction: column;
        justify-content: center;
    }
    .calendar-header {
        font-weight: bold;
        color: #947764;
        text-align: center;
        font-size: 12px;
    }
    /* 修复月份选择框 */
    div[data-testid="stSelectbox"] {
        max-width: 200px;
        margin: 10px 0;
    }
</style>
""", unsafe_allow_html=True)

st.title("📅 早班日历")

tab1, tab2 = st.tabs(["今日早班", "月度日历"])

with tab1:
    today = date.today()
    st.subheader(f"{today.strftime('%Y年%m月%d日')}")

    shift = is_morning_shift(today)
    holiday_label = get_holiday_label(today)

    if shift:
        st.markdown(f'<div class="shift-card shift-yes">今日有早班 🟠</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="shift-card shift-no">今日无早班 🟢</div>', unsafe_allow_html=True)

    if holiday_label:
        st.markdown(f'<div class="holiday-label">{holiday_label}</div>', unsafe_allow_html=True)

with tab2:
    selected_month = st.selectbox("选择月份", [3, 4, 5, 6], format_func=lambda x: f"{x}月")
    year = 2026

    # 生成日历
    first_day = date(year, selected_month, 1)
    first_weekday = first_day.weekday()
    first_weekday_sun = (first_weekday + 1) % 7  # 周日开头

    days = []
    # 前一个月填充
    for i in range(first_weekday_sun):
        prev_day = first_day - timedelta(days=first_weekday_sun - i)
        days.append((prev_day, False))
    # 当前月
    current_day = first_day
    while current_day.month == selected_month:
        days.append((current_day, True))
        current_day += timedelta(days=1)
    # 后一个月填充
    while len(days) < 42:
        days.append((current_day, False))
        current_day += timedelta(days=1)

    # 星期标题（7列）
    cols = st.columns(7)
    for i, day_name in enumerate(["日", "一", "二", "三", "四", "五", "六"]):
        with cols[i]:
            st.markdown(f'<div class="calendar-header">{day_name}</div>', unsafe_allow_html=True)

    # 日期格子（6行×7列）
    for row in range(6):
        cols = st.columns(7)
        for col in range(7):
            idx = row * 7 + col
            d, is_current_month = days[idx]
            shift = is_morning_shift(d)
            is_holiday = d in holiday_dates
            is_weekend = d.weekday() >= 5
            is_rest_work = d in rest_work_dates
            holiday_label = get_holiday_label(d)

            with cols[col]:
                if is_current_month:
                    if shift:
                        bg_color = "#E67E22"
                        text_color = "#FFFFFF"
                    elif is_holiday or is_weekend:
                        bg_color = "#FEF6ED"
                        text_color = "#947764"
                    elif is_rest_work:
                        bg_color = "#FFFFFF"
                        text_color = "#333333"
                    else:
                        bg_color = "#FFFFFF"
                        text_color = "#333333"

                    st.markdown(f"""
                    <div class="calendar-day" style="background-color: {bg_color}; color: {text_color};">
                        {d.day}
                        <div style="font-size: 9px; font-weight: normal; margin-top: 2px;">{holiday_label}</div>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f'<div class="calendar-day" style="background-color: transparent; color: #E0E0E0;">{d.day}</div>', unsafe_allow_html=True)
