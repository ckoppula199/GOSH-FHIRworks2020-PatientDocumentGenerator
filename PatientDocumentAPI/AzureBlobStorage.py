from azure.storage.blob import BlockBlobService


storage_account_key = 'storage_account_key'
storage_account_name = 'storage_account_name'


def get_data_from_azure(file_name, container_name):
    blob_service = BlockBlobService(account_name=storage_account_name, account_key=storage_account_key)
    blob_service.get_blob_to_path(container_name,
                                  file_name,
                                  file_name)


def write_data_to_azure(file_name, container_name):
    blob_service = BlockBlobService(account_name=storage_account_name, account_key=storage_account_key)
    blob_service.create_blob_from_path(container_name,
                                       file_name,
                                       file_name)
