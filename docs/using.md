### **Create Person**

Створюється один запис з БД про певну особу.

|  Код сервісу  | Базова URL                       |
|:-------------:|----------------------------------|
| create_person | http://your-server-ip:8000/?Wsdl |

	
**Параметри запиту** виглядають наступним чином:
```
   <soapenv:Body>
      <spy:create_person>
         <!--Optional:-->
         <spy:person>
            <!--Optional:-->
            <mod:name> Сергій</mod:name>
            <!--Optional:-->
            <mod:surname> Сергій</mod:surname>
            <!--Optional:-->
            <mod:patronym> Ростиславович</mod:patronym>
            <!--Optional:-->
            <mod:dateOfBirth> 1973-07-16</mod:dateOfBirth>
            <!--Optional:-->
            <mod:gender>male</mod:gender>
            <!--Optional:-->
            <mod:rnokpp>7894561230</mod:rnokpp>
            <!--Optional:-->
            <mod:passportNumber>759123846</mod:passportNumber>
            <!--Optional:-->
            <mod:unzr> 19730716-19409</mod:unzr>
         </spy:person>
      </spy:create_person>
   </soapenv:Body>
```
де:

| Рівень <br/> вкладеності | Назва <br/>параметру | Тип даних                         | Значення параметру                                                                                                                        | Обов’язковість |
|:------------------------:|----------------------|-----------------------------------|-------------------------------------------------------------------------------------------------------------------------------------------|:--------------:|
|            3             | 	name                | 	String, <br/>min=1, <br/>max=128 | 	Ім’я                                                                                                                                     |      	Так      |
|            3             | 	surname             | 	String, <br/>min=1, <br/>max=128 | 	Прізвище                                                                                                                                 |      	Так      |
|            3             | 	patronym            | 	String, <br/>min=0,<br/> max=128 | 	По батькові                                                                                                                              |      	Ні       |
|            3             | 	dateOfBirth         | 	String                           | 	Дата народження                                                                                                                          |      	Так      |
|            3             | 	gender              | 	String                           | 	Стать                                                                                                                                    |      	Так      |
|            3             | 	rnokpp              | 	String                           | 	РНОКПП, 10 цифр                                                                                                                          |      	Так      |
|            3             | 	passportNumber      | 	String                           | 	Номер паспорта.<br/> **Для старого формату** – перші 2 символи - літери від А до Я, пробіл, 6 цифр.<br/> **Для нового формату** – 9 цифр |      	Так      |
|            3             | 	unzr                | 	String                           | 	УНЗР, 14 символів в форматі YYYYMMDD-XXXXC, де  YYYY – рік, MM – місяць, DD – день,  XXXXC – 5 цифр                                      |      Так       |


**Відповідь** у разі успішного опрацювання запиту (**Code=200**) виглядатиме наступним чином:
```
<tns:create_personResponse>
         <tns:create_personResult>Новий запис у базі даних створено успішно.</tns:create_personResult>
      </tns:create_personResponse>
```
де:

| Рівень <br/> вкладеності | Назва <br/>параметру     | Тип даних | Значення параметру                   | Обов’язковість |
|:------------------------:|--------------------------|-----------|--------------------------------------|:--------------:|
|            3             | 	tns:create_personResult | 	String   | 	Повідомлення про опрацювання запиту |      	Так      |


Відповідь у разі не успішного опрацювання запиту (**Code=500**) виглядатиме наступним чином:
```
   <soap11env:Body>
      <soap11env:Fault>
         <faultcode>soap11env:Client.SchemaValidationError</faultcode>
         <faultstring>:20:0:ERROR:SCHEMASV:SCHEMAV_CVC_LENGTH_VALID: Element '{models.person}passportNumber': [facet 'length'] The value has a length of '8'; this differs from the allowed length of '9'.</faultstring>
         <faultactor/>
      </soap11env:Fault>
   </soap11env:Body>
```
де:

| Рівень <br/> вкладеності | Назва <br/>параметру | Тип даних | Значення параметру | Обов’язковість |
|:------------------------:|----------------------|-----------|--------------------|:--------------:|
|            3             | 	faultcode           | 	String   | 	Код помилки       |      	Так      |
|            3             | faultstring          | String    | Опис помилки       |      Так       |

### **Get Person by Parameter**
Повертає записи з БД відповідно до заданих параметрів.

|       Код сервісу       | Базова URL                       |
|:-----------------------:|----------------------------------|
| get_person_by_parameter | http://your-server-ip:8000/?Wsdl |

**Параметри запиту**, що передаються в URL-строці виглядають наступним чином:
```
   <soapenv:Body>
      <spy:get_person_by_parameter>
         <!--Optional:-->
         <spy:params>
            <!--Optional:-->
            <mod:key>gender</mod:key>
            <!--Optional:-->
            <mod:value>male</mod:value>
         </spy:params>
      </spy:get_person_by_parameter>
   </soapenv:Body>
```
де:

| Рівень <br/> вкладеності | Назва <br/>параметру | Тип даних | Значення параметру                                                                             | Обов’язковість |
|:------------------------:|----------------------|-----------|------------------------------------------------------------------------------------------------|:--------------:|
|            3             | 	mod:key             | 	String   | 	Вказується конкретний параметр, що стосується певного запису в БД, наприклад, ім’я, УНЗР тощо |      	Так      |
|            3             | mod:value            | String    | Значення вказаного параметру                                                                   |      Так       |

**Відповідь** у разі успішного опрацювання запиту (**Code=200**) виглядатиме наступним чином:
```
   <soap11env:Body>
      <tns:get_person_by_parameterResponse>
         <tns:get_person_by_parameterResult>
            <s0:SpynePersonModel>
               <s0:name>Геннадій</s0:name>
               <s0:surname>Журба</s0:surname>
               <s0:patronym>Аврелійович</s0:patronym>
               <s0:dateOfBirth>2015-11-02</s0:dateOfBirth>
               <s0:gender>male</s0:gender>
               <s0:rnokpp>4258019232</s0:rnokpp>
               <s0:passportNumber>755236884</s0:passportNumber>
               <s0:unzr>20151102-17444</s0:unzr>
            </s0:SpynePersonModel>
            <s0:SpynePersonModel>
               <s0:name>Геннадій</s0:name>
               <s0:surname>Кармалюк</s0:surname>
               <s0:patronym>Климентович</s0:patronym>
               <s0:dateOfBirth>2017-02-21</s0:dateOfBirth>
               <s0:gender>male</s0:gender>
               <s0:rnokpp>3199817002</s0:rnokpp>
               <s0:passportNumber>987654321</s0:passportNumber>
               <s0:unzr>20170221-31678</s0:unzr>
            </s0:SpynePersonModel>
         </tns:get_person_by_parameterResult>
      </tns:get_person_by_parameterResponse>
   </soap11env:Body>
```
де:

| Рівень <br/> вкладеності | Назва <br/>параметру | Тип даних                         | Значення параметру                                                                                                                        | Обов’язковість |
|:------------------------:|----------------------|-----------------------------------|-------------------------------------------------------------------------------------------------------------------------------------------|:--------------:|
|            3             | 	name                | 	String, <br/>min=1, <br/>max=128 | 	Ім’я                                                                                                                                     |      	Так      |
|            3             | 	surname             | 	String, <br/>min=1, <br/>max=128 | 	Прізвище                                                                                                                                 |      	Так      |
|            3             | 	patronym            | 	String, <br/>min=0,<br/> max=128 | 	По батькові                                                                                                                              |      	Ні       |
|            3             | 	dateOfBirth         | 	String                           | 	Дата народження                                                                                                                          |      	Так      |
|            3             | 	gender              | 	String                           | 	Стать                                                                                                                                    |      	Так      |
|            3             | 	rnokpp              | 	String                           | 	РНОКПП, 10 цифр                                                                                                                          |      	Так      |
|            3             | 	passportNumber      | 	String                           | 	Номер паспорта.<br/> **Для старого формату** – перші 2 символи - літери від А до Я, пробіл, 6 цифр.<br/> **Для нового формату** – 9 цифр |      	Так      |
|            3             | 	unzr                | 	String                           | 	УНЗР, 14 символів в форматі YYYYMMDD-XXXXC, де  YYYY – рік, MM – місяць, DD – день,  XXXXC – 5 цифр                                      |      Так       |


**Відповідь** у разі не успішного опрацювання запиту (**Code=500**) виглядатиме наступним чином:

```
   <soap11env:Body>
      <soap11env:Fault>
         <faultcode>soap11env:Client</faultcode>
         <faultstring>Записів за заданими параметрами не знайдено.</faultstring>
         <faultactor/>
      </soap11env:Fault>
   </soap11env:Body> 
```
де:

| Рівень <br/> вкладеності | Назва <br/>параметру | Тип даних | Значення параметру | Обов’язковість |
|:------------------------:|----------------------|-----------|--------------------|:--------------:|
|            3             | 	faultcode           | 	String   | 	Код помилки       |      	Так      |
|            3             | faultstring          | String    | Опис помилки       |      Так       |

### **Edit Person**
Вносить зміни для певного запису з БД про певну особу.

| Код сервісу | Базова URL                       |
|:-----------:|----------------------------------|
| edit_person | http://your-server-ip:8000/?Wsdl |

**Параметри запиту** виглядають наступним чином:
```
   <soapenv:Body>
      <spy:edit_person>
         <!--Optional:-->
         <spy:person>
            <!--Optional:-->
            <mod:name>Геннадій</mod:name>
            <!--Optional:-->
            <mod:surname>Кармалюк</mod:surname>
            <!--Optional:-->
            <mod:patronym>Климентович</mod:patronym>
            <!--Optional:-->
            <mod:dateOfBirth>2017-02-21</mod:dateOfBirth>
            <!--Optional:-->
            <mod:gender>male</mod:gender>
            <!--Optional:-->
            <mod:rnokpp>3199817002</mod:rnokpp>
            <!--Optional:-->
            <mod:passportNumber>998099255</mod:passportNumber>
            <!--Optional:-->
            <mod:unzr>20170221-31678</mod:unzr>
         </spy:person>
      </spy:edit_person>
   </soapenv:Body>
```
де:

| Рівень <br/> вкладеності | Назва <br/>параметру | Тип даних                         | Значення параметру                                                                                                                        | Обов’язковість |
|:------------------------:|----------------------|-----------------------------------|-------------------------------------------------------------------------------------------------------------------------------------------|:--------------:|
|            3             | 	name                | 	String, <br/>min=1, <br/>max=128 | 	Ім’я                                                                                                                                     |      	Так      |
|            3             | 	surname             | 	String, <br/>min=1, <br/>max=128 | 	Прізвище                                                                                                                                 |      	Так      |
|            3             | 	patronym            | 	String, <br/>min=0,<br/> max=128 | 	По батькові                                                                                                                              |      	Ні       |
|            3             | 	dateOfBirth         | 	String                           | 	Дата народження                                                                                                                          |      	Так      |
|            3             | 	gender              | 	String                           | 	Стать                                                                                                                                    |      	Так      |
|            3             | 	rnokpp              | 	String                           | 	РНОКПП, 10 цифр                                                                                                                          |      	Так      |
|            3             | 	passportNumber      | 	String                           | 	Номер паспорта.<br/> **Для старого формату** – перші 2 символи - літери від А до Я, пробіл, 6 цифр.<br/> **Для нового формату** – 9 цифр |      	Так      |
|            3             | 	unzr                | 	String                           | 	УНЗР, 14 символів в форматі YYYYMMDD-XXXXC, де  YYYY – рік, MM – місяць, DD – день,  XXXXC – 5 цифр                                      |      Так       |

**Важливо!** Обмеження сервісу – не можна міняти поле unzr!

**Відповідь** у разі успішного опрацювання запиту (**Code=200**) виглядатиме наступним чином:
```
   <soap11env:Body>
      <tns:edit_personResponse>
         <tns:edit_personResult>Дані для UNZR: 20170221-31678 оновлено успішно</tns:edit_personResult>
      </tns:edit_personResponse>
   </soap11env:Body>
```

де:

| Рівень <br/> вкладеності | Назва <br/>параметру    | Тип даних | Значення параметру                   | Обов’язковість |
|:------------------------:|-------------------------|-----------|--------------------------------------|:--------------:|
|            3             | 	ttns:edit_personResult | 	String   | 	Повідомлення про опрацювання запиту |      	Так      |

**Відповідь** у разі не успішного опрацювання запиту (**Code=500**) може виглядати наступним чином:
```
   <soap11env:Body>
      <soap11env:Fault>
         <faultcode>soap11env:Server</faultcode>
         <faultstring>Запис з UNZR: 20170222-31678 не знайдено</faultstring>
         <faultactor/>
      </soap11env:Fault>
   </soap11env:Body>
```
де:

| Рівень <br/> вкладеності | Назва <br/>параметру | Тип даних | Значення параметру | Обов’язковість |
|:------------------------:|----------------------|-----------|--------------------|:--------------:|
|            3             | 	faultcode           | 	String   | 	Код помилки       |      	Так      |
|            3             | faultstring          | String    | Опис помилки       |      Так       |

### **Delete Person by UNZR**
Дозволяє видалити запис з БД тільки за УНЗР.

|      Код сервісу      | Базова URL                       |
|:---------------------:|----------------------------------|
| delete_person_by_unzr | http://your-server-ip:8000/?Wsdl |

**Параметри запиту** виглядають наступним чином:
```
<soapenv:Body>
      <spy:delete_person_by_unzr>
         <!--Optional:-->
         <spy:unzr>19980507-78945</spy:unzr>
      </spy:delete_person_by_unzr>
   </soapenv:Body> 
```
де:

| Рівень <br/> вкладеності | Назва <br/>параметру | Тип даних | Значення параметру            | Обов’язковість |
|:------------------------:|----------------------|-----------|-------------------------------|:--------------:|
|            3             | 	spy:unzr            | 	String   | 	Значення вказаного параметру |      	Так      |

**Відповідь** у разі успішного опрацювання запиту (**Code=200**) виглядатиме наступним чином:
```
   <soap11env:Body>
      <tns:delete_person_by_unzrResponse>
         <tns:delete_person_by_unzrResult>Успішно видалено 1 запис(ів) з UNZR 19980507-78945.</tns:delete_person_by_unzrResult>
      </tns:delete_person_by_unzrResponse>
   </soap11env:Body>
```
де:

| Рівень <br/> вкладеності | Назва <br/>параметру             | Тип даних | Значення параметру                   | Обов’язковість |
|:------------------------:|----------------------------------|-----------|--------------------------------------|:--------------:|
|            3             | 	tns:delete_person_by_unzrResult | 	String   | 	Повідомлення про опрацювання запиту |      	Так      |

**Відповідь** у разі не успішного опрацювання запиту (**Code=500**) може виглядати наступним чином:
```
   <soap11env:Body>
      <soap11env:Fault>
         <faultcode>soap11env:Client</faultcode>
         <faultstring>Запис з UNZR: 19980507-78945 не знайдено.</faultstring>
         <faultactor/>
      </soap11env:Fault>
   </soap11env:Body>
```
де:

| Рівень <br/> вкладеності | Назва <br/>параметру | Тип даних | Значення параметру | Обов’язковість |
|:------------------------:|----------------------|-----------|--------------------|:--------------:|
|            3             | 	faultcode           | 	String   | 	Код помилки       |      	Так      |
|            3             | faultstring          | String    | Опис помилки       |      Так       |

##
Матеріали створено за підтримки проєкту міжнародної технічної допомоги «Підтримка ЄС цифрової трансформації України (DT4UA)».
