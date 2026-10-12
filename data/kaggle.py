import kagglehub

# Download latest version
path = kagglehub.dataset_download("ahsan81/food-ordering-and-delivery-app-dataset")
# path = kagglehub.dataset_download("sasakitetsuya/comprehensive-analysis-of-restaurant-orders")


print("Path to dataset files:", path)