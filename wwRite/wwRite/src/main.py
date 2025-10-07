from databaser import DataBase
import flet as ft
import time

class App:
    def __init__(self, page: ft.Page):
        self.page = page
        self.page.title = "wwRite"
        self.page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
        self.page.vertical_alignment = ft.CrossAxisAlignment.CENTER
        self.page.padding = 0
        self.page.bgcolor = ft.Colors.GREY_900
        
        self.current_id = None  # ID текущей выбранной заметки
        self.name = "Выберите заметку" # Имя заметки
        self.text_field = ft.TextField(
            hint_text="Запишите...",
            multiline=True,
            cursor_color=ft.Colors.YELLOW,
            border_width=0,
            autofocus=True,
            disabled=True
        )
        
        self.writes_btn = ft.IconButton(ft.Icons.MENU, icon_color=ft.Colors.GREY_900, on_click=lambda e: self.page.open(self.panel_writes()))
        self.add_write_btn = ft.IconButton(ft.Icons.ADD, icon_color=ft.Colors.GREY_900, on_click=self.open_add_write)
        
        self.confirm_add_btn = ft.TextButton("Добавить", on_click=self.add_write, style=ft.ButtonStyle("yellow"))
        self.discard_add_btn = ft.TextButton("Отменить", on_click=lambda e: self.page.close(self.write_add_dlg), style=ft.ButtonStyle("yellow"))
        self.name_field = ft.TextField(hint_text="Название", on_change=self.sleeper, max_length=20, cursor_color=ft.Colors.YELLOW, border_color=ft.Colors.GREY_900, focused_border_color=ft.Colors.GREY_900)
        
        self.block_add_write = ft.Container(
            content=ft.Row(
                [
                    ft.Container(
                        content=ft.Text("Добавить заметку: ", color=ft.Colors.GREY_900),
                        margin=10
                    ),
                    self.add_write_btn
                ], ft.MainAxisAlignment.SPACE_BETWEEN
            ),
            bgcolor=ft.Colors.YELLOW
        )
        
        self.page.drawer = self.panel_writes()
        self.panel_main()
    
    def sleeper(self, e):
        self.confirm_add_btn.disabled = True
        time.sleep(0.3)
        self.confirm_add_btn.disabled = False
        self.confirm_add_btn.update()
        
    def add_write(self, e):
        data = DataBase.get("databaser.json")
        name = self.name_field.value.strip()
        
        if not name:
            self.page.close(self.write_add_dlg)
            self.page.open(ft.SnackBar(ft.Text("Введите название заметки", color=ft.Colors.GREY_900), bgcolor=ft.Colors.YELLOW))
        else:
            # Проверяем, существует ли заметка с таким именем
            names = [item["name"] for item in data]
            if name in names:
                self.page.close(self.write_add_dlg)
                self.page.open(ft.SnackBar(ft.Text("Такая заметка уже существует", color=ft.Colors.GREY_900), bgcolor=ft.Colors.YELLOW)) 
            else:
                # Создаем новую заметку
                new_id = max([item["id"] for item in data], default=0) + 1
                new_write = {
                    "id": new_id,
                    "name": name,
                    "text": ""
                }
                
                data.append(new_write)
                DataBase.load("databaser.json", data)
                
                self.page.close(self.write_add_dlg)
                self.name_field.value = ""
                
                # Обновляем интерфейс
                self.page.drawer = self.panel_writes()
                self.select_write_by_id(new_id)
        self.page.update()
        
    def open_add_write(self, e):
        self.page.close(self.drawer_writes)
        time.sleep(0.2)
        self.page.update()
        self.write_add_dlg = ft.AlertDialog(
            modal=True,
            title=ft.Text("Название заметки"),
            content=ft.Column(
                [
                    self.name_field,
                    ft.Row(
                        [
                            self.discard_add_btn,
                            self.confirm_add_btn
                        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                    )
                ], tight=True
            )
        )
        self.page.open(self.write_add_dlg)
        
    def save_write(self, e):
        if self.current_id is not None:
            data = DataBase.get("databaser.json")
            for item in data:
                if item["id"] == self.current_id:
                    item["text"] = self.text_field.value
                    break
            DataBase.load("databaser.json", data)
        
    def delete_write(self, e, write_id):
        self.page.clean()
        data = DataBase.get("databaser.json")
        data = [item for item in data if item["id"] != write_id]
        DataBase.load("databaser.json", data)
        
        self.page.close(self.drawer_writes)
        self.page.drawer = self.panel_writes()
        
        # Если удаляем текущую заметку, сбрасываем состояние
        if self.current_id == write_id:
            self.current_id = None
            self.name = "Выберите заметку"
            self.text_field.value = ""
            self.text_field.disabled = True
        
        self.panel_main()
        self.page.update()
        
    def select_write(self, e, write_id):
        self.select_write_by_id(write_id)
        self.page.close(self.drawer_writes)
        
    def select_write_by_id(self, write_id):
        data = DataBase.get("databaser.json")
        for item in data:
            if item["id"] == write_id:
                self.current_id = write_id
                self.name = item["name"]
                self.text_field.value = item["text"]
                self.text_field.disabled = False
                self.text_field.on_change = self.save_write
                break
        
        self.page.clean()
        self.panel_main()
        self.page.update()
        
    def panel_writes(self):
        # DataBase.create("databaser.json", [])
        data = DataBase.get("databaser.json")
        
        self.drawer_writes = ft.NavigationDrawer(
            controls=[
                self.block_add_write,
                ft.Container(height=30)
            ],
            bgcolor=ft.Colors.GREY_900
        )
        
        if data:
            for item in data:
                self.drawer_writes.controls.append(
                    ft.Container(
                        content=ft.Row(
                            [
                                ft.IconButton(
                                    ft.Icons.DELETE, 
                                    icon_color=ft.Colors.ON_ERROR, 
                                    on_click=lambda e, id=item["id"]: self.delete_write(e, id)
                                ),
                                ft.Text(item["name"]),
                            ]
                        ),
                        on_click=lambda e, id=item["id"]: self.select_write(e, id),
                        bgcolor=ft.Colors.GREY_700,
                        border=ft.border.only(bottom=ft.BorderSide(2, "grey800")),
                        alignment=ft.alignment.center
                    )
                )
        else:
            self.drawer_writes.controls.append(
                ft.Container(
                    content=ft.Text("Нет заметок...", color=ft.Colors.GREY_700),
                    alignment=ft.alignment.bottom_center,
                    margin=20
                )
            )
            
        return self.drawer_writes
        
    def panel_main(self):
        self.page.add(
            ft.SafeArea(
                ft.Container(
                        content=ft.Row(
                            [
                                ft.Container(content=self.writes_btn),
                                ft.Container(content=ft.Text(self.name, color=ft.Colors.GREY_900))
                            ], 
                            alignment=ft.MainAxisAlignment.START
                        ),
                    bgcolor=ft.Colors.YELLOW,
                    alignment=ft.alignment.top_center
                )
            ),
            ft.Container(
                content=self.text_field,
                expand=True
            )
        )
    
def start(e):
    DataBase.create("databaser.json", []) 
    app = App(e)

ft.app(start)