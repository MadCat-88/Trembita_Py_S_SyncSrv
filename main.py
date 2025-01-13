import logging
from spyne import Application, rpc, ServiceBase, Unicode, Iterable
from spyne.protocol.soap import Soap11
from spyne.server.wsgi import WsgiApplication
from spyne.model.fault import Fault
import models.person
import models.search
import utils.config_utils
import utils.get_person
import utils.validation
from utils.validation import TrSOARValidationERROR
import utils.delete_person
import utils.update_person
import utils.create_peson
from utils.logging_headers import log_soap_headers
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from contextlib import contextmanager

# Цей вебсервіс є частиною навчальних матеріалів для розробників системи "Трембіта".
# Вебсервіс, як приклад, логує всі HTTP-заголовки, які отримує з запитами.
# У промисловому сервісі слід передбачити логування службових заголовків системи "Трембіта".
# Перелік службових заголовків системи "Трембіта":
# Uxp-Clien
# Uxp-Service
# Uxp-Queryid
# Uxp-Userid
# Uxp-Purpose-Ids
# Uxp-Subject-Id

try:

    # Завантаження конфігурації
    conf_obj = utils.config_utils.load_config('config.ini')

    service_host = utils.config_utils.get_config_param(conf_obj, 'service', 'host_interface', 'SERVICE_HOST_INTERFACE', default='0.0.0.0')
    service_port = utils.config_utils.get_config_param(conf_obj, 'service', 'service_port', 'SERVICE_PORT_INTERFACE', default='8080')

    # Налаштовуємо логування
    logger = logging.getLogger(__name__)
    logger.info("Configuration loaded")

    # Встановлення обраного рівня логування для усіх модулів
    for logger_name in logging.root.manager.loggerDict:
        pass

    # Отримуємо URL бази даних
    SQLALCHEMY_DATABASE_URL = utils.config_utils.get_database_url(conf_obj)

except ValueError as e:
    logging.critical(f"Failed to load configuration: {e}")
    raise ValueError (f"Failed to load configuration: {e}")

# Створюємо об'єкт database, який буде використовуватися для виконання запитів
engine = create_engine(SQLALCHEMY_DATABASE_URL, pool_pre_ping=True)

# Створюємо фабрику сесій
Session = sessionmaker(bind=engine)
#db_session = Session()

@contextmanager
def get_db_session():
    """Контекстний менеджер для створення та закриття сесій бази даних."""
    session = Session()
    try:
        yield session
    except Exception as e:
        session.rollback()  # Відкат транзакції при помилці
        logging.critical(f"Помилка при отриманні сесії бази даних: {e}")
        raise e
    finally:
        session.close()  # Закриття сесії

class PersonService(ServiceBase):
    @rpc(models.search.SearchParams, _returns=Iterable(models.person.SpynePersonModel))
    def get_person_by_parameter(ctx, params):
        # Логування параметрів запиту
        logger.info(f"Запит на отримання даних з параметрами: {params}")
        # Логування заголовків SOAP-запиту
        log_soap_headers(ctx)

        params_dict = {params.key: params.value}

        try:
            # Валідація параметрів запиту
            utils.validation.validate_parameter(params.key, params.value, models.person.SpynePersonModel)
            with get_db_session() as db_session:
                # Виконання пошуку в базі даних
                result = utils.get_person.get_person_by_params_from_db(params_dict, db_session)
                # Перевірка на відсутність записів
                if result.code != 0 or not result.message:
                    logger.warning(f"Записів за параметрами {params} не знайдено.")
                    raise Fault(faultcode="Client", faultstring="Записів за заданими параметрами не знайдено.") # Fault з вказівкою помилки

        except TrSOARValidationERROR as e:
            logger.error(f"Помилка валідації параметрів: {e}")
            raise Fault(faultcode="Client", faultstring=f"Помилка валідіції: {e} ")  # Fault з вказівкою помилки

        except Fault as f:
            raise f  # Перехоплення та повторне підняття виключення Fault

        except Exception as e:
            logger.error(f"Сталась помилка під час обробки запиту на отримання даних з параметрами з бази даних: {e}")
            raise Fault(faultcode="Server", faultstring="Неочікувана помилка серверу")

        # Перетворення результату в список об'єктів SpynePersonModel
        persons = [
            models.person.SpynePersonModel(
                name=row.name,
                surname=row.surname,
                patronym=row.patronym,
                dateOfBirth=row.dateOfBirth,
                gender=row.gender,
                rnokpp=row.rnokpp,
                passportNumber=row.passportNumber,
                unzr=row.unzr
            ) for row in result.message
        ]
        return persons

    @rpc(Unicode, _returns=Unicode)
    def delete_person_by_unzr(ctx, unzr):
        logger.info(f"Запит на видалення запису з UNZR: {unzr}")
        try:
            # Валідація UNZR
            utils.validation.validate_parameter("unzr", unzr, models.person.SpynePersonModel)
            with get_db_session() as db_session:
                # Виконання запиту на видалення
                result = utils.delete_person.delete_person_by_unzr(unzr, db_session)
                if result.code == 0:
                    return result.message
                else:
                    logger.error(f"Виникла помилка серверу під час видалення: {result.message}")
                    raise Fault(faultcode="Client", faultstring=result.message)

        except TrSOARValidationERROR as e:
            logger.error(f"Помилка валідації UNZR: {e}")
            raise Fault(faultcode="Client", faultstring=f"Помилка валідіції: {e} ")  # Fault з вказівкою помилки

        except Fault as f:
             raise f  # Перехоплення та повторне підняття виключення Fault

        except Exception as e:
            logger.error(f"Сталась помилка під час обробки запиту на видалення запису у базі даних: {e}")
            raise Fault(faultcode="Server", faultstring="Неочікувана помилка")

    @rpc(models.person.SpynePersonModel, _returns=Unicode)
    def edit_person(ctx, person):
        logger.info(f"Запит на редагування запису для особи з UNZR: {person.unzr}")
        # Валідація надісланих даних
        try:
            models.person.SpynePersonModel.validate(person)

        except TrSOARValidationERROR as e:
            logger.error(f"Помилка валідації даних: {e}")
            raise Fault(faultcode="Client", faultstring=f"Помилка валідіції: {e} ")  # Fault з вказівкою помилки

        except Exception as e:
            logger.error(f"Неочікувана помилка при валідації даних: {e}")
            raise Fault(faultcode="Server", faultstring="Неочікувана помилка")

        person_dict = person.__dict__.copy()

        try:
            with get_db_session() as db_session:
                # Виконання запиту до БД
                result = utils.update_person.update_person_by_unzr(person_dict, db_session)
                if result.code == 0:
                    return result.message
                else:
                    logger.error(f"Сталась помилка при оновленні запису: {result.message}")
                    raise Fault(faultcode="Server", faultstring=result.message)

        except Fault as f:
            raise f  # Перехоплення та повторне підняття виключення Fault

        except Exception as e:
            logger.error(f"Сталась помилка під час обробки запиту на оновлення запису у базі даних: {e}")
            raise Fault(faultcode="Server", faultstring="Неочікувана помилка")

    @rpc(models.person.SpynePersonModel, _returns=Unicode)
    def create_person(ctx, person):
        logger.info(f"Запит на створення запису для особи з UNZR: {person.unzr}")
        # Валідація надісланих даних
        try:
            models.person.SpynePersonModel.validate(person)

        except TrSOARValidationERROR as e:
            logger.error(f"Помилка валідації даних: {e}")
            raise Fault(faultcode="Client", faultstring=f"Помилка валідіції: {e} ")  # Fault з вказівкою помилки

        except Exception as e:
            logger.error(f"Неочікувана помилка при валідації даних: {e}")
            raise Fault(faultcode="Server", faultstring="Неочікувана помилка")


        person_dict = person.__dict__.copy()

        try:
            with get_db_session() as db_session:
                # Виконання запиту до БД
                result = utils.create_peson.create_person(person_dict, db_session)
                if result.code == 0:
                    return result.message
                else:
                    logger.error(f"Сталась помилка при створенні запису: {result.message}")
                    raise Fault(faultcode="Server", faultstring=result.message)

        except Fault as f:
            raise f  # Перехоплення та повторне підняття виключення Fault

        except Exception as e:
            logger.error(f"Сталась помилка підчас обробки запиту на створення запису у базі даних: {e}")
            raise Fault(faultcode="Server", faultstring="Неочікувана помилка")




application = Application([PersonService],
                          tns='spyne.examples.person',
                          in_protocol=Soap11(validator='lxml'),
                          out_protocol=Soap11()
                          )

wsgi_application = WsgiApplication(application)

#цей блок коду виконується тільки при запуску за допомогою Python, без Gunicorn чи Unicorn чи іншого веб-сервера
if __name__ == '__main__':
    from wsgiref.simple_server import make_server

    #Конфігуруємо логування згідно параметрів у файлі кофігураці config.ini
    utils.config_utils.configure_logging(conf_obj)

    #Налаштовуємо адресу та порт для сервера
    server = make_server(service_host, int(service_port), wsgi_application)
    logging.info(f"listening to http://{service_host}:{service_port}")
    logging.info(f"wsdl is at: http://{service_host}:{service_port}/?wsdl")

    #from logging_tree import printout
    #printout()
    #Старт сервера
    server.serve_forever()
