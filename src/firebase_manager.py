from google.cloud.firestore import Client

def send_products_to_firebase(products, database: Client):
    for product in products:
        document_reference = database.document(f"products/{product['id']}") #get/create the document
        document_reference.set(product) #populate the data in the document

def get_products_from_firebase(database: Client):
    products = database.collection('products')
    
    product_obj_list = []
    #get the data from firestore and store it in the list
    for doc_snapshot in products.stream():
        if doc_snapshot.exists:
            product_obj_list.append(doc_snapshot.to_dict())

    return product_obj_list