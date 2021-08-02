# Metaconfig - ru
<br>
Python модуль для удобной работы с конфигурацией приложений.
Создан с целью минимизировать время на описание конфигурации приложения, и предоставить фронтенду метаданные о модели конфигурации для автоматического создания соответствующего UI.
<br>
## Пример использования

<span class="colour" style="color: rgb(136, 132, 111);"># Импортируем необходимые классы из модуля</span>

<span class="colour" style="color: rgb(249, 38, 114);">from</span><span class="colour" style="color: rgb(248, 248, 242);"> metaconfig </span><span class="colour" style="color: rgb(249, 38, 114);">import</span><span class="colour" style="color: rgb(248, 248, 242);"> IntField, Fieldset, ConfigRoot, ListField, StrField, BoolField, JsonFileConfigIO</span>

<br>
<span class="colour" style="color: rgb(136, 132, 111);"># Создадим набор полей, содержащий поля хост и порт</span>
<span class="colour" style="color: rgb(102, 217, 239);">*class*</span><span class="colour" style="color: rgb(248, 248, 242);"> </span><span class="colour" style="color: rgb(166, 226, 46);"><u>HostPort</u></span><span class="colour" style="color: rgb(248, 248, 242);">(</span><span class="colour" style="color: rgb(166, 226, 46);">*<u>Fieldset</u>*</span><span class="colour" style="color: rgb(248, 248, 242);">):</span>
<span class="colour" style="color: rgb(248, 248, 242);">    </span><span class="colour" style="color: rgb(136, 132, 111);"># Определим поле host как StrField с названием "Хост", подсказкой "IP адрес" и значеним по-умолчанию 0.0.0.0</span>
<span class="colour" style="color: rgb(248, 248, 242);">    host </span><span class="colour" style="color: rgb(249, 38, 114);">=</span><span class="colour" style="color: rgb(248, 248, 242);"> StrField(</span><span class="colour" style="color: rgb(253, 151, 31);">*label*</span><span class="colour" style="color: rgb(249, 38, 114);">=</span><span class="colour" style="color: rgb(230, 219, 116);">'Хост'</span><span class="colour" style="color: rgb(248, 248, 242);">, </span><span class="colour" style="color: rgb(253, 151, 31);">*default*</span><span class="colour" style="color: rgb(249, 38, 114);">=</span><span class="colour" style="color: rgb(230, 219, 116);">'0.0.0.0'</span><span class="colour" style="color: rgb(248, 248, 242);">, </span><span class="colour" style="color: rgb(253, 151, 31);">*hint*</span><span class="colour" style="color: rgb(249, 38, 114);">=</span><span class="colour" style="color: rgb(230, 219, 116);">"IP адрес"</span><span class="colour" style="color: rgb(248, 248, 242);">)</span>
<span class="colour" style="color: rgb(248, 248, 242);">    port </span><span class="colour" style="color: rgb(249, 38, 114);">=</span><span class="colour" style="color: rgb(248, 248, 242);"> IntField(</span><span class="colour" style="color: rgb(253, 151, 31);">*label*</span><span class="colour" style="color: rgb(249, 38, 114);">=</span><span class="colour" style="color: rgb(230, 219, 116);">'Порт'</span><span class="colour" style="color: rgb(248, 248, 242);">, </span><span class="colour" style="color: rgb(253, 151, 31);">*default*</span><span class="colour" style="color: rgb(249, 38, 114);">=</span><span class="colour" style="color: rgb(174, 129, 255);">11000</span><span class="colour" style="color: rgb(248, 248, 242);">)</span>

<br>
<span class="colour" style="color: rgb(136, 132, 111);"># Создадим другой набор полей</span>
<span class="colour" style="color: rgb(102, 217, 239);">*class*</span><span class="colour" style="color: rgb(248, 248, 242);"> </span><span class="colour" style="color: rgb(166, 226, 46);"><u>Server</u></span><span class="colour" style="color: rgb(248, 248, 242);">(</span><span class="colour" style="color: rgb(166, 226, 46);">*<u>Fieldset</u>*</span><span class="colour" style="color: rgb(248, 248, 242);">):</span>
<span class="colour" style="color: rgb(248, 248, 242);">    location </span><span class="colour" style="color: rgb(249, 38, 114);">=</span><span class="colour" style="color: rgb(248, 248, 242);"> StrField(</span><span class="colour" style="color: rgb(253, 151, 31);">*label*</span><span class="colour" style="color: rgb(249, 38, 114);">=</span><span class="colour" style="color: rgb(230, 219, 116);">"Местонахождение сервера"</span><span class="colour" style="color: rgb(248, 248, 242);">, </span><span class="colour" style="color: rgb(253, 151, 31);">*default*</span><span class="colour" style="color: rgb(249, 38, 114);">=</span><span class="colour" style="color: rgb(230, 219, 116);">''</span><span class="colour" style="color: rgb(248, 248, 242);">, </span><span class="colour" style="color: rgb(253, 151, 31);">*hint*</span><span class="colour" style="color: rgb(249, 38, 114);">=</span><span class="colour" style="color: rgb(230, 219, 116);">"Страна"</span><span class="colour" style="color: rgb(248, 248, 242);">)</span>
<span class="colour" style="color: rgb(248, 248, 242);">    </span><span class="colour" style="color: rgb(136, 132, 111);"># Используем определенный ранее набор полей с дополнительным пояснением</span>
<span class="colour" style="color: rgb(248, 248, 242);">    connection\_data </span><span class="colour" style="color: rgb(249, 38, 114);">=</span><span class="colour" style="color: rgb(248, 248, 242);"> HostPort(</span><span class="colour" style="color: rgb(253, 151, 31);">*label*</span><span class="colour" style="color: rgb(249, 38, 114);">=</span><span class="colour" style="color: rgb(230, 219, 116);">'Данные для подключения'</span><span class="colour" style="color: rgb(248, 248, 242);">)</span>

<br>
<span class="colour" style="color: rgb(136, 132, 111);"># Создадим корневой узел конфигурации </span>
<span class="colour" style="color: rgb(102, 217, 239);">*class*</span><span class="colour" style="color: rgb(248, 248, 242);"> </span><span class="colour" style="color: rgb(166, 226, 46);"><u>Config</u></span><span class="colour" style="color: rgb(248, 248, 242);">(</span><span class="colour" style="color: rgb(166, 226, 46);">*<u>ConfigRoot</u>*</span><span class="colour" style="color: rgb(248, 248, 242);">):</span>
<span class="colour" style="color: rgb(248, 248, 242);">    \_\_io\_class\_\_ </span><span class="colour" style="color: rgb(249, 38, 114);">=</span><span class="colour" style="color: rgb(248, 248, 242);"> JsonFileConfigIO(</span><span class="colour" style="color: rgb(230, 219, 116);">'proxy.settings'</span><span class="colour" style="color: rgb(248, 248, 242);">)</span>

<span class="colour" style="color: rgb(248, 248, 242);">    </span><span class="colour" style="color: rgb(136, 132, 111);"># Объявим список серверов</span>
<span class="colour" style="color: rgb(248, 248, 242);">    proxy\_pool </span><span class="colour" style="color: rgb(249, 38, 114);">=</span><span class="colour" style="color: rgb(248, 248, 242);"> ListField(</span>
<span class="colour" style="color: rgb(248, 248, 242);">            Server(</span>
<span class="colour" style="color: rgb(248, 248, 242);">                </span><span class="colour" style="color: rgb(253, 151, 31);">*label*</span><span class="colour" style="color: rgb(249, 38, 114);">=</span><span class="colour" style="color: rgb(230, 219, 116);">"Прокси-сервер"</span><span class="colour" style="color: rgb(248, 248, 242);">, </span>
<span class="colour" style="color: rgb(248, 248, 242);">                </span><span class="colour" style="color: rgb(253, 151, 31);">*default*</span><span class="colour" style="color: rgb(249, 38, 114);">=</span><span class="colour" style="color: rgb(248, 248, 242);">{</span>
<span class="colour" style="color: rgb(248, 248, 242);">                    </span><span class="colour" style="color: rgb(230, 219, 116);">'location'</span><span class="colour" style="color: rgb(248, 248, 242);">: </span><span class="colour" style="color: rgb(230, 219, 116);">'USA'</span><span class="colour" style="color: rgb(248, 248, 242);">,</span>
<span class="colour" style="color: rgb(248, 248, 242);">                    </span><span class="colour" style="color: rgb(230, 219, 116);">'connection\_data'</span><span class="colour" style="color: rgb(248, 248, 242);">: {</span>
<span class="colour" style="color: rgb(248, 248, 242);">                        </span><span class="colour" style="color: rgb(230, 219, 116);">'host'</span><span class="colour" style="color: rgb(248, 248, 242);">: </span><span class="colour" style="color: rgb(230, 219, 116);">'proxy.google.com'</span><span class="colour" style="color: rgb(248, 248, 242);">,</span>
<span class="colour" style="color: rgb(248, 248, 242);">                        </span><span class="colour" style="color: rgb(230, 219, 116);">'port'</span><span class="colour" style="color: rgb(248, 248, 242);">: </span><span class="colour" style="color: rgb(230, 219, 116);">'3128'</span>
<span class="colour" style="color: rgb(248, 248, 242);">                    }</span>
<span class="colour" style="color: rgb(248, 248, 242);">                }</span>
<span class="colour" style="color: rgb(248, 248, 242);">            ),</span>
<span class="colour" style="color: rgb(248, 248, 242);">            </span><span class="colour" style="color: rgb(253, 151, 31);">*label*</span><span class="colour" style="color: rgb(249, 38, 114);">=</span><span class="colour" style="color: rgb(230, 219, 116);">'Пул прокси-серверов'</span><span class="colour" style="color: rgb(248, 248, 242);">,</span>
<span class="colour" style="color: rgb(248, 248, 242);">            </span><span class="colour" style="color: rgb(253, 151, 31);">*default*</span><span class="colour" style="color: rgb(249, 38, 114);">=</span><span class="colour" style="color: rgb(248, 248, 242);">[]</span>
<span class="colour" style="color: rgb(248, 248, 242);">        )</span>
<span class="colour" style="color: rgb(248, 248, 242);">    </span>
<span class="colour" style="color: rgb(248, 248, 242);">    </span><span class="colour" style="color: rgb(136, 132, 111);"># и адрес собственного сервера</span>
<span class="colour" style="color: rgb(248, 248, 242);">    home </span><span class="colour" style="color: rgb(249, 38, 114);">=</span><span class="colour" style="color: rgb(248, 248, 242);"> Server(</span>
<span class="colour" style="color: rgb(248, 248, 242);">                </span><span class="colour" style="color: rgb(253, 151, 31);">*label*</span><span class="colour" style="color: rgb(249, 38, 114);">=</span><span class="colour" style="color: rgb(230, 219, 116);">'Домашний сервер'</span><span class="colour" style="color: rgb(248, 248, 242);">, </span>
<span class="colour" style="color: rgb(248, 248, 242);">                </span><span class="colour" style="color: rgb(253, 151, 31);">*default*</span><span class="colour" style="color: rgb(249, 38, 114);">=</span><span class="colour" style="color: rgb(248, 248, 242);">{</span>
<span class="colour" style="color: rgb(248, 248, 242);">                    </span><span class="colour" style="color: rgb(230, 219, 116);">'location'</span><span class="colour" style="color: rgb(248, 248, 242);">: </span><span class="colour" style="color: rgb(230, 219, 116);">'Russia'</span><span class="colour" style="color: rgb(248, 248, 242);">, </span>
<span class="colour" style="color: rgb(248, 248, 242);">                    </span><span class="colour" style="color: rgb(230, 219, 116);">'connection\_data'</span><span class="colour" style="color: rgb(248, 248, 242);">: {</span>
<span class="colour" style="color: rgb(248, 248, 242);">                        </span><span class="colour" style="color: rgb(230, 219, 116);">'host'</span><span class="colour" style="color: rgb(248, 248, 242);">: </span><span class="colour" style="color: rgb(230, 219, 116);">'home.server.com'</span><span class="colour" style="color: rgb(248, 248, 242);">, </span>
<span class="colour" style="color: rgb(248, 248, 242);">                        </span><span class="colour" style="color: rgb(230, 219, 116);">'port'</span><span class="colour" style="color: rgb(248, 248, 242);">: </span><span class="colour" style="color: rgb(174, 129, 255);">4123</span>
<span class="colour" style="color: rgb(248, 248, 242);">                    }</span>
<span class="colour" style="color: rgb(248, 248, 242);">                }</span>
<span class="colour" style="color: rgb(248, 248, 242);">            )</span>

<span class="colour" style="color: rgb(248, 248, 242);">    </span><span class="colour" style="color: rgb(136, 132, 111);"># а так же параметр, разрешающий отключить использование прокси</span>
<span class="colour" style="color: rgb(248, 248, 242);">    use\_proxy </span><span class="colour" style="color: rgb(249, 38, 114);">=</span><span class="colour" style="color: rgb(248, 248, 242);"> BoolField(</span><span class="colour" style="color: rgb(253, 151, 31);">*label*</span><span class="colour" style="color: rgb(249, 38, 114);">=</span><span class="colour" style="color: rgb(230, 219, 116);">'Использовать прокси'</span><span class="colour" style="color: rgb(248, 248, 242);">, </span><span class="colour" style="color: rgb(253, 151, 31);">*default*</span><span class="colour" style="color: rgb(249, 38, 114);">=</span><span class="colour" style="color: rgb(174, 129, 255);">True</span><span class="colour" style="color: rgb(248, 248, 242);">)</span>
<span class="colour" style="color: rgb(248, 248, 242);">    </span>

<span class="colour" style="color: rgb(136, 132, 111);"># Проинициализируем получившуюся конфигурацию</span>
<span class="colour" style="color: rgb(248, 248, 242);">config </span><span class="colour" style="color: rgb(249, 38, 114);">=</span><span class="colour" style="color: rgb(248, 248, 242);"> Config()</span>

<span class="colour" style="color: rgb(136, 132, 111);"># Получим из нее конкретное значение (автокомплиты нам помогут)</span>
<span class="colour" style="color: rgb(102, 217, 239);">print</span><span class="colour" style="color: rgb(248, 248, 242);">(config.home.location)</span>
<span class="colour" style="color: rgb(136, 132, 111);"># Получим все данные из конфигурации</span>
<span class="colour" style="color: rgb(102, 217, 239);">print</span><span class="colour" style="color: rgb(248, 248, 242);">(config.as\_dataset())</span>
<span class="colour" style="color: rgb(136, 132, 111);"># Получим метаданные о конфигурации</span>
<span class="colour" style="color: rgb(102, 217, 239);">print</span><span class="colour" style="color: rgb(248, 248, 242);">(config.as\_metadata())</span>
<span class="colour" style="color: rgb(136, 132, 111);"># Точечно обновим один из параметров</span>
<span class="colour" style="color: rgb(248, 248, 242);">config.update({</span><span class="colour" style="color: rgb(230, 219, 116);">'use\_proxy'</span><span class="colour" style="color: rgb(248, 248, 242);">: </span><span class="colour" style="color: rgb(174, 129, 255);">False</span><span class="colour" style="color: rgb(248, 248, 242);">})</span>
<br>
## Сущности

### Поле

Базовая сущность. Ее свойства - это тип переносимых данных, человекочитаемое название, описание, текущее значение и значение по-умолчанию.

### Список полей

Сущность, позволяющая хранить в себе любое количество полей одинакового типа. Также является полем.

### Набор полей

Сущность для компановки нескольких полей в самостоятельный объект.
Ее свойства - это экземпляры полей. Также является полем, что позволяет ей содержать в качестве свойств экземпляры самой себя.
<br>
## Типы

### metaconfig.types.MetaFieldClass

Базовый класс поля. Реализует в себе абстрактный функционал по хранению метаданных и значений.
Является общим предком для всех классов иерархии.
Предоставляет унифицированный интерфейс для создания экземпляра поля, чтения, сериализации, валидации и записи его значения.

**НЕ ПРЕДНАЗНАЧЕНО ДЛЯ САМОСТОЯТЕЛЬНОГО ИСПОЛЬЗОВАНИЯ**
<br>
#### metaconfig.types.MetaFieldClass.validate(value)

Метод для валидации значения перед записью.
На вход принимает значение, которое подлежит записи.
В случае успеха возвращает None, в случае ошибки валидации поднимает ValueError

#### metaconfig.types.MetaFieldClass.normalize(value)

Метод для нормализации значения перед записью.
На вход принимает значение, которое подлежит записи.
Возвращает нормализованное значение.
Перед выполнением вызывает validate.

#### metaconfig.types.MetaFieldClass.as\_metadata() -> dict

Метод для иерархичной генерации метаданных о поле(ях).
Возвращает dict, содержащий все свойства, присущие полю.

#### metaconfig.types.MetaFieldClass.as\_dataset()

Метод для иехархичного получения данных из поля(ей).
Тип возвращаемого значения определяется реализацией.
<br>
### metaconfig.types.IntField

Поле
Наследуется от MetaFieldClass
Реализует поле с целочисленным значением.
Поддерживает автоматическую нормализацию из строки, если это возможно.

### metaconfig.types.StrField

Поле
Наследуется от MetaFieldClass
Реализует поле со строковым значением.
Приведет любое установленное значение к строке.

### metaconfig.types.FloatField

Поле
Наследуется от MetaFieldClass
Реализует поле со значением с плавающей точкой.
Поддерживает нормализацию из строки (если возможно) и целочисленного значения

### metaconfig.types.BoolField

Поле
Наследуется от MetaFieldClass
Реализует поле с булевым значением.
Поддерживает семантическую реализацию из целого числа и строки по правилам:
`value = int(value) != 0 || value = str(value).lower() == 'true'`

### metaconfig.types.ListField

Список полей
Наследуется от MetaFieldClass
Реализует хранилище для нескольких полей одинакогово типа
Обязательным аргуементом для инициализации является объект наследника MetaFieldClass для определения типа хранимых полей.

### metaconfig.types.Fieldset

Набор полей
Наследуется от MetaFieldClass
Реализует структурную единицу описания конфигурации - модель.
Не подлежит самостоятельному использованию.
Должна являться родительским классом для пользовательских классов, реализующих конкретную структуру конфигурации.

### metaconfig.types.ConfigRoot

Набор полей
Синглтон
Наследуется от Fieldset
Реализует корневую модель конфигурации.
Не подлежит самостоятельному использованию.
Реализует абстрактный функционал по чтению/записи описанной в классе-наследнике структуры конфигурации.
Экземпляр класса-наследника будет являться точкой входа для взаимодействия клиентского кода со структурой конфигурации.

#### metaconfig.types.ConfigRoot.\_\_io\_class\_\_

Статическое поле, подлежащее записи в классе-наследнике ConfigRoot
В качестве значения разрешается экземпляр metaconfig.io.ConfigIoInterface
Если не определен в классе-наследнике, то будет использован metaconfig.io.JsonFileConfiIO по-умолчанию.

### metaconfig.io.ConfigIOInterface

Интерфейс для чтения/записи параметров конфигурации.

#### metaconfig.io.ConfigIOInterface.parse(data: str) -> dict

Абстрактный метод, который должен реализовать парсинг сырых данных в словарь, соответствующий описанной структуре конфигурации.
На вход принимает data:str - сырые данные
Должен вернуть dict - данные, соответствующие структуре конфигурации.

#### metaconfig.io.ConfigIOInterface.serialize(dataset: dict) -> str

Абстрактный метод, который должен реализовать сериализацию текущих данных конфигурации в сырые данные, подлежащие записи на постоянный носитель.
На вход принимает dataset: dict - текущие данные конфигурации
Возвращает str - сырые данные.

#### metaconfig.io.ConfigIOInterface.read() -> dict

Абстрактный метод, который должен реализовать алгоритм чтения сырых данных.
Должен вызывать parse()
Должен вернуть dict, соответствующий структуре конфигурации.

#### metaconfig.io.ConfigIOInterface.write(dataset: dict)

Абстрактный метод, который дложен реализовать алгоритм записи структуры конфигурации в постоянное хранилище.
Должен вызывать serialize()
На вход принимает dataset: dict, содержащий все текущие значения конфигурации.

### metaconfig.io.JsonFileConfigIO

Наследник ConfigIOInterface
Реализует работу с файлов на жестком диске в формате JSON