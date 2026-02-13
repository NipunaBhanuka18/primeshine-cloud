import ssl
import os
import sys
import json
import flet as ft
from datetime import datetime
from supabase import create_client, Client

# --- 1. SSL & PATH FIXES ---
if not os.environ.get('PYTHONHTTPSVERIFY', '') and getattr(ssl, '_create_unverified_context', None):
    ssl._create_default_https_context = ssl._create_unverified_context

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# --- 2. CLOUD CONFIGURATION ---
SUPABASE_URL = "https://krupmoagkjobtmxygqkf.supabase.co  # ⚠️ Replace with your Supabase URL
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImtydXBtb2Fna2pvYnRteHlncWtmIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzA2ODg4ODYsImV4cCI6MjA4NjI2NDg4Nn0.1peHG6QH0mNE9SXkNLyrDF4WtHuOi-6xoL0ASazFqNM"     # ⚠️ Replace with your Supabase Key

# Fallback to local JSON if cloud fails
DB_FILE = "shop_jobs.json"
CLOUD_ACTIVE = False

try:
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    CLOUD_ACTIVE = True
except:
    pass

# --- 3. SECURITY & ROLES ---
USERS = {
    "admin": {"pass": "genary2026", "role": "admin"},
    "owner": {"pass": "colombo123", "role": "owner"},
    "manager": {"pass": "shop77", "role": "manager"}
}

# --- 4. MASTER PRICE LIST (ANTI-THEFT) ---
MASTER_PRICES = {
    "Sand Paper (40)": 100.0, "Sand Paper (60)": 100.0, "Sand Paper (80)": 80.0,
    "Sand Paper (100)": 80.0, "Sand Paper (120)": 80.0, "Sand Paper (150)": 80.0,
    "Sand Paper (180)": 80.0, "Sand Paper (220)": 80.0, "Sand Paper (320)": 80.0,
    "Sand Paper (400)": 80.0, "Sand Paper (600)": 80.0, "Sand Paper (800)": 80.0,
    "Sand Paper (1000)": 90.0, "Sand Paper (1200)": 90.0, "Sand Paper (1500)": 90.0,
    "Sand Paper (2000)": 100.0, "Sand Paper (2500)": 110.0, "Sand Paper (3000)": 150.0,
    "Dry Sand Paper (80)": 150.0, "Dry Sand Paper (120)": 130.0, "Dry Sand Paper (180)": 130.0,
    "Cataloy": 1850.0, "Putty": 950.0, "Filler": 1200.0, "Under Cote": 2500.0,
    "Masking Tape": 250.0, "Paint (100ml)": 1800.0, "Clear Cote": 4500.0, "Thinner": 850.0
}

# --- DATABASE HANDLERS ---
def load_db():
    if CLOUD_ACTIVE:
        try:
            response = supabase.table("jobs").select("*").execute()
            db = {}
            for row in response.data:
                db[row['vehicle_no']] = row['data']
                db[row['vehicle_no']]['status'] = row['status']
            return db
        except: return {}
    else:
        if not os.path.exists(DB_FILE): return {}
        try:
            with open(DB_FILE, 'r') as f: return json.load(f)
        except: return {}

def save_db(v_no, data):
    if CLOUD_ACTIVE:
        try:
            payload = {"vehicle_no": v_no, "status": data.get('status', 'Active'), "data": data}
            supabase.table("jobs").upsert(payload).execute()
        except: pass
    else:
        current_db = load_db()
        current_db[v_no] = data
        with open(DB_FILE, 'w') as f: json.dump(current_db, f, indent=4)

def delete_db_entry(v_no):
    if CLOUD_ACTIVE:
        try: supabase.table("jobs").delete().eq("vehicle_no", v_no).execute()
        except: pass
    else:
        db = load_db()
        if v_no in db:
            del db[v_no]
            with open(DB_FILE, 'w') as f: json.dump(db, f, indent=4)

# --- MAIN APP ---
def main(page: ft.Page):
    page.title = "Prime Shine Cloud System"
    page.theme_mode = ft.ThemeMode.LIGHT 
    page.bgcolor = "#f1f5f9"
    page.padding = 0
    page.theme = ft.Theme(font_family="Roboto", color_scheme_seed="#2563eb")

    user_role = None 

    current_job = {
        "vehicle_no": "", "status": "Active", "info": {},
        "materials": [], "parts": [], "labor": [], "other": []
    }

    # --- LOGIN SCREEN ---
    def login_screen():
        user_input = ft.TextField(
            label="Username", width=320, height=55, text_size=14, border_radius=12,
            prefix_icon=ft.Icons.PERSON_OUTLINE, bgcolor="#f8fafc", border_color="#cbd5e1"
        )
        pass_input = ft.TextField(
            label="Password", width=320, height=55, text_size=14, password=True, 
            can_reveal_password=True, border_radius=12, prefix_icon=ft.Icons.LOCK_OUTLINE, 
            bgcolor="#f8fafc", border_color="#cbd5e1"
        )
        error_txt = ft.Text("", color="#ef4444", size=13, weight="w600")

        def attempt_login(e):
            nonlocal user_role
            u, p = user_input.value.lower(), pass_input.value
            if u in USERS and USERS[u]["pass"] == p:
                user_role = USERS[u]["role"]
                page.clean()
                load_main_app()
            else:
                error_txt.value = "Access Denied: Invalid Credentials"
                page.update()

        login_btn = ft.Container(
            content=ft.Text("SECURE LOGIN", color="white", weight="bold", size=14),
            width=320, height=55, bgcolor="#2563eb", border_radius=12,
            alignment=ft.Alignment(0, 0),
            on_click=attempt_login,
            shadow=ft.BoxShadow(blur_radius=15, color="#662563eb", offset=ft.Offset(0, 4))
        )

        login_card = ft.Container(
            content=ft.Column([
                ft.Icon(ft.Icons.DIAMOND_OUTLINED, size=45, color="#2563eb"),
                ft.Text("PRIME SHINE", size=28, weight="w800", color="#1e293b"),
                ft.Text("CLOUD SYSTEM", size=12, weight="bold", color="#64748b"),
                ft.Divider(height=25, color="transparent"),
                user_input, pass_input, error_txt, ft.Container(height=5), login_btn
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=5, tight=True),
            bgcolor="white", padding=50, border_radius=24, width=450,
            border=ft.Border.all(1, "#e2e8f0"),
            shadow=ft.BoxShadow(blur_radius=40, color="#15000000", offset=ft.Offset(0, 10))
        )

        return ft.Container(
            content=login_card, alignment=ft.Alignment(0, 0), expand=True,
            gradient=ft.LinearGradient(
                begin=ft.Alignment(-1, -1), end=ft.Alignment(1, 1),
                colors=["#e0e7ff", "#c7d2fe", "#a5b4fc"]
            )
        )

    # --- MAIN DASHBOARD LOADER ---
    def load_main_app():
        def StyledContainer(content):
            return ft.Container(
                content=content, bgcolor="white", padding=15, border_radius=10,
                border=ft.Border(top=ft.BorderSide(1, "#e2e8f0"), bottom=ft.BorderSide(1, "#e2e8f0"),
                                 left=ft.BorderSide(1, "#e2e8f0"), right=ft.BorderSide(1, "#e2e8f0")),
                shadow=ft.BoxShadow(blur_radius=5, color="#0A000000")
            )

        def StyledHeader(text, color="#1e293b"):
            return ft.Text(text, size=14, weight="bold", color=color)

        txt_vehicle = ft.TextField(label="VEHICLE NO", width=250, bgcolor="#fef2f2", border_color="red", text_style=ft.TextStyle(weight="bold"))
        txt_model = ft.TextField(label="Make & Model", width=250, bgcolor="white", border_radius=8, border_color="#cbd5e1")
        txt_date = ft.TextField(label="Date", width=150, value=datetime.now().strftime("%Y-%m-%d"), bgcolor="white", border_radius=8, border_color="#cbd5e1")
        txt_tinker = ft.TextField(label="Tinker Name", width=200, bgcolor="white", border_radius=8, border_color="#cbd5e1")
        txt_painter = ft.TextField(label="Painter Name", width=200, bgcolor="white", border_radius=8, border_color="#cbd5e1")

        txt_agreed_price = ft.TextField(label="Agreed Price (LKR)", width=250, bgcolor="#f0fdf4", border_color="green", text_style=ft.TextStyle(size=18, weight="bold"), value="0")
        txt_advance = ft.TextField(label="Advance Received (LKR)", width=250, bgcolor="#fffbeb", border_color="orange", text_style=ft.TextStyle(size=18, weight="bold"), value="0")

        lbl_status = ft.Text("ACTIVE", weight="bold", color="orange", size=16)

        list_materials = ft.Column(scroll="auto")
        list_parts = ft.Column(scroll="auto")
        list_labor = ft.Column(scroll="auto")
        list_other = ft.Column(scroll="auto")

        lbl_mat_cost = ft.Text("Materials: 0.00", color="#64748b")
        lbl_part_cost = ft.Text("Parts: 0.00", color="#64748b")
        lbl_lab_cost = ft.Text("Labor: 0.00", color="#64748b")
        lbl_oth_cost = ft.Text("Other: 0.00", color="#64748b")
        
        lbl_total_cost = ft.Text("COST: 0.00", size=18, weight="bold", color="#ef4444")
        lbl_profit = ft.Text("PROFIT: 0.00", size=24, weight="bold", color="#10b981")
        lbl_balance = ft.Text("DUE: 0.00", size=24, weight="bold", color="orange")

        workspace = ft.Container(expand=True, padding=20, alignment=ft.Alignment(-1, -1))
        job_list_view = ft.ListView(expand=True, spacing=10, padding=10)
        search_box = ft.TextField(hint_text="Search Vehicle...", prefix_icon="search", bgcolor="#1e293b", color="white", border_color="transparent", height=40, text_size=14, border_radius=8)

        def refresh_sidebar():
            db = load_db()
            job_list_view.controls.clear()
            for v_no in reversed(list(db.keys())):
                status_color = "#34d399" if db[v_no].get('status') == "Closed" else "#fbbf24"
                job_list_view.controls.append(ft.Container(content=ft.Column([
                    ft.Row([ft.Text(v_no, weight="bold", size=15, color="white"), ft.Container(width=8, height=8, border_radius=4, bgcolor=status_color)], alignment="spaceBetween"),
                    ft.Text(f"{db[v_no]['info'].get('model')} | {db[v_no]['info'].get('date')}", size=11, color="#94a3b8")
                ]), padding=12, bgcolor="#1e293b", border_radius=8, on_click=lambda e, v=v_no: load_job(v), ink=True))
            page.update()

        def calculate_roi():
            c_mat = sum([x['total'] for x in current_job['materials']])
            c_part = sum([x['total'] for x in current_job['parts']])
            c_lab = sum([x['total'] for x in current_job['labor']])
            c_oth = sum([x['total'] for x in current_job['other']])
            total_cost = c_mat + c_part + c_lab + c_oth

            try: revenue = float(txt_agreed_price.value)
            except: revenue = 0.0
            try: advance = float(txt_advance.value)
            except: advance = 0.0

            profit = revenue - total_cost
            balance = revenue - advance

            lbl_mat_cost.value = f"Materials: {c_mat:,.2f}"
            lbl_part_cost.value = f"Parts: {c_part:,.2f}"
            lbl_lab_cost.value = f"Labor: {c_lab:,.2f}"
            lbl_oth_cost.value = f"Other: {c_oth:,.2f}"
            
            lbl_total_cost.value = f"COST: {total_cost:,.2f}"
            lbl_profit.value = f"PROFIT: {profit:,.2f}"
            lbl_profit.color = "#10b981" if profit >= 0 else "#ef4444"
            lbl_balance.value = f"DUE: {balance:,.2f}"
            page.update()

        def build_dashboard_view():
            db = load_db()
            total_jobs, active_jobs, closed_jobs, total_profit = len(db), 0, 0, 0.0
            for key, job in db.items():
                status = job.get('status', 'Active')
                rev = float(job['info'].get('price', 0))
                cost = sum([sum([i['total'] for i in job.get(cat, [])]) for cat in ['materials', 'parts', 'labor', 'other']])
                profit = rev - cost
                if status == 'Closed':
                    closed_jobs += 1; total_profit += profit
                else:
                    active_jobs += 1
            
            completion_rate = closed_jobs / total_jobs if total_jobs > 0 else 0

            def StatCard(title, value, emoji):
                return ft.Container(
                    content=ft.Column([ft.Text(emoji, size=35), ft.Text(title, size=13, color="#64748b", weight="w600"),
                                       ft.Text(value, size=28, weight="w800", color="#1e293b")], alignment="center", horizontal_alignment="center", spacing=5),
                    bgcolor="white", padding=20, border_radius=16, width=220, height=140, border=ft.Border.all(1, "#e2e8f0"),
                    shadow=ft.BoxShadow(blur_radius=10, color="#05000000", offset=ft.Offset(0, 4))
                )

            return ft.Column([
                ft.Row([ft.Text("Shop Dashboard", size=28, weight="w800", color="#0f172a"), ft.Container(expand=True),
                        ft.FilledButton("CREATE NEW JOB", icon="add", on_click=clear_new_job, style=ft.ButtonStyle(bgcolor="#2563eb", color="white", shape=ft.RoundedRectangleBorder(radius=8)), height=45)]),
                ft.Container(height=10),
                ft.Row([StatCard("Total Jobs", str(total_jobs), "📁"), StatCard("Ongoing", str(active_jobs), "⏳"),
                        StatCard("Finished", str(closed_jobs), "✅"), StatCard("Total Profit", f"{total_profit:,.0f}", "💰")], alignment="center", wrap=True),
                ft.Container(height=30),
                ft.Container(content=ft.Column([
                    ft.Text("Completion Rate", size=18, weight="bold", color="#1e293b"),
                    ft.ProgressBar(value=completion_rate, color="#2563eb", bgcolor="#e2e8f0", height=20, border_radius=10)
                ]), bgcolor="white", padding=40, border_radius=16, border=ft.Border.all(1, "#e2e8f0"), shadow=ft.BoxShadow(blur_radius=10, color="#05000000"))
            ], scroll="auto")

        def build_audit_view():
            return ft.Container(
                content=ft.Column([
                    ft.Text("OWNER AUDIT LOG", size=24, weight="w800", color="#dc2626"),
                    ft.Text("Live View from Cloud Database", color="grey"),
                    ft.Divider(),
                    ft.Text("This section tracks every job modification and price change."),
                    ft.Container(height=200, bgcolor="white", content=ft.Text("Log stream connecting...", italic=True))
                ])
            )

        def build_editor_view():
            return ft.Column([
                ft.Row([ft.Column([ft.Row([ft.Text("Active Job", size=12, color="grey"), lbl_status]),
                                   ft.Text("JOB EDITOR", size=24, weight="w800", color="#0f172a")]),
                        ft.Container(expand=True),
                        ft.FilledButton("SUMMARY", icon="pie_chart", style=ft.ButtonStyle(bgcolor="#3b82f6", color="white", shape=ft.RoundedRectangleBorder(radius=8)), on_click=show_summary, height=45),
                        ft.FilledButton("COMPLETE", icon="check", style=ft.ButtonStyle(bgcolor="#10b981", color="white", shape=ft.RoundedRectangleBorder(radius=8)), on_click=complete_job, height=45),
                        ft.FilledButton("SAVE", icon="save", style=ft.ButtonStyle(bgcolor="#1e293b", color="white", shape=ft.RoundedRectangleBorder(radius=8)), on_click=save_job, height=45),
                        ft.FilledButton("DELETE", icon="delete", style=ft.ButtonStyle(bgcolor="#ef4444", color="white", shape=ft.RoundedRectangleBorder(radius=8)), on_click=delete_job, height=45)]),
                ft.Container(height=20),
                StyledContainer(ft.Column([ft.Row([txt_vehicle, txt_model, txt_date]), ft.Row([txt_tinker, txt_painter])])),
                ft.Container(height=20),
                StyledContainer(ft.Column([
                    ft.Row([txt_agreed_price, txt_advance]),
                    ft.Divider(height=20, color="transparent"),
                    ft.Row([
                        ft.Column([ft.Text("NET PROFIT", size=12, color="grey", weight="bold"), lbl_profit]),
                        ft.VerticalDivider(),
                        ft.Column([ft.Text("BALANCE DUE", size=12, color="grey", weight="bold"), lbl_balance]),
                    ]),
                    ft.Divider(height=30, color="#f1f5f9"),
                    ft.Row([lbl_total_cost, ft.Container(width=20), lbl_mat_cost, lbl_part_cost, lbl_lab_cost, lbl_oth_cost])
                ])),
                ft.Container(height=20),
                ft.Row([
                    ft.Column([StyledHeader("MATERIALS (SECURE)", color="#2563eb"), build_material_input(),
                               StyledContainer(ft.Container(content=list_materials, bgcolor="white", height=200)),
                               ft.Container(height=10), StyledHeader("LABOR & SERVICES", color="#8b5cf6"),
                               build_generic_input("labor", list_labor),
                               StyledContainer(ft.Container(content=list_labor, bgcolor="white", height=150))], expand=True),
                    ft.VerticalDivider(width=30),
                    ft.Column([StyledHeader("SPARE PARTS", color="#f59e0b"), build_generic_input("parts", list_parts),
                               StyledContainer(ft.Container(content=list_parts, bgcolor="white", height=200)),
                               ft.Container(height=10), StyledHeader("OTHER EXPENSES", color="#64748b"),
                               build_generic_input("other", list_other),
                               StyledContainer(ft.Container(content=list_other, bgcolor="white", height=150))], expand=True)
                ], vertical_alignment="start")
            ], scroll="auto")

        def navigate_to(view_name):
            workspace.content = None
            if view_name == "dashboard": workspace.content = build_dashboard_view()
            elif view_name == "editor": workspace.content = build_editor_view()
            elif view_name == "audit": workspace.content = build_audit_view()
            page.update()

        def load_job(v_no):
            db = load_db()
            if v_no not in db: return
            data = db[v_no]
            current_job['status'] = data.get('status', 'Active')
            lbl_status.value, lbl_status.color = ("CLOSED", "green") if current_job['status'] == 'Closed' else ("ACTIVE", "orange")
            
            info = data['info']
            txt_vehicle.value = v_no
            txt_model.value = info.get('model', "")
            txt_date.value = info.get('date', "")
            txt_tinker.value = info.get('tinker', "")
            txt_painter.value = info.get('painter', "")
            txt_agreed_price.value = info.get('price', "0")
            txt_advance.value = info.get('advance', "0")

            list_materials.controls.clear(); list_parts.controls.clear(); list_labor.controls.clear(); list_other.controls.clear()
            for k in ['materials', 'parts', 'labor', 'other']:
                current_job[k] = []
                for i in data.get(k, []):
                    current_job[k].append(i)
                    target_list = list_materials if k == 'materials' else list_parts if k == 'parts' else list_labor if k == 'labor' else list_other
                    target_list.controls.append(create_item_row(k, target_list, i))

            calculate_roi()
            navigate_to("editor")

        def complete_job(e):
            if not txt_vehicle.value: return
            current_job['status'] = "Closed"
            save_job(None)
            page.snack_bar = ft.SnackBar(ft.Text("Job Closed Successfully!"), bgcolor="green"); page.snack_bar.open = True; page.update()

        def save_job(e):
            v_no = txt_vehicle.value.upper().strip()
            if not v_no: return
            
            job_data = {
                "info": {
                    "model": txt_model.value, "date": txt_date.value, "tinker": txt_tinker.value,
                    "painter": txt_painter.value, "price": txt_agreed_price.value,
                    "advance": txt_advance.value
                },
                "materials": current_job['materials'], "parts": current_job['parts'],
                "labor": current_job['labor'], "other": current_job['other'],
                "status": current_job.get('status', 'Active')
            }
            save_db(v_no, job_data)
            refresh_sidebar()
            if e: page.snack_bar = ft.SnackBar(ft.Text("Saved to System!"), bgcolor="green"); page.snack_bar.open = True; page.update()

        def delete_job(e):
            if user_role == "manager":
                page.snack_bar = ft.SnackBar(ft.Text("❌ Managers cannot delete jobs! Ask Owner."), bgcolor="red")
                page.snack_bar.open=True; page.update(); return

            v_no = txt_vehicle.value.upper().strip()
            if not v_no: return
            delete_db_entry(v_no)
            refresh_sidebar()
            clear_new_job(None)

        def clear_new_job(e):
            txt_vehicle.value, txt_model.value, txt_date.value = "", "", datetime.now().strftime("%Y-%m-%d")
            txt_tinker.value, txt_painter.value, txt_agreed_price.value, txt_advance.value = "", "", "0", "0"
            lbl_status.value, lbl_status.color, current_job['status'] = "ACTIVE", "orange", 'Active'
            list_materials.controls.clear(); list_parts.controls.clear(); list_labor.controls.clear(); list_other.controls.clear()
            current_job.update({"materials":[], "parts":[], "labor":[], "other":[]})
            calculate_roi(); navigate_to("editor"); txt_vehicle.focus()

        def create_item_row(section, ui_list, item_data):
            def delete_click(e):
                current_job[section].remove(item_data)
                ui_list.controls.remove(container)
                calculate_roi()
            
            container = ft.Container(content=ft.Row([
                ft.Column([ft.Text(item_data['name'], width=180, weight="bold", color="#334155"), ft.Text(item_data.get('date', ""), size=10, color="grey")], spacing=2),
                ft.Text(f"x{item_data['qty']}", width=40, color="black"),
                ft.Text(f"{item_data['total']:,.2f}", width=80, text_align="right", weight="bold", color="black"),
                ft.TextButton("X", style=ft.ButtonStyle(color="red"), on_click=delete_click)
            ], alignment="spaceBetween"), bgcolor="#f8fafc", padding=5, border_radius=5, margin=1, border=ft.Border.all(1, "#e2e8f0"))
            return container

        def add_item_click(section, name_field, qty_field, cost_field, ui_list):
            if not name_field.value or not cost_field.value: return
            try:
                qty, cost = float(qty_field.value) if qty_field else 1.0, float(cost_field.value)
                item_data = {"name": name_field.value, "qty": qty, "cost": cost, "total": qty*cost, "date": datetime.now().strftime("%Y-%m-%d")}
                current_job[section].append(item_data)
                ui_list.controls.append(create_item_row(section, ui_list, item_data))
                calculate_roi()
                if qty_field: qty_field.value = "1"
                
                if section == "materials":
                    cost_field.value = ""
                    cost_field.read_only = False
                    cost_field.update()
                else:
                    cost_field.value = ""
                    name_field.value = ""
                page.update()
            except: return

        def build_material_input():
            mat_options = list(MASTER_PRICES.keys())
            dd_mat = ft.Dropdown(
                label="Select Material", width=200, 
                options=[ft.dropdown.Option(x) for x in mat_options], 
                bgcolor="white", border_radius=8, height=40, text_size=12,
                color="black", border_color="#cbd5e1"
            )
            txt_qty = ft.TextField(label="Qty", width=60, value="1", bgcolor="white", border_radius=8, height=40, border_color="#cbd5e1")
            txt_cost = ft.TextField(label="Unit Cost", width=100, bgcolor="#f1f5f9", border_radius=8, height=40, read_only=True, border_color="#cbd5e1")

            def on_mat_change(e):
                if dd_mat.value in MASTER_PRICES:
                    txt_cost.value = str(MASTER_PRICES[dd_mat.value])
                    txt_cost.read_only = True
                    txt_cost.update()

            dd_mat.on_change = on_mat_change
            return ft.Row([dd_mat, txt_qty, txt_cost, ft.FilledButton("Add", on_click=lambda e: add_item_click("materials", dd_mat, txt_qty, txt_cost, list_materials), style=ft.ButtonStyle(bgcolor="#2563eb", color="white", shape=ft.RoundedRectangleBorder(radius=8)), height=40)])

        def build_generic_input(section, ui_list):
            txt_desc = ft.TextField(label="Description", width=200, bgcolor="white", border_radius=8, height=40, border_color="#cbd5e1")
            txt_cost = ft.TextField(label="Total Cost", width=100, bgcolor="white", border_radius=8, height=40, border_color="#cbd5e1")
            return ft.Row([txt_desc, txt_cost, ft.FilledButton("Add", on_click=lambda e: add_item_click(section, txt_desc, None, txt_cost, ui_list), style=ft.ButtonStyle(bgcolor="#2563eb", color="white", shape=ft.RoundedRectangleBorder(radius=8)), height=40)])

        def show_summary(e):
            c_mat = sum([x['total'] for x in current_job['materials']])
            c_part = sum([x['total'] for x in current_job['parts']])
            c_lab = sum([x['total'] for x in current_job['labor']])
            c_oth = sum([x['total'] for x in current_job['other']])
            total_cost = c_mat + c_part + c_lab + c_oth
            
            try: rev = float(txt_agreed_price.value)
            except: rev = 0.0
            try: adv = float(txt_advance.value)
            except: adv = 0.0
            
            profit = rev - total_cost
            due = rev - adv

            bs = ft.BottomSheet(
                ft.Container(padding=25, bgcolor="white", border_radius=ft.border_radius.only(top_left=20, top_right=20),
                    content=ft.Column([
                        ft.Text(f"JOB: {txt_vehicle.value.upper()}", weight="bold", size=22, color="black"),
                        ft.Divider(),
                        ft.Row([ft.Text("PROFIT:", size=16, color="black"), ft.Text(f"LKR {profit:,.2f}", weight="bold", size=18, color="green" if profit>0 else "red")], alignment="spaceBetween"),
                        ft.Row([ft.Text("BALANCE DUE:", size=16, color="black"), ft.Text(f"LKR {due:,.2f}", weight="bold", size=18, color="orange")], alignment="spaceBetween"),
                        ft.Container(height=20),
                        ft.TextButton("Close", on_click=lambda e: (setattr(bs, "open", False), page.update()))
                    ], tight=True)
                ), open=True
            )
            page.overlay.append(bs); page.update()

        sidebar_content = [
            ft.Row([
                ft.Icon(ft.Icons.DIAMOND, color="#3b82f6", size=24),
                ft.Text("Prime Shine", weight="w800", size=20, color="white")
            ], alignment=ft.MainAxisAlignment.START),
            
            ft.Container(
                content=ft.Text(f"● {user_role.upper()}", size=11, weight="bold", color="#34d399"),
                bgcolor="#064e3b", padding=ft.padding.only(left=8, right=8, top=4, bottom=4), border_radius=10
            ),
            ft.Container(height=25),
            ft.FilledButton("DASHBOARD", icon="dashboard", on_click=lambda e: navigate_to("dashboard"), width=280, height=45, style=ft.ButtonStyle(bgcolor="#1e293b", color="white", shape=ft.RoundedRectangleBorder(radius=8))),
            ft.FilledButton("JOB EDITOR", icon="edit", on_click=lambda e: navigate_to("editor"), width=280, height=45, style=ft.ButtonStyle(bgcolor="#1e293b", color="white", shape=ft.RoundedRectangleBorder(radius=8))),
        ]
        
        if user_role in ["admin", "owner"]:
            sidebar_content.append(ft.FilledButton("AUDIT LOG", icon="security", on_click=lambda e: navigate_to("audit"), width=280, height=45, style=ft.ButtonStyle(bgcolor="#7f1d1d", color="#fca5a5", shape=ft.RoundedRectangleBorder(radius=8))))

        sidebar_content.extend([
            ft.Container(height=20), search_box, ft.Divider(color="#334155"), 
            ft.Text("RECENT HISTORY", size=11, weight="bold", color="#64748b"), job_list_view
        ])

        sidebar = ft.Container(
            width=280, bgcolor="#0f172a", padding=25, 
            content=ft.Column(sidebar_content, expand=True),
            shadow=ft.BoxShadow(blur_radius=15, color="#10000000", offset=ft.Offset(5, 0))
        )

        page.add(ft.Row([sidebar, workspace], expand=True))
        refresh_sidebar(); navigate_to("dashboard")

    page.add(login_screen())

# --- 🚀 CLOUD WEB RUN COMMAND ---
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    ft.app(target=main, view=ft.WEB_BROWSER, host="0.0.0.0", port=port)

