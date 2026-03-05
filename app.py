import streamlit as st
import pandas as pd
from datetime import date, timedelta, datetime

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

# 调休上班日（键：调休日，值：补哪天的班）
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
    # 处理调休
    if d in rest_work_dates:
        original_date = rest_work_dates[d]
        single = is_single_week(original_date)
        if single and original_date.weekday() in [0, 2, 4]:
            return True
        if (not single) and original_date.weekday() in [1, 3]:
            return True
        return False

    # 周末/节假日不上班
    if d.weekday() >= 5 or d in holiday_dates:
        return False

    # 正常排班
    single = is_single_week(d)
    if single and d.weekday() in [0, 2, 4]:
        return True
    if (not single) and d.weekday() in [1, 3]:
        return True
    return False

def get_holiday_label(d: date) -> str:
    return holiday_dates.get(d, "")

def generate_calendar(days=90):
    """生成指定天数的日历数据"""
    today = date.today()
    calendar_dates = [today + timedelta(days=i) for i in range(days)]
    
    data = []
    for d in calendar_dates:
        # 基础信息
        weekday = d.strftime("%a")
        is_today = d == today
        holiday = get_holiday_label(d)
        is_rest_work = d in rest_work_dates
        
        # 班次判断
        if holiday:
            shift = holiday
        elif is_rest_work:
            shift = "调休早班" if is_morning_shift(d) else "调休晚班"
        elif d.weekday() >= 5:
            shift = "周末"
        else:
            shift = "早班" if is_morning_shift(d) else "晚班"
        
        # 样式标记
        color = "#e6f4ff" if is_today else None
        data.append({
            "日期": d.strftime("%m-%d"),
            "周": weekday,
            "班次": shift,
            "今日标记": is_today,
            "背景色": color
        })
    
    # 转为DataFrame并按周分组（方便显示）
    df = pd.DataFrame(data)
    df["日期周"] = df["日期"] + "\n(" + df["周"] + ")"
    return df

# ===== 页面样式：强制缩小日历（核心！） =====
st.markdown("""
<style>
/* 缩小日历容器，允许横向滚动 */
.stDataFrame {
    width: 100% !important;
    overflow-x: auto !important;
}
/* 强制设置列宽（关键：让单元格变小） */
div[data-testid="stDataFrame"] div[role="grid"] {
    grid-template-columns: repeat(7, 80px) !important; /* 每列固定80px，可按需调小 */
}
/* 缩小单元格内边距和字体 */
div[data-testid="stDataFrame"] td,
div[data-testid="stDataFrame"] th {
    padding: 4px 2px !important; /* 上下4px，左右2px，极致压缩 */
    font-size: 11px !important; /* 小号字体，竖屏更紧凑 */
    text-align: center !important;
    white-space: nowrap !important;
}
/* 今日高亮 */
div[data-testid="stDataFrame"] td[style*="background-color"] {
    font-weight: bold !important;
    color: #1890ff !important;
}
</style>
""", unsafe_allow_html=True)

# ===== 页面布局 =====
st.title("2026 排班日历（小号适配版）")
st.caption("竖屏完整显示7列，支持横向滑动；电脑端正常显示")

# 生成日历数据
df_calendar = generate_calendar(days=90)

# 构建日历矩阵（按周排列，7列）
weeks = []
for i in range(0, len(df_calendar), 7):
    week = df_calendar.iloc[i:i+7]
    # 补全不足7天的周
    while len(week) < 7:
        week = pd.concat([week, pd.DataFrame([{"日期周": "", "班次": ""}])], ignore_index=True)
    weeks.append(week[["日期周", "班次"]].values.flatten())

# 转为日历DF（列：周一到周日）
calendar_df = pd.DataFrame(weeks, columns=["周一", "周二", "周三", "周四", "周五", "周六", "周日"])

# 显示日历（禁用索引，缩小高度）
st.dataframe(
    calendar_df,
    index=False,
    height=400,  # 固定高度，竖屏不占太多空间
    use_container_width=True
)

# 今日提示
today = date.today()
today_shift = "早班" if is_morning_shift(today) else "晚班"
if today in holiday_dates:
    today_shift = holiday_dates[today]
elif today in rest_work_dates:
    today_shift = "调休早班" if is_morning_shift(today) else "调休晚班"
st.info(f"今日({today.strftime('%Y-%m-%d')})：{today_shift}")
