import logging

import azure.functions as func


def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    productid = req.params.get('productid')
    if not productid:
        try:
            req_body = req.get_json()
        except ValueError:
            pass
        else:
            productid = req_body.get('productid')

    if productid:
        return func.HttpResponse(f"The product name for your product id {productid} is Starfruit Explosion and the description is This starfruit ice cream is sinfully delicious!")
    else:
        return func.HttpResponse(
             "This HTTP triggered function executed successfully. Pass the name in the query string or in the request body for a personalized response.",
             status_code=200
        )
