from fastapi import FastAPI, File, UploadFile, HTTPException, Depends, Query, Body, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
import json
import pandas as pd

import logging

from llm import agent, product_agent
from preprocessing import prepare_product_df


product_df = prepare_product_df(pd.read_excel("data/products.xlsx"))

class API:
    def __init__(self):
        self.app = FastAPI()
        self.configure_routes()
        self.configure_cors()

    def configure_cors(self):
        origins = ["*"]  # Allow all origins
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=origins,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    def configure_routes(self):
        @self.app.post("/tagtitle/")
        async def tagtitle(request: Request):
            """Submits text and id

            Returns:
                list: result string, uuid string 
            """
            raw_body = await request.body()
            decoded_body = raw_body.decode("utf-8")
            logging.info(f"Raw body: {decoded_body}")
            data = json.loads(decoded_body)  # Parse JSON explicitly
            try:        
                result = await agent(data)
                result_final = await product_agent(result, product_df)
                
                return JSONResponse(content= result_final )
            except Exception as e:
                logging.error(f"{e} on data: {data} - saving without tags")
                return JSONResponse(content=raw_body)
            
        @self.app.post("/search/")
        async def search(query: str):
            "Returns a sorted list products based on the query results"
            

    
            