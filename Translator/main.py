import requests
from bs4 import BeautifulSoup
from googletrans import Translator

# Создаём переводчик
translator = Translator()


# Создаём функцию, которая будет получать информацию и переводить на русский
def get_russian_words():
    url = "https://randomword.com/"
    try:
        response = requests.get(url)

        # Создаём объект Soup
        soup = BeautifulSoup(response.content, "html.parser")
        # Получаем слово и удаляем пробелы
        english_word = soup.find("div", id="random_word").text.strip()
        # Получаем описание слова
        english_definition = soup.find("div", id="random_word_definition").text.strip()

        # Переводим слово и определение на русский
        russian_word = translator.translate(english_word, dest="ru").text
        russian_definition = translator.translate(english_definition, dest="ru").text

        # Возвращаем словарь с русскими словами и определениями
        return {
            "word": russian_word,
            "definition": russian_definition,
            "original_word": english_word  # Сохраняем оригинальное слово для проверки
        }
    # Функция, которая сообщит об ошибке, но не остановит программу
    except Exception as e:
        print(f"Произошла ошибка: {e}")
        return None


# Создаём функцию, которая будет делать саму игру
def word_game():
    print("Добро пожаловать в игру со словами на русском языке!")

    # Общие счетчики
    total_correct = 0
    total_incorrect = 0
    total_games = 0

    while True:
        # Получаем русское слово и определение
        word_dict = get_russian_words()

        if not word_dict:
            print("Не удалось получить слово. Попробуем еще раз.")
            continue

        word = word_dict.get("word")
        definition = word_dict.get("definition")
        original_word = word_dict.get("original_word")

        total_games += 1

        # Начинаем игру
        print(f"\n🎯 Игра #{total_games}")
        print(f"Значение слова - {definition}")
        hints_used = 0  # Счетчик использованных подсказок
        max_hints = 3  # Максимальное количество подсказок

        while True:
            user_answer = input("Что это за слово? (или 'подсказка' для помощи): ")

            # Проверяем, просит ли пользователь подсказку
            if user_answer.lower() in ['подсказка', 'подсказку', 'помощь', 'hint']:
                if hints_used >= max_hints:
                    print(f"❌ Вы уже использовали все {max_hints} подсказки!")
                    continue

                hints_used += 1

                if len(word) > hints_used:
                    # Показываем буквы по порядку: 1я, 2я, 3я
                    revealed_word = word[:hints_used] + "_" * (len(word) - hints_used)
                    print(f"Подсказка {hints_used}/{max_hints}: {revealed_word} ({len(word)} букв)")

                    # Дополнительная информация для каждой подсказки
                    if hints_used == 1:
                        print(f"💡 Английский вариант начинается с: {original_word[0]}")
                    elif hints_used == 2:
                        if len(original_word) > 1:
                            print(f"💡 Английский вариант: {original_word[:2]}...")
                    elif hints_used == 3:
                        if len(original_word) > 2:
                            print(f"💡 Английский вариант: {original_word[:3]}...")
                        print(f"⚠️ Это ваша последняя подсказка!")
                else:
                    # Если слово короткое, показываем всё
                    print(f"Подсказка {hints_used}/{max_hints}: {word} ({len(word)} букв)")
                    print(f"💡 Английский вариант: {original_word}")

                print(f"📊 Осталось подсказок: {max_hints - hints_used}")
                continue

            # Проверяем ответ (не учитываем регистр)
            # Принимаем как русский, так и английский вариант
            if (user_answer.lower() == word.lower() or
                    user_answer.lower() == original_word.lower()):
                total_correct += 1
                if hints_used == 0:
                    print("🏆 Все верно! Отлично, без подсказок!")
                elif hints_used == 1:
                    print("✅ Все верно! Хорошо, с одной подсказкой!")
                elif hints_used == 2:
                    print("👍 Все верно! Неплохо, с двумя подсказками!")
                else:
                    print("😊 Все верно! Получилось с подсказками!")
                break
            else:
                total_incorrect += 1
                print(f"❌ Ответ неверный, было загадано это слово - {word}")
                print(f"🇺🇸 Английский вариант: {original_word}")
                if hints_used > 0:
                    print(f"📝 Вы использовали {hints_used} подсказок")
                break

        # Показываем общую статистику
        accuracy = (total_correct / total_games) * 100 if total_games > 0 else 0
        print(f"\n📈 Общая статистика:")
        print(f"   ✅ Правильных ответов: {total_correct}")
        print(f"   ❌ Неправильных ответов: {total_incorrect}")
        print(f"   🎯 Точность: {accuracy:.1f}%")
        print(f"   🎮 Всего игр: {total_games}")

        # Создаём возможность закончить игру
        play_again = input("\nХотите сыграть еще раз? (да/нет): ")
        if play_again.lower() not in ['да', 'д', 'yes', 'y']:
            print("\n🎉 Спасибо за игру!")
            print(f"📊 Финальная статистика:")
            print(f"   ✅ Правильных ответов: {total_correct}")
            print(f"   ❌ Неправильных ответов: {total_incorrect}")
            print(f"   🎯 Итоговая точность: {accuracy:.1f}%")

            # Оценка результата
            if accuracy >= 90:
                print("🏆 Превосходный результат!")
            elif accuracy >= 70:
                print("🥉 Отличный результат!")
            elif accuracy >= 50:
                print("👍 Хороший результат!")
            else:
                print("💪 Есть куда расти!")
            break


if __name__ == "__main__":
    word_game()