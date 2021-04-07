# Final Task

Изучить библиотеки lxml, requests, приложение fiddler (установить на локальную машину), технологию xpath.

Исследовать поисковые запросы сайта авиакомпании https://www.airblue.com/ с помощью fiddler.

Написать приложение на python для вывода информации о полётах.

Главная функция приложения принимает 3-4 параметра командной строки:

    IATA-код откуда летим;
    IATA-код куда летим;
    Дата вылета;
    Дата возврата. Необязательный параметр. Если не задан, произвести поиск в одном направлении (one-way);


Главная функция должна вызывать дочерние функции по мере необходимости, и корректно обрабатывать возникающие ошибки. Приложение должно быть логически структурировано, каждая функция должна выполнять свою задачу, и быть настолько простой, насколько это возможно.

Если были заданы некорректные параметры поиска - вывести сообщение об ошибке с указанием некорректных параметров, предложить ввести их заново. Иначе произвести поиск по заданным параметрам.

В случае если для заданных машрута и дат найдены результаты, приложение пишет в стандартный вывод информацию о полётах:

    Точное время вылета и прилёта;
    Длительность перелёта;
    Варианты цен с указанием валюты и класса.


Вся информация должна быть извлечена со страницы с результатами поиска, включая валюту. В случае return полёта необходимо сформировать все возможные комбинации, указать классы, вывести конечную стоимость перелёта туда-обратно. Варианты должны быть отсортированы по цене.

Код приложения должен быть проверен утилитами flake8 и pylint, все замечания должны быть учтены. Также рекомендуется провести самостоятельные тесты приложения: на несуществующих маршрутах и датах, на пограничных значениях дат, и т.д. Все возникающие ошибки должны корректно обрабатываться.

Ошибки ввода должны обрабатываться гладко, выводя уведомление и предлагая пользователю ввести корректные данные.

 

Как и на предыдущих практических этапах, обязательно использование линтеров.

Готовый скрапер присылается на ревью. В случае критичных замечаний мы их пришлем ответным письмом, и их нужно будет исправить.

Иначе - ждем вас на собеседовании ;)
