from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List

import sqlite3

app = FastAPI()

# SQLite database connection
conn = sqlite3.connect('items.db')
cursor = conn.cursor()

# Create items table if it doesn't exist
cursor.execute('''
    CREATE TABLE IF NOT EXISTS items (
        id INTEGER PRIMARY KEY,
        name TEXT,
        description TEXT
    )
''')
conn.commit()


# Pydantic model for Item
class Item(BaseModel):
    name: str
    description: str


# POST endpoint to add items
@app.post("/items/", response_model=Item)
async def create_item(item: Item):
    cursor.execute('''
        INSERT INTO items (name, description)
        VALUES (?, ?)
    ''', (item.name, item.description))
    conn.commit()
    return item


# GET endpoint to retrieve all items
@app.get("/items/", response_model=List[Item])
async def read_items():
    cursor.execute('''
        SELECT name, description FROM items
    ''')
    items = cursor.fetchall()
    return [{"name": name, "description": description} for name, description in items]


# GET endpoint to retrieve a single item by ID
@app.get("/items/{item_id}", response_model=Item)
async def read_item(item_id: int):
    cursor.execute('''
        SELECT name, description FROM items WHERE id=?
    ''', (item_id,))
    item = cursor.fetchone()
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return {"name": item[0], "description": item[1]}


# DELETE endpoint to delete an item by ID
@app.delete("/items/{item_id}", response_model=Item)
async def delete_item(item_id: int):
    cursor.execute('''
        SELECT name, description FROM items WHERE id=?
    ''', (item_id,))
    item = cursor.fetchone()
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")

    cursor.execute('''
        DELETE FROM items WHERE id=?
    ''', (item_id,))
    conn.commit()
    return {"name": item[0], "description": item[1]}

# Esta parte se añade para ejecutar el servidor Uvicorn
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

