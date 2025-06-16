import time
import csv
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import pandas as pd
import matplotlib.pyplot as plt
from bs4 import BeautifulSoup
import scrapy
from scrapy.crawler import CrawlerProcess


class DivanSpider(scrapy.Spider):
    """Scrapy spider для парсинга диванов"""
    name = 'divan_spider'
    start_urls = ['https://www.divan.ru/category/divany-i-kresla']

    def __init__(self):
        self.parsed_data = []

    def parse(self, response):
        divans = response.css('div.LlPhw')

        for divan in divans:
            try:
                price = divan.css('div.q5Uds span::text').get()
                if price:
                    self.parsed_data.append([price])
            except Exception as e:
                self.logger.error(f"Произошла ошибка при парсинге: {e}")
                continue

        # Сохраняем данные в CSV
        self.save_to_csv()

    def save_to_csv(self):
        with open("prices.csv", 'w', newline='', encoding='utf-8-sig') as file:
            writer = csv.writer(file, delimiter=';')
            writer.writerow(['Цена'])
            writer.writerows(self.parsed_data)
        print(f"Scrapy: Спарсено {len(self.parsed_data)} товаров")


def parse_with_selenium():
    """Парсинг с помощью Selenium"""
    print("Запуск парсинга с Selenium...")

    # Настройка Chrome опций для headless режима (опционально)
    chrome_options = Options()
    # chrome_options.add_argument("--headless")  # Раскомментируйте для скрытого режима

    driver = webdriver.Chrome(options=chrome_options)
    url = "https://www.divan.ru/category/divany-i-kresla"
    driver.get(url)
    time.sleep(3)

    divans = driver.find_elements(By.CSS_SELECTOR, 'div.LlPhw')
    parsed_data = []

    for divan in divans:
        try:
            price = divan.find_element(By.CSS_SELECTOR, 'div.q5Uds span').text
            parsed_data.append([price])
        except Exception as e:
            print(f"Произошла ошибка при парсинге: {e}")
            continue

    driver.quit()

    # Сохранение в CSV
    with open("prices.csv", 'w', newline='', encoding='utf-8-sig') as file:
        writer = csv.writer(file, delimiter=';')
        writer.writerow(['Цена'])
        writer.writerows(parsed_data)

    print(f"Selenium: Спарсено {len(parsed_data)} товаров")
    return len(parsed_data)


def parse_with_scrapy():
    """Парсинг с помощью Scrapy"""
    print("Запуск парсинга с Scrapy...")

    # Настройки для Scrapy
    custom_settings = {
        'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'ROBOTSTXT_OBEY': False,
        'CONCURRENT_REQUESTS': 1,
        'DOWNLOAD_DELAY': 1,
        'LOG_LEVEL': 'ERROR'  # Уменьшаем количество логов
    }

    # Запуск spider
    process = CrawlerProcess(custom_settings)
    process.crawl(DivanSpider)
    process.start()


def parse_with_requests():
    """Альтернативный метод с requests + BeautifulSoup (более простой)"""
    print("Запуск парсинга с requests + BeautifulSoup...")

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    url = "https://www.divan.ru/category/divany-i-kresla"
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        divans = soup.find_all('div', class_='LlPhw')

        parsed_data = []
        for divan in divans:
            try:
                price_element = divan.find('div', class_='q5Uds')
                if price_element:
                    price_span = price_element.find('span')
                    if price_span:
                        price = price_span.text
                        parsed_data.append([price])
            except Exception as e:
                print(f"Произошла ошибка при парсинге: {e}")
                continue

        # Сохранение в CSV
        with open("prices.csv", 'w', newline='', encoding='utf-8-sig') as file:
            writer = csv.writer(file, delimiter=';')
            writer.writerow(['Цена'])
            writer.writerows(parsed_data)

        print(f"Requests: Спарсено {len(parsed_data)} товаров")
        return len(parsed_data)
    else:
        print(f"Ошибка загрузки страницы: {response.status_code}")
        return 0


def clean_price(price):
    """Очистка и преобразование цены"""
    try:
        return int(price.replace('руб.', '').replace(' ', '').replace('₽', '').replace(',', '').strip())
    except ValueError as e:
        print(f"Ошибка при преобразовании цены '{price}': {e}")
        return 0


def clean_csv_data():
    """Очистка данных CSV"""
    input_file = 'prices.csv'
    output_file = 'cleaned_prices.csv'

    with open(input_file, mode='r', encoding='utf-8-sig') as infile, \
            open(output_file, mode='w', newline='', encoding='utf-8-sig') as outfile:

        reader = csv.reader(infile, delimiter=';')
        writer = csv.writer(outfile, delimiter=';')

        header = next(reader)
        writer.writerow(header)

        for row in reader:
            if row:
                clean_row = [clean_price(row[0])]
                writer.writerow(clean_row)

    print(f"Обработанные данные сохранены в файл {output_file}")


def create_histogram():
    """Создание гистограммы цен"""
    file_path = 'cleaned_prices.csv'
    data = pd.read_csv(file_path, delimiter=';')
    prices = data['Цена']

    # Удаляем нулевые значения (ошибки парсинга)
    prices = prices[prices > 0]

    plt.figure(figsize=(12, 8))
    plt.hist(prices, bins=15, edgecolor='black', color='skyblue', alpha=0.7)

    mean_price = prices.mean()
    median_price = prices.median()

    plt.axvline(mean_price, color='red', linestyle='--', linewidth=2,
                label=f'Средняя цена: {mean_price:.2f} руб.')
    plt.axvline(median_price, color='green', linestyle='-.', linewidth=2,
                label=f'Медианная цена: {median_price:.2f} руб.')

    plt.title('Гистограмма цен на диваны', fontsize=16, fontweight='bold')
    plt.xlabel('Цена (руб.)', fontsize=14)
    plt.ylabel('Количество товаров', fontsize=14)
    plt.grid(alpha=0.3)
    plt.legend()

    stats_text = f"Количество товаров: {len(prices)}\n" \
                 f"Средняя цена: {mean_price:.2f} руб.\n" \
                 f"Медианная цена: {median_price:.2f} руб.\n" \
                 f"Мин. цена: {prices.min()} руб.\n" \
                 f"Макс. цена: {prices.max()} руб."

    plt.figtext(0.15, 0.8, stats_text, bbox=dict(facecolor='white', alpha=0.8), fontsize=12)
    plt.tight_layout()
    plt.savefig('divan_prices_histogram.png', dpi=300, bbox_inches='tight')
    plt.show()

    print("Анализ данных завершен. Гистограмма сохранена в файл 'divan_prices_histogram.png'")


def main():
    """Главная функция с выбором метода парсинга"""
    print("Выберите метод парсинга:")
    print("1. Selenium (медленный, но надежный)")
    print("2. Scrapy (быстрый, асинхронный)")
    print("3. Requests + BeautifulSoup (простой и быстрый)")

    while True:
        try:
            choice = input("Введите номер (1, 2 или 3): ").strip()

            if choice == '1':
                parse_with_selenium()
                break
            elif choice == '2':
                parse_with_scrapy()
                break
            elif choice == '3':
                parse_with_requests()
                break
            else:
                print("Пожалуйста, введите 1, 2 или 3")
                continue

        except KeyboardInterrupt:
            print("\nОтменено пользователем")
            return
        except Exception as e:
            print(f"Произошла ошибка: {e}")
            continue

    # Обработка данных и создание графика
    try:
        clean_csv_data()
        create_histogram()
    except FileNotFoundError:
        print("Файл с данными не найден. Возможно, парсинг не был выполнен успешно.")
    except Exception as e:
        print(f"Ошибка при обработке данных: {e}")


if __name__ == "__main__":
    main()