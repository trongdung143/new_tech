from langchain_core.prompts import ChatPromptTemplate

tables_description = """
Database schema:

Table Product:
- id: SERIAL PRIMARY KEY
- name: TEXT NOT NULL
- price: NUMERIC NOT NULL
- stock: INT NOT NULL

Table Customer:
- id: SERIAL PRIMARY KEY
- name: TEXT NOT NULL
- email: TEXT NOT NULL

Table Orders:
- id: SERIAL PRIMARY KEY
- customer_id: INT NOT NULL REFERENCES Customer(id)
- order_date: TIMESTAMP NOT NULL DEFAULT NOW()

Table OrderItem:
- id: SERIAL PRIMARY KEY
- order_id: INT NOT NULL REFERENCES Orders(id)
- product_id: INT NOT NULL REFERENCES Product(id)
- quantity: INT NOT NULL


"""


tables_description_detailed = """
Database schema with example data (1 row per table):

Table Product:
- id: SERIAL PRIMARY KEY
- name: TEXT NOT NULL
- price: NUMERIC NOT NULL
- stock: INT NOT NULL
Example row:
1, 'Laptop', 1200, 10

Table Customer:
- id: SERIAL PRIMARY KEY
- name: TEXT NOT NULL
- email: TEXT NOT NULL
Example row:
1, 'Alice', 'alice@example.com'

Table Orders:
- id: SERIAL PRIMARY KEY
- customer_id: INT NOT NULL REFERENCES Customer(id)
- order_date: TIMESTAMP NOT NULL DEFAULT NOW()
Example row:
1, 1, '2025-11-20'

Table OrderItem:
- id: SERIAL PRIMARY KEY
- order_id: INT NOT NULL REFERENCES Orders(id)
- product_id: INT NOT NULL REFERENCES Product(id)
- quantity: INT NOT NULL
Example row:
1, 1, 1, 1  -- Alice bought 1 Laptop
"""

prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            f"""
            You are an expert SQL generator.
            {tables_description_detailed}

            For each user request in Vietnamese:
            1. Explain step by step how to translate the request into SQL.
            2. Finally, output the SQL query **once and only once** between the markers ---SQL START--- and ---SQL END---.
            3. Do not repeat explanations or SQL query.
            """,
        ),
        ("human", "{messages}"),
    ]
)
