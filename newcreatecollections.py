from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.orm.exc import MultipleResultsFound


from database_setup import Collection, Base, ArticleCollection, User, Comments

engine = create_engine('sqlite:///collectionsarticlesusers.db?check_same_thread=false')
# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
# A DBSession() instance establishes all conversations with the database
# and represents a "staging zone" for all the objects loaded into the
# database session object. Any change made against the objects in the
# session won't be persisted into the database until you call
# session.commit(). If you're not happy about the changes, you can
# revert all of them back to the last commit by calling
# session.rollback()
session = DBSession()

# collection 1
User1 = session.query(User).filter_by(id=1).one()

art1 = session.query(ArticleCollection).filter_by(id=4).one()

comment1 = Comments(user_id=1, article_id=4, title = "test",
						 text="Expert believe this season is the most abundant season in terms of vegitables. This is shown clearly in the large spread of faga plant all over the peninsula",
						 article_item=art1, user=User1)

session.add(comment1)
session.commit()

art2 = Comments(user_id=1, title="This is a test for comments db", article_id=4,
						 text="Expert believe this season is the most abundant season in terms of vegitables.all over the peninsula",
						user=User1)
session.add(art2)
session.commit()




# art3 = Comments(user_id=1, name="Hot And Long Summer, Weather Experts Forewarning", collection_id=col2.id,
#                          description="From late May to early September",
# 						 text="Cattle herders are advised to supply plenty of water and sunshade for their livestock in order to shield it from the flaming-hot sun",
# 						 collection=col2, user=User1)

# session.add(art3)
# session.commit()

# art4 = ArticleCollection(user_id=1, name="Vacationers Are In For A Wide Variety Of Activities This Summer", collection_id=col2.id,
#                          description="Activities include conserts, festivals and sports tournaments",
# 						 text="Tis vacation is like no other in country",
# 						 collection=col2, user=User1)
# session.add(art4)
# session.commit()

print "added 2 comments to article no. 4!"
