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
        return "调休"
    else:
        return ""

# ===== Streamlit 页面（竖屏+横屏双适配）=====
st.set_page_config(
    page_title="早班日历",
    page_icon="📅",
    layout="centered"  # 改回居中布局，适配竖屏
)

# 自定义响应式样式（核心修复：竖屏自动适配）
st.markdown("""
<style>
    /* 全局背景 */
    .main {
        background-color: #FFF9F2;
        padding: 10px !important;
    }
    /* 今日早班卡片 */
    .shift-card {
        padding: 20px 10px;
        border-radius: 16px;
        text-align: center;
        font-size: 22px;
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
    /* 节假日标签 */
    .holiday-label {
        font-size: 14px;
        color: #947764;
        text-align: center;
        margin-top: 5px;
    }
    /* 响应式日历网格 - 核心修复 */
    .calendar-grid {
        width: 100% !important;
        overflow-x: auto; /* 竖屏时可横向滑动 */
        padding-bottom: 10px;
    }
    .calendar-row {
        display: flex !important;
        width: 100% !important;
        margin: 2px 0 !important;
    }
    .calendar-col {
        flex: 1 1 calc(100% / 7) !important;
        min-width: 40px !important;
        max-width: 60px !important;
        text-align: center;
    }
    /* 星期标题 */
    .calendar-header {
        font-weight: bold;
        color: #947764;
        font-size: 12px;
        padding: 5px 0;
    }
    /* 日期单元格 */
    .calendar-day {
        padding: 6px 2px !important;
        border-radius: 8px;
        font-weight: bold;
        font-size: 13px;
        min-height: 45px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        margin: 0 1px;
    }
    /* 月份选择框 */
    div[data-testid="stSelectbox"] {
        max-width: 150px;
        margin: 10px auto !important;
        display: block;
    }
    /* 标签页适配 */
    div[data-testid="stTabs"] {
        padding: 0 !important;
    }
</style>
""", unsafe_allow_html=True)

st.title("📅 早班日历")

# 标签页
tab1, tab2 = st.tabs(["今日早班", "月度日历"])

with tab1:
    today = date.today()
    st.subheader(f"{today.strftime('%Y年%m月%d日')}", divider="orange")

    shift = is_morning_shift(today)
    holiday_label = get_holiday_label(today)

    # 今日早班卡片
    if shift:
        st.markdown(f'<div class="shift-card shift-yes">今日有早班 🟠</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="shift-card shift-no">今日无早班 🟢</div>', unsafe_allow_html=True)

    # 节假日/调休标注
    if holiday_label:
        if today in rest_work_dates:
            st.markdown(f'<div class="holiday-label">今日{holiday_label}（补5.4）</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="holiday-label">今日{holiday_label}，放假休息</div>', unsafe_allow_html=True)

with tab2:
    # 月份选择（居中显示）
    selected_month = st.selectbox("选择月份", [3, 4, 5, 6], format_func=lambda x: f"{x}月")
    year = 2026

    # 生成日历数据
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

    # 日历容器（竖屏可横向滑动）
    st.markdown('<div class="calendar-grid">', unsafe_allow_html=True)

    # 星期标题行（响应式）
    st.markdown('<div class="calendar-row">', unsafe_allow_html=True)
    for day_name in ["日", "一", "二", "三", "四", "五", "六"]:
        st.markdown(f'<div class="calendar-col calendar-header">{day_name}</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # 日期行（6行×7列）
    for row in range(6):
        st.markdown('<div class="calendar-row">', unsafe_allow_html=True)
        for col in range(7):
            idx = row * 7 + col
            d, is_current_month = days[idx]
            shift = is_morning_shift(d)
            is_holiday = d in holiday_dates
            is_weekend = d.weekday() >= 5
            is_rest_work = d in rest_work_dates
            holiday_label = get_holiday_label(d)

            # 单元格样式
            if is_current_month:
                if shift:
                    bg_color = "#E67E22"
                    text_color = "#FFFFFF"
                elif is_holiday or is_weekend:
                    bg_color = "#FEF6ED"
                    text_color = "#947764"
                elif is_rest_work:
                    bg_color = "#FFFFFF"
                    text_color = "#8B4513"  # 调休深棕色
                else:
                    bg_color = "#FFFFFF"
                    text_color = "#333333"
            else:
                bg_color = "transparent"
                text_color = "#E0E0E0"

            # 渲染单元格
            day_html = f"""
            <div class="calendar-col">
                <div class="calendar-day" style="background-color: {bg_color}; color: {text_color};">
                    {d.day}
                    {f'<div style="font-size: 8px; margin-top: 2px;">{holiday_label}</div>' if holiday_label else ''}
                </div>
            </div>
            """
            st.markdown(day_html, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)
