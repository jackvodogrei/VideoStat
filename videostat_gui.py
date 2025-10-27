import os
import json
import subprocess
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from datetime import datetime, timedelta
from pathlib import Path
import threading


class VideoStatApp:
    def __init__(self, root):
        self.root = root
        self.root.title("VideoStat - Управление статистикой видеосъемок")
        self.root.geometry("1000x700")
        self.root.configure(bg='#1a1a2e')

        # Стиль
        self.style = ttk.Style()
        self.style.configure('TFrame', background='#1a1a2e')
        self.style.configure('TLabel', background='#1a1a2e', foreground='white')
        self.style.configure('TButton', background='#6a11cb', foreground='white')
        self.style.configure('Header.TLabel', font=('Arial', 16, 'bold'))

        self.config_file = "config.json"
        self.stats_file = "stats.json"
        self.load_config()

        self.create_widgets()
        self.update_stats_display()

    def load_config(self):
        """Загрузка конфигурации"""
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                self.config = json.load(f)
        except FileNotFoundError:
            self.config = {
                "projects": {},
                "video_formats": [".mp4", ".braw", ".mov", ".avi", ".mkv"],
                "last_updated": datetime.now().isoformat()
            }
            self.save_config()

    def save_config(self):
        """Сохранение конфигурации"""
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, ensure_ascii=False, indent=2)

    def create_widgets(self):
        """Создание интерфейса"""
        # Заголовок
        header_frame = ttk.Frame(self.root)
        header_frame.pack(pady=20, padx=20, fill='x')

        title_label = ttk.Label(header_frame, text="VideoStat", style='Header.TLabel')
        title_label.pack()

        subtitle_label = ttk.Label(header_frame, text="Управление статистикой видеосъемок")
        subtitle_label.pack()

        # Основные кнопки
        buttons_frame = ttk.Frame(self.root)
        buttons_frame.pack(pady=10, padx=20, fill='x')

        ttk.Button(buttons_frame, text="📊 Сканировать проекты",
                   command=self.scan_projects).pack(side='left', padx=5)
        ttk.Button(buttons_frame, text="📁 Управление проектами",
                   command=self.manage_projects).pack(side='left', padx=5)
        ttk.Button(buttons_frame, text="⬆️ Экспорт в Git",
                   command=self.export_to_git).pack(side='left', padx=5)
        ttk.Button(buttons_frame, text="🔄 Обновить статистику",
                   command=self.update_stats_display).pack(side='left', padx=5)

        # Статистика
        stats_frame = ttk.LabelFrame(self.root, text="Текущая статистика")
        stats_frame.pack(pady=10, padx=20, fill='x')

        self.stats_text = tk.Text(stats_frame, height=8, bg='#2d2d44', fg='white',
                                  font=('Arial', 10), wrap='word')
        self.stats_text.pack(padx=10, pady=10, fill='both', expand=True)

        # Лог
        log_frame = ttk.LabelFrame(self.root, text="Лог действий")
        log_frame.pack(pady=10, padx=20, fill='both', expand=True)

        self.log_text = tk.Text(log_frame, bg='#2d2d44', fg='white',
                                font=('Arial', 9), wrap='word')
        scrollbar = ttk.Scrollbar(log_frame, orient='vertical', command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=scrollbar.set)

        self.log_text.pack(side='left', padx=10, pady=10, fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')

    def log_message(self, message):
        """Добавление сообщения в лог"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_text.insert('end', f"[{timestamp}] {message}\n")
        self.log_text.see('end')
        self.root.update()

    def scan_projects(self):
        """Сканирование всех проектов"""

        def scan_thread():
            self.log_message("🚀 Начато сканирование проектов...")

            total_footage = 0
            total_projects = 0

            for project_id, project in self.config['projects'].items():
                if not project.get('include_in_stats', True):
                    continue

                project_footage = self.scan_project_footage(project)
                if project_footage > 0:
                    total_footage += project_footage
                    total_projects += 1
                    self.log_message(f"📁 {project['title']}: {project_footage}ч")

            self.config['last_updated'] = datetime.now().isoformat()
            self.save_config()

            self.log_message(f"✅ Сканирование завершено: {total_projects} проектов, {total_footage}ч")
            self.update_stats_display()

        threading.Thread(target=scan_thread, daemon=True).start()

    def scan_project_footage(self, project):
        """Сканирование одного проекта"""
        total_duration = 0

        for folder_path in project.get('folder_mapping', []):
            if not os.path.exists(folder_path):
                continue

            for root, dirs, files in os.walk(folder_path):
                for file in files:
                    file_path = Path(root) / file
                    if file_path.suffix.lower() in [fmt.lower() for fmt in self.config['video_formats']]:
                        # Здесь будет логика определения длительности видео
                        # Пока используем заглушку - размер файла как псевдо-длительность
                        duration = os.path.getsize(file_path) / (1024 * 1024 * 100)  # Примерная логика
                        total_duration += duration

        return round(total_duration, 2)

    def manage_projects(self):
        """Окно управления проектами"""
        manage_window = tk.Toplevel(self.root)
        manage_window.title("Управление проектами")
        manage_window.geometry("800x600")
        manage_window.configure(bg='#1a1a2e')

        # Список проектов
        projects_frame = ttk.LabelFrame(manage_window, text="Проекты")
        projects_frame.pack(pady=10, padx=20, fill='both', expand=True)

        # Кнопки управления
        buttons_frame = ttk.Frame(manage_window)
        buttons_frame.pack(pady=10, padx=20, fill='x')

        ttk.Button(buttons_frame, text="➕ Добавить проект",
                   command=lambda: self.add_project(manage_window)).pack(side='left', padx=5)
        ttk.Button(buttons_frame, text="❌ Закрыть",
                   command=manage_window.destroy).pack(side='right', padx=5)

        # Таблица проектов
        columns = ('Название', 'Тип', 'Статус', 'Часы', 'Видимый', 'Учитывается')
        tree = ttk.Treeview(projects_frame, columns=columns, show='headings', height=15)

        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=100)

        # Заполнение данными
        for project_id, project in self.config['projects'].items():
            tree.insert('', 'end', values=(
                project['title'],
                project.get('type', 'documentary'),
                project.get('status', 'active'),
                project.get('footage_hours', 0),
                '✅' if project.get('visible_in_dashboard', True) else '❌',
                '✅' if project.get('include_in_stats', True) else '❌'
            ))

        tree.pack(padx=10, pady=10, fill='both', expand=True)

    def add_project(self, parent_window):
        """Добавление нового проекта"""
        add_window = tk.Toplevel(parent_window)
        add_window.title("Добавить проект")
        add_window.geometry("600x700")
        add_window.configure(bg='#1a1a2e')

        # Поля формы
        fields_frame = ttk.Frame(add_window)
        fields_frame.pack(pady=20, padx=20, fill='both', expand=True)

        # Название
        ttk.Label(fields_frame, text="Название проекта:").grid(row=0, column=0, sticky='w', pady=5)
        title_entry = ttk.Entry(fields_frame, width=40)
        title_entry.grid(row=0, column=1, sticky='ew', pady=5)

        # Тип проекта
        ttk.Label(fields_frame, text="Тип проекта:").grid(row=1, column=0, sticky='w', pady=5)
        type_combo = ttk.Combobox(fields_frame, values=['documentary', 'interview', 'reportage'])
        type_combo.grid(row=1, column=1, sticky='ew', pady=5)
        type_combo.set('documentary')

        # Статус
        ttk.Label(fields_frame, text="Статус:").grid(row=2, column=0, sticky='w', pady=5)
        status_combo = ttk.Combobox(fields_frame, values=['active', 'completed', 'archive', 'planning'])
        status_combo.grid(row=2, column=1, sticky='ew', pady=5)
        status_combo.set('active')

        # Категория
        ttk.Label(fields_frame, text="Категория:").grid(row=3, column=0, sticky='w', pady=5)
        category_var = tk.StringVar(value='personal')
        ttk.Radiobutton(fields_frame, text="Личный", variable=category_var, value='personal').grid(row=3, column=1,
                                                                                                   sticky='w', pady=2)
        ttk.Radiobutton(fields_frame, text="Коммерческий", variable=category_var, value='commercial').grid(row=4,
                                                                                                           column=1,
                                                                                                           sticky='w',
                                                                                                           pady=2)

        # Клиент (только для коммерческих)
        ttk.Label(fields_frame, text="Имя клиента:").grid(row=5, column=0, sticky='w', pady=5)
        client_entry = ttk.Entry(fields_frame, width=40)
        client_entry.grid(row=5, column=1, sticky='ew', pady=5)

        # Путь к проекту
        ttk.Label(fields_frame, text="Путь к проекту:").grid(row=6, column=0, sticky='w', pady=5)
        path_frame = ttk.Frame(fields_frame)
        path_frame.grid(row=6, column=1, sticky='ew', pady=5)

        path_entry = ttk.Entry(path_frame, width=35)
        path_entry.pack(side='left', fill='x', expand=True)
        ttk.Button(path_frame, text="Обзор",
                   command=lambda: self.browse_folder(path_entry)).pack(side='right', padx=5)

        # Настройки видимости
        ttk.Label(fields_frame, text="Настройки отображения:").grid(row=7, column=0, sticky='w', pady=10)
        visibility_frame = ttk.Frame(fields_frame)
        visibility_frame.grid(row=7, column=1, sticky='w', pady=10)

        visible_var = tk.BooleanVar(value=True)
        include_var = tk.BooleanVar(value=True)

        ttk.Checkbutton(visibility_frame, text="Видим в дашборде", variable=visible_var).pack(anchor='w')
        ttk.Checkbutton(visibility_frame, text="Учитывать в статистике", variable=include_var).pack(anchor='w')

        # Кофе
        ttk.Label(fields_frame, text="Кружки кофе:").grid(row=8, column=0, sticky='w', pady=5)
        coffee_frame = ttk.Frame(fields_frame)
        coffee_frame.grid(row=8, column=1, sticky='w', pady=5)

        coffee_var = tk.IntVar(value=0)
        coffee_label = ttk.Label(coffee_frame, text="0")
        coffee_label.pack(side='left', padx=5)

        ttk.Button(coffee_frame, text="-", width=3,
                   command=lambda: coffee_var.set(max(0, coffee_var.get() - 1))).pack(side='left')
        ttk.Button(coffee_frame, text="+", width=3,
                   command=lambda: coffee_var.set(coffee_var.get() + 1)).pack(side='left')

        # Хронометраж
        ttk.Label(fields_frame, text="Хронометраж эфира (минуты):").grid(row=9, column=0, sticky='w', pady=5)
        runtime_entry = ttk.Entry(fields_frame, width=40)
        runtime_entry.grid(row=9, column=1, sticky='ew', pady=5)

        # Кнопки сохранения
        buttons_frame = ttk.Frame(add_window)
        buttons_frame.pack(pady=10, padx=20, fill='x')

        def save_project():
            project_id = title_entry.get().lower().replace(' ', '_')

            self.config['projects'][project_id] = {
                'title': title_entry.get(),
                'type': type_combo.get(),
                'status': status_combo.get(),
                'category': category_var.get(),
                'client_name': client_entry.get() if category_var.get() == 'commercial' else '',
                'visible_in_dashboard': visible_var.get(),
                'include_in_stats': include_var.get(),
                'coffee_cups': coffee_var.get(),
                'final_runtime_minutes': int(runtime_entry.get() or 0),
                'folder_mapping': [path_entry.get()],
                'footage_hours': 0
            }

            self.save_config()
            self.log_message(f"✅ Добавлен проект: {title_entry.get()}")
            add_window.destroy()
            parent_window.destroy()
            self.manage_projects()

        ttk.Button(buttons_frame, text="💾 Сохранить проект",
                   command=save_project).pack(side='left', padx=5)
        ttk.Button(buttons_frame, text="❌ Отмена",
                   command=add_window.destroy).pack(side='right', padx=5)

    def browse_folder(self, entry_widget):
        """Выбор папки"""
        folder = filedialog.askdirectory()
        if folder:
            entry_widget.delete(0, 'end')
            entry_widget.insert(0, folder)

    def export_to_git(self):
        """Экспорт статистики в Git"""

        def export_thread():
            self.log_message("📤 Начало экспорта в Git...")

            # Генерация stats.json
            stats_data = self.generate_stats_json()

            with open(self.stats_file, 'w', encoding='utf-8') as f:
                json.dump(stats_data, f, ensure_ascii=False, indent=2)

            # Git операции (упрощенно)
            try:
                subprocess.run(['git', 'add', self.stats_file], check=True, capture_output=True)
                subprocess.run(['git', 'commit', '-m', f'VideoStat update {datetime.now().strftime("%Y-%m-%d %H:%M")}'],
                               check=True, capture_output=True)
                subprocess.run(['git', 'push'], check=True, capture_output=True)
                self.log_message("✅ Данные успешно экспортированы в Git")
            except Exception as e:
                self.log_message(f"❌ Ошибка экспорта в Git: {e}")

        threading.Thread(target=export_thread, daemon=True).start()

    def generate_stats_json(self):
        """Генерация публичной статистики"""
        public_projects = []
        nda_stats = {
            'total_count': 0,
            'total_footage_hours': 0,
            'total_coffee_cups': 0,
            'total_released_minutes': 0
        }

        total_footage = 0
        total_released = 0
        total_coffee = 0

        for project_id, project in self.config['projects'].items():
            if project.get('include_in_stats', True):
                total_footage += project.get('footage_hours', 0)
                total_released += project.get('final_runtime_minutes', 0)
                total_coffee += project.get('coffee_cups', 0)

            if project.get('visible_in_dashboard', True):
                public_projects.append({
                    'title': project['title'],
                    'type': project.get('type', 'documentary'),
                    'status': project.get('status', 'active'),
                    'category': project.get('category', 'personal'),
                    'footage_hours': project.get('footage_hours', 0),
                    'final_runtime_minutes': project.get('final_runtime_minutes', 0),
                    'coffee_cups': project.get('coffee_cups', 0),
                    'production_days': project.get('production_days', 0)
                })
            else:
                nda_stats['total_count'] += 1
                nda_stats['total_footage_hours'] += project.get('footage_hours', 0)
                nda_stats['total_coffee_cups'] += project.get('coffee_cups', 0)
                nda_stats['total_released_minutes'] += project.get('final_runtime_minutes', 0)

        return {
            'last_updated': datetime.now().isoformat(),
            'total_footage_hours': total_footage,
            'total_released_minutes': total_released,
            'total_coffee_cups': total_coffee,
            'public_projects': public_projects,
            'nda_projects': nda_stats if nda_stats['total_count'] > 0 else None
        }

    def update_stats_display(self):
        """Обновление отображения статистики"""
        total_projects = len(self.config['projects'])
        active_projects = sum(1 for p in self.config['projects'].values()
                              if p.get('status') == 'active' and p.get('include_in_stats', True))

        total_footage = sum(p.get('footage_hours', 0) for p in self.config['projects'].values()
                            if p.get('include_in_stats', True))

        total_released = sum(p.get('final_runtime_minutes', 0) for p in self.config['projects'].values()
                             if p.get('include_in_stats', True))

        visible_projects = sum(1 for p in self.config['projects'].values()
                               if p.get('visible_in_dashboard', True))

        nda_projects = total_projects - visible_projects

        stats_text = f"""📊 Общая статистика:

📁 Проекты: {total_projects} всего
   • 🟢 В работе: {active_projects}
   • 👁️ Видимых: {visible_projects}
   • 🔒 NDA: {nda_projects}

🎬 Материал:
   • 📹 Съемочные часы: {total_footage}ч
   • 🎬 Хронометраж эфира: {total_released}мин ({total_released / 60:.1f}ч)

☕ Кофе-метрики:
   • Всего кружек: {sum(p.get('coffee_cups', 0) for p in self.config['projects'].values())}

🕐 Последнее обновление: {self.config.get('last_updated', 'никогда')}"""

        self.stats_text.delete('1.0', 'end')
        self.stats_text.insert('1.0', stats_text)


def main():
    root = tk.Tk()
    app = VideoStatApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()