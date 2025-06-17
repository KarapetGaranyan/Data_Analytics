from selenium import webdriver
from selenium.webdriver import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import pandas as pd
import time
import os
import glob
import re
from datetime import datetime
from tkinter import Tk, filedialog, messagebox
import sys


class EgrulDownloader:
    def __init__(self):
        self.browser = None
        self.wait = None
        self.download_folder = self.get_downloads_folder()
        self.stats = {
            'total': 0,
            'success': 0,
            'failed': 0,
            'skipped': 0
        }

    def print_header(self):
        """Красивый заголовок программы"""
        print("=" * 70)
        print("🏢 АВТОМАТИЧЕСКОЕ СКАЧИВАНИЕ ВЫПИСОК ИЗ ЕГРЮЛ 🏢".center(70))
        print("=" * 70)
        print("📋 Программа автоматически скачивает выписки по списку ИНН")
        print("📁 Файлы автоматически переименовываются по названию компании")
        print("=" * 70)

    def print_separator(self, char="─", length=50):
        """Печать разделителя"""
        print(char * length)

    def print_step(self, step_num, total_steps, description):
        """Печать текущего шага"""
        print(f"\n📌 Шаг {step_num}/{total_steps}: {description}")
        self.print_separator()

    def print_progress(self, current, total, company_name=""):
        """Печать прогресса"""
        percentage = (current / total) * 100
        bar_length = 30
        filled_length = int(bar_length * current // total)
        bar = "█" * filled_length + "░" * (bar_length - filled_length)

        print(f"\r🔄 Прогресс: [{bar}] {percentage:.1f}% ({current}/{total})", end="")
        if company_name:
            print(f" | {company_name[:30]}...", end="" if len(company_name) > 30 else "")
        print("")

    def print_stats(self):
        """Печать статистики"""
        print(f"\n📊 СТАТИСТИКА ВЫПОЛНЕНИЯ:")
        print(f"   ✅ Успешно обработано: {self.stats['success']}")
        print(f"   ❌ Ошибок: {self.stats['failed']}")
        print(f"   ⏭️ Пропущено: {self.stats['skipped']}")
        print(f"   📈 Всего компаний: {self.stats['total']}")

        if self.stats['total'] > 0:
            success_rate = (self.stats['success'] / self.stats['total']) * 100
            print(f"   🎯 Процент успеха: {success_rate:.1f}%")

    def get_downloads_folder(self):
        """Получение пути к папке загрузок"""
        return os.path.join(os.path.expanduser('~'), 'Downloads')

    def clean_filename(self, filename):
        """Очистка имени файла от недопустимых символов"""
        invalid_chars = r'[<>:"/\\|?*]'
        clean_name = re.sub(invalid_chars, '', filename)
        clean_name = clean_name.strip()

        if not clean_name:
            clean_name = "Компания"

        # Ограничиваем длину имени файла
        if len(clean_name) > 100:
            clean_name = clean_name[:100]

        return clean_name

    def rename_latest_file(self, company_name):
        """Поиск и переименование последнего скачанного файла"""
        safe_name = self.clean_filename(company_name)
        pdf_files = glob.glob(os.path.join(self.download_folder, '*.pdf'))

        if not pdf_files:
            return False, "PDF файлы не найдены"

        latest_file = max(pdf_files, key=os.path.getctime)
        new_filename = f"{safe_name}.pdf"
        new_path = os.path.join(self.download_folder, new_filename)

        # Если файл с таким именем уже существует, добавляем timestamp
        if os.path.exists(new_path):
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            new_filename = f"{safe_name}_{timestamp}.pdf"
            new_path = os.path.join(self.download_folder, new_filename)

        try:
            os.rename(latest_file, new_path)
            return True, new_filename
        except Exception as e:
            return False, str(e)

    def normalize_inn(self, inn_value):
        """Нормализация ИНН"""
        if pd.isna(inn_value):
            return None

        inn_str = str(inn_value).strip()
        inn_digits = re.sub(r'\D', '', inn_str)

        if len(inn_digits) < 10:
            inn_digits = inn_digits.zfill(10)
        elif len(inn_digits) < 12 and len(inn_digits) > 10:
            inn_digits = inn_digits.zfill(12)

        return inn_digits

    def select_excel_file(self):
        """Выбор Excel файла"""
        self.print_step(1, 4, "Выбор Excel файла")

        root = Tk()
        root.withdraw()

        print("📂 Откроется диалоговое окно для выбора Excel файла...")
        excel_file_path = filedialog.askopenfilename(
            title="Выберите Excel-файл с данными компаний",
            filetypes=[
                ("Excel files", "*.xlsx"),
                ("Excel files", "*.xls"),
                ("All files", "*.*")
            ]
        )

        if not excel_file_path:
            print("❌ Файл не выбран. Программа завершена.")
            return None

        print(f"✅ Выбран файл: {os.path.basename(excel_file_path)}")
        print(f"📍 Полный путь: {excel_file_path}")
        return excel_file_path

    def process_excel_file(self, excel_file_path):
        """Обработка Excel файла"""
        self.print_step(2, 4, "Обработка Excel файла")

        try:
            print("📖 Чтение Excel файла...")
            df = pd.read_excel(excel_file_path, header=None, dtype=str)

            print(f"📏 Размер файла: {df.shape[0]} строк, {df.shape[1]} столбцов")

            # Переименовываем столбцы
            df.columns = ['company_name', 'inn'] + [f'col_{i}' for i in range(2, len(df.columns))]

            # Очистка данных
            print("🧹 Очистка и нормализация данных...")
            df['company_name'] = df['company_name'].apply(lambda x: str(x).strip('\'"') if pd.notna(x) else x)
            df['inn'] = df['inn'].apply(self.normalize_inn)

            # Удаление пустых строк
            df_filtered = df.dropna(subset=['company_name', 'inn'])
            removed_rows = len(df) - len(df_filtered)

            if removed_rows > 0:
                print(f"🗑️ Удалено {removed_rows} пустых строк")

            company_data = list(zip(df_filtered['company_name'], df_filtered['inn']))

            print(f"✅ Готово к обработке: {len(company_data)} компаний")

            # Показываем первые 5 записей для проверки
            print("\n👀 Первые 5 записей для проверки:")
            for i, (name, inn) in enumerate(company_data[:5], 1):
                print(f"   {i}. {name[:50]}{'...' if len(name) > 50 else ''} (ИНН: {inn})")

            if len(company_data) > 5:
                print(f"   ... и еще {len(company_data) - 5} записей")

            return company_data

        except Exception as e:
            print(f"❌ Ошибка при обработке Excel файла: {e}")
            print("💡 Убедитесь, что:")
            print("   • Файл имеет формат .xlsx или .xls")
            print("   • Первый столбец содержит названия компаний")
            print("   • Второй столбец содержит ИНН")
            return None

    def confirm_processing(self, company_data):
        """Подтверждение обработки"""
        self.print_step(3, 4, "Подтверждение параметров")

        print(f"📋 Количество компаний: {len(company_data)}")
        print(f"📁 Папка сохранения: {self.download_folder}")
        print(f"⏱️ Примерное время выполнения: {len(company_data) * 8} секунд")

        self.print_separator()

        while True:
            confirm = input("❓ Начать скачивание выписок? (да/нет/показать список): ").lower().strip()

            if confirm in ['да', 'д', 'yes', 'y']:
                return True
            elif confirm in ['нет', 'н', 'no', 'n']:
                print("❌ Операция отменена пользователем.")
                return False
            elif confirm in ['показать список', 'список', 'показать', 'list']:
                print("\n📋 ПОЛНЫЙ СПИСОК КОМПАНИЙ:")
                for i, (name, inn) in enumerate(company_data, 1):
                    print(f"   {i:3d}. {name} (ИНН: {inn})")
                self.print_separator()
            else:
                print("⚠️ Пожалуйста, введите 'да', 'нет' или 'показать список'")

    def setup_browser(self):
        """Настройка браузера"""
        print("🌐 Настройка браузера...")

        chrome_options = Options()
        # Можно раскомментировать для работы в фоновом режиме
        # chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")

        # Настройки для скачивания файлов
        prefs = {
            "download.default_directory": self.download_folder,
            "download.prompt_for_download": False,
            "plugins.always_open_pdf_externally": True
        }
        chrome_options.add_experimental_option("prefs", prefs)

        try:
            self.browser = webdriver.Chrome(options=chrome_options)
            self.wait = WebDriverWait(self.browser, 15)
            print("✅ Браузер успешно запущен")
            return True
        except Exception as e:
            print(f"❌ Ошибка запуска браузера: {e}")
            print("💡 Убедитесь, что Chrome и ChromeDriver установлены")
            return False

    def process_companies(self, company_data):
        """Обработка списка компаний"""
        self.print_step(4, 4, "Скачивание выписок")

        self.stats['total'] = len(company_data)

        print(f"🎯 Начинаем обработку {len(company_data)} компаний...")
        start_time = time.time()

        for i, (name, inn) in enumerate(company_data, 1):
            try:
                self.print_progress(i, len(company_data), name)

                print(f"\n🏢 [{i}/{len(company_data)}] Обработка: {name}")
                print(f"🆔 ИНН: {inn}")

                # Переходим на сайт
                print("   🌐 Переход на сайт ЕГРЮЛ...")
                self.browser.get("https://egrul.nalog.ru/index.html")

                # Поиск
                print("   🔍 Поиск по ИНН...")
                search_box = self.wait.until(EC.presence_of_element_located((By.ID, "query")))
                search_box.clear()
                search_box.send_keys(inn)
                search_box.send_keys(Keys.RETURN)

                # Получение выписки
                print("   📄 Запрос выписки...")
                button = self.wait.until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, "button.btn-with-icon.btn-excerpt.op-excerpt"))
                )
                button.click()

                # Ожидание скачивания
                print("   ⏳ Ожидание скачивания...")
                time.sleep(6)

                # Переименование файла
                print("   📝 Переименование файла...")
                success, result = self.rename_latest_file(name)

                if success:
                    print(f"   ✅ Успешно: {result}")
                    self.stats['success'] += 1
                else:
                    print(f"   ⚠️ Файл скачан, но не переименован: {result}")
                    self.stats['success'] += 1

            except Exception as e:
                print(f"   ❌ Ошибка: {e}")
                self.stats['failed'] += 1

                # Пауза перед следующей попыткой
                time.sleep(2)

        # Итоговая статистика
        elapsed_time = time.time() - start_time

        print(f"\n🏁 ОБРАБОТКА ЗАВЕРШЕНА!")
        print(f"⏱️ Время выполнения: {elapsed_time:.1f} секунд")
        self.print_stats()

        if self.stats['success'] > 0:
            print(f"\n📁 Все файлы сохранены в: {self.download_folder}")

    def run(self):
        """Главная функция запуска"""
        try:
            self.print_header()

            # Выбор файла
            excel_file_path = self.select_excel_file()
            if not excel_file_path:
                return

            # Обработка Excel
            company_data = self.process_excel_file(excel_file_path)
            if not company_data:
                return

            # Подтверждение
            if not self.confirm_processing(company_data):
                return

            # Настройка браузера
            if not self.setup_browser():
                return

            # Обработка компаний
            self.process_companies(company_data)

        except KeyboardInterrupt:
            print("\n\n⚠️ Программа прервана пользователем")
        except Exception as e:
            print(f"\n❌ Критическая ошибка: {e}")
        finally:
            if self.browser:
                print("\n🔒 Закрытие браузера...")
                self.browser.quit()

            print("\n👋 Программа завершена. Нажмите Enter для выхода...")
            input()


if __name__ == "__main__":
    downloader = EgrulDownloader()
    downloader.run()