from gradio_client import Client
c = Client("JeremelleV/idmvton", verbose=True)
print(c.view_api())  # should print the /tryon endpoint
