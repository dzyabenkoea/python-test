import datetime as dt
from fastapi import FastAPI, HTTPException, Query
from database import engine, Session, Base, City, User, Picnic, PicnicRegistration
from weather_controller import WeatherController
from models import RegisterUserRequest, UserModel
from api_helpers import picnic_table_to_list

app = FastAPI()
weather_controller = WeatherController()


@app.get('/cities', summary='Список городов', tags=['Cities'])
def cities_list(q: str = Query(description="Название города", default=None)):
    """
    Получение списка городов
    """
    if q is not None:
        cities = Session().query(City).where(City.name.like(f'{q.capitalize()}%'))
    else:
        cities = Session().query(City).all()

    return [{'id': city.id, 'name': city.name, 'weather': city.weather} for city in cities]


@app.post('/cities', summary='Создание города', description='Создание города по его названию', tags=['Cities'])
def create_city(city: str = Query(description="Название города", default=None)):
    if city is None:
        raise HTTPException(status_code=400, detail='Параметр city должен быть указан')
    city_exists = weather_controller.check_existing(city)
    if not city_exists:
        raise HTTPException(status_code=400, detail='Параметр city должен быть существующим городом')

    city_object = Session().query(City).filter(City.name == city.capitalize()).first()
    if city_object is None:
        city_object = City(name=city.capitalize())
        s = Session()
        s.add(city_object)
        s.commit()

    return {'id': city_object.id, 'name': city_object.name, 'weather': city_object.weather}


@app.get('/users', summary='Список пользователей', tags=['Users'])
def users_list(age_min: int = Query(description='Минимальный возраст', default=None),
               age_max: int = Query(description='Максимальный возраст', default=None)):
    """
    Список пользователей
    """
    users = []
    if age_min is not None and age_max is not None:
        users = Session().query(User).where(age_min < User.age < age_max)
    elif age_min is not None:
        users = Session().query(User).where(User.age > age_min)
    elif age_max is not None:
        users = Session().query(User).where(User.age < age_max)
    else:
        users = Session().query(User).all()

    return [{
        'id': user.id,
        'name': user.name,
        'surname': user.surname,
        'age': user.age,
    } for user in users]


@app.post('/users', summary='Создание пользователя', response_model=UserModel, tags=['Users'])
def register_user(user: RegisterUserRequest):
    """
    Регистрация пользователя
    """
    user_object = User(**user.dict())
    s = Session()
    s.add(user_object)
    s.commit()

    return UserModel.from_orm(user_object)


@app.get('/picnics/', summary='Список пикников', tags=['Picnics'])
def all_picnics(datetime: dt.datetime = Query(default=None, description='Время пикника (по умолчанию не задано)'),
                past: bool = Query(default=True, description='Включая уже прошедшие пикники')):
    """
    Список всех пикников
    """
    table = Session().query(Picnic.id, Picnic.time, PicnicRegistration.user_id, City.name) \
        .join(PicnicRegistration, Picnic.id == PicnicRegistration.picnic_id, isouter=True) \
        .join(City, City.id == Picnic.city_id, isouter=True) \
        .group_by(Picnic.id, Picnic.time, PicnicRegistration.user_id, City.name) \
        .order_by(Picnic.id)
    print(table)
    if datetime is not None:
        table = table.filter(Picnic.time == datetime)
    if not past:
        table = table.filter(Picnic.time >= dt.datetime.now())

    return picnic_table_to_list(table)


@app.post('/picnics/', summary='Добавление пикника', tags=['Picnics'])
def picnic_add(city_id: int = None, datetime: dt.datetime = None):
    p = Picnic(city_id=city_id, time=datetime)
    s = Session()
    s.add(p)
    s.commit()

    return {
        'id': p.id,
        'city': Session().query(City).filter(City.id == p.city_id).first().name,
        'time': p.time,
    }


@app.post('/picnics/register', summary='Регистрация на пикник', tags=['Picnics'])
def register_to_picnic(picnic_id, user_id):
    picnic_registration = PicnicRegistration(picnic_id=picnic_id, user_id=user_id)
    s = Session()
    s.add(picnic_registration)
    s.commit()

    return {
        'id': picnic_registration.id,
    }
