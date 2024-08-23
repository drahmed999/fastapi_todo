from typing import Annotated,List
from fastapi import FastAPI,Depends,HTTPException
from sqlmodel import SQLModel,Field,Session,create_engine,select
from fastapi_learning import settings
from contextlib import asynccontextmanager


# in sql model  is  engine and in engine in session
#create sql model class 

class Todo(SQLModel,table=True):
    id:int|None=Field(default=None,primary_key=True)
    task:str=Field()
    is_completed:bool=Field(default=False)    

class Todo_get(SQLModel):
    id:int
    task:str
    is_completed:bool    
    
connection_string:str=str(settings.db_url).replace("postgresql","postgresql+psycopg")    


# echo reflects changes of engine in terminal and ssl for encryption
engine=create_engine(connection_string,connect_args={"sslmode":"require"},echo=True)



def create_tables():
    SQLModel.metadata.create_all(engine)    
# the metdata takes all the class u have created in the aql model  and creates it in your db



# lifespan so that first function to run is this i.e create tables foremost
@asynccontextmanager
async def lifespan(app:FastAPI):
   print("creating tables")
   create_tables()
   yield 





app=FastAPI(lifespan=lifespan,
            # title="hello world db",
            # version="0.0.1",
            # servers=[{
            #     "url":"http://127.0.0.1:8000",
            #     "description":"fast_api"
                
                
            # }]
            )
# session=Session(engine)
    
# todo:Todo=Todo(task="hello") 
    
# print ({"before todo":todo})
    
    
# session.add(todo)
# session.commit()
# print ({"after commit":todo})

# session.close()    
    

async def session_manager():
    with Session(engine) as session:
        yield session 
    
    

@app.get("/")
async def get():
    return{"hello":"world"}


@app.get("/all/",response_model=List[Todo_get])
async def get_all (session:Annotated[Session,Depends(session_manager)]):
    statement= select(Todo)
    all_todos=session.exec(statement).all()
    return  all_todos
@app.post("/create_todo",response_model=Todo_get)
async def create_todo(todo:Todo,session:Annotated[Session,Depends(session_manager)])->Todo_get:
    session.add(todo)
    session.commit()
    session.refresh(todo)
    return Todo_get.from_orm(todo)

@app.get("/get_single_todo/{todo_id}",response_model=Todo)
async def get_single_todo(todo_id:int,session:Annotated[Session,Depends(session_manager)]):
    statement=select(Todo).where(Todo.id==todo_id)
    single_todo=session.exec(statement).first()
    if not single_todo:
        raise HTTPException(detail="todo not found",status_code=404)
    return single_todo

@app.put('/edit_todo/{todo_id}',response_model=Todo_get)
async def edit_id(todo_id:int,todo:Todo,session:Annotated[Session,Depends(session_manager)])->Todo:
    statement=select(Todo).where(Todo.id==todo_id)
    existing_todo=session.exec(statement).first()
    if existing_todo:
        existing_todo.task=todo.task
        existing_todo.is_completed=todo.is_completed
        session.commit()
        session.refresh(existing_todo)
        return existing_todo
    else:
        raise  HTTPException(status_code=404 ,detail="todo not found")
@app.delete("/delete_Todo/{todo_id}",)
async def delete_todo(todo_id:int,session:Annotated[Session,Depends(session_manager)]):
    statement=session.get(Todo,todo_id)
    if statement:
        session.delete(statement)
        session.commit()
        return{"todo_deleted":"successfully"}
    else:
        raise HTTPException(status_code=404, detail="TODO NOT FOUND")