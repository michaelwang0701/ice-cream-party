import streamlit as st
import pandas as pd
from datetime import datetime

# ==========================================
# 0. 多人連線核心 (Global State)
# ==========================================
@st.cache_resource
class GameState:
    def __init__(self):
        self.users = {}
        self.market = []
        self.logs = []

def get_state():
    return st.session_state.game_state

if 'game_state' not in st.session_state:
    st.session_state.game_state = GameState()

state = get_state()

# ==========================================
# 1. 產品資料庫
# ==========================================
CATALOG = {
    # --- 雪糕區 (NT$965 / 24入) ---
    "巧克力脆杏仁 (雪糕)": {"price": 965, "qty": 24, "category": "雪糕", "unit": "支"},
    "草莓 (雪糕)": {"price": 965, "qty": 24, "category": "雪糕", "unit": "支"},
    "抹茶脆果仁 (雪糕)": {"price": 965, "qty": 24, "category": "雪糕", "unit": "支"},
    "淇淋巧酥 (雪糕)": {"price": 965, "qty": 24, "category": "雪糕", "unit": "支"},
    "香草焦糖脆杏仁 (雪糕)": {"price": 965, "qty": 24, "category": "雪糕", "unit": "支"},
    "芒果百香果脆皮 (雪糕)": {"price": 965, "qty": 24, "category": "雪糕", "unit": "支"},
    "蜜桃覆盆子脆皮 (雪糕)": {"price": 965, "qty": 24, "category": "雪糕", "unit": "支"},
    "羅馬提拉米蘇脆皮 (雪糕)": {"price": 965, "qty": 24, "category": "雪糕", "unit": "支"},
    "岩鹽焦糖 (雪糕)": {"price": 965, "qty": 24, "category": "雪糕", "unit": "支"},

    # --- 迷你杯區 (NT$900 / 24入) ---
    "夏威夷果仁 (迷你杯)": {"price": 900, "qty": 24, "category": "迷你杯", "unit": "杯"},
    "香草 (迷你杯)": {"price": 900, "qty": 24, "category": "迷你杯", "unit": "杯"},
    "草莓 (迷你杯)": {"price": 900, "qty": 24, "category": "迷你杯", "unit": "杯"},
    "比利時巧克力 (迷你杯)": {"price": 900, "qty": 24, "category": "迷你杯", "unit": "杯"},
    "淇淋巧酥 (迷你杯)": {"price": 900, "qty": 24, "category": "迷你杯", "unit": "杯"},
    "焦糖奶油脆餅 (迷你杯)": {"price": 900, "qty": 24, "category": "迷你杯", "unit": "杯"},
    "藍莓 (迷你杯)": {"price": 900, "qty": 24, "category": "迷你杯", "unit": "杯"},
    "草莓起司蛋糕 (迷你杯)": {"price": 900, "qty": 24, "category": "迷你杯", "unit": "杯"},
    "仲夏野莓 (迷你杯)": {"price": 900, "qty": 24, "category": "迷你杯", "unit": "杯"},
    "抹茶 (迷你杯)": {"price": 900, "qty": 24, "category": "迷你杯", "unit": "杯"},
    "芒果 (迷你杯)": {"price": 900, "qty": 24, "category": "迷你杯", "unit": "杯"},
    "芒果雪酪 (迷你杯)": {"price": 900, "qty": 24, "category": "迷你杯", "unit": "杯"},
    "開心果 (迷你杯)": {"price": 900, "qty": 24, "category": "迷你杯", "unit": "杯"},
    "蘭姆葡萄 (迷你杯)": {"price": 900, "qty": 24, "category": "迷你杯", "unit": "杯"},
    "巴黎草莓覆盆子馬卡龍 (迷你杯)": {"price": 900, "qty": 24, "category": "迷你杯", "unit": "杯"},
    "巧克力甘納許馬卡龍 (迷你杯)": {"price": 900, "qty": 24, "category": "迷你杯", "unit": "杯"},
    "羅馬提拉米蘇 (迷你杯)": {"price": 900, "qty": 24, "category": "迷你杯", "unit": "杯"},
    "馬德里吉拿棒 (迷你杯)": {"price": 900, "qty": 24, "category": "迷你杯", "unit": "杯"},
    "抹茶巧酥 (迷你杯)": {"price": 900, "qty": 24, "category": "迷你杯", "unit": "杯"},
    "可可巧酥 (迷你杯)": {"price": 900, "qty": 24, "category": "迷你杯", "unit": "杯"},

    # --- 日本進口區 ---
    "匠選玉露綠茶迷你杯 (日本)": {"price": 1750, "qty": 36, "category": "日本特選", "unit": "杯"},
    "豐潤草莓雪酥 (日本)": {"price": 1750, "qty": 36, "category": "日本特選", "unit": "個"},
    "薄荷可可餅乾雪糕 (日本)": {"price": 1950, "qty": 40, "category": "日本特選", "unit": "支"},
    "多重莓果牛乳雪糕 (日本)": {"price": 1950, "qty": 40, "category": "日本特選", "unit": "支"},
}

# ==========================================
# 2. 系統邏輯設定
# ==========================================
st.set_page_config(page_title="雪糕交易所 (多人版)", page_icon="🍦", layout="wide")

st.markdown("""
<style>
div.stButton > button {width: 100%; border-radius: 8px;}
</style>
""", unsafe_allow_html=True)

if 'page' not in st.session_state:
    st.session_state.page = "home"
if 'current_user' not in st.session_state:
    st.session_state.current_user = None

# --- 函數區 ---

def login(name):
    st.session_state.current_user = name
    st.session_state.page = "trade"
    st.rerun()

def logout():
    st.session_state.current_user = None
    st.session_state.page = "home"
    st.rerun()

def register_user(name, selected_flavor_key):
    if name in state.users:
        st.error(f"⚠️ 名字 '{name}' 已經有人用了！請直接登入。")
        return
    if len(state.users) >= 8:
        st.error("🛑 人數已達上限 8 人！")
        return
    
    product_info = CATALOG[selected_flavor_key]
    qty = product_info['qty']
    price = product_info['price']
    
    state.users[name] = {
        "initial_flavor": selected_flavor_key,
        "debt": price,
        "max_qty": qty,
        "inventory": [selected_flavor_key] * qty
    }
    timestamp = datetime.now().strftime("%H:%M")
    state.logs.append(f"[{timestamp}] 🆕 {name} 帶著 {qty} 個 [{selected_flavor_key}] 加入戰局！")
    login(name)

def release_to_market(user, flavor, qty):
    user_inv = state.users[user]["inventory"]
    current_count = user_inv.count(flavor)
    if current_count >= qty:
        for _ in range(qty):
            user_inv.remove(flavor)
            state.market.append(flavor)
        timestamp = datetime.now().strftime("%H:%M")
        state.logs.append(f"[{timestamp}] 📤 {user} 放入公共冰箱: {qty} 個 [{flavor}]")
        st.rerun()
    else:
        st.error("數量不足！")

def claim_from_market(user, flavor, qty):
    user_data = state.users[user]
    user_inv = user_data["inventory"]
    max_q = user_data["max_qty"]
    
    available_space = max_q - len(user_inv)
    if available_space < qty:
        st.error(f"🛑 冰箱空間不足！剩 {available_space} 格，你想拿 {qty} 個。")
        return
    
    market_count = state.market.count(flavor)
    if market_count < qty:
        st.error("市場數量不足！")
        st.rerun()
        return

    for _ in range(qty):
        if flavor in state.market:
            state.market.remove(flavor)
            user_inv.append(flavor)
    
    timestamp = datetime.now().strftime("%H:%M")
    state.logs.append(f"[{timestamp}] 📥 {user} 從公共冰箱拿走: {qty} 個 [{flavor}]")
    st.rerun()

def calculate_settlement_plan():
    """
    分貨演算法：
    計算每種口味的 (原本持有者 -> 需要者) 的流向
    目標：最小化搬運次數，以「誰要拿出多少給誰」為 output
    """
    instructions = [] # 儲存格式: {'giver': name, 'receiver': name, 'flavor': flavor, 'amount': qty}
    
    # 1. 找出所有口味的供需狀況
    all_flavors = set()
    for u in state.users.values():
        all_flavors.add(u['initial_flavor'])
        all_flavors.update(u['inventory'])

    for flavor in all_flavors:
        givers = {} # 誰有多餘的? {name: qty}
        receivers = {} # 誰需要? {name: qty}

        for name, data in state.users.items():
            # 他原本這箱有多少 (如果是他買的這箱)
            physical_hold = data['max_qty'] if data['initial_flavor'] == flavor else 0
            # 他現在想要多少
            wanted = data['inventory'].count(flavor)
            
            diff = physical_hold - wanted
            
            if diff > 0:
                givers[name] = diff
            elif diff < 0:
                receivers[name] = abs(diff)
        
        # 2. 配對 (Greedy Match)
        g_names = list(givers.keys())
        r_names = list(receivers.keys())
        
        while g_names and r_names:
            g_name = g_names[0]
            r_name = r_names[0]
            
            amount = min(givers[g_name], receivers[r_name])
            
            instructions.append({
                'giver': g_name,
                'receiver': r_name,
                'flavor': flavor,
                'amount': amount
            })
            
            givers[g_name] -= amount
            receivers[r_name] -= amount
            
            if givers[g_name] == 0: g_names.pop(0)
            if receivers[r_name] == 0: r_names.pop(0)
            
    return instructions

# ==========================================
# 3. 頁面路由
# ==========================================

# --- 頁面 A: 首頁 (只有登入) ---
if st.session_state.page == "home":
    st.title("🍦 雪糕交易所")
    st.caption("請輸入名字加入或登入。")
    
    col1, col2 = st.columns(2, gap="large")
    
    with col1:
        with st.container(border=True):
            st.subheader("🆕 新朋友登記")
            new_name = st.text_input("輸入你的名字", key="reg_name")
            
            cat_filter = st.radio("選擇系列", ["雪糕", "迷你杯", "日本特選"], horizontal=True)
            filtered_options = {} 
            for k, v in CATALOG.items():
                if v['category'] == cat_filter:
                    display_text = f"{k} (NT${v['price']} / {v['qty']}{v['unit']})"
                    filtered_options[display_text] = k
            
            selected_display = st.selectbox("選擇你買的那一箱", list(filtered_options.keys()))
            
            if st.button("登記並入場", type="primary"):
                if new_name:
                    real_key = filtered_options[selected_display]
                    register_user(new_name, real_key)
                else:
                    st.error("名字不能空白")

    with col2:
        with st.container(border=True):
            st.subheader("👤 老鳥登入")
            if not state.users:
                st.info("尚無資料，請先登記")
            else:
                user_list = list(state.users.keys())
                login_name = st.selectbox("選擇你的名字", user_list)
                if st.button("登入"):
                    login(login_name)
    
    # 注意：這裡已經移除「偷看紀錄」的區塊

# --- 頁面 B: 交易介面 ---
elif st.session_state.page == "trade":
    current_user = st.session_state.current_user
    st.empty() # Auto refresh anchor

    with st.sidebar:
        st.title(f"👤 {current_user}")
        if st.button("🚪 登出", type="secondary"):
            logout()
        st.divider()
        st.info("🟢 已連線")
        
        st.divider()
        # --- 新增功能：切換到分貨指南 ---
        if st.button("📦 計算分貨步驟 (結算用)"):
            st.session_state.page = "settlement"
            st.rerun()

    st.subheader(f"👋 {current_user}，開始交換！")

    # 1. 公共冰箱
    st.info("🧊 **公共冰箱 (Public Fridge)**")
    if not state.market:
        st.markdown("*🍃 空的*")
    else:
        market_counts = pd.Series(state.market).value_counts().sort_index()
        m_cols = st.columns(4)
        for idx, (item, count) in enumerate(market_counts.items()):
            with m_cols[idx % 4]:
                with st.container(border=True):
                    st.write(f"**{item}**")
                    st.caption(f"剩: {count}")
                    take_qty = st.selectbox("數量", range(1, count+1), key=f"m_sel_{item}")
                    if st.button("拿取", key=f"m_btn_{item}"):
                        claim_from_market(current_user, item, take_qty)

    st.divider()

    # 2. 個人冰箱
    u_data = state.users[current_user]
    inv = u_data['inventory']
    max_q = u_data['max_qty']
    current_q = len(inv)
    
    c1, c2 = st.columns([3, 1])
    with c1: st.subheader("🏠 我的冰箱")
    with c2: st.metric("應付金額", f"${u_data['debt']}")

    st.progress(current_q / max_q)
    if current_q == max_q: st.success("✅ 已滿箱")
    else: st.warning(f"⚠️ 還差 {max_q - current_q} 個")

    st.markdown("##### 📤 釋出")
    my_inv_counts = pd.Series(inv).value_counts().sort_index()
    if not my_inv_counts.empty:
        with st.container(border=True):
            rc1, rc2, rc3 = st.columns([3, 2, 2])
            with rc1: flavor_out = st.selectbox("口味", my_inv_counts.index, key="out_flavor")
            with rc2: 
                max_out = my_inv_counts[flavor_out]
                qty_out = st.selectbox("數量", range(1, max_out+1), key="out_qty")
            with rc3: 
                st.write(""); st.write("")
                if st.button("釋出"): release_to_market(current_user, flavor_out, qty_out)
    
    st.caption(f"持有: {' | '.join([f'{k} x{v}' for k, v in my_inv_counts.items()])}")
    st.divider()
    
    # 3. 結算表與紀錄
    t1, t2 = st.tabs(["團員狀態", "交易紀錄"])
    with t1:
        if state.users:
            s_list = []
            for name, data in state.users.items():
                comp = pd.Series(data['inventory']).value_counts()
                comp_str = ", ".join([f"{k}x{v}" for k, v in comp.items()])
                status = "✅" if len(data['inventory']) == data['max_qty'] else "⚠️"
                s_list.append({"姓名": name, "狀態": status, "內容": comp_str})
            st.dataframe(pd.DataFrame(s_list), use_container_width=True)
    with t2:
        for log in reversed(state.logs[-15:]):
            st.text(log)

# --- 頁面 C: 分貨指南 (Settlement Plan) ---
elif st.session_state.page == "settlement":
    st.title("📦 實體分貨指南")
    st.caption("這是給 Michael 看的。依照指示，可以用最少動作完成分貨。")
    
    if st.button("⬅️ 返回交易介面"):
        st.session_state.page = "trade"
        st.rerun()
    
    st.divider()
    
    # 計算指令
    instructions = calculate_settlement_plan()
    
    if not instructions:
        st.success("🎉 所有人拿的都跟原本買的一樣，或是已經分完了！不需要移動。")
    else:
        # 將指令依照「發貨人 (Giver)」分組，這樣 Michael 只要抱著一箱去發就好
        df_inst = pd.DataFrame(instructions)
        givers = df_inst['giver'].unique()
        
        for giver in givers:
            giver_tasks = df_inst[df_inst['giver'] == giver]
            flavor_name = state.users[giver]['initial_flavor']
            
            with st.container(border=True):
                st.subheader(f"📦 請打開 {giver} 的箱子")
                st.info(f"箱子口味：**{flavor_name}**")
                
                st.markdown("#### 👇 請執行以下動作：")
                for _, row in giver_tasks.iterrows():
                    st.write(f"➡️ 拿 **{row['amount']}** 個給 **{row['receiver']}**")
                
                # 計算剩下多少自己留
                total_given = giver_tasks['amount'].sum()
                initial_qty = state.users[giver]['max_qty']
                remaining = initial_qty - total_given
                
                st.markdown("---")
                st.success(f"✅ 發完後，箱子裡應該剩 **{remaining}** 個 (這是 {giver} 自己要吃的)")
