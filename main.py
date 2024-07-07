import logging
from spyne import Application, rpc, ServiceBase, Integer, Unicode, Iterable
from spyne.protocol.soap import Soap11
from spyne.server.wsgi import WsgiApplication
from spyne.model.complex import ComplexModel
from spyne.model.primitive import String
from spyne.model.fault import Fault
import models.person
import models.search
import utils.config_utils
import utils.get_person
import utils.validation
import databases
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

try:
    conf_obj = utils.config_utils.load_config('config.ini')
    # Налаштовуємо логування
    utils.config_utils.configure_logging(conf_obj)
    logger = logging.getLogger(__name__)
    logger.info("Configuration loaded")
    # Отримуємо URL бази даних
    SQLALCHEMY_DATABASE_URL = utils.config_utils.get_database_url(conf_obj)
except ValueError as e:
    logging.critical(f"Failed to load configuration: {e}")
    exit(1)

# створюємо об'єкт database, який буде використовуватися для виконання запитів
#database = databases.Database(SQLALCHEMY_DATABASE_URL)

engine = create_engine(SQLALCHEMY_DATABASE_URL)
Session = sessionmaker(bind=engine)
db_session = Session()

people = {}
from datetime import datetime
class PersonService(ServiceBase):
    @rpc(models.search.SearchParams, _returns=Iterable(models.person.SpynePersonModel))
    def get_person_by_parameter(ctx, params):
        print(params)
        params_dict = {params.key: params.value}

        try:
            utils.validation.validate_parameter_name(params.key, models.person.SpynePersonModel)
            result = utils.get_person.get_person_by_params_from_db(params_dict, db_session)
        except Exception as e:
            raise Fault(faultcode="Server", faultstring=str(e))

        # Преобразуем результат в список объектов SpynePersonModel
        persons = [
            models.person.SpynePersonModel(
                id=row.id,
                name=row.name,
                surname=row.surname,
                patronym=row.patronym,
                dateOfBirth=row.dateOfBirth,
                gender=row.gender,
                rnokpp=row.rnokpp,
                passportNumber=row.passportNumber,
                unzr=row.unzr
            ) for row in result
        ]
        return persons

application = Application([PersonService],
    tns='spyne.examples.person',
    in_protocol=Soap11(validator='lxml'),
    out_protocol=Soap11()
)

wsgi_application = WsgiApplication(application)

if __name__ == '__main__':
    import logging
    from wsgiref.simple_server import make_server

    logging.basicConfig(level=logging.DEBUG)
    logging.getLogger('spyne.protocol.xml').setLevel(logging.DEBUG)

    server = make_server('127.0.0.1', 8000, wsgi_application)
    logging.info("listening to http://127.0.0.1:8000")
    logging.info("wsdl is at: http://127.0.0.1:8000/?wsdl")

    server.serve_forever()