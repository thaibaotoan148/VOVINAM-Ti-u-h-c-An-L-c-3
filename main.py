import streamlit as st
import pandas as pd
import datetime
import base64
import io
import os
from PIL import Image, ImageDraw

st.set_page_config(
    page_title="Điểm danh Vovinam - TH An Lạc 3",
    page_icon="🥋",
    layout="wide"
)


# Hàm tự động xóa nền trắng bên ngoài Logo (giữ nguyên chi tiết trắng bên trong)
def remove_white_background(image_source):
    if isinstance(image_source, str):
        img = Image.open(image_source).convert("RGBA")
    else:
        img = Image.open(io.BytesIO(image_source)).convert("RGBA")

    w, h = img.size

    # Quét toàn bộ viền ngoài của ảnh để xóa phần nền trắng bao quanh
    edge_points = (
            [(x, 0) for x in range(0, w, 2)] +
            [(x, h - 1) for x in range(0, w, 2)] +
            [(0, y) for y in range(0, h, 2)] +
            [(w - 1, y) for y in range(0, h, 2)]
    )
    for pt in edge_points:
        r, g, b, a = img.getpixel(pt)
        if a > 0 and r > 200 and g > 200 and b > 200:
            ImageDraw.floodfill(img, pt, (0, 0, 0, 0), thresh=70)

    # Cắt sát khung hình logo sau khi bỏ nền trắng
    bbox = img.getbbox()
    if bbox:
        img = img.crop(bbox)

    cw, ch = img.size
    # Nếu là logo hình tròn (tỉ lệ ngang và dọc xấp xỉ nhau), bo tròn viền mịn tuyệt đối
    if 0.90 <= (cw / ch) <= 1.10:
        mask = Image.new("L", (cw, ch), 0)
        draw = ImageDraw.Draw(mask)
        draw.ellipse((1, 1, cw - 2, ch - 2), fill=255)
        img.putalpha(mask)

    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return base64.b64encode(buf.getvalue()).decode()


# SVG dự phòng không nền trắng nếu chưa tải file ảnh lên
SVG_SHIELD_NO_BG = """
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 240 310" width="110" height="135" style="background:transparent; filter: drop-shadow(0 4px 8px rgba(0,0,0,0.4));">
  <path d="M8,8 H232 V185 C232,255 178,298 120,302 C62,298 8,255 8,185 Z" fill="#FFF200" stroke="#0060B6" stroke-width="10"/>
  <text x="120" y="68" text-anchor="middle" fill="#ED1C24" font-family="Arial Black, Impact, sans-serif" font-weight="900" font-size="40">VOVINAM</text>
  <text x="120" y="110" text-anchor="middle" fill="#0060B6" font-family="Arial Black, sans-serif" font-weight="900" font-size="25">VIỆT VÕ ĐẠO</text>
  <circle cx="120" cy="202" r="76" fill="#FFFFFF"/>
  <path d="M120,130 A72,72 0 0,0 120,274 A36,36 0 0,0 120,202 A36,36 0 0,1 120,130 Z" fill="#ED1C24"/>
  <path d="M120,130 A72,72 0 0,1 120,274 A36,36 0 0,1 120,202 A36,36 0 0,0 120,130 Z" fill="#0060B6"/>
  <path d="M95,144 L118,140 L132,154 L115,166 L112,180 L130,200 L145,220 L142,246 L125,264 L112,258 L124,240 L125,213 L102,188 L98,166 L85,156 Z" fill="#FFF200"/>
  <circle cx="155" cy="202" r="3" fill="#FFF200"/>
  <circle cx="158" cy="235" r="3" fill="#FFF200"/>
</svg>
"""

SVG_CIRCLE_NO_BG = """
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 300 300" width="130" height="130" style="background:transparent; filter: drop-shadow(0 4px 8px rgba(0,0,0,0.4));">
  <defs>
    <path id="arcL" d="M 35,155 A 115,115 0 0,1 150,35"/>
    <path id="arcR" d="M 150,35 A 115,115 0 0,1 265,155"/>
    <path id="arcB" d="M 42,190 A 118,118 0 0,0 258,190"/>
  </defs>
  <circle cx="150" cy="150" r="144" fill="#FFF200" stroke="#000000" stroke-width="6"/>
  <circle cx="150" cy="150" r="92" fill="#FFFFFF"/>
  <path d="M150,62 A88,88 0 0,0 150,238 A44,44 0 0,0 150,150 A44,44 0 0,1 150,62 Z" fill="#ED1C24"/>
  <path d="M150,62 A88,88 0 0,1 150,238 A44,44 0 0,1 150,150 A44,44 0 0,0 150,62 Z" fill="#1B3F94"/>
  <text font-family="Arial Black, Impact, sans-serif" font-weight="900" font-size="24" fill="#ED1C24"><textPath href="#arcL" startOffset="10%">VOVINAM</textPath></text>
  <text font-family="Arial Black, Impact, sans-serif" font-weight="900" font-size="22" fill="#1B3F94"><textPath href="#arcR" startOffset="6%">VIỆT VÕ ĐẠO</textPath></text>
  <text font-family="Arial Black, sans-serif" font-weight="900" font-size="25" fill="#000000"><textPath href="#arcB" startOffset="16%">TH AN LẠC 3</textPath></text>
</svg>
"""


def get_clean_logo_html(filenames, fallback_svg):
    for fn in filenames:
        if os.path.exists(fn):
            try:
                b64_clean = remove_white_background(fn)
                return f'<img src="data:image/png;base64,{b64_clean}" style="height:130px; width:auto; object-fit:contain; background:transparent; filter: drop-shadow(0 4px 8px rgba(0,0,0,0.4));">'
            except Exception:
                pass
    return fallback_svg


FILE_HS = "ds_11_vosinh_anlac3.csv"
FILE_LS = "lich_su_diem_danh_anlac3.csv"

# Danh sách 11 em võ sinh (chỉ gồm STT và Họ tên)
DANH_SACH_11_EM = [
    {"STT": 1, "Họ và tên": "Phạm An Nhiên"},
    {"STT": 2, "Họ và tên": "Lương Ngọc Hoàng Yến"},
    {"STT": 3, "Họ và tên": "Nguyễn Kỳ Xuân Thịnh"},
    {"STT": 4, "Họ và tên": "Thiên Bảo"},
    {"STT": 5, "Họ và tên": "Chu Đức Phát"},
    {"STT": 6, "Họ và tên": "Hồ Nguyễn Khoa Đông"},
    {"STT": 7, "Họ và tên": "Bùi Nguyễn Anh Huy"},
    {"STT": 8, "Họ và tên": "Lê Nguyễn Lam Phương"},
    {"STT": 9, "Họ và tên": "Nguyễn Minh Quốc Thuận"},
    {"STT": 10, "Họ và tên": "Vũ Ngọc Bảo Trâm"},
    {"STT": 11, "Họ và tên": "Vũ Ngọc An Nhiên"},
]


def load_hs():
    if not os.path.exists(FILE_HS):
        df = pd.DataFrame(DANH_SACH_11_EM)
        df.to_csv(FILE_HS, index=False, encoding="utf-8-sig")
        return df
    return pd.read_csv(FILE_HS, encoding="utf-8-sig")


def load_ls():
    if not os.path.exists(FILE_LS):
        df = pd.DataFrame(columns=["Ngày", "Thứ", "Ca học", "STT", "Họ và tên", "Trạng thái", "Ghi chú"])
        df.to_csv(FILE_LS, index=False, encoding="utf-8-sig")
        return df
    return pd.read_csv(FILE_LS, encoding="utf-8-sig")


df_hs = load_hs()
df_ls = load_ls()

# ================= SIDEBAR: CẬP NHẬT ẢNH GỐC & TỰ XÓA NỀN TRẮNG =================
menu = st.sidebar.radio(
    "📌 DANH MỤC QUẢN LÝ:",
    ["📋 Điểm danh buổi tập", "📊 Lịch sử & Xuất Excel", "➕ Quản lý danh sách"]
)

st.sidebar.markdown("---")
with st.sidebar.expander("🖼️ Cài đặt 2 ảnh Logo gốc (Tự xóa nền)",
                         expanded=not (os.path.exists("logo_vovinam.png") and os.path.exists("logo_anlac3.png"))):
    st.caption("Chọn 2 ảnh từ máy tính, hệ thống sẽ tự động cắt sạch nền trắng ở góc và lưu vĩnh viễn:")
    up_shield = st.file_uploader("1. Logo Khiên Vovinam", type=["png", "jpg", "jpeg"], key="up1")
    if up_shield is not None:
        b64_data = remove_white_background(up_shield.getvalue())
        with open("logo_vovinam.png", "wb") as f:
            f.write(base64.b64decode(b64_data))
        st.success("Đã xóa nền trắng & lưu Logo Vovinam!")

    up_circle = st.file_uploader("2. Logo Tròn TH An Lạc 3", type=["png", "jpg", "jpeg"], key="up2")
    if up_circle is not None:
        b64_data = remove_white_background(up_circle.getvalue())
        with open("logo_anlac3.png", "wb") as f:
            f.write(base64.b64decode(b64_data))
        st.success("Đã xóa nền trắng & lưu Logo An Lạc 3!")

# Hiển thị Banner với 2 Logo đã tách nền trắng hoàn toàn
left_logo_html = get_clean_logo_html(["logo_vovinam.png", "logo1.png", "logo_vovinam.jpg"], SVG_SHIELD_NO_BG)
right_logo_html = get_clean_logo_html(["logo_anlac3.png", "logo2.png", "logo_anlac3.jpg"], SVG_CIRCLE_NO_BG)

st.html(f"""
<div style="
    background: linear-gradient(135deg, #072554 0%, #0d47a1 50%, #1565c0 100%);
    border-radius: 18px;
    padding: 18px 32px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    border-bottom: 6px solid #FFF200;
    box-shadow: 0 8px 20px rgba(13, 71, 161, 0.25);
    font-family: 'Segoe UI', Arial, sans-serif;
">
    <div style="display:flex; align-items:center; background:transparent;">{left_logo_html}</div>
    <div style="text-align: center; color: white; flex: 1; padding: 0 15px;">
        <div style="color: #FFF200; font-size: 18px; font-weight: 800; letter-spacing: 2px;">VOVINAM - VIỆT VÕ ĐẠO</div>
        <div style="color: #FFFFFF; font-size: 32px; font-weight: 900; margin: 6px 0 12px 0; text-shadow: 0 2px 4px rgba(0,0,0,0.35);">
            CLB TIỂU HỌC AN LẠC 3
        </div>
        <div style="
            background-color: #FFF200;
            color: #072554;
            padding: 7px 22px;
            border-radius: 30px;
            font-weight: 800;
            font-size: 15px;
            display: inline-block;
            box-shadow: 0 3px 8px rgba(0,0,0,0.2);
        ">
            ⏰ Ca học: Thứ 2 - 4 - 6 &nbsp;|&nbsp; 16h45 - 18h15
        </div>
    </div>
    <div style="display:flex; align-items:center; background:transparent;">{right_logo_html}</div>
</div>
""")

# ================= 1. ĐIỂM DANH BUỔI TẬP =================
if menu == "📋 Điểm danh buổi tập":
    thu_vn = {0: "Thứ 2", 1: "Thứ 3", 2: "Thứ 4", 3: "Thứ 5", 4: "Thứ 6", 5: "Thứ 7", 6: "Chủ Nhật"}

    c1, c2 = st.columns(2)
    with c1:
        ngay_tap = st.date_input("📅 Ngày điểm danh:", datetime.date.today())
        thu_hien_tai = thu_vn[ngay_tap.weekday()]
    with c2:
        st.text_input("⏰ Ca học cố định:", value=f"{thu_hien_tai} | 16h45 - 18h15 (Thứ 2 - 4 - 6)", disabled=True)

    df_check = df_hs.copy()
    if "Có mặt" not in df_check.columns:
        df_check["Có mặt"] = True
    if "Ghi chú" not in df_check.columns:
        df_check["Ghi chú"] = ""

    b1, b2, _ = st.columns([1.6, 1.6, 4.8])
    with b1:
        if st.button("✅ Có mặt tất cả", use_container_width=True):
            st.session_state["chon_tat_ca"] = True
    with b2:
        if st.button("⚪ Bỏ chọn tất cả", use_container_width=True):
            st.session_state["chon_tat_ca"] = False

    if "chon_tat_ca" in st.session_state:
        df_check["Có mặt"] = st.session_state["chon_tat_ca"]

    edited_df = st.data_editor(
        df_check[["STT", "Họ và tên", "Có mặt", "Ghi chú"]],
        column_config={
            "STT": st.column_config.NumberColumn("STT", disabled=True, width="small"),
            "Họ và tên": st.column_config.TextColumn("Họ và tên võ sinh", disabled=True, width="large"),
            "Có mặt": st.column_config.CheckboxColumn("Có mặt", default=True),
            "Ghi chú": st.column_config.TextColumn("Ghi chú (Xin phép / Đi trễ)", width="large"),
        },
        disabled=["STT", "Họ và tên"],
        hide_index=True,
        use_container_width=True,
        height=435
    )

    tong_so = len(edited_df)
    so_co_mat = int(edited_df["Có mặt"].sum())
    so_vang = tong_so - so_co_mat

    k1, k2, k3 = st.columns(3)
    k1.metric("👥 Tổng số võ sinh", f"{tong_so} em")
    k2.metric("🟢 Có mặt", f"{so_co_mat} em")
    k3.metric("🔴 Vắng mặt", f"{so_vang} em")

    if st.button("💾 LƯU ĐIỂM DANH BUỔI TẬP", type="primary", use_container_width=True):
        new_rows = []
        for _, r in edited_df.iterrows():
            new_rows.append({
                "Ngày": ngay_tap.strftime("%d/%m/%Y"),
                "Thứ": thu_hien_tai,
                "Ca học": "Thứ 2-4-6 (16h45 - 18h15)",
                "STT": r["STT"],
                "Họ và tên": r["Họ và tên"],
                "Trạng thái": "Có mặt" if r["Có mặt"] else "Vắng",
                "Ghi chú": r["Ghi chú"]
            })
        df_save = pd.concat([df_ls, pd.DataFrame(new_rows)], ignore_index=True)
        df_save.drop_duplicates(subset=["Ngày", "Họ và tên"], keep="last", inplace=True)
        df_save.to_csv(FILE_LS, index=False, encoding="utf-8-sig")
        st.success(f"🎉 Đã lưu điểm danh ngày {ngay_tap.strftime('%d/%m/%Y')} ({thu_hien_tai}) thành công!")

# ================= 2. LỊCH SỬ & XUẤT EXCEL =================
elif menu == "📊 Lịch sử & Xuất Excel":
    st.subheader("📊 Lịch sử điểm danh CLB Tiểu học An Lạc 3")
    if df_ls.empty:
        st.info("Chưa có dữ liệu điểm danh nào được lưu.")
    else:
        st.dataframe(df_ls, use_container_width=True, hide_index=True)
        csv_file = df_ls.to_csv(index=False, encoding="utf-8-sig").encode("utf-8-sig")
        st.download_button(
            label="📥 Tải file báo cáo Excel (.csv)",
            data=csv_file,
            file_name=f"Diem_Danh_Vovinam_AnLac3_{datetime.date.today()}.csv",
            mime="text/csv",
            type="primary"
        )

# ================= 3. QUẢN LÝ DANH SÁCH =================
elif menu == "➕ Quản lý danh sách":
    st.subheader("➕ Thêm võ sinh mới vào CLB")
    with st.form("them_vo_sinh"):
        ho_ten_moi = st.text_input("Nhập họ và tên võ sinh:")
        nut_them = st.form_submit_button("Thêm vào danh sách")
        if nut_them and ho_ten_moi.strip():
            stt_moi = len(df_hs) + 1
            df_hs = pd.concat([df_hs, pd.DataFrame([{"STT": stt_moi, "Họ và tên": ho_ten_moi.strip()}])],
                              ignore_index=True)
            df_hs.to_csv(FILE_HS, index=False, encoding="utf-8-sig")
            st.success(f"Đã thêm võ sinh **{ho_ten_moi}** thành công!")
            st.rerun()

    st.write("### Danh sách hiện tại:")
    st.dataframe(df_hs, use_container_width=True, hide_index=True)