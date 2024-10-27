from sqlmodel import create_engine, SQLModel, Session

DATABASE_URL= "postgresql://postgres.kotrelswlnmzhguhcwgq:Reaper95$!code@aws-0-us-east-1.pooler.supabase.com:6543/postgres"

engine = create_engine(DATABASE_URL, echo=True)

def init_db():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session