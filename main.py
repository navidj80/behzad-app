import flet as ft
from datetime import datetime
import sqlite3

# --- تنظیمات پایگاه داده محلی (SQLite) ---
def init_db():
    conn = sqlite3.connect("cashier_records.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT,
            pos_amount REAL,
            bank_amount REAL,
            diff REAL,
            status TEXT
        )
    """)
    conn.commit()
    conn.close()

def main(page: ft.Page):
    page.title = "مدیریت صندوق و کارتخوان"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.scroll = ft.ScrollMode.AUTO
    page.theme_mode = ft.ThemeMode.LIGHT

    # راه‌اندازی دیتابیس در شروع برنامه
    init_db()

    # فیلدهای ورودی
    txt_date = ft.TextField(label="تاریخ", value=datetime.now().strftime("%Y-%m-%d"), width=300)
    txt_pos = ft.TextField(label="مبلغ کل کارتخوان (تومان)", keyboard_type=ft.KeyboardType.NUMBER, width=300)
    txt_bank = ft.TextField(label="مبلغ واریزی بانک (تومان)", keyboard_type=ft.KeyboardType.NUMBER, width=300)
    
    # بخش نمایش نتیجه لحظه‌ای
    txt_result = ft.Text("", size=16, weight=ft.FontWeight.BOLD)
    
    # کانتینر برای نمایش لیست رکوردها
    records_column = ft.Column(spacing=10, scroll=ft.ScrollMode.AUTO)

    def load_records():
        """بارگذاری اطلاعات از دیتابیس و نمایش روی صفحه"""
        records_column.controls.clear()
        conn = sqlite3.connect("cashier_records.db")
        cursor = conn.cursor()
        cursor.execute("SELECT id, date, pos_amount, bank_amount, diff, status FROM records ORDER BY id DESC")
        rows = cursor.fetchall()
        conn.close()

        for row in rows:
            rec_id, date_val, pos_val, bank_val, diff_val, status_val = row
            
            # تعیین رنگ متن اختلاف بر اساس وضعیت
            if diff_val == 0:
                color = "green"
            elif diff_val > 0:
                color = "blue"
            else:
                color = "red"

            # دکمه حذف هر رکورد
            def delete_record(e, r_id=rec_id):
                conn = sqlite3.connect("cashier_records.db")
                cursor = conn.cursor()
                cursor.execute("DELETE FROM records WHERE id = ?", (r_id,))
                conn.commit()
                conn.close()
                load_records()

            card = ft.Card(
                content=ft.Container(
                    content=ft.Column([
                        ft.Row([
                            ft.Text(f"تاریخ: {date_val}", weight=ft.FontWeight.BOLD),
                            # اصلاح نام آیکون به صورت رشته‌ای
                            ft.IconButton(icon="delete", icon_color="red", on_click=delete_record, tooltip="حذف این رکورد")
                        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                        ft.Text(f"کارتخوان: {pos_val:,.0f} | بانک: {bank_val:,.0f}"),
                        ft.Text(f"اختلاف: {diff_val:,.0f} ({status_val})", color=color, weight=ft.FontWeight.BOLD),
                    ]),
                    padding=10,
                )
            )
            records_column.controls.append(card)
        page.update()

    def calculate_and_save(e):
        try:
            date_val = txt_date.value
            pos_val = float(txt_pos.value)
            bank_val = float(txt_bank.value)
            
            diff = bank_val - pos_val
            
            # تعیین وضعیت اختلاف
            if diff == 0:
                status_text = "تسویه کامل"
                color = "green"
            elif diff > 0:
                status_text = f"اضافه: {abs(diff):,.0f}"
                color = "blue"
            else:
                status_text = f"کسری: {abs(diff):,.0f}"
                color = "red"

            txt_result.value = f"محاسبه شد: {status_text}"
            txt_result.color = color

            # ذخیره در پایگاه داده SQLite
            conn = sqlite3.connect("cashier_records.db")
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO records (date, pos_amount, bank_amount, diff, status)
                VALUES (?, ?, ?, ?, ?)
            """, (date_val, pos_val, bank_val, diff, status_text))
            conn.commit()
            conn.close()

            # پاک کردن فیلدهای ورودی و به‌روزرسانی لیست
            txt_pos.value = ""
            txt_bank.value = ""
            load_records()

        except ValueError:
            txt_result.value = "لطفاً مبلغ‌ها را به صورت عدد معتبر وارد کنید."
            txt_result.color = "red"
            page.update()

    btn_submit = ft.Button(content="محاسبه و ذخیره دائم", on_click=calculate_and_save, width=300)

    # بارگذاری اولیه رکوردها هنگام باز شدن برنامه
    load_records()

    # چیدمان عناصر صفحه
    page.add(
        ft.Text("ثبت حساب روزانه کارتخوان و بانک", size=18, weight=ft.FontWeight.BOLD),
        ft.Divider(),
        txt_date,
        txt_pos,
        txt_bank,
        btn_submit,
        ft.Divider(),
        txt_result,
        ft.Text("گزارش‌های ذخیره‌شده:", weight=ft.FontWeight.BOLD),
        ft.Container(
            content=records_column, 
            height=300, 
            border_radius=10
        )
    )

ft.run(main)