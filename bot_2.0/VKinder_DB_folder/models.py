import sqlalchemy as sq
from sqlalchemy.orm import declarative_base, relationship


Base = declarative_base()


class User(Base):
    __tablename__ = 'user'

    vk_user_id = sq.Column(sq.Integer, primary_key=True)
    first_name = sq.Column(sq.String(length=20), nullable=False)
    sex = sq.Column(sq.Integer, nullable=False)
    age = sq.Column(sq.Integer, nullable=False)
    city = sq.Column(sq.String(length=20), nullable=False)

    user_offer = relationship('UserOffer', back_populates='user', cascade='all, delete')
    interest_person = relationship('InterestPerson', back_populates='user', cascade='all, delete')

    def __str__(self):
        return f'{self.vk_user_id, self.first_name, self.sex, self.age, self.city}'


class Offer(Base):
    __tablename__ = 'offer'

    vk_offer_id = sq.Column(sq.Integer, primary_key=True)
    first_name = sq.Column(sq.String(length=20), nullable=False)
    last_name = sq.Column(sq.String(length=20), nullable=False)
    sex = sq.Column(sq.Integer, nullable=False)
    age = sq.Column(sq.Integer, nullable=False)
    city = sq.Column(sq.String(length=20), nullable=False)

    user_offer = relationship('UserOffer', back_populates='offer', cascade='all, delete')
    photo = relationship('Photo', back_populates='offer', cascade='all, delete')
    interest_person = relationship('InterestPerson', back_populates='offer', cascade='all, delete')

    def __str__(self):
        return f'{self.vk_offer_id, self.first_name, self.last_name, self.sex, self.age, self.city}'


class UserOffer(Base):
    __tablename__ = 'user_offer'

    user_offer_id = sq.Column(sq.Integer, primary_key=True)
    vk_user_id = sq.Column(sq.Integer, sq.ForeignKey('user.vk_user_id', ondelete='CASCADE'), nullable=False)
    vk_offer_id = sq.Column(sq.Integer, sq.ForeignKey('offer.vk_offer_id', ondelete='CASCADE'), nullable=False)
    black_list = sq.Column(sq.Integer, nullable=False, default=0)
    favorite_list = sq.Column(sq.Integer, nullable=False, default=0)

    user = relationship('User', back_populates='user_offer')
    offer = relationship('Offer', back_populates='user_offer')

    def __str__(self):
        return f'{self.black_list}'


class Photo(Base):
    __tablename__ = 'photo'

    id_photo = sq.Column(sq.Integer, primary_key=True)
    vk_offer_id = sq.Column(sq.Integer, sq.ForeignKey('offer.vk_offer_id', ondelete='CASCADE'), nullable=False)

    offer = relationship('Offer', back_populates='photo')

    def __str__(self):
        return f'{self.vk_offer_id, self.photo_url}'


class Interest(Base):
    __tablename__ = 'interest'

    interest_id = sq.Column(sq.Integer, primary_key=True)
    interest = sq.Column(sq.String(length=50), nullable=False)

    interest_person = relationship('InterestPerson', back_populates='interest', cascade='all, delete')

    def __str__(self):
        return self.interest


class InterestPerson(Base):
    __tablename__ = 'interest_person'

    interest_person_id = sq.Column(sq.Integer, primary_key=True)
    vk_user_id = sq.Column(sq.Integer, sq.ForeignKey('user.vk_user_id', ondelete='CASCADE'))
    vk_offer_id = sq.Column(sq.Integer, sq.ForeignKey('offer.vk_offer_id', ondelete='CASCADE'))
    interest_id = sq.Column(sq.Integer, sq.ForeignKey('interest.interest_id', ondelete='CASCADE'), nullable=False)

    user = relationship('User', back_populates='interest_person')
    offer = relationship('Offer', back_populates='interest_person')
    interest = relationship('Interest', back_populates='interest_person')


def create_table(engine):
    Base.metadata.create_all(engine)
