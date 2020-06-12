Рассмотрим стандартную задачу анализа данных -- вычисление
пользовательской метрики с использование скрытого файла правильных меток
в задаче.

Для доступа к
[шаблонной задаче](https://contest.yandex.ru/admin/ng#/problem/215/2020_06_12/si57q5EHBf)
можно написать [@atolstikov](https://t.me/atolstikov). Будет
предоставлен доступ на чтение, и можно будет склонировать задачу.

Для запуска чекера на python, которому требуются дополнительные
библиотеки, используется следующий пайплайн:
* problem-with-checker, т.е. мы запустим собственную обертку на запуск
  решения под компилятором, у которого есть библиотеки, а потом
  интерпретируем вывод этого решения в чекере
* В настройках соревнования для задачи оставляем единственный компилятор
  yandexdataschool (данный компилятор иногда меняется в плане содержания
  библиотек, если требуется долгая поддержка задачи, свяжитесь в чате
  администраторов с командой сервиса). Если в соревновании все задачи
  одного типа, то можно оставить единственный компилятор на соревнование,
  если такие задачи не все, то на вкладке Посылки, настраиваем отдельный
  компилятор для задачи.
* Чтобы участники видимо сообщение об ошибках при вычислении метрики, в
  настройках соревнования нужно включить отображение вывода
  постпроцессора
* Копируем в задачу файлы: `Makefile`, `run.sh`, `doit.sh`,
  `postprocessor.py`, `score.py`
  * `Makefile` описывает два таргета `build` для стадии обработки
    присланного участником файла (в шаблонном случае данные копируются
    просто в файл `data.csv` из присланного участником, файла `doit.sh`)
    и стадии запуска на каждом тесте (для этого в задаче создан один
    фиктивный тест, запускается score.py)
  * `score.py` читает файл участника и файл настоящих меток и вычисляет
    метрику, если неверный формат, то выводит сообщение в $$, что
    позднее будет обработано чекером и постпроцессором
    * скрипт должен завершаться с кодом возврата 0
    * если что-то пошло не так в задаче, то можно предусмотреть какую
      обработки ошибки в чекере и там можно вызвать `quitf(_fail,
      message)`
    * если у участника что-то не так с форматом файла, то лучше ему об
      этом сообщить, используя механизм сообщения в знаках доллара
    * если с файлом участника все хорошо, то нужно вывести итоговый
      результат
    * **Так как используется механизм запуска решения для оценки файла с
      предсказаниями, то выводить нужно в тот файл, как указано в
      настройках задачи (в примере в файла `answers.csv`).**
* Дополнительные файлы/обработки
  * Файлы для компиляции: `Makefile`, `doit.sh`, `run.sh`, `score.py`,
    `true_answers.csv`
  * Файлы для времени запуска: `run.sh`, `score.py`, `true_answers.csv`
  * Файлы постпроцессинга: `postprocessor.py`
* Скомпилировать чекер `pointscmp.cpp`, выбрав тип "Код возврата
  testlib". Выставить опцию, что чекер выставляет баллы (он их
 транслирует из вывода `score.py`).

Опциональные параметры:
* открыть условие в формате html и удалить часть про ограничение на
  время и память, сохранить html
* Входной файл:    test.csv, данные предоставленные участнику, могут
  отсутствовать в задаче
* Выходной файл    answers.csv, имя файла, которое мы хотим ожидать от
  участника