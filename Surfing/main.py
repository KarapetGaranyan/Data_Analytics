from selenium import webdriver
from selenium.webdriver import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import random


def get_valid_links(browser):
    """Получает список валидных ссылок на статьи Википедии из текущей страницы"""
    links = browser.find_elements(By.CSS_SELECTOR, "#mw-content-text a[href^='/wiki/']")
    valid_links = []
    link_elements = []

    for link in links:
        link_text = link.text.strip()
        href = link.get_attribute('href')
        # Фильтрация ссылок: они должны быть на статьи, а не на служебные страницы
        if (link_text and not link_text.startswith("[") and len(link_text) > 1 and
                not ":" in href.split("/wiki/")[1] and
                not "#" in href and
                not "Служебная:" in href and
                not "Файл:" in href and
                not "Портал:" in href):
            if link_text not in [l[0] for l in valid_links]:  # Избегаем дубликатов
                valid_links.append((link_text, href))
                link_elements.append(link)
                if len(valid_links) >= 15:  # Ограничиваем количество ссылок
                    break

    return valid_links, link_elements


def browse_paragraphs(browser):
    """Функция для листания параграфов статьи"""
    # Получаем все параграфы на странице
    paragraphs = browser.find_elements(By.CSS_SELECTOR, "#mw-content-text p")
    valid_paragraphs = [p for p in paragraphs if p.text.strip()]

    if not valid_paragraphs:
        print("На этой странице нет параграфов для просмотра.")
        return

    current_idx = 0
    total = len(valid_paragraphs)

    while True:
        # Выводим текущий параграф
        print(f"\n--- Параграф {current_idx + 1}/{total} ---")
        print(valid_paragraphs[current_idx].text)

        # Запрашиваем действие пользователя
        action = input("\nДействия: [n] - следующий, [p] - предыдущий, [q] - выход в главное меню: ").lower()

        if action == 'n' or action == 'н':  # Следующий (с учетом русской раскладки)
            current_idx = (current_idx + 1) % total
        elif action == 'p' or action == 'з':  # Предыдущий (с учетом русской раскладки)
            current_idx = (current_idx - 1) % total
        elif action == 'q' or action == 'й':  # Выход (с учетом русской раскладки)
            break
        else:
            print("Неизвестная команда. Используйте [n], [p] или [q].")


def navigate_page(browser, level=0):
    """
    Навигация по странице Википедии.
    level - уровень вложенности (0 - первоначальная страница, >0 - связанная страница)
    """
    try:
        # Ожидание загрузки содержимого
        WebDriverWait(browser, 10).until(
            EC.presence_of_element_located((By.ID, "content"))
        )

        # Получаем заголовок текущей статьи
        title = browser.find_element(By.ID, "firstHeading").text
        print(f"\n{'=' * 50}")
        print(f"Текущая статья: {title}")
        print(f"{'=' * 50}")

        # Получаем первый абзац для краткого описания
        paragraphs = browser.find_elements(By.TAG_NAME, "p")
        for paragraph in paragraphs:
            if paragraph.text.strip():
                print(f"\nКраткое описание: {paragraph.text}")
                break

        while True:
            print("\nВыберите действие:")
            print("1. Листать параграфы текущей статьи")
            print("2. Перейти на одну из связанных страниц")
            print("3. Выйти", end="")

            if level > 0:
                print(" на предыдущую страницу")
            else:
                print(" из программы")

            choice = input("\nВаш выбор (1-3): ")

            if choice == "1":
                # Листать параграфы
                browse_paragraphs(browser)

            elif choice == "2":
                # Получаем список связанных страниц
                valid_links, link_elements = get_valid_links(browser)

                if not valid_links:
                    print("\nНе найдено связанных страниц для перехода.")
                    continue

                print("\nСвязанные страницы:")
                for i, (link_text, _) in enumerate(valid_links, 1):
                    print(f"{i}. {link_text}")

                try:
                    link_choice = int(input("\nВыберите номер страницы для перехода (0 для отмены): "))
                    if link_choice == 0:
                        continue
                    if 1 <= link_choice <= len(valid_links):
                        # Сохраняем текущий URL для возможности возврата
                        current_url = browser.current_url

                        # Переходим по выбранной ссылке
                        print(f"\nПереход на страницу: {valid_links[link_choice - 1][0]}")
                        link_elements[link_choice - 1].click()

                        # Рекурсивно вызываем навигацию по новой странице с увеличением уровня
                        navigate_page(browser, level + 1)

                        # После возврата с вложенной страницы, возвращаемся на текущую
                        browser.get(current_url)
                        WebDriverWait(browser, 10).until(
                            EC.presence_of_element_located((By.ID, "content"))
                        )
                    else:
                        print("Неверный номер страницы.")
                except ValueError:
                    print("Введите число.")

            elif choice == "3":
                # Выход
                if level > 0:
                    # Возврат на предыдущую страницу
                    return
                else:
                    # Выход из программы
                    print("Выход из программы.")
                    return True  # Сигнал для выхода из программы

            else:
                print("Неверный выбор. Пожалуйста, выберите 1, 2 или 3.")

    except Exception as e:
        print(f"Произошла ошибка при навигации: {e}")
        if level > 0:
            return
        else:
            return True


def search_wikipedia():
    """Основная функция программы для поиска в Википедии"""
    # Запрос у пользователя
    user_query = input("Введите запрос для поиска в Википедии: ")

    # Настройка Chrome
    chrome_options = Options()
    # Раскомментируйте следующую строку, если хотите запустить браузер в фоновом режиме
    # chrome_options.add_argument("--headless")

    # Инициализация браузера
    browser = webdriver.Chrome(options=chrome_options)

    try:
        # Переход на главную страницу Википедии
        browser.get("https://ru.wikipedia.org")

        # Поиск запроса
        search_input = browser.find_element(By.NAME, "search")
        search_input.clear()
        search_input.send_keys(user_query)
        search_input.send_keys(Keys.RETURN)

        # Ожидание загрузки результатов
        WebDriverWait(browser, 10).until(
            EC.presence_of_element_located((By.ID, "content"))
        )

        # Проверка, перешли ли мы сразу на страницу статьи или на страницу результатов поиска
        current_url = browser.current_url

        if "search" in current_url:
            try:
                # Мы на странице результатов поиска, нужно кликнуть на первый результат
                first_result = WebDriverWait(browser, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, ".mw-search-result-heading a"))
                )
                first_result.click()

                # Ожидание загрузки страницы статьи
                WebDriverWait(browser, 10).until(
                    EC.presence_of_element_located((By.ID, "content"))
                )
            except:
                print("Не найдено результатов поиска. Попробуйте другой запрос.")
                browser.quit()
                return False

        # Начинаем навигацию по странице
        exit_program = navigate_page(browser)

        # Если пользователь решил полностью выйти из программы
        if exit_program:
            return False
        else:
            # Предлагаем начать новый поиск
            new_search = input("\nХотите выполнить новый поиск? (да/нет): ").lower()
            if new_search == "да" or new_search == "д" or new_search == "y" or new_search == "yes":
                browser.quit()
                return True  # Сигнал для нового поиска

        return False

    except Exception as e:
        print(f"Произошла ошибка: {e}")
        return False

    finally:
        # Задержка перед закрытием браузера
        time.sleep(1)
        browser.quit()


def main():
    """Основная функция программы"""
    print("=" * 60)
    print("Программа для поиска информации в Википедии через консоль".center(60))
    print("=" * 60)

    continue_search = True
    while continue_search:
        continue_search = search_wikipedia()


if __name__ == "__main__":
    main()