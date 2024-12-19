import pathlib
from yandex_cloud_ml_sdk import YCloudML


def local_path(path: str) -> pathlib.Path:
    return pathlib.Path(__file__).parent / path


def main() -> None:
    folder_id = input("folder_id: ")
    auth_token = input("service account auth token: ")

    sdk = YCloudML(folder_id=folder_id,
                   auth=auth_token)

    model_name = input("model name: ")
    dataset_path = input("dataset path: ")

    dataset_draft = sdk.datasets.completions.from_path_deferred(
        path=local_path(dataset_path),
        upload_format='jsonlines',
        name=model_name+"_dataset",
    )

    operation = dataset_draft.upload()
    dataset = operation.wait()
    print(f'created new dataset {dataset=}')

    base_model = sdk.models.completions('yandexgpt-lite')

    new_model = base_model.tune(
        dataset,
        validation_datasets=dataset,
        name=model_name
    )
    print(f'resulting {new_model}')

    tuned_uri = new_model.uri
    print("\nuri: "+tuned_uri+"\n")


if __name__ == '__main__':
    main()
